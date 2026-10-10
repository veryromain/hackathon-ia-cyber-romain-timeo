const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture, time } = require("@nomicfoundation/hardhat-network-helpers");

const e18 = (n) => ethers.parseEther(String(n));
const Risk = { None: 0, StepUp: 1, Hold: 2 };
const DAY = 24 * 3600;

const GUARDED = {
  reviewDelay: 60,
  holdDelay: 3600,
  keyLifetime: 15 * DAY,
  periodLength: DAY,
  periodCap: e18(100_000),
  stepUpExtra: 1,
};
// Portefeuille témoin : un simple 2 sur 5, sans délai, sans plafond, sans moniteur ni registre.
const UNGUARDED = {
  reviewDelay: 0,
  holdDelay: 0,
  keyLifetime: 3650 * DAY,
  periodLength: DAY,
  periodCap: ethers.MaxUint256,
  stepUpExtra: 0,
};
const TREASURY = e18(1_000_000);

async function deployFixture() {
  const [deployer, alice, bruno, chloe, david, emma, monitor, oracle, supplier, mule, outsider, frank] = await ethers.getSigners();
  const owners = [alice, bruno, chloe, david, emma];

  const Token = await ethers.getContractFactory("MockToken");
  const Registry = await ethers.getContractFactory("RiskRegistry");
  const Wallet = await ethers.getContractFactory("TreasuryGuard");

  const musd = await Token.deploy("Mock USD", "mUSD");
  const registry = await Registry.deploy(deployer.address);
  await registry.grantRole(await registry.ORACLE_ROLE(), oracle.address);

  const ownerAddresses = owners.map((o) => o.address);
  const wallet = await Wallet.deploy(musd.target, ownerAddresses, 2, monitor.address, registry.target, GUARDED);
  const plain = await Wallet.deploy(musd.target, ownerAddresses, 2, ethers.ZeroAddress, ethers.ZeroAddress, UNGUARDED);
  await musd.mint(wallet.target, TREASURY);
  await musd.mint(plain.target, TREASURY);

  return { musd, registry, wallet, plain, deployer, alice, bruno, chloe, david, emma, monitor, oracle, supplier, mule, outsider, frank };
}

/// Propose un paiement et renvoie son identifiant.
async function propose(wallet, signer, to, amount, memo = "paiement") {
  const id = await wallet.proposalCount();
  await wallet.connect(signer).proposePayment(to.address ?? to, amount, memo);
  return id;
}

