// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/// @notice Pool d'échange minimal à produit constant (x * y = k), sans frais ni parts de liquidité.
/// @dev Son prix instantané sert d'oracle au coffre. C'est la faiblesse rejouée dans le scénario :
///      avec peu de liquidité, quelques échanges suffisent à gonfler le prix.
contract SimplePool {
    using SafeERC20 for IERC20;

    IERC20 public immutable token; // le collatéral coté
    IERC20 public immutable quote; // l'actif du coffre (mUSD)
    uint256 public reserveToken;
    uint256 public reserveQuote;

    event LiquidityAdded(address indexed provider, uint256 tokenAmount, uint256 quoteAmount);
    event Swapped(address indexed trader, bool quoteIn, uint256 amountIn, uint256 amountOut, uint256 priceAfter);

    constructor(IERC20 token_, IERC20 quote_) {
        token = token_;
        quote = quote_;
    }

    function addLiquidity(uint256 tokenAmount, uint256 quoteAmount) external {
        token.safeTransferFrom(msg.sender, address(this), tokenAmount);
        quote.safeTransferFrom(msg.sender, address(this), quoteAmount);
        reserveToken += tokenAmount;
        reserveQuote += quoteAmount;
        emit LiquidityAdded(msg.sender, tokenAmount, quoteAmount);
    }

    /// @param quoteIn true pour acheter le jeton avec du mUSD, false pour le vendre.
    function swap(bool quoteIn, uint256 amountIn) external returns (uint256 amountOut) {
        require(amountIn > 0 && reserveToken > 0 && reserveQuote > 0, "pool vide");
        if (quoteIn) {
            amountOut = (reserveToken * amountIn) / (reserveQuote + amountIn);
            quote.safeTransferFrom(msg.sender, address(this), amountIn);
            reserveQuote += amountIn;
            reserveToken -= amountOut;
            token.safeTransfer(msg.sender, amountOut);
        } else {
            amountOut = (reserveQuote * amountIn) / (reserveToken + amountIn);
            token.safeTransferFrom(msg.sender, address(this), amountIn);
            reserveToken += amountIn;
            reserveQuote -= amountOut;
            quote.safeTransfer(msg.sender, amountOut);
        }
        emit Swapped(msg.sender, quoteIn, amountIn, amountOut, price());
    }

    /// @return Prix d'un jeton en mUSD, avec 18 décimales.
    function price() public view returns (uint256) {
        if (reserveToken == 0) return 0;
        return (reserveQuote * 1e18) / reserveToken;
    }
}
