// Rejeu de la FORME du piratage de Drift (1er avril 2026, environ 285 M$) sur notre portefeuille.
// Ce que les sources publiques décrivent : des clés d'administration et de multi-signature compromises après des
// mois d'approche, puis la trésorerie vidée en 31 retraits et 12 minutes.
// Ce que ce script rejoue : l'attaquant tient deux clés de signataires (le seuil du portefeuille) et propose
// 31 paiements en 12 minutes vers ses adresses, 285 000 mUSD au total (1 mUSD pour 1 000 $).
// Ce qu'il ne rejoue pas : l'ingénierie sociale, ni la prise des droits d'administration d'un protocole (Drift
// n'était pas un portefeuille de trésorerie ; c'est la cadence et le vol de clés qui sont repris).
// Rien n'est truqué : si le garde ne freine pas un paiement, le script l'exécute et le bilan le dit.
// Le relais et le moteur de score doivent tourner à côté.
// Usage : npm run drift:local   ou   npm run drift:fuji
//   DRIFT_SPAN_S=720 (durée de l'attaque), DRIFT_COUNT=31, DRIFT_KEYS=3 (clés volées, par défaut le seuil), RESPOND=0 pour ne pas geler ni annuler à la fin
const hre = require("hardhat");
const { loadDeployment } = require("../lib/deployment");

const { ethers } = hre;
const COUNT = Number(process.env.DRIFT_COUNT || 31);
const SPAN_S = Number(process.env.DRIFT_SPAN_S || 720);
const TOTAL = 285000;
const KEYS = (threshold) => Number(process.env.DRIFT_KEYS || threshold);
const RISK = ["aucun", "signatures en plus", "mise en attente"];
const e18 = (n) => ethers.parseEther(String(n));
const fmt = (wei) => Number(ethers.formatEther(wei)).toLocaleString("fr-FR", { maximumFractionDigits: 0 });
const sleep = (seconds) => new Promise((resolve) => setTimeout(resolve, Math.max(0, seconds) * 1000));
const clock = () => new Date().toLocaleTimeString("fr-FR");
// Adresses de l'attaquant, sans clé : elles ne font que recevoir. Mêmes adresses sur tous les réseaux.
const addr = (label) => ethers.getAddress("0x" + ethers.id("Breaker/drift/" + label).slice(26));
// Tirage reproductible (mêmes montants et même cadence à chaque rejeu).
function generator(seed) {
  let state = seed;
  return () => { state = (state * 1664525 + 1013904223) % 4294967296; return state / 4294967296; };
}
// Sur Fuji, le nœud qui répond n'a pas toujours encore vu le bloc qu'on vient d'écrire : on réessaie.
async function retry(action, attempts = 6) {
  for (let i = 1; ; i++) {
    try { return await action(); } catch (error) { if (i >= attempts) throw error; await sleep(3); }
  }
}

