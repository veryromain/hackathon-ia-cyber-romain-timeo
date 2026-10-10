// Prépare les comptes de TEST pour Avalanche Fuji (tâche T6).
// Crée une phrase secrète dans ia-2/.env si elle n'existe pas encore (fichier ignoré par Git),
// puis affiche les adresses publiques qui en dérivent. La phrase elle-même n'est jamais affichée.
// Usage : npm run fuji:setup
const fs = require("fs");
const path = require("path");
const { ethers } = require("ethers");

const ENV_FILE = path.join(__dirname, "..", ".env");
const OUT_FILE = path.join(__dirname, "..", "deployments", "fuji-comptes.json");
const ROLES = ["déployeur", "signataire 1", "signataire 2", "signataire 3", "signataire 4", "signataire 5", "moniteur", "oracle", "prestataire habituel", "prestataire habituel 2"];
const FAUCET = "https://build.avax.network/docs/dapps/smart-contract-dev/get-test-funds";

function readEnv() {
  if (!fs.existsSync(ENV_FILE)) return {};
  const entries = {};
  for (const line of fs.readFileSync(ENV_FILE, "utf8").split(/\r?\n/)) {
    const match = line.match(/^([A-Z_]+)=(.*)$/);
    if (match) entries[match[1]] = match[2].trim();
  }
  return entries;
}

function main() {
  const env = readEnv();
  let phrase = env.FUJI_MNEMONIC;
  if (!phrase) {
    phrase = ethers.Wallet.createRandom().mnemonic.phrase;
    const lines = fs.existsSync(ENV_FILE) ? fs.readFileSync(ENV_FILE, "utf8").split(/\r?\n/).filter((l) => !l.startsWith("FUJI_MNEMONIC=")) : [
      "# Fichier local, ignoré par Git. Ne jamais le committer ni le partager dans un message.",
      "# Phrase secrète de TEST du hackathon : ses comptes ne reçoivent que des AVAX du faucet Fuji.",
      "FUJI_RPC_URL=https://api.avax-test.network/ext/bc/C/rpc",
    ];
    while (lines.length && lines[lines.length - 1] === "") lines.pop();
    lines.push(`FUJI_MNEMONIC=${phrase}`, "");
    fs.writeFileSync(ENV_FILE, lines.join("\n"));
    console.log("Phrase secrète de test créée dans ia-2/.env (ignoré par Git).");
  } else {
    console.log("Phrase secrète de test déjà présente dans ia-2/.env.");
  }

  // Même chemin de dérivation que Hardhat : m/44'/60'/0'/0/i
  const accounts = ROLES.map((role, index) => ({
    index, role, address: ethers.HDNodeWallet.fromPhrase(phrase, undefined, `m/44'/60'/0'/0/${index}`).address,
  }));
  fs.mkdirSync(path.dirname(OUT_FILE), { recursive: true });
  fs.writeFileSync(OUT_FILE, JSON.stringify({ network: "fuji", chain_id: 43113, note: "Adresses publiques de comptes de test. Aucune clé ici.", accounts }, null, 2) + "\n");

  console.log("\nComptes de test (adresses publiques) :");
  for (const a of accounts) console.log(`  ${String(a.index).padStart(2)}  ${a.role.padEnd(24)} ${a.address}`);
  console.log(`\nÀ faire : demander des AVAX de test pour le DÉPLOYEUR, ${accounts[0].address}`);
  console.log(`  Mode d'emploi du faucet : ${FAUCET}`);
  console.log("  Puis : npm run fuji:fund (répartit vers les autres comptes), npm run deploy:fuji");
}

main();
