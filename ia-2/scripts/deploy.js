// Déploie le jeton de test, le registre et le portefeuille gardé, puis note les adresses dans
// ia-2/deployments/<réseau>.json pour le relais et les scénarios.
// Usage : npm run deploy:local   (après « npm run node » dans un autre terminal)
const fs = require("fs");
const path = require("path");
const hre = require("hardhat");

const { ethers, network } = hre;
const DAY = 86400;

async function main() {
  const signers = await ethers.getSigners();
  if (signers.length < 8) {
    throw new Error(`Il faut 8 comptes (déployeur, 5 signataires, moniteur, oracle) ; ce réseau en fournit ${signers.length}.`);
  }
  const [deployer, ...rest] = signers;
  const owners = rest.slice(0, 5);
  const monitor = rest[5];
  const oracle = rest[6];

  // Délais courts par défaut, pour qu'une démo en direct tienne en quelques minutes.
  const config = {
    reviewDelay: Number(process.env.REVIEW_DELAY || 30),
    holdDelay: Number(process.env.HOLD_DELAY || 180),
    keyLifetime: 15 * DAY,
    periodLength: DAY,
    periodCap: ethers.parseEther(process.env.PERIOD_CAP || "100000"),
    stepUpExtra: 1,
  };

  const musd = await (await ethers.getContractFactory("MockToken")).deploy("Mock USD", "mUSD");
  await musd.waitForDeployment();
  const registry = await (await ethers.getContractFactory("RiskRegistry")).deploy(deployer.address);
  await registry.waitForDeployment();
  await (await registry.grantRole(await registry.ORACLE_ROLE(), oracle.address)).wait();
  const wallet = await (await ethers.getContractFactory("TreasuryGuard")).deploy(
    musd.target, owners.map((o) => o.address), 2, monitor.address, registry.target, config
  );
  const receipt = await wallet.deploymentTransaction().wait();
  await (await musd.mint(wallet.target, ethers.parseEther("1000000"))).wait();

  const deployment = {
    network: network.name,
    chain_id: Number((await ethers.provider.getNetwork()).chainId),
    deploy_block: receipt.blockNumber,
    musd: musd.target,
    registry: registry.target,
    wallet: wallet.target,
    owners: owners.map((o) => o.address),
    monitor: monitor.address,
    oracle: oracle.address,
    config: { ...config, periodCap: config.periodCap.toString() },
  };
  const dir = path.join(__dirname, "..", "deployments");
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, `${network.name}.json`), JSON.stringify(deployment, null, 2) + "\n");
  console.log(`Déployé sur ${network.name} (bloc ${receipt.blockNumber})`);
  console.log(`  portefeuille : ${wallet.target}`);
  console.log(`  registre     : ${registry.target}`);
  console.log(`  mUSD         : ${musd.target}`);
  console.log(`  délai d'examen ${config.reviewDelay} s, mise en attente ${config.holdDelay} s`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
