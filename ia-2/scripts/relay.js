// Relais entre la chaîne et le moteur de score (tâche T3).
//   chaîne  -> events.jsonl   : tout ce qu'émettent le portefeuille et le registre
//   alerts.jsonl -> chaîne    : le moniteur signale le paiement (flagRisk)
//   flags.jsonl  -> chaîne    : l'oracle inscrit ou retire une adresse du registre
//   actions.jsonl -> chaîne   : un signataire agit depuis le tableau de bord (approuver, annuler, geler,
//                               dégeler, exécuter) ; le résultat est écrit dans actions-resultats.jsonl
// Formats : shared/format-evenements.md et shared/format-actions.md.
// Les fichiers sont dans shared/ par défaut (RELAY_DIR pour changer).
// Usage : npm run relay:local   ou   npm run relay:fuji
const fs = require("fs");
const path = require("path");
const hre = require("hardhat");
const { loadDeployment } = require("../lib/deployment");
const { createNormalizer, LEVELS } = require("../lib/normalize");

const DIR = process.env.RELAY_DIR ? path.resolve(process.env.RELAY_DIR) : path.join(__dirname, "..", "..", "shared");
const POLL_MS = Number(process.env.RELAY_POLL_MS || 1000);
const FILES = {
  events: path.join(DIR, "events.jsonl"), alerts: path.join(DIR, "alerts.jsonl"), flags: path.join(DIR, "flags.jsonl"),
  actions: path.join(DIR, "actions.jsonl"), results: path.join(DIR, "actions-resultats.jsonl"),
};
const clock = () => new Date().toLocaleTimeString("fr-FR");
const short = (text) => String(text).split("\n")[0].slice(0, 160);

/// Nom de l'erreur du contrat quand il y en a une (« NotEnoughApprovals(2, 3) »), sinon le message abrégé.
function describeError(error) {
  if (error && error.revert && error.revert.name) return `${error.revert.name}(${[...error.revert.args].join(", ")})`;
  const message = String((error && (error.shortMessage || error.message)) || error);
  const custom = message.match(/custom error '([^']+)'/);
  return custom ? custom[1] : short(message);
}

/// Lit les lignes complètes ajoutées à un fichier depuis le dernier passage.
function makeTail(file, { fromEnd = false } = {}) {
  let offset = fromEnd && fs.existsSync(file) ? fs.statSync(file).size : 0;
  let rest = "";
  return () => {
    if (!fs.existsSync(file)) return [];
    const size = fs.statSync(file).size;
    if (size < offset) { offset = 0; rest = ""; } // fichier vidé ou réécrit : on repart du début
    if (size === offset) return [];
    const buffer = Buffer.alloc(size - offset);
    const fd = fs.openSync(file, "r");
    fs.readSync(fd, buffer, 0, buffer.length, offset);
    fs.closeSync(fd);
    offset = size;
    const parts = (rest + buffer.toString("utf8")).split("\n");
    rest = parts.pop();
    const rows = [];
    for (const line of parts) {
      if (!line.trim()) continue;
      try { rows.push(JSON.parse(line)); } catch { console.warn(`[${clock()}] ligne illisible ignorée dans ${path.basename(file)}`); }
    }
    return rows;
  };
}

