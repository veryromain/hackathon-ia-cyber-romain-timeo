// Scénario de démonstration en direct : un paiement normal, puis une fraude en rafale
// (deux signataires trompés, gros virements vers une adresse inconnue).
// Le relais et le moteur de score doivent tourner à côté pour que les paiements soient signalés.
// Usage : npm run scenario:local        RESPOND=1 pour qu'un signataire gèle et annule à la fin
const hre = require("hardhat");
const { loadDeployment } = require("../lib/deployment");

const { ethers } = hre;
const e18 = (n) => ethers.parseEther(String(n));
const fmt = (wei) => Number(ethers.formatEther(wei)).toLocaleString("fr-FR", { maximumFractionDigits: 0 });
const sleep = (seconds) => new Promise((resolve) => setTimeout(resolve, seconds * 1000));
const RISK = ["aucun", "signatures en plus", "mise en attente"];
const FRAUD_COUNT = Number(process.env.FRAUD_COUNT || 3);

async function main() {
  const { info, signerOf, musd, wallet } = await loadDeployment(hre);
  const [alice, bruno, chloe, david, emma] = info.owners.map(signerOf);
  const signers = await ethers.getSigners();
  const supplier = signers[8].address; // fournisseur habituel
  const mule = ethers.Wallet.createRandom().address; // adresse jamais vue
  const review = info.config.reviewDelay;

  async function propose(signer, to, amount, memo) {
    const id = Number(await wallet.proposalCount());
    await (await wallet.connect(signer).proposePayment(to, e18(amount), memo)).wait();
    console.log(`  paiement ${id} proposé : ${amount.toLocaleString("fr-FR")} mUSD, « ${memo} »`);
    return id;
  }

  async function tryExecute(signer, id) {
    const p = await wallet.getProposal(id);
    const valid = Number(await wallet.validApprovals(id));
    const required = Number(await wallet.requiredApprovals(id));
    const state = `risque : ${RISK[Number(p.risk)]}, ${valid}/${required} signatures`;
    if (valid < required) return console.log(`  paiement ${id} BLOQUÉ (${state})`);
    // Un paiement sans risque part dès la fin du délai d'examen : on réessaie quelques secondes si la chaîne dit « trop tôt ».
    for (let attempt = 0; attempt < 10; attempt++) {
      try {
        await (await wallet.connect(signer).execute(id)).wait();
        return console.log(`  paiement ${id} EXÉCUTÉ (${state})`);
      } catch (error) {
        const message = (error.shortMessage || error.message).split("\n")[0];
        if (!message.includes("TooEarly")) return console.log(`  paiement ${id} refusé : ${message}`);
        if (Number(p.risk) === 2) return console.log(`  paiement ${id} EN ATTENTE (${state})`);
        await sleep(2);
      }
    }
    console.log(`  paiement ${id} toujours en attente (${state})`);
  }

  const before = await musd.balanceOf(wallet.target);
  console.log(`Trésorerie au départ : ${fmt(before)} mUSD\n`);

  console.log("1. Paiement normal à un fournisseur habituel");
  const normal = await propose(alice, supplier, 3150, "Facture hébergement cloud octobre 2026");
  await (await wallet.connect(bruno).approve(normal)).wait();
  console.log(`  approuvé par un deuxième signataire, attente du délai d'examen (${review} s)…`);
  await sleep(review + 2);
  await tryExecute(bruno, normal);

  console.log(`\n2. Fraude : deux signataires trompés, ${FRAUD_COUNT} virements vers ${mule}`);
  const memos = ["URGENT - virement confidentiel, acquisition en cours", "Très urgent : à traiter avant ce soir, ne pas ébruiter", "Opération confidentielle validée par la direction"];
  const ids = [];
  for (let i = 0; i < FRAUD_COUNT; i++) {
    const id = await propose(emma, mule, 95000 - i * 1500, memos[i % memos.length]);
    await (await wallet.connect(david).approve(id)).wait();
    ids.push(id);
    await sleep(4);
  }
  console.log(`  attente du délai d'examen (${review} s), le temps que le moniteur rende son verdict…`);
  await sleep(review + 2);
  console.log("  les fraudeurs tentent d'exécuter :");
  for (const id of ids) await tryExecute(david, id);

  if (process.env.RESPOND === "1") {
    console.log("\n3. Un signataire alerté gèle le portefeuille et annule les paiements suspects");
    await (await wallet.connect(alice).freeze("Alerte du garde, vérification en cours")).wait();
    for (const id of ids) {
      const p = await wallet.getProposal(id);
      if (!p.executed && !p.cancelled) await (await wallet.connect(alice).cancel(id, "fraude confirmée")).wait();
    }
    console.log("  portefeuille gelé, paiements en suspens annulés");
  }

  const after = await musd.balanceOf(wallet.target);
  const stolen = await musd.balanceOf(mule);
  const attempted = ids.reduce((sum, _, i) => sum + 95000 - i * 1500, 0);
  console.log(`\nBilan : ${fmt(stolen)} mUSD partis chez le fraudeur sur ${attempted.toLocaleString("fr-FR")} tentés.`);
  console.log(`Trésorerie : ${fmt(after)} mUSD.`);
  void chloe;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
