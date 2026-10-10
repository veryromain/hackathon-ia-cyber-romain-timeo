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
    uint64 public constant KEY_PROBATION = 2 days;
    bool public frozen;

    address[] public ownerList;
    mapping(address => uint64) public keyExpiresAt; // 0 = pas signataire
    mapping(address => uint64) public keyTrustedAfter; // clés initiales établies, clés remplacées en probation
    mapping(address => uint256) public keyEpoch; // une adresse réajoutée ne récupère jamais ses anciens votes

    Proposal[] private _proposals;
    mapping(uint256 => mapping(address => bool)) public hasApproved;
    mapping(uint256 => mapping(address => uint256)) private _approvalEpoch;

    uint64 public windowStart;
    uint256 public windowSpent;

    uint256 public unfreezeRound;
    mapping(uint256 => mapping(address => bool)) public hasApprovedUnfreeze;
    mapping(uint256 => mapping(address => uint256)) private _unfreezeEpoch;

    // --- Clé de contrainte ---
    // Un signataire menacé signe avec une seconde clé. À l'écran, tout se passe comme d'habitude ; en réalité,
    // la proposition devient inexécutable et les paiements s'arrêtent sans qu'aucun événement de gel soit émis.
    // Rien de tout cela n'est lisible par l'interface du contrat. Sur une chaîne publique, le stockage et le code
    // restent consultables : la discrétion vaut pour celui qui regarde l'écran de sa victime, pas pour un auditeur.
    mapping(bytes32 => address) private _duressOwner; // keccak256(clé de contrainte) => signataire
    mapping(address => bytes32) private _duressHashOf; // signataire => hash de sa clé de contrainte
    mapping(uint256 => bool) private _underDuress; // proposition touchée par une clé de contrainte
    mapping(address => bool) private _coerced; // signataire dont la clé de contrainte a servi : exclu du dégel
    bool private _silentFreeze;

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
    event OwnerProbationStarted(address indexed owner, uint64 trustedAfter, uint256 epoch);
    event KeyRevokedBySelf(address indexed previousOwner, address indexed newOwner);
    event Frozen(address indexed by, string reason);
    event UnfreezeApproved(address indexed owner, uint256 approvals, uint256 requiredApprovals);
    event Unfrozen(address indexed by);

    error NotActiveOwner();
    error NotRiskOracle();
    error OwnerInProbation(uint64 trustedAfter);
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
            keyTrustedAfter[owner] = uint64(block.timestamp);
            keyEpoch[owner] = 1;
            ownerList.push(owner);
        }
        windowStart = uint64(block.timestamp);
    }

    modifier onlyActiveOwner() {
        if (!isActiveOwner(msg.sender)) revert NotActiveOwner();
        _;
    }

    // --- Paiements ---

    function proposePayment(address to, uint256 amount, string calldata memo) external returns (uint256 id) {
        (address owner, bool duress) = _signer();
        if (frozen) revert WalletFrozen();
        if (to == address(0) || amount == 0) revert InvalidParameter();
        id = _newProposal(Kind.Payment, owner, to, address(0), amount, config.reviewDelay);
        emit PaymentProposed(id, owner, to, amount, memo, requiredApprovals(id), _proposals[id].executableAfter);
        _approveAs(id, owner, duress);

        // Règles appliquées par le portefeuille lui-même, sans attendre le moniteur.
        if (address(registry) != address(0)) {
            uint8 level = registry.levelOf(to);
            if (level > 0) _raiseRisk(id, level >= 2 ? Risk.Hold : Risk.StepUp, "FLAGGED_ADDRESS", address(registry));
        }
        if (_proposals[id].risk == Risk.None && _overCap(amount)) {
            _raiseRisk(id, Risk.StepUp, "OVER_PERIOD_CAP", address(this));
        }
    }

    function approve(uint256 id) external {
        (address owner, bool duress) = _signer();
        _requirePending(id);
        if (hasApproved[id][owner] && _approvalEpoch[id][owner] == keyEpoch[owner]) revert AlreadyApproved();
        _approveAs(id, owner, duress);
    }

    /// @notice Enregistre (ou retire, avec un hash nul) la clé de contrainte de l'appelant.
    /// @param duressKeyHash keccak256 de l'adresse de la clé de contrainte, sur 20 octets. Seul le hash est
    ///        inscrit : l'adresse n'apparaît sur la chaîne que le jour où la clé sert.
    function setDuressKey(bytes32 duressKeyHash) external onlyActiveOwner {
        if (duressKeyHash != bytes32(0)) {
            address holder = _duressOwner[duressKeyHash];
            if (holder != address(0) && holder != msg.sender) revert InvalidParameter();
        }
        bytes32 previous = _duressHashOf[msg.sender];
        if (previous != bytes32(0)) delete _duressOwner[previous];
        _duressHashOf[msg.sender] = duressKeyHash;
        if (duressKeyHash != bytes32(0)) _duressOwner[duressKeyHash] = msg.sender;
    }

    // --- Clé d'identité froide (extension de la clé de contrainte, décision de Romain du 10/10 22:10) ---
    // La même seconde clé, gardée hors ligne, sert aussi à couper sa propre clé de tous les jours si elle est volée :
    // sans quorum, sans délai, même portefeuille gelé. La nouvelle clé entre en probation comme toute clé remplacée,
    // donc un voleur qui tiendrait aussi la clé d'identité ne gagnerait aucun pouvoir immédiat. La clé d'identité
    // ne peut toujours ni payer, ni exécuter, ni annuler, ni dégeler : elle freine ou retire, jamais plus.

    /// @notice Révoque immédiatement la clé de tous les jours de l'appelant (identifié par sa clé d'identité)
    ///         et la remplace par `newKey`, qui entre en probation. Le lien avec la clé d'identité est conservé.
    function revokeMyKey(address newKey) external {
        bytes32 h = keccak256(abi.encodePacked(msg.sender));
        address owner = _duressOwner[h];
        if (owner == address(0) || !isActiveOwner(owner)) revert NotActiveOwner();
        if (newKey == address(0) || keyExpiresAt[newKey] != 0 || newKey == msg.sender) revert InvalidParameter();
        _replaceOwner(owner, newKey);
        delete _duressHashOf[owner];
        _duressHashOf[newKey] = h;
        _duressOwner[h] = newKey;
        emit KeyRevokedBySelf(owner, newKey);
    }

    /// @notice Seule action du moniteur : relever le niveau de risque d'un paiement en attente.
    function flagRisk(uint256 id, Risk level, string calldata reason) external {
        if (msg.sender != riskOracle || riskOracle == address(0)) revert NotRiskOracle();
        _requirePending(id);
        if (_proposals[id].kind != Kind.Payment) revert NotAPayment();
        if (level <= _proposals[id].risk) revert RiskCannotDecrease();
        _raiseRisk(id, level, reason, msg.sender);
    }

    function execute(uint256 id) external nonReentrant {
        (address owner, bool duress) = _signer();
        _requirePending(id);
        Proposal storage p = _proposals[id];
        // Le gel arrête les paiements, pas le remplacement d'un signataire compromis.
        if (frozen && p.kind == Kind.Payment) revert WalletFrozen();

        uint256 approvals = validApprovals(id);
        uint256 required = requiredApprovals(id);
        if (approvals < required) revert NotEnoughApprovals(approvals, required);

        // Contrainte : la même erreur qu'une mise en attente en cours, avec une échéance plausible qui recule.
        if (duress || _underDuress[id] || (_silentFreeze && p.kind == Kind.Payment)) {
            revert TooEarly(uint64(block.timestamp) + config.holdDelay);
        }

        // Le recours unanime concerne les paiements, jamais la gouvernance.
        // Sur un paiement renforcé, les clés en probation ne peuvent pas fournir cette unanimité.
        uint64 notBefore = p.executableAfter;
        if (p.kind == Kind.Payment && approvals == ownerList.length) {
            uint64 base = p.proposedAt + config.reviewDelay;
            if (base < notBefore) notBefore = base;
        }
        if (block.timestamp < notBefore) revert TooEarly(notBefore);

        p.executed = true;
        if (p.kind == Kind.Payment) {
            _spend(p.value);
            asset.safeTransfer(p.target, p.value);
            emit PaymentExecuted(id, p.target, p.value, owner);
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

    function proposeReplaceOwner(address previousOwner, address newOwner) external returns (uint256 id) {
        (address owner, bool duress) = _signer();
        if (keyExpiresAt[previousOwner] == 0 || newOwner == address(0) || keyExpiresAt[newOwner] != 0) {
            revert InvalidParameter();
        }
        id = _newProposal(Kind.ReplaceOwner, owner, newOwner, previousOwner, 0, config.holdDelay);
        _emitConfigProposed(id);
        _approveAs(id, owner, duress);
    }

    function proposeThreshold(uint256 newThreshold) external returns (uint256 id) {
        (address owner, bool duress) = _signer();
        if (newThreshold == 0 || newThreshold > ownerList.length) revert InvalidParameter();
        id = _newProposal(Kind.ChangeThreshold, owner, address(0), address(0), newThreshold, config.holdDelay);
        _emitConfigProposed(id);
        _approveAs(id, owner, duress);
    }

    // --- Gel : un seul signataire suffit pour geler, il en faut davantage pour dégeler ---

    function freeze(string calldata reason) external onlyActiveOwner {
        if (frozen) revert WalletFrozen();
        frozen = true;
        emit Frozen(msg.sender, reason);
    }

    /// @dev Lève aussi le gel silencieux d'une clé de contrainte. Le vote du signataire contraint est
    ///      enregistré comme les autres mais ne compte pas : ce sont ses collègues qui décident de la reprise.
    function approveUnfreeze() external onlyActiveOwner {
        if (!frozen && !_silentFreeze) revert NotFrozen();
        if (!isEstablishedOwner(msg.sender)) revert OwnerInProbation(keyTrustedAfter[msg.sender]);
        if (hasApprovedUnfreeze[unfreezeRound][msg.sender] && _unfreezeEpoch[unfreezeRound][msg.sender] == keyEpoch[msg.sender]) {
            revert AlreadyApproved();
        }
        hasApprovedUnfreeze[unfreezeRound][msg.sender] = true;
        _unfreezeEpoch[unfreezeRound][msg.sender] = keyEpoch[msg.sender];

        uint256 approvals;
        for (uint256 i = 0; i < ownerList.length; i++) {
            address owner = ownerList[i];
            if (hasApprovedUnfreeze[unfreezeRound][owner] && isEstablishedOwner(owner)
                && _unfreezeEpoch[unfreezeRound][owner] == keyEpoch[owner] && !_coerced[owner]) approvals++;
        }
        uint256 required = _withExtra(threshold);
        emit UnfreezeApproved(msg.sender, approvals, required);
        if (approvals >= required) {
            frozen = false;
            _silentFreeze = false;
            for (uint256 i = 0; i < ownerList.length; i++) delete _coerced[ownerList[i]];
            unfreezeRound++;
            emit Unfrozen(msg.sender);
        }
    }

    // --- Lecture ---

    function isActiveOwner(address account) public view returns (bool) {
        return keyExpiresAt[account] > block.timestamp;
    }

    /// @notice Une clé remplacée ne participe aux quorums renforcés qu'après deux jours.
    ///         Les signataires initiaux sont établis à la création du portefeuille.
    function isEstablishedOwner(address account) public view returns (bool) {
        return isActiveOwner(account) && block.timestamp >= keyTrustedAfter[account];
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

    /// @notice Compte les votes de l'incarnation actuelle des clés encore actives.
    ///         Gouvernance, risque et dépassement de plafond : seules les clés établies comptent.
    ///         Paiement ordinaire : une clé en probation peut encore participer au quorum de base.
    function validApprovals(uint256 id) public view returns (uint256 approvals) {
        Proposal storage p = _proposals[id];
        bool establishedOnly = p.kind != Kind.Payment || p.risk != Risk.None || _overCap(p.value);
        for (uint256 i = 0; i < ownerList.length; i++) {
            address owner = ownerList[i];
            if (hasApproved[id][owner] && _approvalEpoch[id][owner] == keyEpoch[owner]
                && (establishedOnly ? isEstablishedOwner(owner) : isActiveOwner(owner))) approvals++;
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

    /// @return owner Le signataire au nom duquel l'appel est fait.
    /// @return duress Vrai si l'appel vient de sa clé de contrainte et non de sa clé habituelle.
    function _signer() private view returns (address owner, bool duress) {
        if (isActiveOwner(msg.sender)) return (msg.sender, false);
        owner = _duressOwner[keccak256(abi.encodePacked(msg.sender))];
        if (owner == address(0) || !isActiveOwner(owner)) revert NotActiveOwner();
        duress = true;
    }

    function _newProposal(Kind kind, address proposer, address target, address subject, uint256 value, uint64 delay)
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
                proposer: proposer,
                target: target,
                subject: subject,
                value: value
            })
        );
    }

    function _emitConfigProposed(uint256 id) private {
        Proposal storage p = _proposals[id];
        emit ConfigProposed(id, p.kind, p.proposer, p.target, p.subject, p.value, requiredApprovals(id), p.executableAfter);
    }

    /// @dev Sous contrainte, l'approbation est enregistrée et annoncée comme n'importe quelle autre.
    ///      La seule différence est invisible : la proposition ne s'exécutera plus et les paiements s'arrêtent.
    function _approveAs(uint256 id, address owner, bool duress) private {
        if (duress) {
            _underDuress[id] = true;
            _coerced[owner] = true;
            _silentFreeze = true;
        }
        hasApproved[id][owner] = true;
        _approvalEpoch[id][owner] = keyEpoch[owner];
        emit Approved(id, owner, validApprovals(id), requiredApprovals(id));
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
        delete keyTrustedAfter[previousOwner];
        uint64 expiry = _expiryFromNow();
        keyExpiresAt[newOwner] = expiry;
        keyTrustedAfter[newOwner] = uint64(block.timestamp) + KEY_PROBATION;
        keyEpoch[newOwner]++;
        emit OwnerProbationStarted(newOwner, keyTrustedAfter[newOwner], keyEpoch[newOwner]);
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
