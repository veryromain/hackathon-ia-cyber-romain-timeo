const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture, time } = require("@nomicfoundation/hardhat-network-helpers");

const e18 = (n) => ethers.parseEther(String(n));
const Level = { Normal: 0, Limited: 1, Paused: 2 };

const LISTING_DELAY = 3600;
const OUTFLOW_WINDOW = 600;
const OUTFLOW_CAP = e18(10_000);

async function deployFixture() {
  const [admin, config, guardian, human, alice, bob, attacker] = await ethers.getSigners();

  const Token = await ethers.getContractFactory("MockToken");
  const Pool = await ethers.getContractFactory("SimplePool");
  const Vault = await ethers.getContractFactory("BreakerVault");

  const musd = await Token.deploy("Mock USD", "mUSD");
  const vault = await Vault.deploy(musd.target, admin.address, LISTING_DELAY, OUTFLOW_CAP, OUTFLOW_WINDOW);

  await vault.connect(admin).grantRole(await vault.CONFIG_ROLE(), config.address);
  await vault.connect(admin).grantRole(await vault.GUARDIAN_ROLE(), guardian.address);
  await vault.connect(admin).grantRole(await vault.RESUME_ROLE(), human.address);

  // Collatéral légitime : pool profond, prix de 20 mUSD.
  const wavax = await Token.deploy("Mock Wrapped AVAX", "mWAVAX");
  const wavaxPool = await Pool.deploy(wavax.target, musd.target);
  await wavax.mint(admin.address, e18(100_000));
  await musd.mint(admin.address, e18(2_000_000));
  await wavax.connect(admin).approve(wavaxPool.target, ethers.MaxUint256);
  await musd.connect(admin).approve(wavaxPool.target, ethers.MaxUint256);
  await wavaxPool.connect(admin).addLiquidity(e18(100_000), e18(2_000_000));

  await vault.connect(config).proposeCollateral(wavax.target, wavaxPool.target, 5000);
  await time.increase(LISTING_DELAY);
  await vault.connect(config).listCollateral(wavax.target);

  // Deux déposants apportent 1 000 000 mUSD au total.
  for (const user of [alice, bob]) {
    await musd.mint(user.address, e18(500_000));
    await musd.connect(user).approve(vault.target, ethers.MaxUint256);
    await vault.connect(user).deposit(e18(500_000));
  }

  return { vault, musd, wavax, wavaxPool, Token, Pool, admin, config, guardian, human, alice, bob, attacker };
}

/// Prépare l'attaque inspirée de Drift, jusqu'au dépôt du faux collatéral. Ne tire encore aucun fonds.
async function prepareAttack({ vault, musd, Token, Pool, admin, attacker }) {
  // 1. Faux jeton et pool sans liquidité : 1 000 FAKE contre 10 mUSD.
  const fake = await Token.connect(attacker).deploy("Carbon Fake Token", "FAKE");
  const fakePool = await Pool.connect(attacker).deploy(fake.target, musd.target);
  await fake.mint(attacker.address, e18(5_000_000));
  await musd.mint(attacker.address, e18(100));
  await fake.connect(attacker).approve(fakePool.target, ethers.MaxUint256);
  await musd.connect(attacker).approve(fakePool.target, ethers.MaxUint256);
  await fakePool.connect(attacker).addLiquidity(e18(1_000), e18(10));

  // 2. Quelques dizaines de mUSD d'achats suffisent à porter le prix de 0,01 à 1 mUSD.
  await fakePool.connect(attacker).swap(true, e18(90));

  // 3. Prise de pouvoir : un signataire trompé accorde CONFIG_ROLE à l'attaquant.
  await vault.connect(admin).grantRole(await vault.CONFIG_ROLE(), attacker.address);

  // 4. Délai de sécurité ramené à zéro, puis listing immédiat du faux jeton.
  await vault.connect(attacker).setListingDelay(0);
  await vault.connect(attacker).proposeCollateral(fake.target, fakePool.target, 5000);
  await vault.connect(attacker).listCollateral(fake.target);

  // 5. Dépôt du faux collatéral : 4 000 000 FAKE « valent » 4 000 000 mUSD.
  await fake.connect(attacker).approve(vault.target, ethers.MaxUint256);
  await vault.connect(attacker).depositCollateral(fake.target, e18(4_000_000));

  return { fake, fakePool };
}

