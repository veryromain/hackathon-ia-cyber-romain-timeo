// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IRiskRegistry {
    function levelOf(address account) external view returns (uint8);
}

/// @title TreasuryGuard : portefeuille de trésorerie à plusieurs signataires, avec garde antifraude
/// @notice Un paiement est proposé, approuvé par M signataires sur N, puis exécuté après un délai d'examen.
///         Pendant ce délai, le moniteur peut signaler le paiement : le portefeuille exige alors des
///         signatures supplémentaires (StepUp) ou impose en plus une mise en attente (Hold).
///         Le moniteur ne peut qu'ajouter cette friction. Il ne propose, n'approuve, n'exécute,
///         n'annule ni ne gèle rien, et ne peut jamais abaisser un niveau de risque.
/// @dev Prototype de hackathon, non audité. Un seul actif, supposé à 18 décimales.
contract TreasuryGuard is ReentrancyGuard {
    using SafeERC20 for IERC20;

    enum Risk {
        None,
        StepUp, // signatures supplémentaires
        Hold // signatures supplémentaires et délai d'attente
    }

    enum Kind {
        Payment,
        ReplaceOwner,
        ChangeThreshold
    }

    struct Config {
        uint64 reviewDelay; // délai d'examen de tout paiement, pendant lequel le moniteur peut le signaler
        uint64 holdDelay; // délai d'attente d'un paiement en Hold et de tout changement de configuration
        uint64 keyLifetime; // durée de validité d'une clé de signataire
        uint64 periodLength; // durée de la fenêtre du plafond
        uint256 periodCap; // sorties par fenêtre au-delà desquelles il faut des signatures supplémentaires
        uint8 stepUpExtra; // nombre de signatures supplémentaires exigées
    }

    struct Proposal {
        Kind kind;
        Risk risk;
        bool executed;
        bool cancelled;
        uint64 proposedAt;
        uint64 executableAfter;
        address proposer;
        address target; // bénéficiaire du paiement, ou nouveau signataire
        address subject; // signataire remplacé (ReplaceOwner)
        uint256 value; // montant, ou nouveau seuil
    }

    IERC20 public immutable asset;
    address public immutable riskOracle; // le moniteur ; adresse nulle = portefeuille sans garde
    IRiskRegistry public immutable registry; // registre des adresses signalées ; adresse nulle = aucun

    Config public config;
    uint256 public threshold;
    bool public frozen;

    address[] public ownerList;
    mapping(address => uint64) public keyExpiresAt; // 0 = pas signataire

    Proposal[] private _proposals;
    mapping(uint256 => mapping(address => bool)) public hasApproved;

    uint64 public windowStart;
    uint256 public windowSpent;

    uint256 public unfreezeRound;
    mapping(uint256 => mapping(address => bool)) public hasApprovedUnfreeze;

    event PaymentProposed(
        uint256 indexed id,
        address indexed proposer,
        address indexed to,
        uint256 amount,
        string memo,
        uint256 requiredApprovals,
        uint64 executableAfter
    );
    event ConfigProposed(
        uint256 indexed id,
        Kind kind,
        address indexed proposer,
        address target,
        address subject,
        uint256 value,
        uint256 requiredApprovals,
        uint64 executableAfter
    );
    event Approved(uint256 indexed id, address indexed owner, uint256 approvals, uint256 requiredApprovals);
    event RiskFlagged(
        uint256 indexed id,
        Risk level,
        string reason,
        address indexed by,
        uint256 requiredApprovals,
        uint64 executableAfter
    );
    event PaymentExecuted(uint256 indexed id, address indexed to, uint256 amount, address indexed executor);
    event Cancelled(uint256 indexed id, address indexed by, string reason);
    event OwnerReplaced(address indexed previousOwner, address indexed newOwner, uint64 keyExpiresAt);
    event ThresholdChanged(uint256 previousThreshold, uint256 newThreshold);
    event Frozen(address indexed by, string reason);
    event UnfreezeApproved(address indexed owner, uint256 approvals, uint256 requiredApprovals);
    event Unfrozen(address indexed by);

    error NotActiveOwner();
    error NotRiskOracle();
    error WalletFrozen();
    error NotFrozen();
    error NotPending();
    error NotAPayment();
    error AlreadyApproved();
    error TooEarly(uint64 executableAfter);
    error NotEnoughApprovals(uint256 approvals, uint256 requiredApprovals);
    error RiskCannotDecrease();
    error InvalidParameter();

    constructor(
        IERC20 asset_,
        address[] memory owners_,
        uint256 threshold_,
        address riskOracle_,
        IRiskRegistry registry_,
        Config memory config_
    ) {
        if (address(asset_) == address(0) || owners_.length == 0) revert InvalidParameter();
        if (threshold_ == 0 || threshold_ > owners_.length || config_.periodLength == 0) revert InvalidParameter();
        asset = asset_;
        riskOracle = riskOracle_;
        registry = registry_;
        config = config_;
        threshold = threshold_;
        uint64 expiry = _expiryFromNow();
        for (uint256 i = 0; i < owners_.length; i++) {
            address owner = owners_[i];
            if (owner == address(0) || keyExpiresAt[owner] != 0) revert InvalidParameter();
            keyExpiresAt[owner] = expiry;
            ownerList.push(owner);
        }
        windowStart = uint64(block.timestamp);
    }

    modifier onlyActiveOwner() {
        if (!isActiveOwner(msg.sender)) revert NotActiveOwner();
        _;
    }

    // --- Paiements ---

    function proposePayment(address to, uint256 amount, string calldata memo)
        external
        onlyActiveOwner
        returns (uint256 id)
    {
        if (frozen) revert WalletFrozen();
        if (to == address(0) || amount == 0) revert InvalidParameter();
        id = _newProposal(Kind.Payment, to, address(0), amount, config.reviewDelay);
        emit PaymentProposed(id, msg.sender, to, amount, memo, requiredApprovals(id), _proposals[id].executableAfter);
        _approve(id);

        // Règles appliquées par le portefeuille lui-même, sans attendre le moniteur.
        if (address(registry) != address(0)) {
            uint8 level = registry.levelOf(to);
            if (level > 0) _raiseRisk(id, level >= 2 ? Risk.Hold : Risk.StepUp, "FLAGGED_ADDRESS", address(registry));
        }
        if (_proposals[id].risk == Risk.None && _overCap(amount)) {
            _raiseRisk(id, Risk.StepUp, "OVER_PERIOD_CAP", address(this));
        }
    }

    function approve(uint256 id) external onlyActiveOwner {
        _requirePending(id);
        if (hasApproved[id][msg.sender]) revert AlreadyApproved();
        _approve(id);
    }

    /// @notice Seule action du moniteur : relever le niveau de risque d'un paiement en attente.
    function flagRisk(uint256 id, Risk level, string calldata reason) external {
        if (msg.sender != riskOracle || riskOracle == address(0)) revert NotRiskOracle();
        _requirePending(id);
        if (_proposals[id].kind != Kind.Payment) revert NotAPayment();
        if (level <= _proposals[id].risk) revert RiskCannotDecrease();
        _raiseRisk(id, level, reason, msg.sender);
    }

    function execute(uint256 id) external onlyActiveOwner nonReentrant {
        _requirePending(id);
        Proposal storage p = _proposals[id];
        // Le gel arrête les paiements, pas le remplacement d'un signataire compromis.
        if (frozen && p.kind == Kind.Payment) revert WalletFrozen();

        uint256 approvals = validApprovals(id);
        uint256 required = requiredApprovals(id);
        if (approvals < required) revert NotEnoughApprovals(approvals, required);

        // À l'unanimité des signataires, seul le délai d'examen de base s'applique : ils gardent le dernier mot.
        uint64 notBefore = p.executableAfter;
        if (approvals == ownerList.length) {
            uint64 base = p.proposedAt + config.reviewDelay;
            if (base < notBefore) notBefore = base;
        }
        if (block.timestamp < notBefore) revert TooEarly(notBefore);

        p.executed = true;
        if (p.kind == Kind.Payment) {
            _spend(p.value);
            asset.safeTransfer(p.target, p.value);
            emit PaymentExecuted(id, p.target, p.value, msg.sender);
        } else if (p.kind == Kind.ReplaceOwner) {
            _replaceOwner(p.subject, p.target);
        } else {
            if (p.value == 0 || p.value > ownerList.length) revert InvalidParameter();
            emit ThresholdChanged(threshold, p.value);
            threshold = p.value;
        }
    }

    function cancel(uint256 id, string calldata reason) external onlyActiveOwner {
        _requirePending(id);
        _proposals[id].cancelled = true;
        emit Cancelled(id, msg.sender, reason);
    }

    // --- Signataires et seuil : toujours avec signatures supplémentaires et délai d'attente ---

    function proposeReplaceOwner(address previousOwner, address newOwner) external onlyActiveOwner returns (uint256 id) {
        if (keyExpiresAt[previousOwner] == 0 || newOwner == address(0) || keyExpiresAt[newOwner] != 0) {
            revert InvalidParameter();
        }
        id = _newProposal(Kind.ReplaceOwner, newOwner, previousOwner, 0, config.holdDelay);
        _emitConfigProposed(id);
        _approve(id);
    }

    function proposeThreshold(uint256 newThreshold) external onlyActiveOwner returns (uint256 id) {
        if (newThreshold == 0 || newThreshold > ownerList.length) revert InvalidParameter();
        id = _newProposal(Kind.ChangeThreshold, address(0), address(0), newThreshold, config.holdDelay);
        _emitConfigProposed(id);
        _approve(id);
    }

    // --- Gel : un seul signataire suffit pour geler, il en faut davantage pour dégeler ---

    function freeze(string calldata reason) external onlyActiveOwner {
        if (frozen) revert WalletFrozen();
        frozen = true;
        emit Frozen(msg.sender, reason);
    }

    function approveUnfreeze() external onlyActiveOwner {
        if (!frozen) revert NotFrozen();
        if (hasApprovedUnfreeze[unfreezeRound][msg.sender]) revert AlreadyApproved();
        hasApprovedUnfreeze[unfreezeRound][msg.sender] = true;

        uint256 approvals;
        for (uint256 i = 0; i < ownerList.length; i++) {
            address owner = ownerList[i];
            if (hasApprovedUnfreeze[unfreezeRound][owner] && isActiveOwner(owner)) approvals++;
        }
        uint256 required = _withExtra(threshold);
        emit UnfreezeApproved(msg.sender, approvals, required);
        if (approvals >= required) {
            frozen = false;
            unfreezeRound++;
            emit Unfrozen(msg.sender);
        }
    }

    // --- Lecture ---

    function isActiveOwner(address account) public view returns (bool) {
        return keyExpiresAt[account] > block.timestamp;
    }

    function ownerCount() external view returns (uint256) {
        return ownerList.length;
    }

    function proposalCount() external view returns (uint256) {
        return _proposals.length;
    }

    function getProposal(uint256 id) external view returns (Proposal memory) {
        return _proposals[id];
    }

    /// @notice Ne compte que les signataires dont la clé est encore valide : remplacer un signataire
    ///         ou laisser sa clé expirer rend caduques les approbations données avec l'ancienne clé.
    function validApprovals(uint256 id) public view returns (uint256 approvals) {
        for (uint256 i = 0; i < ownerList.length; i++) {
            address owner = ownerList[i];
            if (hasApproved[id][owner] && isActiveOwner(owner)) approvals++;
        }
    }

    function requiredApprovals(uint256 id) public view returns (uint256) {
        Proposal storage p = _proposals[id];
        if (p.kind != Kind.Payment) return _withExtra(threshold);
        if (p.risk != Risk.None || _overCap(p.value)) return _withExtra(threshold);
        return threshold;
    }

    /// @return Sorties déjà exécutées dans la fenêtre courante du plafond.
    function spentInWindow() public view returns (uint256) {
        return block.timestamp >= windowStart + config.periodLength ? 0 : windowSpent;
    }

    // --- Interne ---

    function _newProposal(Kind kind, address target, address subject, uint256 value, uint64 delay)
        private
        returns (uint256 id)
    {
        id = _proposals.length;
        _proposals.push(
            Proposal({
                kind: kind,
                risk: Risk.None,
                executed: false,
                cancelled: false,
                proposedAt: uint64(block.timestamp),
                executableAfter: uint64(block.timestamp) + delay,
                proposer: msg.sender,
                target: target,
                subject: subject,
                value: value
            })
        );
    }

    function _emitConfigProposed(uint256 id) private {
        Proposal storage p = _proposals[id];
        emit ConfigProposed(id, p.kind, msg.sender, p.target, p.subject, p.value, requiredApprovals(id), p.executableAfter);
    }

    function _approve(uint256 id) private {
        hasApproved[id][msg.sender] = true;
        emit Approved(id, msg.sender, validApprovals(id), requiredApprovals(id));
    }

    function _raiseRisk(uint256 id, Risk level, string memory reason, address by) private {
        Proposal storage p = _proposals[id];
        p.risk = level;
        if (level == Risk.Hold) {
            uint64 heldUntil = uint64(block.timestamp) + config.holdDelay;
            if (heldUntil > p.executableAfter) p.executableAfter = heldUntil;
        }
        emit RiskFlagged(id, level, reason, by, requiredApprovals(id), p.executableAfter);
    }

    function _replaceOwner(address previousOwner, address newOwner) private {
        if (keyExpiresAt[previousOwner] == 0 || keyExpiresAt[newOwner] != 0) revert InvalidParameter();
        for (uint256 i = 0; i < ownerList.length; i++) {
            if (ownerList[i] == previousOwner) {
                ownerList[i] = newOwner;
                break;
            }
        }
        delete keyExpiresAt[previousOwner];
        uint64 expiry = _expiryFromNow();
        keyExpiresAt[newOwner] = expiry;
        emit OwnerReplaced(previousOwner, newOwner, expiry);
    }

    function _spend(uint256 amount) private {
        if (block.timestamp >= windowStart + config.periodLength) {
            windowStart = uint64(block.timestamp);
            windowSpent = 0;
        }
        windowSpent += amount;
    }

    function _overCap(uint256 amount) private view returns (bool) {
        return amount > config.periodCap || spentInWindow() > config.periodCap - amount;
    }

    function _withExtra(uint256 base) private view returns (uint256) {
        uint256 required = base + config.stepUpExtra;
        return required > ownerList.length ? ownerList.length : required;
    }

    function _expiryFromNow() private view returns (uint64) {
        uint256 expiry = block.timestamp + config.keyLifetime;
        return expiry > type(uint64).max ? type(uint64).max : uint64(expiry);
    }

    function _requirePending(uint256 id) private view {
        if (id >= _proposals.length || _proposals[id].executed || _proposals[id].cancelled) revert NotPending();
    }
}
