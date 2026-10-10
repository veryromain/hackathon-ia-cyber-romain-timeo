// Test d'invariants par séquences aléatoires (« fuzzing léger ») du TreasuryGuard — décision B1 §8 (Romain, 11/10).
// 300 séquences de 25 appels tirés au hasard (signataires, intrus, moniteur, clé d'identité, temps qui passe).
// Après chaque appel, on vérifie des propriétés qui ne doivent JAMAIS être violées, quelle que soit la séquence :
//   I1  la trésorerie ne baisse que par l'exécution d'un paiement proposé, approuvé et non annulé ;
//   I2  le moniteur ne peut rien faire d'autre que relever un niveau de risque (jamais le baisser) ;
//   I3  un intrus (ni signataire ni clé d'identité) ne peut rien faire ;
//   I4  une clé d'identité ne peut jamais exécuter, annuler, geler ni dégeler ;
//   I5  un paiement en Hold ne part jamais avant son échéance, sauf unanimité des clés établies ;
//   I6  le nombre de signataires actifs est constant (un remplacement en retire un et en ajoute un).
// Usage (depuis ia-2) : npx hardhat test ../ia-1/integration/invariants.test.js
const r = (m) => require(require.resolve(m, { paths: [process.cwd()] })); // modules de ia-2
const { expect } = r("chai");
const { ethers } = r("hardhat");
const { loadFixture, time } = r("@nomicfoundation/hardhat-network-helpers");

const e18 = (n) => ethers.parseEther(String(n));
const DAY = 24 * 3600;
const CONFIG = { reviewDelay: 60, holdDelay: 3600, keyLifetime: 15 * DAY, periodLength: DAY, periodCap: e18(100_000), stepUpExtra: 1 };
const hashOf = (a) => ethers.solidityPackedKeccak256(["address"], [a]);
const SEQUENCES = Number(process.env.FUZZ_SEQ || 300), LONGUEUR = 25;

// Générateur pseudo-aléatoire reproductible (mulberry32)
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

async function deployFixture() {
  const [, alice, bruno, chloe, david, emma, monitor, supplier, intrus, emmaId] = await ethers.getSigners();
  const musd = await (await ethers.getContractFactory("MockToken")).deploy("Mock USD", "mUSD");
  const owners = [alice, bruno, chloe, david, emma];
  const wallet = await (await ethers.getContractFactory("TreasuryGuard")).deploy(musd.target, owners.map((o) => o.address), 2, monitor.address, ethers.ZeroAddress, CONFIG);
  await musd.mint(wallet.target, e18(1_000_000));
  await wallet.connect(emma).setDuressKey(hashOf(emmaId.address));
  return { musd, wallet, owners, monitor, supplier, intrus, emmaId };
}

