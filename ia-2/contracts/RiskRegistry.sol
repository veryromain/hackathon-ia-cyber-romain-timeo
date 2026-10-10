// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

/// @title RiskRegistry : registre public des adresses signalées
/// @notice L'oracle Web2 vers Web3 y inscrit les adresses accusées de fraude. Un signalement porte
///         le hash de sa preuve, expire tout seul et peut être retiré après contestation.
///         Le registre ne bloque rien : les portefeuilles qui le consultent ajoutent de la friction.
/// @dev Prototype de hackathon, non audité.
contract RiskRegistry is AccessControl {
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");

    struct Flag {
        uint8 level; // 1 = signatures supplémentaires, 2 = mise en attente
        uint64 expiresAt;
        bytes32 evidenceHash;
    }

    mapping(address => Flag) private _flags;

    event AddressFlagged(
        address indexed flagged,
        uint8 level,
        string category,
        bytes32 evidenceHash,
        uint64 expiresAt,
        address indexed by
    );
    event AddressUnflagged(address indexed flagged, address indexed by);

    error InvalidFlag();
    error NotFlagged();

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }

    function flag(address account, uint8 level, string calldata category, bytes32 evidenceHash, uint64 expiresAt)
        external
        onlyRole(ORACLE_ROLE)
    {
        if (account == address(0) || level == 0 || level > 2 || expiresAt <= block.timestamp) revert InvalidFlag();
        _flags[account] = Flag(level, expiresAt, evidenceHash);
        emit AddressFlagged(account, level, category, evidenceHash, expiresAt, msg.sender);
    }

    /// @notice Retrait par l'oracle, ou par l'administrateur quand une contestation aboutit.
    function unflag(address account) external {
        if (!hasRole(ORACLE_ROLE, msg.sender) && !hasRole(DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert AccessControlUnauthorizedAccount(msg.sender, ORACLE_ROLE);
        }
        if (_flags[account].level == 0) revert NotFlagged();
        delete _flags[account];
        emit AddressUnflagged(account, msg.sender);
    }

    /// @return Niveau de risque courant de l'adresse : 0 si elle n'est pas signalée ou si le signalement a expiré.
    function levelOf(address account) external view returns (uint8) {
        Flag memory f = _flags[account];
        return f.expiresAt > block.timestamp ? f.level : 0;
    }

    function flagOf(address account) external view returns (uint8 level, uint64 expiresAt, bytes32 evidenceHash) {
        Flag memory f = _flags[account];
        return (f.level, f.expiresAt, f.evidenceHash);
    }
}
