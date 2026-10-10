// Mesure le gas des transactions du portefeuille et du garde sur la chaîne locale, pour chiffrer
// le coût d'exploitation dans le modèle économique. Usage : npm run gas
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

const e18 = (n) => ethers.parseEther(String(n));
const DAY = 24 * 3600;

async function gasOf(txPromise) {
  const receipt = await (await txPromise).wait();
  return receipt.gasUsed;
}

async function main() {
  const [deployer, alice, bruno, chloe, monitor, oracle, supplier, mule] = await ethers.getSigners();
  const Token = await ethers.getContractFactory("MockToken");
  const Registry = await ethers.getContractFactory("RiskRegistry");
  const Wallet = await ethers.getContractFactory("TreasuryGuard");

  const musd = await Token.deploy("Mock USD", "mUSD");
  const registry = await Registry.deploy(deployer.address);
  await registry.grantRole(await registry.ORACLE_ROLE(), oracle.address);
  const config = { reviewDelay: 60, holdDelay: 3600, keyLifetime: 15 * DAY, periodLength: DAY, periodCap: e18(100000), stepUpExtra: 1 };
  const owners = [alice.address, bruno.address, chloe.address, deployer.address, supplier.address];
  const wallet = await Wallet.deploy(musd.target, owners, 2, monitor.address, registry.target, config);
  await musd.mint(wallet.target, e18(1000000));

  const results = {};
  results["Déploiement du portefeuille (une fois)"] = (await wallet.deploymentTransaction().wait()).gasUsed;
  results["Déploiement du registre (une fois)"] = (await registry.deploymentTransaction().wait()).gasUsed;

  results["Signataire : proposer un paiement"] = await gasOf(wallet.connect(alice).proposePayment(supplier.address, e18(3000), "Facture cloud 2026-09"));
  results["Signataire : approuver"] = await gasOf(wallet.connect(bruno).approve(0));
  await time.increase(60);
  results["Signataire : exécuter"] = await gasOf(wallet.connect(bruno).execute(0));

  await wallet.connect(alice).proposePayment(mule.address, e18(95000), "URGENT confidentiel");
  results["Garde : signaler StepUp"] = await gasOf(wallet.connect(monitor).flagRisk(1, 1, "NEW_RECIPIENT"));
  results["Garde : signaler Hold"] = await gasOf(wallet.connect(monitor).flagRisk(1, 2, "NEW_RECIPIENT;AMOUNT_OUTLIER;URGENCY_MEMO"));
  const expiresAt = (await time.latest()) + 30 * DAY;
  results["Oracle : inscrire une adresse au registre"] = await gasOf(registry.connect(oracle).flag(mule.address, 2, "scam_report", ethers.id("preuve"), expiresAt));
  results["Signataire : geler"] = await gasOf(wallet.connect(chloe).freeze("alerte du garde"));
  results["Signataire : annuler"] = await gasOf(wallet.connect(chloe).cancel(1, "fraude confirmée"));

  for (const [name, gas] of Object.entries(results)) console.log(`${name.padEnd(44)} ${String(gas).padStart(8)} gas`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