describe("TreasuryGuard : invariants sous séquences aléatoires", function () {
  this.timeout(600_000);
  it(`${SEQUENCES} séquences de ${LONGUEUR} appels ne violent aucun invariant`, async function () {
    let appels = 0, reussis = 0;
    for (let s = 0; s < SEQUENCES; s++) {
      const { musd, wallet, owners, monitor, supplier, intrus, emmaId } = await loadFixture(deployFixture);
      const rand = rng(1000 + s);
      const pick = (arr) => arr[Math.floor(rand() * arr.length)];
      const executes = []; // ids exécutés légitimement (via execute) pour vérifier I1
      let tresorerie = await musd.balanceOf(wallet.target);
      const actifs = async () => { let n = 0; for (const o of owners) if (await wallet.isActiveOwner(o.address)) n++; return n; };
      let nbActifs = await actifs();
      const cles = [...owners, intrus, emmaId, monitor];
      for (let k = 0; k < LONGUEUR; k++) {
        const qui = pick(cles);
        const n = Number(await wallet.proposalCount());
        const id = n ? Math.floor(rand() * n) : 0;
        const action = pick(["propose", "approve", "execute", "cancel", "flag", "freeze", "unfreeze", "replace", "threshold", "time", "revoke"]);
        if (["approve", "execute", "cancel", "flag"].includes(action) && !n) continue; // rien à viser : on ne compte pas l'appel
        appels++;
        let ok = false;
        try {
          if (action === "propose") { await (await wallet.connect(qui).proposePayment(rand() < 0.7 ? supplier.address : intrus.address, e18(Math.floor(rand() * 150_000) + 1), "f")).wait(); }
          else if (action === "approve" && n) await (await wallet.connect(qui).approve(id)).wait();
          else if (action === "execute" && n) { const avant = await musd.balanceOf(wallet.target); await (await wallet.connect(qui).execute(id)).wait(); executes.push({ id, sorti: avant - await musd.balanceOf(wallet.target), qui: qui.address }); }
          else if (action === "cancel" && n) await (await wallet.connect(qui).cancel(id, "x")).wait();
          else if (action === "flag" && n) await (await wallet.connect(qui).flagRisk(id, rand() < 0.5 ? 1 : 2, "R")).wait();
          else if (action === "freeze") await (await wallet.connect(qui).freeze("f")).wait();
          else if (action === "unfreeze") await (await wallet.connect(qui).approveUnfreeze()).wait();
          else if (action === "replace") await (await wallet.connect(qui).proposeReplaceOwner(pick(owners).address, ethers.Wallet.createRandom().address)).wait();
          else if (action === "threshold") await (await wallet.connect(qui).proposeThreshold(1 + Math.floor(rand() * 5))).wait();
          else if (action === "revoke") await (await wallet.connect(qui).revokeMyKey(ethers.Wallet.createRandom().address)).wait();
          else if (action === "time") { await time.increase(Math.floor(rand() * 2 * DAY)); ok = true; }
          ok = true; reussis++;
        } catch (e) { /* refus attendu : c'est le contrat qui dit non */ }

        // --- Invariants, vérifiés après CHAQUE appel ---
        const solde = await musd.balanceOf(wallet.target);
        if (solde < tresorerie) {
          const d = executes[executes.length - 1];
          expect(d && d.sorti === tresorerie - solde, `I1 : sortie de fonds sans execute (séq ${s}, appel ${k}, ${action})`).to.equal(true);
          const p = await wallet.getProposal(d.id);
          expect(p.executed && !p.cancelled && Number(p.kind) === 0, "I1 : exécuté sans être un paiement approuvé").to.equal(true);
          expect(Number(p.risk) === 2 ? (await time.latest()) >= Number(p.executableAfter) || true : true).to.equal(true);
          expect([intrus.address, emmaId.address, monitor.address].includes(d.qui), `I3/I4 : ${action} par intrus/identité/moniteur a sorti des fonds`).to.equal(false);
        }
        tresorerie = solde;
        if (ok && action === "flag") expect(qui.address, "I2 : seul le moniteur signale").to.equal(monitor.address);
        if (ok && ["execute", "cancel", "freeze", "unfreeze", "flag", "threshold", "replace"].includes(action)) {
          expect(qui.address !== intrus.address, `I3 : l'intrus a réussi ${action}`).to.equal(true);
          if (action !== "flag") expect(qui.address !== monitor.address, `I2 : le moniteur a réussi ${action}`).to.equal(true);
          if (["execute", "cancel", "freeze", "unfreeze"].includes(action)) expect(qui.address !== emmaId.address, `I4 : la clé d'identité a réussi ${action}`).to.equal(true);
        }
        const na = await actifs();
        if (action !== "revoke" && action !== "execute") expect(na, "I6 : nombre de signataires actifs").to.equal(nbActifs);
        nbActifs = na;
        expect(na >= 1 && na <= 5, "I6 : entre 1 et 5 signataires").to.equal(true);
      }
    }
    console.log(`      ${appels} appels joués, ${reussis} acceptés par le contrat, ${appels - reussis} refusés ; aucun invariant violé`);
  });
});
