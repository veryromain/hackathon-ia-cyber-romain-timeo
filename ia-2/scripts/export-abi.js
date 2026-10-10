// Copie les ABI des contrats dans shared/abi/ pour le moniteur Python (ia-1).
// Usage : npm run export-abi
const fs = require("fs");
const path = require("path");
const hre = require("hardhat");

const CONTRACTS = ["BreakerVault", "SimplePool", "MockToken"];

async function main() {
  await hre.run("compile");
  const outDir = path.join(__dirname, "..", "..", "shared", "abi");
  fs.mkdirSync(outDir, { recursive: true });
  for (const name of CONTRACTS) {
    const artifact = await hre.artifacts.readArtifact(name);
    fs.writeFileSync(path.join(outDir, `${name}.json`), JSON.stringify(artifact.abi, null, 2) + "\n");
    console.log(`ABI écrite : shared/abi/${name}.json`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
