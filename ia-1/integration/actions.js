// Exécuteur d'actions pour la démo locale (R5b) : lit shared/actions.jsonl, signe avec la clé de test du
// signataire indiqué, écrit shared/actions-resultats.jsonl. Format : shared/format-actions.md.
// Sur Fuji, c'est le relais de Timéo qui fera ce travail (les clés n'existent que sur son PC).
// Usage (depuis ia-2) : npx hardhat run ../ia-1/integration/actions.js --network localhost
const fs = require("fs");
const path = require("path");
const hre = require(require.resolve("hardhat", { paths: [process.cwd()] })); // hardhat de ia-2
const { loadDeployment } = require(path.join(process.cwd(), "lib", "deployment"));

const DIR = process.env.RELAY_DIR ? path.resolve(process.env.RELAY_DIR) : path.join(__dirname, "..", "..", "shared");
const IN = path.join(DIR, "actions.jsonl");
const OUT = path.join(DIR, "actions-resultats.jsonl");
const clock = () => new Date().toLocaleTimeString("fr-FR");

async function main() {
  const { info, signerOf, wallet } = await loadDeployment(hre);
  const owners = new Set(info.owners.map((o) => o.toLowerCase()));
  for (const f of [IN, OUT]) if (!fs.existsSync(f)) fs.writeFileSync(f, "");
  let offset = fs.statSync(IN).size; // on ignore les actions d'une session précédente
  console.log(`[${clock()}] Exécuteur d'actions prêt : ${IN}`);

  async function executer(a) {
    const by = String(a.by || "").toLowerCase();
    if (!owners.has(by)) throw new Error("unknown_signer");
    const s = signerOf(a.by);
    const w = wallet.connect(s);
    let tx;
    if (a.action === "approve") tx = await w.approve(a.payment_id);
    else if (a.action === "cancel") tx = await w.cancel(a.payment_id, String(a.reason || "annulé par un signataire"));
    else if (a.action === "freeze") tx = await w.freeze(String(a.reason || "gel par un signataire"));
    else if (a.action === "unfreeze") tx = await w.approveUnfreeze();
    else throw new Error("unknown_action");
    const r = await tx.wait();
    return r.hash;
  }

  setInterval(async () => {
    const size = fs.statSync(IN).size;
    if (size <= offset) return;
    const fd = fs.openSync(IN, "r");
    const buf = Buffer.alloc(size - offset);
    fs.readSync(fd, buf, 0, buf.length, offset);
    fs.closeSync(fd);
    offset = size;
    for (const line of buf.toString("utf8").split("\n").filter((l) => l.trim())) {
      let a;
      try { a = JSON.parse(line); } catch { continue; }
      let res;
      try {
        const hash = await executer(a);
        res = { id: a.id, status: "done", tx_hash: hash, at: Math.floor(Date.now() / 1000) };
        console.log(`[${clock()}] ${a.action} ${a.payment_id ?? ""} par ${String(a.by).slice(0, 8)} → ${hash.slice(0, 12)}…`);
      } catch (e) {
        const msg = (e.shortMessage || e.message || String(e)).split("\n")[0].slice(0, 160);
        res = { id: a.id, status: "error", error: msg, at: Math.floor(Date.now() / 1000) };
        console.log(`[${clock()}] ${a.action} ${a.payment_id ?? ""} ÉCHEC : ${msg}`);
      }
      fs.appendFileSync(OUT, JSON.stringify(res) + "\n");
    }
  }, 1000);
}
main().catch((e) => { console.error(e); process.exitCode = 1; });
