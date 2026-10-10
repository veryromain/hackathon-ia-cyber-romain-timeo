// État du déploiement Fuji en LECTURE SEULE : aucune clé nécessaire, ça marche sur le Mac de Romain.
// Usage (depuis ia-2) : npx hardhat run ../ia-1/integration/etat-fuji.js --network fuji
const fs = require("fs");
const path = require("path");
const hre = require(require.resolve("hardhat", { paths: [process.cwd()] })); // hardhat de ia-2
const { ethers } = hre;
const RISK = ["aucun", "signatures en plus", "mise en attente"];
const fmt = (wei) => Number(ethers.formatEther(wei)).toLocaleString("fr-FR", { maximumFractionDigits: 4 });

async function main() {
  const dep = path.join(process.cwd(), "deployments");
  const info = JSON.parse(fs.readFileSync(path.join(dep, "fuji.json"), "utf8"));
  const comptes = JSON.parse(fs.readFileSync(path.join(dep, "fuji-comptes.json"), "utf8")).accounts;
  const wallet = await ethers.getContractAt("TreasuryGuard", info.wallet);
  const musd = await ethers.getContractAt("MockToken", info.musd);
  const latest = await ethers.provider.getBlockNumber();

  console.log(`Fuji, bloc ${latest} (${latest - info.deploy_block} blocs depuis le déploiement)`);
  console.log(`Portefeuille ${info.wallet} : ${(await wallet.frozen()) ? "GELÉ (npm run unfreeze:fuji)" : "non gelé"}`);
  console.log(`Trésorerie : ${fmt(await musd.balanceOf(info.wallet))} mUSD`);
  console.log(`Clés disponibles sur cette machine : ${(await ethers.getSigners()).length} (0 = FUJI_MNEMONIC absent de ia-2/.env, lecture seule)`);

  console.log("\nComptes de test (AVAX pour le gas) :");
  for (const c of comptes) console.log(`  ${c.role.padEnd(24)} ${c.address}  ${fmt(await ethers.provider.getBalance(c.address))} AVAX`);

  const n = Number(await wallet.proposalCount());
  console.log(`\nPaiements proposés : ${n}`);
  for (let i = 0; i < n; i++) {
    const p = await wallet.getProposal(i);
    const etat = p.executed ? "exécuté" : p.cancelled ? "annulé" : "en cours";
    console.log(`  ${String(i).padStart(3)}  ${fmt(p.value).padStart(12)} mUSD  vers ${p.target}  risque : ${RISK[Number(p.risk)]}  ${etat}`);
  }
}
main().catch((e) => { console.error(e.shortMessage || e.message); process.exitCode = 1; });
