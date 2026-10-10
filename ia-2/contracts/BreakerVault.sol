// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IPriceSource {
    /// @return Prix d'un jeton de collatéral dans l'actif du coffre, avec 18 décimales.
    function price() external view returns (uint256);
}

/// @title BreakerVault : coffre de prêt minimal muni d'un disjoncteur
/// @notice Les déposants apportent l'actif ; les emprunteurs le sortent contre un collatéral listé.
///         Trois rôles séparés portent la réponse à incident :
///         - CONFIG_ROLE liste les collatéraux (le pouvoir que l'attaquant détourne dans le scénario) ;
///         - GUARDIAN_ROLE ne peut que durcir le niveau de garde (limiter, puis mettre en pause) ;
///         - RESUME_ROLE, tenu par un humain, est le seul à pouvoir relancer le coffre.
///         Aucun rôle ne peut déplacer les fonds des déposants.
/// @dev Prototype de hackathon, non audité. Tous les jetons sont supposés avoir 18 décimales.
///      Pas d'intérêts ni de liquidations : ce n'est pas l'objet de la démonstration.
contract BreakerVault is AccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    bytes32 public constant CONFIG_ROLE = keccak256("CONFIG_ROLE");
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");
    bytes32 public constant RESUME_ROLE = keccak256("RESUME_ROLE");

    enum GuardLevel {
        Normal, // aucune restriction
        Limited, // sorties plafonnées par fenêtre de temps
        Paused // aucune entrée ni sortie, sauf les remboursements
    }

    struct Collateral {
        address priceSource;
        uint16 ltvBps; // part de la valeur du collatéral empruntable, en points de base
        bool listed;
    }

    struct Proposal {
        address priceSource;
        uint16 ltvBps;
        uint64 readyAt;
    }

    IERC20 public immutable asset;
    uint64 public immutable outflowWindow; // durée d'une fenêtre de plafonnement, en secondes
    uint256 public immutable limitedOutflowCap; // sorties maximales par fenêtre au niveau Limited

    GuardLevel public guardLevel;
    uint64 public listingDelay; // délai de sécurité entre la proposition et le listing d'un collatéral
    uint64 public windowStart;
    uint256 public windowOutflow;

    uint256 public totalDeposits;
    uint256 public totalDebt;
    mapping(address => uint256) public deposits;
    mapping(address => uint256) public debt;
    mapping(address => Collateral) public collaterals;
    mapping(address => Proposal) public proposals;
    mapping(address => mapping(address => uint256)) public collateralOf; // compte => jeton => quantité
    address[] public collateralList;

    event Deposited(address indexed account, uint256 amount);
    event Withdrawn(address indexed account, uint256 amount);
    event Borrowed(address indexed account, uint256 amount, uint256 debtAfter);
    event Repaid(address indexed account, uint256 amount, uint256 debtAfter);
    event CollateralDeposited(address indexed account, address indexed token, uint256 amount);
    event CollateralWithdrawn(address indexed account, address indexed token, uint256 amount);
    event CollateralProposed(address indexed token, address priceSource, uint16 ltvBps, uint64 readyAt);
    event CollateralListed(address indexed token, address priceSource, uint16 ltvBps);
    event ListingDelayChanged(uint64 previousDelay, uint64 newDelay);
    event GuardLevelChanged(GuardLevel previousLevel, GuardLevel newLevel, address indexed by, string reason);

    error VaultPaused();
    error OutflowCapExceeded(uint256 requested, uint256 remaining);
    error InsufficientLiquidity(uint256 requested, uint256 available);
    error InsufficientBalance();
    error NotListed();
    error ProposalNotReady(uint64 readyAt);
    error BorrowLimitExceeded(uint256 debtAfter, uint256 limit);
    error CannotLowerGuardLevel();
    error AlreadyNormal();
    error InvalidParameter();

    constructor(IERC20 asset_, address admin, uint64 listingDelay_, uint256 limitedOutflowCap_, uint64 outflowWindow_) {
        if (address(asset_) == address(0) || admin == address(0) || outflowWindow_ == 0) revert InvalidParameter();
        asset = asset_;
        listingDelay = listingDelay_;
        limitedOutflowCap = limitedOutflowCap_;
        outflowWindow = outflowWindow_;
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }

    modifier notPaused() {
        if (guardLevel == GuardLevel.Paused) revert VaultPaused();
        _;
    }

    // --- Déposants ---

    function deposit(uint256 amount) external nonReentrant notPaused {
        deposits[msg.sender] += amount;
        totalDeposits += amount;
        asset.safeTransferFrom(msg.sender, address(this), amount);
        emit Deposited(msg.sender, amount);
    }

    function withdraw(uint256 amount) external nonReentrant notPaused {
        if (deposits[msg.sender] < amount) revert InsufficientBalance();
        _recordOutflow(amount);
        deposits[msg.sender] -= amount;
        totalDeposits -= amount;
        asset.safeTransfer(msg.sender, amount);
        emit Withdrawn(msg.sender, amount);
    }

    // --- Emprunteurs ---

    function depositCollateral(address token, uint256 amount) external nonReentrant notPaused {
        if (!collaterals[token].listed) revert NotListed();
        collateralOf[msg.sender][token] += amount;
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        emit CollateralDeposited(msg.sender, token, amount);
    }

    function withdrawCollateral(address token, uint256 amount) external nonReentrant notPaused {
        if (collateralOf[msg.sender][token] < amount) revert InsufficientBalance();
        collateralOf[msg.sender][token] -= amount;
        uint256 limit = borrowLimit(msg.sender);
        if (debt[msg.sender] > limit) revert BorrowLimitExceeded(debt[msg.sender], limit);
        IERC20(token).safeTransfer(msg.sender, amount);
        emit CollateralWithdrawn(msg.sender, token, amount);
    }

    function borrow(uint256 amount) external nonReentrant notPaused {
        uint256 debtAfter = debt[msg.sender] + amount;
        uint256 limit = borrowLimit(msg.sender);
        if (debtAfter > limit) revert BorrowLimitExceeded(debtAfter, limit);
        _recordOutflow(amount);
        debt[msg.sender] = debtAfter;
        totalDebt += amount;
        asset.safeTransfer(msg.sender, amount);
        emit Borrowed(msg.sender, amount, debtAfter);
    }

    /// @notice Toujours possible, même en pause : rembourser ne fait qu'améliorer la situation du coffre.
    function repay(uint256 amount) external nonReentrant {
        if (debt[msg.sender] < amount) revert InsufficientBalance();
        debt[msg.sender] -= amount;
        totalDebt -= amount;
        asset.safeTransferFrom(msg.sender, address(this), amount);
        emit Repaid(msg.sender, amount, debt[msg.sender]);
    }

    // --- Configuration ---

    function proposeCollateral(address token, address priceSource, uint16 ltvBps) external onlyRole(CONFIG_ROLE) {
        if (token == address(0) || priceSource == address(0) || ltvBps == 0 || ltvBps > 10_000) revert InvalidParameter();
        uint64 readyAt = uint64(block.timestamp) + listingDelay;
        proposals[token] = Proposal(priceSource, ltvBps, readyAt);
        emit CollateralProposed(token, priceSource, ltvBps, readyAt);
    }

    function listCollateral(address token) external onlyRole(CONFIG_ROLE) {
        Proposal memory p = proposals[token];
        if (p.priceSource == address(0)) revert NotListed();
        if (block.timestamp < p.readyAt) revert ProposalNotReady(p.readyAt);
        if (!collaterals[token].listed) collateralList.push(token);
        collaterals[token] = Collateral(p.priceSource, p.ltvBps, true);
        delete proposals[token];
        emit CollateralListed(token, p.priceSource, p.ltvBps);
    }

    /// @dev Faiblesse volontaire du scénario : le délai de sécurité peut être réduit sans délai.
    ///      Un coffre sérieux protégerait ce réglage par le délai lui-même. Le moniteur doit
    ///      traiter toute baisse comme un signe précurseur.
    function setListingDelay(uint64 newDelay) external onlyRole(CONFIG_ROLE) {
        emit ListingDelayChanged(listingDelay, newDelay);
        listingDelay = newDelay;
    }

    // --- Disjoncteur ---

    /// @notice Le gardien ne peut que durcir : Normal, puis Limited, puis Paused. Il ne déplace aucun fonds.
    function escalate(GuardLevel newLevel, string calldata reason) external onlyRole(GUARDIAN_ROLE) {
        if (newLevel <= guardLevel) revert CannotLowerGuardLevel();
        emit GuardLevelChanged(guardLevel, newLevel, msg.sender, reason);
        guardLevel = newLevel;
        if (newLevel == GuardLevel.Limited) {
            windowStart = uint64(block.timestamp);
            windowOutflow = 0;
        }
    }

    /// @notice La relance est une décision humaine, portée par un rôle distinct du gardien.
    function resume(string calldata reason) external onlyRole(RESUME_ROLE) {
        if (guardLevel == GuardLevel.Normal) revert AlreadyNormal();
        emit GuardLevelChanged(guardLevel, GuardLevel.Normal, msg.sender, reason);
        guardLevel = GuardLevel.Normal;
    }

    // --- Lecture ---

    function liquidity() public view returns (uint256) {
        return asset.balanceOf(address(this));
    }

    function collateralCount() external view returns (uint256) {
        return collateralList.length;
    }

    /// @return limit Montant maximal que le compte peut devoir, d'après ses collatéraux et leurs prix courants.
    function borrowLimit(address account) public view returns (uint256 limit) {
        uint256 n = collateralList.length;
        for (uint256 i = 0; i < n; i++) {
            address token = collateralList[i];
            uint256 amount = collateralOf[account][token];
            if (amount == 0) continue;
            Collateral memory c = collaterals[token];
            uint256 value = (amount * IPriceSource(c.priceSource).price()) / 1e18;
            limit += (value * c.ltvBps) / 10_000;
        }
    }

    /// @return Sorties encore permises dans la fenêtre courante (illimité hors niveau Limited).
    function remainingOutflow() public view returns (uint256) {
        if (guardLevel != GuardLevel.Limited) return type(uint256).max;
        if (block.timestamp >= windowStart + outflowWindow) return limitedOutflowCap;
        return limitedOutflowCap > windowOutflow ? limitedOutflowCap - windowOutflow : 0;
    }

    function _recordOutflow(uint256 amount) private {
        uint256 available = liquidity();
        if (amount > available) revert InsufficientLiquidity(amount, available);
        if (guardLevel != GuardLevel.Limited) return;
        if (block.timestamp >= windowStart + outflowWindow) {
            windowStart = uint64(block.timestamp);
            windowOutflow = 0;
        }
        uint256 remaining = limitedOutflowCap > windowOutflow ? limitedOutflowCap - windowOutflow : 0;
        if (amount > remaining) revert OutflowCapExceeded(amount, remaining);
        windowOutflow += amount;
    }
}
