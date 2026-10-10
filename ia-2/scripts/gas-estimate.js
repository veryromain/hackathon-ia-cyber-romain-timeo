// Mesure le gas des transactions du gardien sur la chaîne locale, pour chiffrer le coût
// d'exploitation dans le modèle économique. Usage : npm run gas
const { ethers } = require("hardhat");

async function gasOf(txPromise) {
  const receipt = await (await txPromise).wait();
  return receipt.gasUsed;
}

async function main() {
  const [admin, guardian, human] = await ethers.getSigners();
  const Token = await ethers.getContractFactory("MockToken");
  const Vault = await ethers.getContractFactory("BreakerVault");
  const musd = await Token.deploy("Mock USD", "mUSD");
  const vault = await Vault.deploy(musd.target, admin.address, 3600, ethers.parseEther("10000"), 600);
  await vault.grantRole(await vault.GUARDIAN_ROLE(), guardian.address);
  await vault.grantRole(await vault.RESUME_ROLE(), human.address);

  const reason = "LISTING_DELAY_LOWERED;THIN_LIQUIDITY_COLLATERAL;BORROW_BURST score=0.93";
  const results = {
    deploiement_du_coffre: (await vault.deploymentTransaction().wait()).gasUsed,
    escalade_vers_Limited: await gasOf(vault.connect(guardian).escalate(1, reason)),
    escalade_vers_Paused: await gasOf(vault.connect(guardian).escalate(2, reason)),
    relance_par_un_humain: await gasOf(vault.connect(human).resume("incident clos, validation humaine")),
  };
  for (const [name, gas] of Object.entries(results)) console.log(`${name.padEnd(24)} ${gas} gas`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
