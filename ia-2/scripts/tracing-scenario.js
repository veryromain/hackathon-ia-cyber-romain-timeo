// Scénario du traçage des fonds (tâche T9, PLAN.md section 4 ter).
// Un arnaqueur reçoit 100 000 mUSD, les disperse vers trois mules, une plateforme d'échange et un
// innocent (quelques centimes de « poussière »), puis l'oracle le signale. L'organisation propose
// ensuite trois paiements : à une mule, à l'innocent et à la plateforme.
// Le relais doit tourner à côté : c'est lui qui écrit les lignes `token_transfer` dans events.jsonl.
// Usage : npm run tracing:local   ou   npm run tracing:fuji
const fs = require("fs");
const path = require("path");
const hre = require("hardhat");
const { loadDeployment } = require("../lib/deployment");

const { ethers } = hre;
const DIR = process.env.RELAY_DIR ? path.resolve(process.env.RELAY_DIR) : path.join(__dirname, "..", "..", "shared");
const SERVICES = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "..", "shared", "services-connus.json"), "utf8")).services;
const e18 = (n) => ethers.parseEther(String(n));
const sleep = (seconds) => new Promise((resolve) => setTimeout(resolve, seconds * 1000));
// Adresses de destination sans clé : elles ne font que recevoir. Mêmes adresses sur tous les réseaux.
const addr = (label) => ethers.getAddress("0x" + ethers.id("Breaker/tracage/" + label).slice(26));

async function main() {
  const { info, signerOf, musd, registry, wallet } = await loadDeployment(hre);
  const [deployer] = await ethers.getSigners();
  const [owner1, owner2] = info.owners.map(signerOf);
  const oracle = signerOf(info.oracle);

  const scammer = ethers.Wallet.createRandom().connect(ethers.provider);
  const mules = [addr("mule-1"), addr("mule-2"), addr("mule-3")];
  const innocent = addr("innocent");
  const exchange = ethers.getAddress(SERVICES.find((s) => s.kind === "exchange").address);

  console.log("1. L'arnaqueur encaisse 100 000 mUSD");
  await (await deployer.sendTransaction({ to: scammer.address, value: ethers.parseEther("0.01") })).wait(); // de quoi payer le gas
  await (await musd.connect(deployer).mint(scammer.address, e18(100000))).wait();

  console.log("2. Il disperse les fonds avant d'être repéré");
  const dispersal = [
    [mules[0], 18000, "mule 1 (18 %)"], [mules[1], 12000, "mule 2 (12 %)"], [mules[2], 10000, "mule 3 (10 %)"],
    [exchange, 30000, "plateforme d'échange (30 %)"], [innocent, 0.01, "un innocent, 0,01 mUSD de poussière"],
  ];
  for (const [to, amount, label] of dispersal) {
    await (await musd.connect(scammer).transfer(to, e18(amount))).wait();
    console.log(`   ${String(amount).padStart(7)} mUSD -> ${label}`);
  }

  console.log("3. L'oracle signale l'arnaqueur");
  const expiresAt = Math.floor(Date.now() / 1000) + 30 * 86400;
  await (await registry.connect(oracle).flag(scammer.address, 2, "scam_report", ethers.id("preuve/tracage"), expiresAt)).wait();
  console.log("   attente : le relais remonte les transferts sortis de cette adresse…");
  await sleep(8);

  console.log("4. L'organisation propose trois paiements");
  const payments = [
    [mules[0], 4800, "Facture prestataire Atlas Conseil", "mule", "fraud"],
    [innocent, 2000, "Facture traduction de la documentation", "innocent_dusted", "normal"],
    [exchange, 5000, "Conversion de trésorerie sur la plateforme d'échange", "known_service", "normal"],
  ];
  const labels = [];
  for (const [to, amount, memo, role, label] of payments) {
    const id = Number(await wallet.proposalCount());
    await (await wallet.connect(owner1).proposePayment(to, e18(amount), memo)).wait();
    await (await wallet.connect(owner2).approve(id)).wait();
    labels.push({ payment_id: id, label, scenario: "tainted_" + role });
    console.log(`   paiement ${id} : ${amount} mUSD vers ${role}`);
  }

  const lower = (a) => a.toLowerCase();
  const roles = {
    network: info.network, chain_id: info.chain_id,
    scammer: lower(scammer.address), mules: mules.map(lower), innocent_dusted: lower(innocent), known_service: lower(exchange),
    scammer_outflows_musd: { mules: [18000, 12000, 10000], known_service: 30000, innocent_dusted: 0.01, total: 70000.01 },
    payments: labels,
    expected: "Le paiement vers la mule doit être freiné (TAINTED_FUNDS) ; ceux vers l'innocent et vers le service connu ne doivent rien recevoir à ce titre.",
  };
  fs.mkdirSync(DIR, { recursive: true });
  fs.writeFileSync(path.join(DIR, "tracage-roles.json"), JSON.stringify(roles, null, 2) + "\n");
  console.log(`\nRôles et étiquettes écrits dans ${path.join(DIR, "tracage-roles.json")}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
