// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @notice Jeton de test à émission libre. Sert de faux dollar (mUSD) et de faux collatéral.
/// @dev Aucune valeur : tout le monde peut en créer. Réservé à la chaîne locale et au testnet.
contract MockToken is ERC20 {
    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {}

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}
