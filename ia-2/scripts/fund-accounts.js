// Répartit les AVAX de test du déployeur vers les comptes qui signent des transactions
// (5 signataires, moniteur, oracle). Sans effet sur les comptes déjà approvisionnés.
// Usage : npm run fuji:fund          AVAX_PAR_COMPTE=0.05 pour changer le montant
const hre = require("hardhat");

const { ethers, network } = hre;
const ROLES = ["déployeur", "signataire 1", "signataire 2", "signataire 3", "signataire 4", "signataire 5", "moniteur", "oracle"];

async function main() {
  const signers = (await ethers.getSigners()).slice(0, ROLES.length);
  if (signers.length < ROLES.length) throw new Error("Phrase secrète absente : lancer d'abord npm run fuji:setup.");
  const [deployer, ...others] = signers;
  const fmt = (wei) => Number(ethers.formatEther(wei)).toFixed(4);

  const available = await ethers.provider.getBalance(deployer.address);
  console.log(`Réseau ${network.name}. Déployeur ${deployer.address} : ${fmt(available)} AVAX`);
  if (available === 0n) {
    console.log("Le déployeur n'a aucun AVAX : demander des AVAX de test au faucet pour cette adresse, puis relancer.");
    process.exitCode = 1;
    return;
  }

  // Par défaut 0,05 AVAX par compte, sans jamais dépasser la moitié de ce qu'a le déployeur.
  const wanted = ethers.parseEther(process.env.AVAX_PAR_COMPTE || "0.05");
  const ceiling = available / 2n / BigInt(others.length);
  const amount = wanted < ceiling ? wanted : ceiling;

  for (let i = 0; i < others.length; i++) {
    const account = others[i];
    const balance = await ethers.provider.getBalance(account.address);
    if (balance >= amount / 2n) {
      console.log(`  ${ROLES[i + 1].padEnd(14)} ${account.address} : ${fmt(balance)} AVAX, déjà approvisionné`);
      continue;
    }
    const tx = await deployer.sendTransaction({ to: account.address, value: amount });
    await tx.wait();
    console.log(`  ${ROLES[i + 1].padEnd(14)} ${account.address} : +${fmt(amount)} AVAX (${tx.hash})`);
  }
  console.log(`Reste au déployeur : ${fmt(await ethers.provider.getBalance(deployer.address))} AVAX`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