describe("TreasuryGuard", function () {
  describe("paiement normal", function () {
    it("s'exécute avec 2 signatures sur 5 après le délai d'examen", async function () {
      const { wallet, musd, alice, bruno, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(3_000), "Facture cloud");
      await wallet.connect(bruno).approve(id);

      await expect(wallet.connect(bruno).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly");
      await time.increase(GUARDED.reviewDelay);
      await expect(wallet.connect(bruno).execute(id))
        .to.emit(wallet, "PaymentExecuted")
        .withArgs(id, supplier.address, e18(3_000), bruno.address);
      expect(await musd.balanceOf(supplier.address)).to.equal(e18(3_000));
    });

    it("compte la proposition comme première approbation et refuse un doublon", async function () {
      const { wallet, alice, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(100));
      expect(await wallet.validApprovals(id)).to.equal(1n);
      await expect(wallet.connect(alice).approve(id)).to.be.revertedWithCustomError(wallet, "AlreadyApproved");
      await time.increase(GUARDED.reviewDelay);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "NotEnoughApprovals").withArgs(1, 2);
    });

    it("réserve toutes les actions aux signataires", async function () {
      const { wallet, alice, outsider, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(100));
      await expect(wallet.connect(outsider).proposePayment(supplier.address, 1n, "x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(outsider).approve(id)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(outsider).execute(id)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(outsider).cancel(id, "x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(outsider).freeze("x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
    });

    it("un paiement annulé ne peut plus être exécuté", async function () {
      const { wallet, alice, bruno, chloe, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(100));
      await wallet.connect(bruno).approve(id);
      await expect(wallet.connect(chloe).cancel(id, "doublon")).to.emit(wallet, "Cancelled").withArgs(id, chloe.address, "doublon");
      await time.increase(GUARDED.reviewDelay);
      await expect(wallet.connect(bruno).execute(id)).to.be.revertedWithCustomError(wallet, "NotPending");
    });
  });

  describe("signalement par le moniteur", function () {
    it("StepUp exige une signature de plus, sans délai supplémentaire", async function () {
      const { wallet, alice, bruno, chloe, monitor, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(12_000), "Nouveau prestataire");
      await expect(wallet.connect(monitor).flagRisk(id, Risk.StepUp, "NEW_RECIPIENT")).to.emit(wallet, "RiskFlagged");
      expect(await wallet.requiredApprovals(id)).to.equal(3n);

      await wallet.connect(bruno).approve(id);
      await time.increase(GUARDED.reviewDelay);
      await expect(wallet.connect(bruno).execute(id)).to.be.revertedWithCustomError(wallet, "NotEnoughApprovals").withArgs(2, 3);
      await wallet.connect(chloe).approve(id);
      await expect(wallet.connect(chloe).execute(id)).to.emit(wallet, "PaymentExecuted");
    });

    it("Hold ajoute le délai d'attente, pendant lequel un signataire peut annuler", async function () {
      const { wallet, musd, alice, bruno, chloe, david, monitor, mule } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, mule, e18(95_000), "URGENT confidentiel");
      await wallet.connect(monitor).flagRisk(id, Risk.Hold, "NEW_RECIPIENT;AMOUNT_OUTLIER;URGENCY_MEMO");
      await wallet.connect(bruno).approve(id);
      await wallet.connect(chloe).approve(id);

      await time.increase(GUARDED.reviewDelay);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly");
      await wallet.connect(david).cancel(id, "fraude confirmée");
      await time.increase(GUARDED.holdDelay);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "NotPending");
      expect(await musd.balanceOf(mule.address)).to.equal(0n);
    });

    it("le moniteur ne peut que relever le risque d'un paiement en attente", async function () {
      const { wallet, alice, bruno, monitor, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(100));
      await wallet.connect(monitor).flagRisk(id, Risk.Hold, "BURST");
      await expect(wallet.connect(monitor).flagRisk(id, Risk.StepUp, "x")).to.be.revertedWithCustomError(wallet, "RiskCannotDecrease");
      await expect(wallet.connect(monitor).flagRisk(id, Risk.None, "x")).to.be.revertedWithCustomError(wallet, "RiskCannotDecrease");

      // Aucun autre pouvoir : ni proposer, ni approuver, ni exécuter, ni annuler, ni geler.
      await expect(wallet.connect(monitor).proposePayment(supplier.address, 1n, "x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(monitor).approve(id)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(monitor).execute(id)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(monitor).cancel(id, "x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(monitor).freeze("x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");

      await wallet.connect(bruno).cancel(id, "test");
      await expect(wallet.connect(monitor).flagRisk(id, Risk.Hold, "x")).to.be.revertedWithCustomError(wallet, "NotPending");
    });

    it("personne d'autre que le moniteur ne peut signaler", async function () {
      const { wallet, alice, outsider, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(100));
      for (const signer of [alice, outsider]) {
        await expect(wallet.connect(signer).flagRisk(id, Risk.Hold, "x")).to.be.revertedWithCustomError(wallet, "NotRiskOracle");
      }
    });

    it("à l'unanimité, les signataires passent outre le délai d'attente", async function () {
      const { wallet, alice, bruno, chloe, david, emma, monitor, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(50_000), "Acquisition validée en conseil");
      await wallet.connect(monitor).flagRisk(id, Risk.Hold, "AMOUNT_OUTLIER");
      for (const owner of [bruno, chloe, david]) await wallet.connect(owner).approve(id);
      await time.increase(GUARDED.reviewDelay);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly");
      await wallet.connect(emma).approve(id);
      await expect(wallet.connect(emma).execute(id)).to.emit(wallet, "PaymentExecuted");
    });
  });

  describe("règles appliquées par le portefeuille", function () {
    it("au-delà du plafond de la période, exige une signature de plus", async function () {
      const { wallet, alice, bruno, chloe, supplier } = await loadFixture(deployFixture);
      const first = await propose(wallet, alice, supplier, e18(80_000));
      await wallet.connect(bruno).approve(first);
      await time.increase(GUARDED.reviewDelay);
      await wallet.connect(bruno).execute(first);

      const second = await wallet.proposalCount();
      await expect(wallet.connect(alice).proposePayment(supplier.address, e18(30_000), "second"))
        .to.emit(wallet, "RiskFlagged")
        .withArgs(second, Risk.StepUp, "OVER_PERIOD_CAP", wallet.target, 3, anyUint64);
      await wallet.connect(bruno).approve(second);
      await time.increase(GUARDED.reviewDelay);
      await expect(wallet.connect(bruno).execute(second)).to.be.revertedWithCustomError(wallet, "NotEnoughApprovals");
      await wallet.connect(chloe).approve(second);
      await wallet.connect(chloe).execute(second);

      // Une nouvelle période remet le compteur à zéro.
      await time.increase(GUARDED.periodLength);
      expect(await wallet.spentInWindow()).to.equal(0n);
      const third = await propose(wallet, alice, supplier, e18(80_000));
      expect(await wallet.requiredApprovals(third)).to.equal(2n);
    });

    it("met en attente un paiement vers une adresse du registre, tant que le signalement est valide", async function () {
      const { wallet, registry, alice, oracle, deployer, mule } = await loadFixture(deployFixture);
      const evidence = ethers.id("https://exemple-signalements.test/fil/1842\nArnaque : ...");
      const expiresAt = (await time.latest()) + 30 * DAY;
      await expect(registry.connect(oracle).flag(mule.address, 2, "scam_report", evidence, expiresAt))
        .to.emit(registry, "AddressFlagged")
        .withArgs(mule.address, 2, "scam_report", evidence, expiresAt, oracle.address);

      const held = await wallet.proposalCount();
      await expect(wallet.connect(alice).proposePayment(mule.address, e18(1_000), "x"))
        .to.emit(wallet, "RiskFlagged")
        .withArgs(held, Risk.Hold, "FLAGGED_ADDRESS", registry.target, 3, anyUint64);

      // Contestation aboutie : l'administrateur retire le signalement.
      await expect(registry.connect(deployer).unflag(mule.address)).to.emit(registry, "AddressUnflagged");
      const free = await propose(wallet, alice, mule, e18(1_000));
      expect((await wallet.getProposal(free)).risk).to.equal(Risk.None);

      // Un signalement expiré ne compte plus.
      const soon = (await time.latest()) + 100;
      await registry.connect(oracle).flag(mule.address, 1, "scam_report", evidence, soon);
      expect(await registry.levelOf(mule.address)).to.equal(1n);
      await time.increase(200);
      expect(await registry.levelOf(mule.address)).to.equal(0n);
    });

    it("le registre n'accepte que l'oracle", async function () {
      const { registry, alice, mule } = await loadFixture(deployFixture);
      const expiresAt = (await time.latest()) + DAY;
      await expect(registry.connect(alice).flag(mule.address, 2, "x", ethers.ZeroHash, expiresAt)).to.be.revertedWithCustomError(
        registry,
        "AccessControlUnauthorizedAccount"
      );
      await expect(registry.connect(alice).unflag(mule.address)).to.be.revertedWithCustomError(registry, "AccessControlUnauthorizedAccount");
    });
  });

  describe("gel", function () {
    it("un signataire gèle, il en faut trois pour dégeler", async function () {
      const { wallet, alice, bruno, chloe, david, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(100));
      await wallet.connect(bruno).approve(id);
      await time.increase(GUARDED.reviewDelay);

      await expect(wallet.connect(david).freeze("alerte du garde")).to.emit(wallet, "Frozen").withArgs(david.address, "alerte du garde");
      await expect(wallet.connect(bruno).execute(id)).to.be.revertedWithCustomError(wallet, "WalletFrozen");
      await expect(wallet.connect(alice).proposePayment(supplier.address, 1n, "x")).to.be.revertedWithCustomError(wallet, "WalletFrozen");

      await wallet.connect(alice).approveUnfreeze();
      await wallet.connect(bruno).approveUnfreeze();
      expect(await wallet.frozen()).to.equal(true);
      await expect(wallet.connect(chloe).approveUnfreeze()).to.emit(wallet, "Unfrozen").withArgs(chloe.address);
      await wallet.connect(bruno).execute(id);
    });
  });

  describe("signataires, clés et seuil", function () {
    it("une clé expirée ne peut plus rien, et ses approbations ne comptent plus", async function () {
      const { wallet, alice, bruno, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(100));
      await wallet.connect(bruno).approve(id);
      expect(await wallet.validApprovals(id)).to.equal(2n);

      await time.increase(GUARDED.keyLifetime);
      expect(await wallet.isActiveOwner(alice.address)).to.equal(false);
      expect(await wallet.validApprovals(id)).to.equal(0n);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(alice).proposePayment(supplier.address, 1n, "x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
    });

    it("remplacer un signataire demande trois signatures et le délai d'attente, et annule ses approbations", async function () {
      const { wallet, alice, bruno, chloe, emma, frank, supplier } = await loadFixture(deployFixture);
      // Emma a approuvé un paiement avec sa clé, qui va être remplacée.
      const payment = await propose(wallet, emma, supplier, e18(100));

      const id = await wallet.proposalCount();
      await wallet.connect(alice).proposeReplaceOwner(emma.address, frank.address);
      await wallet.connect(bruno).approve(id);
      await time.increase(GUARDED.holdDelay);
      await expect(wallet.connect(bruno).execute(id)).to.be.revertedWithCustomError(wallet, "NotEnoughApprovals").withArgs(2, 3);
      await wallet.connect(chloe).approve(id);
      await expect(wallet.connect(chloe).execute(id)).to.emit(wallet, "OwnerReplaced");

      expect(await wallet.isActiveOwner(emma.address)).to.equal(false);
      expect(await wallet.isActiveOwner(frank.address)).to.equal(true);
      expect(await wallet.validApprovals(payment)).to.equal(0n);
      await expect(wallet.connect(emma).approve(payment)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
    });

    it("changer le seuil passe par la même procédure renforcée", async function () {
      const { wallet, alice, bruno, chloe, monitor } = await loadFixture(deployFixture);
      const id = await wallet.proposalCount();
      await expect(wallet.connect(alice).proposeThreshold(1)).to.emit(wallet, "ConfigProposed");
      await expect(wallet.connect(monitor).flagRisk(id, Risk.Hold, "x")).to.be.revertedWithCustomError(wallet, "NotAPayment");
      await wallet.connect(bruno).approve(id);
      await wallet.connect(chloe).approve(id);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly");
      await time.increase(GUARDED.holdDelay);
      await expect(wallet.connect(alice).execute(id)).to.emit(wallet, "ThresholdChanged").withArgs(2, 1);
      expect(await wallet.threshold()).to.equal(1n);
    });

    it("on peut remplacer un signataire compromis pendant un gel", async function () {
      const { wallet, alice, bruno, chloe, emma, frank } = await loadFixture(deployFixture);
      await wallet.connect(alice).freeze("clé d'Emma compromise");
      const id = await wallet.proposalCount();
      await wallet.connect(alice).proposeReplaceOwner(emma.address, frank.address);
      await wallet.connect(bruno).approve(id);
      await wallet.connect(chloe).approve(id);
      await time.increase(GUARDED.holdDelay);
      await expect(wallet.connect(alice).execute(id)).to.emit(wallet, "OwnerReplaced");
    });
  });

  describe("scénario de fraude : deux signataires trompés, rafale vers une adresse inconnue", function () {
    const PAYMENTS = 10;
    const AMOUNT = e18(95_000);

    it("sans garde, 95 % de la trésorerie part en dix paiements", async function () {
      const { plain, musd, david, emma, mule } = await loadFixture(deployFixture);
      for (let i = 0; i < PAYMENTS; i++) {
        const id = await propose(plain, emma, mule, AMOUNT, "URGENT confidentiel");
        await plain.connect(david).approve(id);
        await plain.connect(david).execute(id);
      }
      expect(await musd.balanceOf(mule.address)).to.equal(AMOUNT * BigInt(PAYMENTS));
      expect(await musd.balanceOf(plain.target)).to.equal(TREASURY - AMOUNT * BigInt(PAYMENTS));
    });

    it("avec le garde, chaque paiement est mis en attente et rien ne sort", async function () {
      const { wallet, musd, alice, david, emma, monitor, mule } = await loadFixture(deployFixture);
      const ids = [];
      for (let i = 0; i < PAYMENTS; i++) {
        const id = await propose(wallet, emma, mule, AMOUNT, "URGENT confidentiel");
        await wallet.connect(david).approve(id);
        // Le moniteur rend son verdict pendant le délai d'examen.
        await wallet.connect(monitor).flagRisk(id, Risk.Hold, "NEW_RECIPIENT;AMOUNT_OUTLIER;BURST");
        ids.push(id);
      }

      // Les deux signataires trompés n'y arrivent pas seuls, même après le délai d'examen.
      await time.increase(GUARDED.reviewDelay);
      await expect(wallet.connect(david).execute(ids[0])).to.be.revertedWithCustomError(wallet, "NotEnoughApprovals").withArgs(2, 3);

      // Un signataire alerté gèle puis annule tout pendant la mise en attente.
      await wallet.connect(alice).freeze("alerte du garde");
      for (const id of ids) await wallet.connect(alice).cancel(id, "fraude confirmée");
      await time.increase(GUARDED.holdDelay);

      expect(await musd.balanceOf(mule.address)).to.equal(0n);
      expect(await musd.balanceOf(wallet.target)).to.equal(TREASURY);
    });

    it("même sans moniteur, le plafond de la période limite la casse à deux signataires", async function () {
      const { wallet, musd, david, emma, mule } = await loadFixture(deployFixture);
      const ids = [];
      for (let i = 0; i < PAYMENTS; i++) {
        const id = await propose(wallet, emma, mule, AMOUNT, "URGENT confidentiel");
        await wallet.connect(david).approve(id);
        ids.push(id);
      }
      await time.increase(GUARDED.reviewDelay);
      await wallet.connect(david).execute(ids[0]);
      // Le deuxième dépasserait le plafond de 100 000 : il lui faut une troisième signature.
      await expect(wallet.connect(david).execute(ids[1])).to.be.revertedWithCustomError(wallet, "NotEnoughApprovals").withArgs(2, 3);
      expect(await musd.balanceOf(mule.address)).to.equal(AMOUNT);
    });
  });
});

// Accepte n'importe quelle valeur pour un argument d'événement dont l'heure exacte importe peu.
function anyUint64(value) {
  return typeof value === "bigint";
}
