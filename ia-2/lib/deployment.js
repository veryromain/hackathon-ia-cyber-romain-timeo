// Recharge un déploiement noté par scripts/deploy.js : contrats attachés et signataires par rôle.
const fs = require("fs");
const path = require("path");

async function loadDeployment(hre) {
  const { ethers, network } = hre;
  const file = path.join(__dirname, "..", "deployments", `${network.name}.json`);
  if (!fs.existsSync(file)) {
    throw new Error(`Aucun déploiement pour le réseau « ${network.name} ». Lancer d'abord le script de déploiement.`);
  }
  const info = JSON.parse(fs.readFileSync(file, "utf8"));
  const signers = await ethers.getSigners();
  const signerOf = (address) => {
    const signer = signers.find((s) => s.address.toLowerCase() === address.toLowerCase());
    if (!signer) throw new Error(`Pas de clé disponible pour ${address} sur ce réseau.`);
    return signer;
  };
  return {
    info,
    signerOf,
    musd: await ethers.getContractAt("MockToken", info.musd),
    registry: await ethers.getContractAt("RiskRegistry", info.registry),
    wallet: await ethers.getContractAt("TreasuryGuard", info.wallet),
  };
}

module.exports = { loadDeployment };