async function main() {
  const { ethers } = hre;
  const { info, signerOf, registry, wallet } = await loadDeployment(hre);
  const monitor = signerOf(info.monitor);
  const oracle = signerOf(info.oracle);
  const normalizer = createNormalizer({ provider: ethers.provider, wallet, registry, assetAddress: info.musd, chainId: info.chain_id });

  fs.mkdirSync(DIR, { recursive: true });
  fs.writeFileSync(FILES.events, ""); // reconstruit depuis le déploiement à chaque démarrage
  for (const file of [FILES.alerts, FILES.flags, FILES.actions, FILES.results]) if (!fs.existsSync(file)) fs.writeFileSync(file, "");
  // Les alertes et les actions visent un numéro de paiement : celles d'une session précédente ne valent plus rien,
  // on les saute. Les signalements d'adresses, eux, restent valables d'une session à l'autre : on les rejoue tous.
  const nextAlerts = makeTail(FILES.alerts, { fromEnd: true });
  const nextFlags = makeTail(FILES.flags);
  const nextActions = makeTail(FILES.actions, { fromEnd: true });
  const owners = new Set(info.owners.map((owner) => owner.toLowerCase()));
  let lastBlock = info.deploy_block - 1;

  console.log(`[${clock()}] Relais démarré sur ${info.network}, portefeuille ${info.wallet}`);
  console.log(`[${clock()}] Fichiers : ${DIR}`);

  // Traçage des fonds : on suit les transferts du jeton qui sortent des adresses inscrites au registre.
  const watched = new Set();

  async function pumpEvents() {
    const latest = await ethers.provider.getBlockNumber();
    if (latest <= lastBlock) return;
    const from = lastBlock + 1;
    const events = [];
    const stillWatched = [...watched];
    for (const event of await normalizer.collect(from, latest)) {
      events.push(event);
      if (event.type === "address_unflagged") watched.delete(event.data.flagged);
      if (event.type !== "address_flagged" || watched.has(event.data.flagged)) continue;
      // Nouvelle adresse signalée : on remonte aussi dans le passé, car l'argent a souvent déjà été dispersé.
      watched.add(event.data.flagged);
      events.push(...(await normalizer.collectTransfers([event.data.flagged], info.deploy_block, latest)));
    }
    // Transferts récents des adresses déjà suivies avant ce passage.
    events.push(...(await normalizer.collectTransfers(stillWatched, from, latest)));
    lastBlock = latest;
    if (!events.length) return;
    fs.appendFileSync(FILES.events, events.map((e) => JSON.stringify(e)).join("\n") + "\n");
    for (const e of events) {
      if (e.type === "token_transfer") {
        const amount = Number(ethers.formatEther(e.data.amount)).toLocaleString("fr-FR", { maximumFractionDigits: 2 });
        console.log(`[${clock()}] traçage -> ${e.data.from.slice(0, 10)}… a envoyé ${amount} mUSD à ${e.data.to.slice(0, 10)}…`);
        continue;
      }
      const id = e.data.payment_id ?? e.data.proposal_id ?? "";
      console.log(`[${clock()}] chaîne -> ${e.type} ${id} ${e.data.level || ""} ${e.data.reason || ""}`.trimEnd());
    }
  }

  async function pumpAlerts() {
    for (const alert of nextAlerts()) {
      const level = LEVELS.indexOf(alert.level);
      if (level < 1 || !Number.isInteger(alert.payment_id)) {
        console.warn(`[${clock()}] alerte ignorée (niveau ou identifiant invalide) : ${JSON.stringify(alert).slice(0, 120)}`);
        continue;
      }
      const reason = (alert.reasons || []).map((r) => r.code).join(";") || "ANOMALY_MODEL";
      try {
        const tx = await wallet.connect(monitor).flagRisk(alert.payment_id, level, reason);
        await tx.wait();
        console.log(`[${clock()}] alerte -> paiement ${alert.payment_id} signalé ${alert.level} (${reason}) ${tx.hash}`);
      } catch (error) {
        // Refus attendus : paiement déjà exécuté ou annulé, ou niveau déjà atteint.
        console.warn(`[${clock()}] alerte refusée par le portefeuille pour le paiement ${alert.payment_id} : ${short(error.shortMessage || error.message)}`);
      }
    }
  }

  async function pumpFlags() {
    for (const flag of nextFlags()) {
      try {
        if (flag.remove) {
          await (await registry.connect(oracle).unflag(flag.address)).wait();
          console.log(`[${clock()}] oracle -> ${flag.address} retirée du registre`);
          continue;
        }
        const level = LEVELS.indexOf(flag.level);
        if (level < 1) throw new Error("niveau invalide");
        const tx = await registry.connect(oracle).flag(flag.address, level, flag.category || "scam_report", flag.evidence_hash, flag.expires_at);
        await tx.wait();
        console.log(`[${clock()}] oracle -> ${flag.address} inscrite au registre, niveau ${flag.level} ${tx.hash}`);
      } catch (error) {
        console.warn(`[${clock()}] signalement refusé pour ${flag.address} : ${short(error.shortMessage || error.message)}`);
      }
    }
  }

  /// Une action de signataire venue du tableau de bord, signée avec la clé de test de ce signataire.
  /// Le relais n'ajoute aucun pouvoir : le portefeuille refuse ce que ce signataire n'a pas le droit de faire.
  async function runAction(action) {
    const by = String(action.by || "").toLowerCase();
    if (!owners.has(by)) throw new Error("unknown_signer");
    const signed = wallet.connect(signerOf(action.by));
    const needsId = ["approve", "cancel", "execute"].includes(action.action);
    if (needsId && !Number.isInteger(action.payment_id)) throw new Error("invalid_payment_id");
    switch (action.action) {
      case "approve": return signed.approve(action.payment_id);
      case "cancel": return signed.cancel(action.payment_id, String(action.reason || "annulé par un signataire"));
      case "execute": return signed.execute(action.payment_id);
      case "freeze": return signed.freeze(String(action.reason || "gel par un signataire"));
      case "unfreeze": return signed.approveUnfreeze();
      default: throw new Error("unknown_action");
    }
  }

  async function pumpActions() {
    for (const action of nextActions()) {
      const label = `${action.action} ${action.payment_id ?? ""}`.trim();
      let result;
      try {
        const receipt = await (await runAction(action)).wait();
        result = { id: action.id, status: "done", tx_hash: receipt.hash, at: Math.floor(Date.now() / 1000) };
        console.log(`[${clock()}] action -> ${label} par ${String(action.by).slice(0, 10)}… ${receipt.hash}`);
      } catch (error) {
        const message = describeError(error);
        result = { id: action.id, status: "error", error: message, at: Math.floor(Date.now() / 1000) };
        console.warn(`[${clock()}] action refusée (${label}) : ${message}`);
      }
      fs.appendFileSync(FILES.results, JSON.stringify(result) + "\n");
    }
  }

  let stopping = false;
  process.on("SIGINT", () => { stopping = true; });
  while (!stopping) {
    try {
      await pumpEvents();
      await pumpFlags();
      await pumpAlerts();
      await pumpActions();
      await pumpEvents();
    } catch (error) {
      console.warn(`[${clock()}] erreur passagère : ${short(error.message)}`);
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_MS));
  }
  console.log(`[${clock()}] Relais arrêté.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
