// Démo de la clé d'identité froide (décision de Romain, 10/10 22:10).
// 1. Bien avant : Emma déclare sa clé d'identité (seul le hash part sur la chaîne). On lui envoie un peu d'AVAX de test.
// 2. Sa clé de tous les jours est volée : le voleur propose un gros paiement et le fait approuver par un complice.
// 3. Emma, depuis son téléphone / portefeuille matériel, RÉVOQUE sa clé avec sa clé d'identité : seule, tout de suite.
// 4. Le voleur ne peut plus rien faire ; la nouvelle clé d'Emma est en probation ; les collègues annulent le paiement.
// Le relais et le moteur tournent à côté : le moteur signale le paiement (gros montant, inconnu) et voit la révocation.
// Usage (depuis ia-2) : npx hardhat run ../ia-1/integration/scenario_identite.js --network localhost|fuji
const path = require("path");
const hre = require(require.resolve("hardhat", { paths: [process.cwd()] }));
const { loadDeployment } = require(path.join(process.cwd(), "lib", "deployment"));
const { ethers } = hre;
const sleep = (s) => new Promise((r) => setTimeout(r, s * 1000));
const hashOf = (a) => ethers.solidityPackedKeccak256(["address"], [a]);

(async () => {
  const { info, signerOf, wallet, musd } = await loadDeployment(hre);
  const [alice, bruno, chloe, david, emma] = info.owners.map(signerOf);
  const deployer = signerOf(info.deployer || info.owners[0]) ?? alice;
  const net = await ethers.provider.getNetwork();
  const identite = ethers.Wallet.createRandom().connect(ethers.provider);

  console.log("0. Bien avant : Emma déclare sa clé d'identité (seul son hash part sur la chaîne)");
  await (await wallet.connect(emma).setDuressKey(hashOf(identite.address))).wait();
  // Un peu d'AVAX de test pour que la clé d'identité puisse payer le gas de sa révocation (en prod : le téléphone / le portefeuille matériel).
  const financeur = (await ethers.getSigners())[0];
  await (await financeur.sendTransaction({ to: identite.address, value: ethers.parseEther(Number(net.chainId) === 31337 ? "1" : "0.01") })).wait();
  console.log(`   clé d'identité : ${identite.address} (jamais utilisée au quotidien)\n`);

  console.log("1. La clé de tous les jours d'Emma est volée : le voleur propose 80 000 mUSD vers lui-même, un complice (David) approuve");
  const voleur = ethers.Wallet.createRandom().address;
  const id = Number(await wallet.proposalCount());
  await (await wallet.connect(emma).proposePayment(voleur, ethers.parseEther("80000"), "Règlement fournisseur - urgent")).wait();
  await (await wallet.connect(david).approve(id)).wait();
  console.log(`   paiement ${id} proposé et approuvé 2/2 par la clé volée d'Emma + David`);
  await sleep(3);

  console.log("\n2. Emma s'en aperçoit : depuis son téléphone, elle RÉVOQUE sa clé volée avec sa clé d'identité (seule, sans quorum)");
  const nouvelle = ethers.Wallet.createRandom().address;
  const tx = await (await wallet.connect(identite).revokeMyKey(nouvelle)).wait();
  console.log(`   KeyRevokedBySelf : ${emma.address} → ${nouvelle}  (tx ${tx.hash})`);
  console.log(`   ancienne clé active ? ${await wallet.isActiveOwner(emma.address)} | nouvelle clé active ? ${await wallet.isActiveOwner(nouvelle)} | établie (hors probation) ? ${await wallet.isEstablishedOwner(nouvelle)}`);

  console.log("\n3. Le voleur tente de continuer avec la clé volée");
  for (const [nom, f] of [["exécuter le paiement", () => wallet.connect(emma).execute(id)], ["proposer un autre paiement", () => wallet.connect(emma).proposePayment(voleur, ethers.parseEther("50000"), "x")]]) {
    try { await (await f()).wait(); console.log(`   ${nom} : PASSÉ (ne devrait pas)`); }
    catch (e) { console.log(`   ${nom} : refusé (${(e.shortMessage || e.message).split("\n")[0].slice(0, 60)})`); }
  }

  console.log("\n4. Les collègues annulent le paiement du voleur");
  await (await wallet.connect(alice).cancel(id, "clé d'Emma compromise, révoquée par elle-même")).wait();
  console.log(`   paiement ${id} annulé. Trésorerie : ${ethers.formatEther(await musd.balanceOf(wallet.target))} mUSD ; chez le voleur : ${ethers.formatEther(await musd.balanceOf(voleur))} mUSD`);
})().catch((e) => { console.error(e); process.exitCode = 1; });
