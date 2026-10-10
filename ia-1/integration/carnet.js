// Écrit le carnet d'adresses de la démo locale : le fournisseur habituel du scénario de Timéo (compte n° 8).
// Usage (depuis ia-2) : npx hardhat run ../ia-1/integration/carnet.js --network localhost
const hre = require(require.resolve("hardhat", { paths: [process.cwd()] })); // hardhat de ia-2
const path = require("path");
async function main() {
  const signers = await hre.ethers.getSigners();
  const carnet = [signers[8].address.toLowerCase()];
  require("fs").writeFileSync(path.join(__dirname, "carnet-local.json"), JSON.stringify(carnet));
  console.log("carnet :", carnet);
}
main();
