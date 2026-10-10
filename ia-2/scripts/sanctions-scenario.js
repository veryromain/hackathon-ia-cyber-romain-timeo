// Scénario de l'oracle sur le vrai Web : un paiement vers une adresse que l'oracle a trouvée sur des
// listes de sanctions publiques. Avant de lancer ce script, il faut que l'oracle ait écrit l'adresse dans
// flags.jsonl (python -m oracle.collecte_apify --recherche 0x… --out ../shared/flags.jsonl) et que le
// relais l'ait inscrite au registre.
// Le paiement n'est jamais exécuté : le script l'annule à la fin, quoi qu'il arrive.
// Usage : npm run sanctions:local   ou   npm run sanctions:fuji   (SANCTION_TARGET pour changer d'adresse)
const hre = require("hardhat");
const { loadDeployment } = require("../lib/deployment");

const { ethers } = hre;
const TARGET = ethers.getAddress((process.env.SANCTION_TARGET || "0x098B716B8Aaf21512996dC57EB0615e2383E2f96").toLowerCase());
const AMOUNT = ethers.parseEther("25000");
const RISK = ["none", "step_up", "hold"];
const sleep = (seconds) => new Promise((resolve) => setTimeout(resolve, seconds * 1000));
// Sur Fuji, le nœud qui répond à une lecture n'a pas toujours encore vu le bloc qu'on vient d'écrire :
// on réessaie quelques secondes avant de conclure à un échec.
async function retry(action, attempts = 6) {
  for (let i = 1; ; i++) {
    try { return await action(); } catch (error) { if (i >= attempts) throw error; await sleep(3); }
  }
}
const musdOf = (wei) => Number(ethers.formatEther(wei)).toLocaleString("fr-FR");

async function main() {
  const { info, signerOf, musd, registry, wallet } = await loadDeployment(hre);

  console.log(`1. Ce que le registre sait de ${TARGET}`);
  const [level, expiresAt, evidenceHash] = await registry.flagOf(TARGET);
  if ((await registry.levelOf(TARGET)) === 0n) {
    throw new Error("Adresse absente du registre : lancer d'abord l'oracle (collecte_apify --recherche) et le relais.");
  }
  console.log(`   niveau ${RISK[Number(level)]}, preuve ${evidenceHash}, valable jusqu'au ${new Date(Number(expiresAt) * 1000).toLocaleDateString("fr-FR")}`);
  if (await wallet.frozen()) throw new Error("Portefeuille gelé : le dégeler d'abord (npm run unfreeze:…).");

  // Signataires dont la clé est valide et sortie de probation, dans l'ordre du portefeuille.
  const owners = [];
  for (let i = 0; i < Number(await wallet.ownerCount()); i++) {
    const owner = await wallet.ownerList(i);
    if (await wallet.isEstablishedOwner(owner)) {
      try { owners.push(signerOf(owner)); } catch { /* clé absente de cette machine */ }
    }
  }
  const before = await musd.balanceOf(info.wallet);

  console.log(`2. Un signataire propose ${musdOf(AMOUNT)} mUSD vers cette adresse`);
  const receipt = await (await wallet.connect(owners[0]).proposePayment(TARGET, AMOUNT, "Facture fournisseur, règlement à réception")).wait();
  const id = Number(receipt.logs.map((log) => wallet.interface.parseLog(log)).find((log) => log && log.name === "PaymentProposed").args.id);
  try {
    let p = await retry(() => wallet.getProposal(id));
    console.log(`   paiement ${id} : le portefeuille l'a classé ${RISK[Number(p.risk)]} tout seul, à la proposition`);

    console.log("3. Les autres signataires approuvent quand même");
    const required = Number(await wallet.requiredApprovals(id));
    for (const owner of owners.slice(1, required)) await retry(async () => (await wallet.connect(owner).approve(id)).wait());
    console.log(`   ${Number(await wallet.validApprovals(id))} signatures sur ${required} exigées`);

    console.log(`4. Après le délai d'examen (${info.config.reviewDelay} s), ils tentent de l'exécuter`);
    await sleep(info.config.reviewDelay + 5);
    try {
      await wallet.connect(owners[0]).execute.staticCall(id);
      console.log("   ⚠️ INATTENDU : le portefeuille accepterait l'exécution");
    } catch (error) {
      p = await wallet.getProposal(id);
      // Selon le réseau, l'erreur du contrat arrive décodée, en clair dans le message, ou en données brutes.
      const message = String(error.shortMessage || error.message);
      const data = error.data || (error.info && error.info.error && error.info.error.data);
      const parsed = !error.revert && typeof data === "string" && data.length >= 10 ? wallet.interface.parseError(data) : null;
      const name = (error.revert || parsed || {}).name || (message.match(/custom error '(\w+)/) || [, message.slice(0, 120)])[1];
      console.log(`   refusé par le portefeuille : ${name}, pas avant ${new Date(Number(p.executableAfter) * 1000).toLocaleTimeString("fr-FR")}`);
    }
  } finally {
    console.log("5. Un signataire annule le paiement");
    await retry(async () => (await wallet.connect(owners[0]).cancel(id, "destinataire sous sanctions")).wait());
  }

  const after = await musd.balanceOf(info.wallet);
  console.log(`\nSorti du portefeuille : ${musdOf(before - after)} mUSD. Reçu par l'adresse sanctionnée : ${musdOf(await musd.balanceOf(TARGET))} mUSD.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
