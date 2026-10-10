require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

// La phrase secrète de test vient de .env (ignoré par Git), jamais du dépôt.
// Le déploiement a besoin de 8 comptes (déployeur, 5 signataires, moniteur, oracle) : ils sont dérivés d'une seule phrase.
const fujiAccounts = process.env.FUJI_MNEMONIC ? { mnemonic: process.env.FUJI_MNEMONIC, count: 10 } : [];

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: { optimizer: { enabled: true, runs: 200 }, evmVersion: "cancun" },
  },
  networks: {
    // SIM_START n'est défini que par le générateur de jeux de données, pour simuler des mois passés.
    // allowBlocksWithSameTimestamp : sans lui, plusieurs transactions dans la même seconde font
    // avancer l'heure de la chaîne locale plus vite que l'heure réelle, ce qui fausse les délais en démo.
    hardhat: { allowBlocksWithSameTimestamp: true, ...(process.env.SIM_START ? { initialDate: process.env.SIM_START } : {}) },
    fuji: {
      url: process.env.FUJI_RPC_URL || "https://api.avax-test.network/ext/bc/C/rpc",
      chainId: 43113,
      accounts: fujiAccounts,
    },
  },
};
