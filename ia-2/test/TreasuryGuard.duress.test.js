const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture, time } = require("@nomicfoundation/hardhat-network-helpers");

const e18 = (n) => ethers.parseEther(String(n));
const DAY = 24 * 3600;
const CONFIG = { reviewDelay: 60, holdDelay: 3600, keyLifetime: 15 * DAY, periodLength: DAY, periodCap: e18(100_000), stepUpExtra: 1 };
const TREASURY = e18(1_000_000);
const hashOf = (address) => ethers.solidityPackedKeccak256(["address"], [address]);

async function deployFixture() {
  const [deployer, alice, bruno, chloe, david, emma, monitor, supplier, mule, outsider, emmaDuress, frank] = await ethers.getSigners();
  const Token = await ethers.getContractFactory("MockToken");
  const Wallet = await ethers.getContractFactory("TreasuryGuard");
  const musd = await Token.deploy("Mock USD", "mUSD");
  const owners = [alice, bruno, chloe, david, emma].map((o) => o.address);
  const wallet = await Wallet.deploy(musd.target, owners, 2, monitor.address, ethers.ZeroAddress, CONFIG);
  await musd.mint(wallet.target, TREASURY);
  // Emma déclare sa clé de contrainte : seul le hash part sur la chaîne.
  await wallet.connect(emma).setDuressKey(hashOf(emmaDuress.address));
  return { musd, wallet, deployer, alice, bruno, chloe, david, emma, monitor, supplier, mule, outsider, emmaDuress, frank };
}

async function propose(wallet, signer, to, amount, memo = "paiement") {
  const id = await wallet.proposalCount();
  await wallet.connect(signer).proposePayment(to.address ?? to, amount, memo);
  return id;
}

