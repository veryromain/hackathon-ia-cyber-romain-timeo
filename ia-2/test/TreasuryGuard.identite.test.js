// Clé d'identité froide : la clé de contrainte peut aussi révoquer la clé de tous les jours de son propriétaire.
// Proposition de Romain (branche identite-froide), à relire par Timéo.
const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture, time } = require("@nomicfoundation/hardhat-network-helpers");

const e18 = (n) => ethers.parseEther(String(n));
const DAY = 24 * 3600;
const CONFIG = { reviewDelay: 60, holdDelay: 3600, keyLifetime: 15 * DAY, periodLength: DAY, periodCap: e18(100_000), stepUpExtra: 1 };
const hashOf = (address) => ethers.solidityPackedKeccak256(["address"], [address]);

async function deployFixture() {
  const [, alice, bruno, chloe, david, emma, monitor, supplier, outsider, emmaIdentity, emmaNew] = await ethers.getSigners();
  const musd = await (await ethers.getContractFactory("MockToken")).deploy("Mock USD", "mUSD");
  const wallet = await (await ethers.getContractFactory("TreasuryGuard")).deploy(
    musd.target, [alice, bruno, chloe, david, emma].map((o) => o.address), 2, monitor.address, ethers.ZeroAddress, CONFIG);
  await musd.mint(wallet.target, e18(1_000_000));
  await wallet.connect(emma).setDuressKey(hashOf(emmaIdentity.address)); // la clé d'identité d'Emma, gardée hors ligne
  return { musd, wallet, alice, bruno, chloe, david, emma, monitor, supplier, outsider, emmaIdentity, emmaNew };
}

describe("TreasuryGuard : clé d'identité froide", function () {
  it("Emma coupe sa clé volée avec sa clé d'identité, seule et immédiatement", async function () {
    const { wallet, emma, emmaIdentity, emmaNew } = await loadFixture(deployFixture);
    await expect(wallet.connect(emmaIdentity).revokeMyKey(emmaNew.address))
      .to.emit(wallet, "KeyRevokedBySelf").withArgs(emma.address, emmaNew.address)
      .and.to.emit(wallet, "OwnerReplaced");
    expect(await wallet.isActiveOwner(emma.address)).to.equal(false);
    expect(await wallet.isActiveOwner(emmaNew.address)).to.equal(true);
  });

  it("le voleur de l'ancienne clé ne peut plus rien faire", async function () {
    const { wallet, emma, emmaIdentity, emmaNew, supplier } = await loadFixture(deployFixture);
    await wallet.connect(emmaIdentity).revokeMyKey(emmaNew.address);
    await expect(wallet.connect(emma).proposePayment(supplier.address, e18(1000), "x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
    await expect(wallet.connect(emma).freeze("x")).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
  });

  it("la nouvelle clé entre en probation : un voleur de la clé d'identité ne gagne aucun pouvoir immédiat", async function () {
    const { wallet, emmaIdentity, emmaNew } = await loadFixture(deployFixture);
    await wallet.connect(emmaIdentity).revokeMyKey(emmaNew.address);
    expect(await wallet.isEstablishedOwner(emmaNew.address)).to.equal(false);
    await time.increase(2 * DAY + 1);
    expect(await wallet.isEstablishedOwner(emmaNew.address)).to.equal(true);
  });

  it("la clé d'identité reste liée à la personne : elle vaut pour la nouvelle clé", async function () {
    const { wallet, emmaIdentity, emmaNew, outsider } = await loadFixture(deployFixture);
    await wallet.connect(emmaIdentity).revokeMyKey(emmaNew.address);
    await expect(wallet.connect(emmaIdentity).revokeMyKey(outsider.address)).to.emit(wallet, "KeyRevokedBySelf").withArgs(emmaNew.address, outsider.address);
  });

  it("personne d'autre ne peut révoquer, et pas vers une adresse déjà signataire", async function () {
    const { wallet, alice, emmaIdentity, outsider } = await loadFixture(deployFixture);
    await expect(wallet.connect(outsider).revokeMyKey(outsider.address)).to.be.revertedWithCustomError(wallet, "NotActiveOwner");
    await expect(wallet.connect(emmaIdentity).revokeMyKey(alice.address)).to.be.revertedWithCustomError(wallet, "InvalidParameter");
    await expect(wallet.connect(emmaIdentity).revokeMyKey(emmaIdentity.address)).to.be.revertedWithCustomError(wallet, "InvalidParameter");
  });

  it("la révocation marche même portefeuille gelé, et la clé d'identité ne peut toujours pas payer", async function () {
    const { wallet, alice, emmaIdentity, emmaNew, supplier } = await loadFixture(deployFixture);
    await wallet.connect(alice).freeze("alerte");
    await expect(wallet.connect(emmaIdentity).revokeMyKey(emmaNew.address)).to.emit(wallet, "KeyRevokedBySelf");
    await expect(wallet.connect(emmaIdentity).execute(0)).to.be.reverted;
  });
});
