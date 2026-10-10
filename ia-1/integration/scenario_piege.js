// Démo de l'idée 2 : un attaquant qui a lu le carnet propose un paiement vers une adresse piège.
// Usage (depuis ia-2) : PIEGE=0x… npx hardhat run ../ia-1/integration/scenario_piege.js --network localhost|fuji
const path = require("path");
const hre = require(require.resolve("hardhat", { paths: [process.cwd()] }));
const { loadDeployment } = require(path.join(process.cwd(), "lib", "deployment"));
const { ethers } = hre;
(async () => {
  const { info, signerOf, wallet } = await loadDeployment(hre);
  const [, , , david, emma] = info.owners.map(signerOf);
  const piege = process.env.PIEGE;
  const id = Number(await wallet.proposalCount());
  await (await wallet.connect(emma).proposePayment(piege, ethers.parseEther("7200"), "Facture Cabinet Dupont - conseil")).wait();
  await (await wallet.connect(david).approve(id)).wait();
  console.log(`Paiement ${id} proposé : 7 200 mUSD vers l'adresse piège ${piege} (« Cabinet Dupont » n'existe pas : seul un lecteur du carnet pouvait la proposer)`);
})().catch((e) => { console.error(e); process.exitCode = 1; });