describe("BreakerVault", function () {
  describe("fonctionnement normal", function () {
    it("accepte les dépôts et rend les retraits", async function () {
      const { vault, musd, alice } = await loadFixture(deployFixture);
      await expect(vault.connect(alice).withdraw(e18(1_000)))
        .to.emit(vault, "Withdrawn")
        .withArgs(alice.address, e18(1_000));
      expect(await musd.balanceOf(alice.address)).to.equal(e18(1_000));
      expect(await vault.deposits(alice.address)).to.equal(e18(499_000));
    });

    it("refuse un retrait supérieur au dépôt", async function () {
      const { vault, alice } = await loadFixture(deployFixture);
      await expect(vault.connect(alice).withdraw(e18(500_001))).to.be.revertedWithCustomError(vault, "InsufficientBalance");
    });

    it("prête contre un collatéral listé, dans la limite du ratio", async function () {
      const { vault, wavax, bob } = await loadFixture(deployFixture);
      await wavax.mint(bob.address, e18(100));
      await wavax.connect(bob).approve(vault.target, ethers.MaxUint256);
      await vault.connect(bob).depositCollateral(wavax.target, e18(100));

      // 100 mWAVAX à 20 mUSD, ratio de 50 % : 1 000 mUSD empruntables.
      expect(await vault.borrowLimit(bob.address)).to.equal(e18(1_000));
      await vault.connect(bob).borrow(e18(1_000));
      await expect(vault.connect(bob).borrow(1n)).to.be.revertedWithCustomError(vault, "BorrowLimitExceeded");
      await expect(vault.connect(bob).withdrawCollateral(wavax.target, 1n)).to.be.revertedWithCustomError(vault, "BorrowLimitExceeded");
    });

    it("refuse un collatéral non listé", async function () {
      const { vault, Token, bob } = await loadFixture(deployFixture);
      const other = await Token.deploy("Other", "OTH");
      await expect(vault.connect(bob).depositCollateral(other.target, 1n)).to.be.revertedWithCustomError(vault, "NotListed");
    });
  });

  describe("listing des collatéraux", function () {
    it("impose le délai de sécurité", async function () {
      const { vault, Token, Pool, musd, config } = await loadFixture(deployFixture);
      const token = await Token.deploy("New", "NEW");
      const pool = await Pool.deploy(token.target, musd.target);
      await vault.connect(config).proposeCollateral(token.target, pool.target, 5000);
      await expect(vault.connect(config).listCollateral(token.target)).to.be.revertedWithCustomError(vault, "ProposalNotReady");
      await time.increase(LISTING_DELAY);
      await expect(vault.connect(config).listCollateral(token.target)).to.emit(vault, "CollateralListed");
    });

    it("réserve le listing au rôle de configuration", async function () {
      const { vault, wavax, wavaxPool, alice, guardian } = await loadFixture(deployFixture);
      for (const signer of [alice, guardian]) {
        await expect(vault.connect(signer).proposeCollateral(wavax.target, wavaxPool.target, 5000)).to.be.revertedWithCustomError(
          vault,
          "AccessControlUnauthorizedAccount"
        );
        await expect(vault.connect(signer).setListingDelay(0)).to.be.revertedWithCustomError(vault, "AccessControlUnauthorizedAccount");
      }
    });
  });

  describe("disjoncteur", function () {
    it("le gardien durcit le niveau mais ne peut ni l'abaisser ni relancer", async function () {
      const { vault, guardian } = await loadFixture(deployFixture);
      await expect(vault.connect(guardian).escalate(Level.Limited, "score 0.7"))
        .to.emit(vault, "GuardLevelChanged")
        .withArgs(Level.Normal, Level.Limited, guardian.address, "score 0.7");
      await expect(vault.connect(guardian).escalate(Level.Limited, "idem")).to.be.revertedWithCustomError(vault, "CannotLowerGuardLevel");
      await vault.connect(guardian).escalate(Level.Paused, "score 0.95");
      await expect(vault.connect(guardian).escalate(Level.Normal, "retour")).to.be.revertedWithCustomError(vault, "CannotLowerGuardLevel");
      await expect(vault.connect(guardian).resume("retour")).to.be.revertedWithCustomError(vault, "AccessControlUnauthorizedAccount");
    });

    it("seul le gardien peut durcir, seul l'humain peut relancer", async function () {
      const { vault, admin, config, alice, guardian, human } = await loadFixture(deployFixture);
      for (const signer of [admin, config, alice, human]) {
        await expect(vault.connect(signer).escalate(Level.Paused, "x")).to.be.revertedWithCustomError(vault, "AccessControlUnauthorizedAccount");
      }
      await expect(vault.connect(human).resume("rien à relancer")).to.be.revertedWithCustomError(vault, "AlreadyNormal");
      await vault.connect(guardian).escalate(Level.Paused, "alerte");
      for (const signer of [admin, config, alice]) {
        await expect(vault.connect(signer).resume("x")).to.be.revertedWithCustomError(vault, "AccessControlUnauthorizedAccount");
      }
      await expect(vault.connect(human).resume("incident clos"))
        .to.emit(vault, "GuardLevelChanged")
        .withArgs(Level.Paused, Level.Normal, human.address, "incident clos");
      expect(await vault.guardLevel()).to.equal(Level.Normal);
    });

    it("au niveau Limited, plafonne les sorties par fenêtre", async function () {
      const { vault, guardian, alice, bob } = await loadFixture(deployFixture);
      await vault.connect(guardian).escalate(Level.Limited, "prudence");
      await vault.connect(alice).withdraw(e18(6_000));
      expect(await vault.remainingOutflow()).to.equal(e18(4_000));
      await expect(vault.connect(bob).withdraw(e18(4_001))).to.be.revertedWithCustomError(vault, "OutflowCapExceeded");
      await vault.connect(bob).withdraw(e18(4_000));
      await expect(vault.connect(alice).withdraw(1n)).to.be.revertedWithCustomError(vault, "OutflowCapExceeded");

      await time.increase(OUTFLOW_WINDOW);
      expect(await vault.remainingOutflow()).to.equal(OUTFLOW_CAP);
      await vault.connect(alice).withdraw(e18(10_000));
    });

    it("en pause, bloque dépôts, retraits et emprunts mais accepte les remboursements", async function () {
      const { vault, musd, wavax, guardian, alice, bob } = await loadFixture(deployFixture);
      await wavax.mint(bob.address, e18(100));
      await wavax.connect(bob).approve(vault.target, ethers.MaxUint256);
      await vault.connect(bob).depositCollateral(wavax.target, e18(100));
      await vault.connect(bob).borrow(e18(500));

      await vault.connect(guardian).escalate(Level.Paused, "vidage en cours");
      await expect(vault.connect(alice).withdraw(1n)).to.be.revertedWithCustomError(vault, "VaultPaused");
      await expect(vault.connect(alice).deposit(1n)).to.be.revertedWithCustomError(vault, "VaultPaused");
      await expect(vault.connect(bob).borrow(1n)).to.be.revertedWithCustomError(vault, "VaultPaused");
      await expect(vault.connect(bob).withdrawCollateral(wavax.target, 1n)).to.be.revertedWithCustomError(vault, "VaultPaused");

      await musd.connect(bob).approve(vault.target, ethers.MaxUint256);
      await expect(vault.connect(bob).repay(e18(500))).to.emit(vault, "Repaid").withArgs(bob.address, e18(500), 0n);
    });
  });

  describe("scénario d'attaque inspiré de Drift", function () {
    const DRAIN_STEPS = 31n;

    it("sans disjoncteur, le coffre est vidé en 31 emprunts", async function () {
      const ctx = await loadFixture(deployFixture);
      const { vault, musd, attacker } = ctx;
      const { fakePool } = await prepareAttack(ctx);
      expect(await fakePool.price()).to.equal(e18(1));

      const initial = await vault.liquidity();
      const step = initial / DRAIN_STEPS;
      for (let i = 0n; i < DRAIN_STEPS; i++) await vault.connect(attacker).borrow(step);

      const left = await vault.liquidity();
      expect(left).to.be.lessThan(e18(1));
      expect(await musd.balanceOf(attacker.address)).to.be.greaterThan(e18(999_999));
    });

    it("avec une pause après le troisième emprunt, plus de 90 % des fonds restent", async function () {
      const ctx = await loadFixture(deployFixture);
      const { vault, attacker, guardian } = ctx;
      await prepareAttack(ctx);

      const initial = await vault.liquidity();
      const step = initial / DRAIN_STEPS;
      for (let i = 0; i < 3; i++) await vault.connect(attacker).borrow(step);
      await vault.connect(guardian).escalate(Level.Paused, "emprunts en rafale sur collatéral neuf");

      await expect(vault.connect(attacker).borrow(step)).to.be.revertedWithCustomError(vault, "VaultPaused");
      const left = await vault.liquidity();
      expect((left * 100n) / initial).to.be.greaterThanOrEqual(90n);
    });

    it("avec une pause dès le listing du faux jeton, rien ne sort", async function () {
      const ctx = await loadFixture(deployFixture);
      const { vault, attacker, guardian } = ctx;
      await prepareAttack(ctx);

      const initial = await vault.liquidity();
      await vault.connect(guardian).escalate(Level.Paused, "collatéral neuf à liquidité dérisoire, délai ramené à zéro");
      await expect(vault.connect(attacker).borrow(e18(1))).to.be.revertedWithCustomError(vault, "VaultPaused");
      expect(await vault.liquidity()).to.equal(initial);
    });
  });
});