async function main() {
  const { info, signerOf, musd, wallet } = await loadDeployment(hre);
  const owners = [];
  for (let i = 0; i < Number(await wallet.ownerCount()); i++) {
    const owner = await wallet.ownerList(i);
    if (await wallet.isEstablishedOwner(owner)) {
      try { owners.push(signerOf(owner)); } catch { /* clé absente de cette machine */ }
    }
  }
  if (await wallet.frozen()) throw new Error("Portefeuille gelé : le dégeler d'abord (npm run unfreeze:…).");
  const threshold = Number(await wallet.threshold());
  if (owners.length < KEYS(threshold) + 1) throw new Error("Il faut les clés du seuil, plus un signataire honnête.");
  const honest = owners[0];
  const stolen = owners.slice(owners.length - KEYS(threshold)); // les clés compromises : le seuil, sauf DRIFT_KEYS
  const review = info.config.reviewDelay;

  // Montants et cadence : 31 retraits inégaux, espacés irrégulièrement.
  const random = generator(20260401);
  const weights = Array.from({ length: COUNT }, () => 0.4 + random() * 1.6);
  const sum = weights.reduce((a, b) => a + b, 0);
  const amounts = weights.map((w) => Math.round((TOTAL * w) / sum / 100) * 100);
  amounts[COUNT - 1] += TOTAL - amounts.reduce((a, b) => a + b, 0);
  const gaps = Array.from({ length: COUNT }, (_, i) => (i === 0 ? 0 : 0.3 + random() * 1.4));
  const gapSum = gaps.reduce((a, b) => a + b, 0) || 1;
  const offsets = [];
  gaps.reduce((t, g) => { offsets.push(t + (g * SPAN_S) / gapSum); return offsets[offsets.length - 1]; }, 0);
  const destinations = ["portefeuille-1", "portefeuille-2", "portefeuille-3", "portefeuille-4"].map(addr);

  const before = await musd.balanceOf(info.wallet);
  console.log(`Trésorerie au départ : ${fmt(before)} mUSD. Seuil : ${threshold} signatures sur ${Number(await wallet.ownerCount())}.`);
  console.log(`L'attaquant tient ${stolen.length} clés de signataires. ${COUNT} retraits prévus en ${Math.round(SPAN_S / 60)} min, ${TOTAL.toLocaleString("fr-FR")} mUSD.\n`);

  const payments = []; // { id, amount, tryAt, outcome }
  async function attempt(payment) {
    const p = await retry(() => wallet.getProposal(payment.id));
    const valid = Number(await wallet.validApprovals(payment.id));
    const required = Number(await wallet.requiredApprovals(payment.id));
    const state = `${RISK[Number(p.risk)]}, ${valid}/${required} signatures`;
    try {
      await wallet.connect(stolen[0]).execute.staticCall(payment.id);
    } catch {
      payment.outcome = valid < required ? "bloqué" : "en attente";
      return console.log(`[${clock()}]    retrait ${payment.id} ${payment.outcome.toUpperCase()} (${state})`);
    }
    await (await wallet.connect(stolen[0]).execute(payment.id)).wait(); // le garde n'a rien freiné : l'argent part vraiment
    payment.outcome = "exécuté";
    console.log(`[${clock()}]    retrait ${payment.id} EXÉCUTÉ : ${payment.amount.toLocaleString("fr-FR")} mUSD partis (${state})`);
  }
  const attemptDue = async () => {
    for (const payment of payments) if (!payment.outcome && Date.now() >= payment.tryAt) await attempt(payment);
  };

  const start = Date.now();
  try {
    for (let i = 0; i < COUNT; i++) {
      while (Date.now() < start + offsets[i] * 1000) { await attemptDue(); await sleep(1); }
      const to = destinations[i % destinations.length];
      const receipt = await (await wallet.connect(stolen[0]).proposePayment(to, e18(amounts[i]), "Rééquilibrage de trésorerie")).wait();
      const id = Number(receipt.logs.map((log) => wallet.interface.parseLog(log)).find((log) => log && log.name === "PaymentProposed").args.id);
      for (const key of stolen.slice(1)) await retry(async () => (await wallet.connect(key).approve(id)).wait());
      payments.push({ id, amount: amounts[i], tryAt: Date.now() + (review + 8) * 1000 });
      console.log(`[${clock()}] retrait ${i + 1}/${COUNT} proposé et approuvé : ${amounts[i].toLocaleString("fr-FR")} mUSD (paiement ${id})`);
    }
    console.log(`\nDernier retrait proposé après ${Math.round((Date.now() - start) / 1000)} s. L'attaquant tente d'exécuter ce qui reste :`);
    while (payments.some((payment) => !payment.outcome)) { await attemptDue(); await sleep(1); }
  } finally {
    if (process.env.RESPOND !== "0" && payments.length) {
      console.log("\nUn signataire honnête, alerté, gèle le portefeuille et annule les retraits en suspens");
      await retry(async () => { if (!(await wallet.frozen())) await (await wallet.connect(honest).freeze("Clés compromises, retraits en série")).wait(); });
      for (const payment of payments) {
        if (payment.outcome === "exécuté") continue;
        await retry(async () => (await wallet.connect(honest).cancel(payment.id, "vol de clés confirmé")).wait());
      }
      console.log(`  portefeuille gelé, ${payments.filter((payment) => payment.outcome !== "exécuté").length} retraits annulés (dégel : npm run unfreeze:${info.network === "fuji" ? "fuji" : "local"})`);
    }
  }

  const after = await musd.balanceOf(info.wallet);
  const count = (outcome) => payments.filter((payment) => payment.outcome === outcome).length;
  console.log(`\nBilan : ${count("exécuté")} retraits exécutés, ${count("bloqué")} bloqués faute de signatures, ${count("en attente")} mis en attente.`);
  console.log(`Parti chez l'attaquant : ${fmt(before - after)} mUSD sur ${TOTAL.toLocaleString("fr-FR")} tentés. Trésorerie : ${fmt(after)} mUSD.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
