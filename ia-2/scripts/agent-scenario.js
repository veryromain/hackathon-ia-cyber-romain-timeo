// Scénario de l'agent cosignataire : un signataire humain propose seul, l'agent décide de cosigner ou non.
// L'agent (ia-1/agent/agent.py, --mode cosignataire) et le relais doivent tourner à côté ; l'agent tient la clé
// du signataire n° AGENT_INDEX (3 par défaut, soit le quatrième). Aucun autre humain ne signe dans ce script :
// tout ce qui s'exécute l'est grâce à la signature de l'agent.
// Usage : npm run agent:local   ou   npm run agent:fuji
const hre = require("hardhat");
const { loadDeployment } = require("../lib/deployment");

const { ethers } = hre;
const e18 = (n) => ethers.parseEther(String(n));
const fmt = (wei) => Number(ethers.formatEther(wei)).toLocaleString("fr-FR", { maximumFractionDigits: 0 });
const sleep = (seconds) => new Promise((resolve) => setTimeout(resolve, seconds * 1000));
const RISK = ["aucun", "signatures en plus", "mise en attente"];
const WAIT_S = Number(process.env.AGENT_WAIT_S || 25);
async function retry(action, attempts = 6) {
  for (let i = 1; ; i++) {
    try { return await action(); } catch (error) { if (i >= attempts) throw error; await sleep(3); }
  }
}

async function main() {
  const { info, signerOf, musd, wallet } = await loadDeployment(hre);
  const human = signerOf(info.owners[0]);
  const agent = info.owners[Number(process.env.AGENT_INDEX || 3)];
  const supplier = info.known_recipients[0];
  const unknown = ethers.getAddress("0x" + ethers.id("Breaker/agent/inconnu").slice(26));
  const treasury = await musd.balanceOf(info.wallet);
  console.log(`Trésorerie : ${fmt(treasury)} mUSD. Agent cosignataire : ${agent}\n`);

  const cases = [
    ["1. Facture habituelle à un fournisseur du carnet", supplier, 3200n * 10n ** 18n, "Facture hébergement octobre"],
    ["2. Même fournisseur, mais 60 % de la trésorerie d'un coup", supplier, (treasury * 60n) / 100n, "Avance sur contrat annuel"],
    ["3. Destinataire jamais vu", unknown, e18(4800), "Facture prestataire Atlas Conseil"],
  ];
  const pending = [];
  try {
    for (const [title, to, amount, memo] of cases) {
      console.log(title);
      const receipt = await (await wallet.connect(human).proposePayment(to, amount, memo)).wait();
      const id = Number(receipt.logs.map((log) => wallet.interface.parseLog(log)).find((log) => log && log.name === "PaymentProposed").args.id);
      pending.push(id);
      console.log(`  paiement ${id} proposé par un seul humain : ${fmt(amount)} mUSD. L'agent instruit le dossier…`);
      let signed = false;
      for (let t = 0; t < WAIT_S && !signed; t += 2) { await sleep(2); signed = await wallet.hasApproved(id, agent); }
      const p = await retry(() => wallet.getProposal(id));
      const valid = Number(await wallet.validApprovals(id));
      const required = Number(await wallet.requiredApprovals(id));
      console.log(`  l'agent ${signed ? "A COSIGNÉ" : "N'A PAS SIGNÉ"} ; risque : ${RISK[Number(p.risk)]} ; ${valid}/${required} signatures`);
      if (valid < required) {
        // Vocabulaire fixé par Romain (11/10 09:15) : « signature en plus » et « mise en attente », jamais « bloqué ».
        console.log(Number(p.risk) === 2
          ? "  → mise en attente : il faut une signature humaine en plus, puis un délai. Rien ne part.\n"
          : "  → signature en plus : le paiement attend qu'un humain de plus le signe.\n");
        continue;
      }
      for (let attempt = 0; attempt < 25; attempt++) {
        try {
          await (await wallet.connect(human).execute(id)).wait();
          pending.pop();
          console.log("  → paiement exécuté après le délai d'examen\n");
          break;
        } catch (error) {
          if (attempt === 24) console.log("  → toujours en attente\n");
          await sleep(2);
        }
      }
    }
  } finally {
    for (const id of pending) await retry(async () => (await wallet.connect(human).cancel(id, "fin du scénario de l'agent")).wait());
  }
  const after = await musd.balanceOf(info.wallet);
  console.log(`Sorti : ${fmt(treasury - after)} mUSD (la facture habituelle). Paiements non signés par l'agent annulés : ${pending.length}.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
