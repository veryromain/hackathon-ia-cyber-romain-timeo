// Vérification « zéro secret » : cherche les VRAIES valeurs des fichiers .env (et les clés privées dérivées de la
// phrase Fuji) dans les fichiers suivis par Git et dans tout l'historique, puis des motifs génériques de secrets.
// N'affiche jamais une valeur : seulement le nom de la variable, le fichier et le commit.
// À lancer sur CHAQUE poste qui a un .env (les valeurs ne sont pas les mêmes sur le PC et sur le Mac).
// Usage : cd ia-2 && npm run zero-secret
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const repo = path.resolve(process.argv[2] || path.join(__dirname, "..", ".."));
const git = (args, opts = {}) => execFileSync("git", ["-C", repo, ...args], { encoding: "utf8", maxBuffer: 1 << 30, ...opts });
const tryGit = (args) => { try { return git(args); } catch (e) { return e.stdout || ""; } };

// 1. Les secrets réels, lus dans tous les .env présents sur le disque (suivis ou non).
const envFiles = tryGit(["ls-files", "--others", "--ignored", "--exclude-standard", "--cached"]).split("\n")
  .filter((f) => /(^|\/)\.env(\.|$)/.test(f) && !/node_modules|\.venv/.test(f));
const secrets = []; // { name, value, from }
const NOT_SECRET = /^(true|false|[a-z]{2}-[a-z]+-[0-9]|\d{1,6}|https?:\/\/[^@]*|[a-z0-9.-]+\.(com|net|org|io|fr)|us\.anthropic\.[\w.:-]+|[\w.-]+@[\w.-]+)$/i;
for (const f of envFiles) {
  const full = path.join(repo, f);
  if (!fs.existsSync(full)) continue;
  for (const line of fs.readFileSync(full, "utf8").split(/\r?\n/)) {
    const m = line.match(/^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/);
    if (!m) continue;
    const value = m[2].trim().replace(/^["']|["']$/g, "");
    if (value.length < 8 || NOT_SECRET.test(value)) continue;
    secrets.push({ name: m[1], value, from: f });
  }
}
console.log("Fichiers .env lus :", envFiles.join(", ") || "(aucun)");
console.log("Variables traitées comme secrets :", secrets.map((s) => `${s.name} (${s.from}, ${s.value.length} car.)`).join(" ; ") || "(aucune)");

// Clés privées des comptes Fuji, dérivées de la phrase secrète.
const modules = process.argv[3] || path.join(__dirname, "..", "node_modules");
for (const s of secrets.filter((x) => /MNEMONIC/i.test(x.name))) {
  try {
    const { ethers } = require(path.join(modules, "ethers"));
    for (let i = 0; i < 20; i++) {
      const w = ethers.HDNodeWallet.fromPhrase(s.value, undefined, `m/44'/60'/0'/0/${i}`);
      secrets.push({ name: `clé privée du compte Fuji n°${i}`, value: w.privateKey.slice(2), from: "dérivée" });
    }
    const words = s.value.split(/\s+/);
    if (words.length >= 12) secrets.push({ name: s.name + " (6 premiers mots)", value: words.slice(0, 6).join(" "), from: s.from });
  } catch (e) { console.log("dérivation des clés impossible :", e.message.split("\n")[0]); }
}

// 2. Chaque valeur : dans les fichiers suivis, puis dans tout l'historique (toutes branches).
let found = 0;
const tracked = git(["ls-files"]).split("\n").filter(Boolean);
console.log(`\nFichiers suivis par Git : ${tracked.length}. Commits (toutes branches) : ${git(["rev-list", "--all", "--count"]).trim()}.`);
for (const s of secrets) {
  const inTree = tryGit(["grep", "-l", "-F", "-e", s.value, "--"]).split("\n").filter(Boolean);
  const inHistory = tryGit(["log", "--all", "--oneline", "-S" + s.value]).split("\n").filter(Boolean);
  if (inTree.length || inHistory.length) {
    found++;
    console.log(`  ⚠️ ${s.name} : fichiers suivis [${inTree.join(", ")}] ; commits [${inHistory.map((l) => l.slice(0, 60)).join(" | ")}]`);
  }
}
console.log(found ? `→ ${found} secret(s) réel(s) retrouvé(s) dans Git.` : "→ Aucune valeur réelle des .env (ni clé privée dérivée) dans les fichiers suivis ni dans l'historique.");

// 3. Un .env suivi par Git ?
const trackedEnv = tracked.filter((f) => /(^|\/)\.env(\.|$)/.test(f));
const everEnv = [...new Set(tryGit(["log", "--all", "--name-only", "--pretty=format:", "--diff-filter=A"]).split("\n").filter((f) => /(^|\/)\.env(\.|$)/.test(f)))];
console.log("\nFichiers .env suivis aujourd'hui :", trackedEnv.join(", ") || "(aucun)");
console.log("Fichiers .env ajoutés un jour dans l'historique :", everEnv.join(", ") || "(aucun)");

// 4. Motifs génériques, sur tout l'historique : attrape un secret qui ne serait plus dans nos .env.
const PATTERNS = {
  "clé Bedrock (ABSK…)": "ABSK[A-Za-z0-9+/=]{20,}",
  "variable Bedrock avec valeur": "AWS_BEARER_TOKEN_BEDROCK\\s*[=:]\\s*[\"']?[A-Za-z0-9+/=_-]{16,}",
  "clé d'accès AWS": "(AKIA|ASIA)[0-9A-Z]{16}",
  "jeton Apify": "apify_api_[A-Za-z0-9]{20,}",
  "clé Anthropic / OpenAI": "sk-(ant-)?[A-Za-z0-9_-]{24,}",
  "jeton GitHub": "(ghp|gho|ghs|ghu|github_pat)_[A-Za-z0-9_]{20,}",
  "jeton de bot Telegram": "[0-9]{8,10}:AA[A-Za-z0-9_-]{30,}",
  "clé privée (bloc PEM)": "-----BEGIN [A-Z ]*PRIVATE KEY-----",
  "variable de clé privée avec valeur": "(PRIVATE_KEY|MNEMONIC|SMTP_PASSWORD|APIFY_TOKEN|TELEGRAM_BOT_TOKEN|CLOUDFLARE_API_TOKEN|API_KEY|SECRET)\\s*[=:]\\s*[\"']?[A-Za-z0-9+/_ -]{12,}",
  "jeton Slack / Stripe / Google": "(xox[baprs]-[A-Za-z0-9-]{10,}|sk_live_[A-Za-z0-9]{16,}|AIza[0-9A-Za-z_-]{35})",
};
console.log("\nMotifs génériques dans l'historique complet (lignes ajoutées) :");
const history = git(["log", "--all", "-p", "--no-color", "--unified=0", "--pretty=format:@@@%h %s"]);
let commit = "", file = "";
const hits = {};
for (const line of history.split("\n")) {
  if (line.startsWith("@@@")) { commit = line.slice(3, 60); continue; }
  if (line.startsWith("+++ ")) { file = line.slice(6); continue; }
  if (!line.startsWith("+")) continue;
  for (const [label, source] of Object.entries(PATTERNS)) {
    const m = line.match(new RegExp(source));
    if (!m) continue;
    const key = `${label} — ${file}`;
    (hits[key] = hits[key] || { n: 0, commits: new Set(), sample: "" }).n++;
    hits[key].commits.add(commit.split(" ")[0]);
    // Aperçu masqué : le début de la ligne sans la valeur trouvée.
    if (!hits[key].sample) hits[key].sample = line.slice(1, 1 + Math.min(line.indexOf(m[0]) - 1 + 28, 70)).replace(/[A-Za-z0-9+/=_-]{14,}/g, "‹masqué›");
  }
}
const keys = Object.keys(hits);
if (!keys.length) console.log("  aucun");
for (const k of keys) console.log(`  ${k} : ${hits[k].n} ligne(s), commits ${[...hits[k].commits].slice(0, 4).join(",")} ; aperçu : ${hits[k].sample}`);

// 5. Morceaux de secrets : un secret coupé par un retour à la ligne (transcription, journal) échappe à la
//    recherche exacte. On cherche donc chaque secret par tranches de 20 caractères (3 mots pour une phrase secrète).
console.log("\nMorceaux de secrets (fichiers suivis et historique) :");
const treeText = tryGit(["grep", "-I", "-h", "-e", ""]);
let pieces = 0;
for (const s of secrets.filter((x) => x.from !== "dérivée" && !/premiers mots/.test(x.name))) {
  const chunks = [];
  const words = s.value.split(/\s+/);
  if (words.length >= 12) for (let i = 0; i + 3 <= words.length; i++) chunks.push(words.slice(i, i + 3).join(" "));
  else if (s.value.length >= 24) { for (let i = 0; i + 20 <= s.value.length; i += 20) chunks.push(s.value.slice(i, i + 20)); chunks.push(s.value.slice(-20)); }
  else continue; // valeur courte : la recherche exacte du point 2 suffit
  const inHistory = chunks.filter((c) => history.includes(c)).length;
  const inTree = chunks.filter((c) => treeText.includes(c)).length;
  pieces += inHistory + inTree;
  console.log(`  ${s.name} : ${chunks.length} morceaux cherchés ; historique ${inHistory} ; fichiers suivis ${inTree}`);
}

const problems = found + pieces + keys.length + trackedEnv.filter((f) => !f.endsWith(".example")).length;
console.log(problems ? `\n⚠️ ${problems} point(s) à examiner ci-dessus.` : "\n✅ Zéro secret : rien trouvé dans les fichiers suivis ni dans l'historique.");
process.exitCode = problems ? 1 : 0;
