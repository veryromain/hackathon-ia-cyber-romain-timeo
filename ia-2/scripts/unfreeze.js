// Lève le gel du portefeuille après une démo : trois signataires votent le dégel, l'un après l'autre.
// Usage : npm run unfreeze:local   ou   npm run unfreeze:fuji
const hre = require("hardhat");
const { loadDeployment } = require("../lib/deployment");

async function main() {
  const { info, signerOf, wallet } = await loadDeployment(hre);
  if (!(await wallet.frozen())) {
    console.log("Le portefeuille n'est pas gelé : rien à faire.");
    return;
  }
  for (const address of info.owners) {
    if (!(await wallet.frozen())) break;
    const owner = signerOf(address);
    if (await wallet.hasApprovedUnfreeze(await wallet.unfreezeRound(), address)) continue;
    const receipt = await (await wallet.connect(owner).approveUnfreeze()).wait();
    console.log(`  ${address} vote le dégel (${receipt.hash})`);
  }
  console.log((await wallet.frozen()) ? "Toujours gelé : pas assez de signataires actifs." : "Portefeuille dégelé.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