describe("TreasuryGuard : clé de contrainte", function () {
  describe("enregistrement", function () {
    it("seul un signataire actif déclare une clé de contrainte, et une clé ne sert qu'à un seul signataire", async function () {
      const { wallet, alice, outsider, emmaDuress, frank } = await loadFixture(deployFixture);
      await expect(wallet.connect(outsider).setDuressKey(hashOf(frank.address))).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await expect(wallet.connect(alice).setDuressKey(hashOf(emmaDuress.address))).to.be.revertedWithCustomError(wallet, "InvalidParameter");
    });

    it("n'émet aucun événement et n'ouvre aucun droit ordinaire à la clé de contrainte", async function () {
      const { wallet, alice, emmaDuress, frank } = await loadFixture(deployFixture);
      const receipt = await (await wallet.connect(alice).setDuressKey(hashOf(frank.address))).wait();
      expect(receipt.logs.length).to.equal(0);
      expect(await wallet.isActiveOwner(emmaDuress.address)).to.equal(false);
      expect(await wallet.ownerCount()).to.equal(5n);
      // Annuler, geler et dégeler restent réservés aux clés habituelles.
      await expect(wallet.connect(emmaDuress).freeze("x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
    });

    it("une clé inconnue reste refusée, une clé de contrainte retirée aussi", async function () {
      const { wallet, alice, emma, emmaDuress, outsider, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(100));
      await expect(wallet.connect(outsider).approve(id)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
      await wallet.connect(emma).setDuressKey(ethers.ZeroHash);
      await expect(wallet.connect(emmaDuress).approve(id)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
    });
  });

  describe("approbation sous contrainte", function () {
    it("ressemble en tout point à une approbation normale", async function () {
      const { wallet, alice, emma, emmaDuress, mule } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, mule, e18(90_000), "Virement exigé");
      // L'événement nomme Emma, pas sa clé de contrainte, et le compteur passe à 2 sur 2.
      await expect(wallet.connect(emmaDuress).approve(id)).to.emit(wallet, "Approved").withArgs(id, emma.address, 2, 2);
      expect(await wallet.validApprovals(id)).to.equal(2n);
      expect(await wallet.hasApproved(id, emma.address)).to.equal(true);
      expect(await wallet.frozen()).to.equal(false);
      await expect(wallet.connect(emmaDuress).approve(id)).to.be.revertedWithCustomError(wallet, "AlreadyApproved");
    });

    it("rend le paiement inexécutable, avec l'erreur d'une mise en attente et une échéance qui recule", async function () {
      const { wallet, musd, alice, emmaDuress, mule } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, mule, e18(90_000));
      await wallet.connect(emmaDuress).approve(id);

      await time.increase(CONFIG.reviewDelay);
      const first = (await time.latest()) + 1 + CONFIG.holdDelay;
      await time.setNextBlockTimestamp(first - CONFIG.holdDelay);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly").withArgs(first);

      // Même après le délai annoncé, et même par la clé de contrainte : toujours « trop tôt ».
      await time.increase(2 * CONFIG.holdDelay);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly");
      await expect(wallet.connect(emmaDuress).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly");
      expect(await musd.balanceOf(mule.address)).to.equal(0n);
    });

    it("arrête en silence tous les paiements, sans événement de gel", async function () {
      const { wallet, musd, alice, bruno, emmaDuress, supplier, mule } = await loadFixture(deployFixture);
      const honest = await propose(wallet, alice, supplier, e18(1_000), "Facture ordinaire");
      await wallet.connect(bruno).approve(honest);
      const forced = await propose(wallet, alice, mule, e18(90_000));

      const receipt = await (await wallet.connect(emmaDuress).approve(forced)).wait();
      const names = receipt.logs.map((log) => wallet.interface.parseLog(log).name);
      expect(names).to.deep.equal(["Approved"]);
      expect(await wallet.frozen()).to.equal(false);

      await time.increase(CONFIG.reviewDelay);
      await expect(wallet.connect(bruno).execute(honest)).to.be.revertedWithCustomError(wallet, "TooEarly");
      expect(await musd.balanceOf(supplier.address)).to.equal(0n);
    });

    it("fonctionne aussi quand le signataire contraint doit proposer lui-même le paiement", async function () {
      const { wallet, musd, bruno, emma, emmaDuress, mule } = await loadFixture(deployFixture);
      const id = await wallet.proposalCount();
      await expect(wallet.connect(emmaDuress).proposePayment(mule.address, e18(90_000), "Virement exigé"))
        .to.emit(wallet, "PaymentProposed")
        .withArgs(id, emma.address, mule.address, e18(90_000), "Virement exigé", 2, anyValue);
      expect((await wallet.getProposal(id)).proposer).to.equal(emma.address);
      await wallet.connect(bruno).approve(id);
      await time.increase(CONFIG.reviewDelay);
      await expect(wallet.connect(bruno).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly");
      expect(await musd.balanceOf(mule.address)).to.equal(0n);
    });

    it("bloque de la même façon un changement de signataire approuvé sous contrainte", async function () {
      const { wallet, alice, bruno, david, emmaDuress, frank } = await loadFixture(deployFixture);
      const id = await wallet.proposalCount();
      await wallet.connect(alice).proposeReplaceOwner(david.address, frank.address);
      await wallet.connect(bruno).approve(id);
      await wallet.connect(emmaDuress).approve(id);
      await time.increase(CONFIG.holdDelay);
      await expect(wallet.connect(alice).execute(id)).to.be.revertedWithCustomError(wallet, "TooEarly");
      expect(await wallet.isActiveOwner(frank.address)).to.equal(false);
    });
  });

  describe("reprise par les autres signataires", function () {
    it("trois collègues lèvent le gel silencieux ; le paiement contraint reste bloqué, les autres repartent", async function () {
      const { wallet, musd, alice, bruno, chloe, david, emmaDuress, supplier, mule } = await loadFixture(deployFixture);
      const honest = await propose(wallet, alice, supplier, e18(1_000));
      await wallet.connect(bruno).approve(honest);
      const forced = await propose(wallet, alice, mule, e18(90_000));
      await wallet.connect(emmaDuress).approve(forced);
      await time.increase(CONFIG.reviewDelay);

      await wallet.connect(alice).approveUnfreeze();
      await wallet.connect(bruno).approveUnfreeze();
      await expect(wallet.connect(bruno).execute(honest)).to.be.revertedWithCustomError(wallet, "TooEarly");
      await expect(wallet.connect(chloe).approveUnfreeze()).to.emit(wallet, "Unfrozen").withArgs(chloe.address);

      await wallet.connect(bruno).execute(honest);
      expect(await musd.balanceOf(supplier.address)).to.equal(e18(1_000));
      await expect(wallet.connect(alice).execute(forced)).to.be.revertedWithCustomError(wallet, "TooEarly");
      await wallet.connect(david).cancel(forced, "signé sous contrainte");
      expect(await musd.balanceOf(mule.address)).to.equal(0n);
      // Le portefeuille est revenu à la normale : un nouveau dégel n'a plus d'objet.
      await expect(wallet.connect(david).approveUnfreeze()).to.be.revertedWithCustomError(wallet, "NotFrozen");
    });

    it("le vote du signataire contraint est accepté en apparence mais ne compte pas", async function () {
      const { wallet, alice, bruno, chloe, emma, emmaDuress, mule } = await loadFixture(deployFixture);
      const forced = await propose(wallet, alice, mule, e18(90_000));
      await wallet.connect(emmaDuress).approve(forced);

      // Forcée de « débloquer », Emma vote avec sa clé habituelle : enregistré, compté pour zéro.
      await expect(wallet.connect(emma).approveUnfreeze()).to.emit(wallet, "UnfreezeApproved").withArgs(emma.address, 0, 3);
      await wallet.connect(alice).approveUnfreeze();
      await expect(wallet.connect(bruno).approveUnfreeze()).to.emit(wallet, "UnfreezeApproved").withArgs(bruno.address, 2, 3);
      await expect(wallet.connect(chloe).approveUnfreeze()).to.emit(wallet, "Unfrozen");
    });

    it("sans clé de contrainte utilisée, le dégel reste refusé hors gel", async function () {
      const { wallet, alice } = await loadFixture(deployFixture);
      await expect(wallet.connect(alice).approveUnfreeze()).to.be.revertedWithCustomError(wallet, "NotFrozen");
    });

    it("un gel officiel par un collègue alerté se combine avec le gel silencieux", async function () {
      const { wallet, alice, bruno, chloe, david, emmaDuress, mule } = await loadFixture(deployFixture);
      const forced = await propose(wallet, alice, mule, e18(90_000));
      await wallet.connect(emmaDuress).approve(forced);
      await expect(wallet.connect(david).freeze("Emma signe sous contrainte")).to.emit(wallet, "Frozen");
      await time.increase(CONFIG.reviewDelay);
      await expect(wallet.connect(alice).execute(forced)).to.be.revertedWithCustomError(wallet, "WalletFrozen");
      for (const owner of [alice, bruno, chloe]) await wallet.connect(owner).approveUnfreeze();
      expect(await wallet.frozen()).to.equal(false);
      await expect(wallet.connect(alice).execute(forced)).to.be.revertedWithCustomError(wallet, "TooEarly");
    });
  });

  describe("sans contrainte, rien ne change", function () {
    it("la clé habituelle d'un signataire qui a déclaré une clé de contrainte signe normalement", async function () {
      const { wallet, musd, alice, emma, supplier } = await loadFixture(deployFixture);
      const id = await propose(wallet, alice, supplier, e18(2_000));
      await wallet.connect(emma).approve(id);
      await time.increase(CONFIG.reviewDelay);
      await expect(wallet.connect(emma).execute(id)).to.emit(wallet, "PaymentExecuted").withArgs(id, supplier.address, e18(2_000), emma.address);
      expect(await musd.balanceOf(supplier.address)).to.equal(e18(2_000));
    });

    it("la clé de contrainte d'un signataire remplacé ne vaut plus rien", async function () {
      const { wallet, alice, bruno, chloe, emma, emmaDuress, frank, supplier } = await loadFixture(deployFixture);
      const swap = await wallet.proposalCount();
      await wallet.connect(alice).proposeReplaceOwner(emma.address, frank.address);
      await wallet.connect(bruno).approve(swap);
      await wallet.connect(chloe).approve(swap);
      await time.increase(CONFIG.holdDelay);
      await wallet.connect(alice).execute(swap);

      const id = await propose(wallet, alice, supplier, e18(100));
      await expect(wallet.connect(emmaDuress).approve(id)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
    });
  });
});

function anyValue() {
  return true;
}
