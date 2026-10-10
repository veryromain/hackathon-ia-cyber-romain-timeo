// Démo Web2 → Web3 : un paiement banal vers une adresse que l'oracle a signalée sur le Web.
// Prérequis : chaîne locale, déploiement, relais, moteur de score en direct, et l'oracle qui a écrit
// l'adresse dans shared/flags.jsonl (le relais l'inscrit au registre).
// Usage (depuis ia-2) : ADRESSE=0x… npx hardhat run ../ia-1/integration/scenario_oracle.js --network localhost
const path = require("path");
const hre = require(require.resolve("hardhat", { paths: [process.cwd()] })); // hardhat de ia-2
const { loadDeployment } = require(path.join(process.cwd(), "lib", "deployment"));
const { ethers } = hre;
const sleep = (s) => new Promise((r) => setTimeout(r, s * 1000));
const RISK = ["aucun", "signatures en plus", "mise en attente"];

async function main() {
  const cible = process.env.ADRESSE;
  const { info, signerOf, musd, wallet, registry } = await loadDeployment(hre);
  const [alice, bruno, chloe, david, emma] = info.owners.map(signerOf);

  console.log(`Registre : niveau de ${cible} = ${await registry.levelOf(cible)} (0 rien, 1 signatures en plus, 2 mise en attente)`);
  if (await wallet.frozen()) {
    for (const o of [alice, bruno, chloe]) {
      if (!(await wallet.frozen())) break;
      await (await wallet.connect(o).approveUnfreeze()).wait();
    }
    console.log(`Portefeuille dégelé par plusieurs signataires : ${!(await wallet.frozen())}`);
  }
  const id = Number(await wallet.proposalCount());
  await (await wallet.connect(emma).proposePayment(cible, ethers.parseEther("4800"), "Facture prestation octobre")).wait();
  await (await wallet.connect(david).approve(id)).wait();
  console.log(`Paiement ${id} proposé : 4 800 mUSD, « Facture prestation octobre », vers l'adresse signalée sur le Web`);
  await sleep(Number(info.config.reviewDelay) + 2);
  const p = await wallet.getProposal(id);
  const etat = `risque : ${RISK[Number(p.risk)]}, ${await wallet.validApprovals(id)}/${await wallet.requiredApprovals(id)} signatures`;
  try {
    await (await wallet.connect(david).execute(id)).wait();
    console.log(`Paiement ${id} EXÉCUTÉ (${etat})`);
  } catch (e) {
    console.log(`Paiement ${id} BLOQUÉ (${etat}) : ${(e.shortMessage || e.message).split("\n")[0]}`);
  }
  console.log(`Solde de l'adresse signalée : ${ethers.formatEther(await musd.balanceOf(cible))} mUSD`);
}
main().catch((e) => { console.error(e); process.exitCode = 1; });
