// Scénario de la clé de contrainte : un signataire menacé approuve un gros paiement avec sa seconde clé.
// À l'écran, le paiement est « approuvé, 2 sur 2 ». En réalité il ne s'exécutera jamais, les autres
// paiements s'arrêtent en silence, et les collègues peuvent reprendre la main.
// Le relais peut tourner à côté : le moteur de score reconnaît la contrainte au fait que la transaction
// d'approbation n'est pas signée par l'adresse du signataire nommé dans l'événement.
// Usage : npm run duress:local   (RESPOND=1 pour que trois collègues lèvent le gel et annulent)
const hre = require("hardhat");
const { loadDeployment } = require("../lib/deployment");

const { ethers } = hre;
const e18 = (n) => ethers.parseEther(String(n));
const sleep = (seconds) => new Promise((resolve) => setTimeout(resolve, seconds * 1000));
const reason = (error) => {
  const text = String(error.shortMessage || error.message);
  const custom = text.match(/custom error '([^']+)'/);
  return error.revert ? error.revert.name : custom ? custom[1].replace(/\(.*/, "") : text.split("\n")[0];
};

async function main() {
  const { info, signerOf, musd, wallet } = await loadDeployment(hre);
  const [deployer] = await ethers.getSigners();
  const [alice, bruno, chloe, david, emma] = info.owners.map(signerOf);
  const mule = ethers.Wallet.createRandom().address;
  const review = info.config.reviewDelay;

  console.log("0. Bien avant : Emma déclare une clé de contrainte (seul son hash part sur la chaîne)");
  const duressKey = ethers.Wallet.createRandom().connect(ethers.provider);
  await (await deployer.sendTransaction({ to: duressKey.address, value: ethers.parseEther("0.01") })).wait(); // gas
  await (await wallet.connect(emma).setDuressKey(ethers.solidityPackedKeccak256(["address"], [duressKey.address]))).wait();

  console.log("1. Un complice propose 90 000 mUSD vers une adresse inconnue");
  const id = Number(await wallet.proposalCount());
  await (await wallet.connect(david).proposePayment(mule, e18(90000), "Règlement urgent, dossier confidentiel")).wait();

  console.log("2. Emma, sous la menace, approuve avec sa clé de contrainte");
  const receipt = await (await wallet.connect(duressKey).approve(id)).wait();
  const approved = wallet.interface.parseLog(receipt.logs[0]);
  console.log(`   ce que tout le monde voit : paiement ${id} approuvé par ${approved.args.owner} (${approved.args.approvals} sur ${approved.args.requiredApprovals})`);
  console.log(`   ce que le moteur remarque : la transaction est signée par ${duressKey.address}, pas par Emma`);
  console.log(`   portefeuille gelé officiellement ? ${await wallet.frozen()}`);

  console.log(`3. Attente du délai d'examen (${review} s), puis le fraudeur tente d'exécuter`);
  await sleep(review + 3);
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      await (await wallet.connect(david).execute(id)).wait();
      console.log("   EXÉCUTÉ : le mécanisme n'a pas fonctionné");
    } catch (error) {
      console.log(`   tentative ${attempt} refusée : ${reason(error)} (la même erreur qu'une mise en attente)`);
    }
    if (attempt === 1) await sleep(4);
  }

  if (process.env.RESPOND === "1") {
    console.log("4. Prévenus par le moteur, trois collègues reprennent la main");
    for (const owner of [alice, bruno, chloe]) await (await wallet.connect(owner).approveUnfreeze()).wait();
    await (await wallet.connect(alice).cancel(id, "approuvé sous contrainte")).wait();
    console.log("   gel silencieux levé, paiement annulé");
  }
  console.log(`\nBilan : ${ethers.formatEther(await musd.balanceOf(mule))} mUSD parti chez le fraudeur sur 90 000 tentés.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
