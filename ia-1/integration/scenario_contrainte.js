// Démo de la clé de contrainte / d'identité : un signataire menacé « approuve » avec sa seconde clé.
// À l'écran : approuvé. En réalité : paiement inexécutable, arrêt silencieux, et le moteur alerte les AUTRES signataires en privé.
// Usage (depuis ia-2) : SIGNATAIRE=3 npx hardhat run ../ia-1/integration/scenario_contrainte.js --network localhost|fuji
const path = require("path");
const hre = require(require.resolve("hardhat", { paths: [process.cwd()] }));
const { loadDeployment } = require(path.join(process.cwd(), "lib", "deployment"));
const { ethers } = hre;
const sleep = (s) => new Promise((r) => setTimeout(r, s * 1000));
const hashOf = (a) => ethers.solidityPackedKeccak256(["address"], [a]);
(async () => {
  const { info, signerOf, wallet, musd } = await loadDeployment(hre);
  const owners = info.owners.map(signerOf);
  const idx = Number(process.env.SIGNATAIRE || 3);
  const victime = owners[idx];
  let proposeur = null;  // premier autre signataire encore actif (une clé révoquée par une démo précédente ne compte plus)
  for (const o of owners) if (o.address !== victime.address && (await wallet.isActiveOwner(o.address))) { proposeur = o; break; }
  const net = await ethers.provider.getNetwork();
  const identite = ethers.Wallet.createRandom().connect(ethers.provider);
  console.log(`0. Bien avant : le signataire ${idx} déclare sa clé d'identité (hash seulement sur la chaîne)`);
  await (await wallet.connect(victime).setDuressKey(hashOf(identite.address))).wait();
  await (await (await ethers.getSigners())[0].sendTransaction({ to: identite.address, value: ethers.parseEther(Number(net.chainId) === 31337 ? "1" : "0.01") })).wait();
  console.log("\n1. Sous pression, on lui fait approuver un gros paiement vers l'adresse de l'extorqueur");
  const extorqueur = ethers.Wallet.createRandom().address;
  const id = Number(await wallet.proposalCount());
  await (await wallet.connect(proposeur).proposePayment(extorqueur, ethers.parseEther("60000"), "Règlement partenaire")).wait();
  console.log(`   paiement ${id} proposé par un complice ; le signataire menacé approuve... avec sa clé d'identité`);
  await (await wallet.connect(identite).approve(id)).wait();
  const p = await wallet.getProposal(id);
  console.log(`   à l'écran : ${await wallet.validApprovals(id)}/${await wallet.requiredApprovals(id)} signatures, gelé officiellement ? ${await wallet.frozen()}`);
  await sleep(Number(info.config.reviewDelay) + 2);
  console.log("\n2. L'extorqueur tente d'exécuter");
  try { await (await wallet.connect(proposeur).execute(id)).wait(); console.log("   EXÉCUTÉ (ne devrait pas)"); }
  catch (e) { console.log(`   refusé : ${(e.shortMessage || e.message).split("\n")[0].slice(0, 80)}`); }
  console.log(`   Trésorerie : ${ethers.formatEther(await musd.balanceOf(wallet.target))} mUSD ; chez l'extorqueur : ${ethers.formatEther(await musd.balanceOf(extorqueur))} mUSD`);
})().catch((e) => { console.error(e); process.exitCode = 1; });
