const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture, time } = require("@nomicfoundation/hardhat-network-helpers");
const DAY = 86400;
const e18 = n => ethers.parseEther(String(n));
const config = { reviewDelay: 60, holdDelay: 3600, keyLifetime: 15 * DAY, periodLength: DAY, periodCap: e18(100000), stepUpExtra: 1 };

async function fixture() {
  const [deployer, alice, bruno, chloe, david, emma, monitor, frank, supplier] = await ethers.getSigners();
  const token = await (await ethers.getContractFactory("MockToken")).deploy("Mock USD", "mUSD");
  const wallet = await (await ethers.getContractFactory("TreasuryGuard")).deploy(token.target, [alice,bruno,chloe,david,emma].map(s=>s.address), 2, monitor.address, ethers.ZeroAddress, config);
  await token.mint(wallet.target, e18(1000000));
  return { wallet,token,alice,bruno,chloe,david,emma,monitor,frank,supplier };
}
async function replace(f, oldOwner, newOwner) {
  const id = await f.wallet.proposalCount();
  await f.wallet.connect(f.alice).proposeReplaceOwner(oldOwner.address,newOwner.address);
  await f.wallet.connect(f.bruno).approve(id);
  await f.wallet.connect(f.chloe).approve(id);
  await time.increase(config.holdDelay);
  await f.wallet.connect(f.alice).execute(id);
}
async function payment(f, amount=1000) {
  const id = await f.wallet.proposalCount();
  await f.wallet.connect(f.alice).proposePayment(f.supplier.address,e18(amount),"facture");
  return id;
}
describe("TreasuryGuard — probation et gouvernance",function(){
  it("laisse les clés initiales établies et les clés neuves payer au quorum ordinaire",async function(){
    const f = await loadFixture(fixture);
    expect(await f.wallet.isEstablishedOwner(f.alice.address)).to.equal(true);
    await replace(f,f.emma,f.frank);
    expect(await f.wallet.isEstablishedOwner(f.frank.address)).to.equal(false);
    const id = await payment(f);
    await f.wallet.connect(f.frank).approve(id);
    await time.increase(config.reviewDelay);
    await expect(f.wallet.connect(f.alice).execute(id)).to.emit(f.wallet,"PaymentExecuted");
  });
  for(const risk of [1,2]) it("une clé neuve ne fournit pas la troisième signature du niveau "+risk,async function(){
    const f=await loadFixture(fixture);await replace(f,f.emma,f.frank);
    const id=await payment(f);
    await f.wallet.connect(f.bruno).approve(id);
    await f.wallet.connect(f.frank).approve(id);
    await f.wallet.connect(f.monitor).flagRisk(id,risk,"NEW_OWNER_APPROVES");
    expect(await f.wallet.validApprovals(id)).to.equal(2n);
    await time.increase(config.holdDelay);
    await expect(f.wallet.connect(f.frank).execute(id)).to.be.revertedWithCustomError(f.wallet,"NotEnoughApprovals").withArgs(2,3);
    expect(await f.token.balanceOf(f.supplier.address)).to.equal(0n);
    await f.wallet.connect(f.chloe).approve(id);
    await expect(f.wallet.connect(f.chloe).execute(id)).to.emit(f.wallet,"PaymentExecuted");
  });
  it("compte la clé neuve exactement à la fin des deux jours de probation",async function(){
    const f=await loadFixture(fixture);await replace(f,f.emma,f.frank);
    const id=await payment(f);await f.wallet.connect(f.monitor).flagRisk(id,1,"x");
    await f.wallet.connect(f.bruno).approve(id);await f.wallet.connect(f.frank).approve(id);
    const until=await f.wallet.keyTrustedAfter(f.frank.address);
    await time.increaseTo(until-1n);expect(await f.wallet.validApprovals(id)).to.equal(2n);
    await time.increaseTo(until);expect(await f.wallet.validApprovals(id)).to.equal(3n);
    await expect(f.wallet.connect(f.frank).execute(id)).to.emit(f.wallet,"PaymentExecuted");
  });
  it("ne laisse pas une clé neuve contourner le plafond avec un troisième vote",async function(){
    const f=await loadFixture(fixture);await replace(f,f.emma,f.frank);
    const id=await payment(f,120000);await f.wallet.connect(f.bruno).approve(id);await f.wallet.connect(f.frank).approve(id);
    await time.increase(config.reviewDelay);
    await expect(f.wallet.connect(f.alice).execute(id)).to.be.revertedWithCustomError(f.wallet,"NotEnoughApprovals").withArgs(2,3);
  });
  it("exclut une clé neuve du dégel puis l'autorise après probation",async function(){
    const f=await loadFixture(fixture);await replace(f,f.emma,f.frank);
    await f.wallet.connect(f.alice).freeze("incident");
    await f.wallet.connect(f.alice).approveUnfreeze();await f.wallet.connect(f.bruno).approveUnfreeze();
    await expect(f.wallet.connect(f.frank).approveUnfreeze()).to.be.revertedWithCustomError(f.wallet,"OwnerInProbation");
    expect(await f.wallet.frozen()).to.equal(true);
    await time.increaseTo(await f.wallet.keyTrustedAfter(f.frank.address));
    await expect(f.wallet.connect(f.frank).approveUnfreeze()).to.emit(f.wallet,"Unfrozen");
  });
  it("une clé en probation n'abaisse pas le seuil avec deux complices",async function(){
    const f=await loadFixture(fixture);await replace(f,f.emma,f.frank);
    const id=await f.wallet.proposalCount();await f.wallet.connect(f.alice).proposeThreshold(1);
    await f.wallet.connect(f.bruno).approve(id);await f.wallet.connect(f.frank).approve(id);
    await time.increase(config.holdDelay);
    await expect(f.wallet.connect(f.alice).execute(id)).to.be.revertedWithCustomError(f.wallet,"NotEnoughApprovals").withArgs(2,3);
  });
  it("même l'unanimité ne raccourcit pas le délai de gouvernance",async function(){
    const f=await loadFixture(fixture);const id=await f.wallet.proposalCount();await f.wallet.connect(f.alice).proposeThreshold(1);
    for(const s of [f.bruno,f.chloe,f.david,f.emma])await f.wallet.connect(s).approve(id);
    await time.increase(config.reviewDelay);
    await expect(f.wallet.connect(f.emma).execute(id)).to.be.revertedWithCustomError(f.wallet,"TooEarly");
    await time.increase(config.holdDelay);
    await expect(f.wallet.connect(f.emma).execute(id)).to.emit(f.wallet,"ThresholdChanged");
  });
  it("réajouter une ancienne adresse ne ressuscite pas ses approbations de paiement",async function(){
    const f=await loadFixture(fixture);const id=await payment(f);await f.wallet.connect(f.emma).approve(id);
    await replace(f,f.emma,f.frank);await replace(f,f.frank,f.emma);
    expect(await f.wallet.keyEpoch(f.emma.address)).to.equal(2n);
    expect(await f.wallet.validApprovals(id)).to.equal(1n);
    await expect(f.wallet.connect(f.alice).execute(id)).to.be.revertedWithCustomError(f.wallet,"NotEnoughApprovals");
    await f.wallet.connect(f.emma).approve(id);
    await expect(f.wallet.connect(f.emma).execute(id)).to.emit(f.wallet,"PaymentExecuted");
  });
  it("réajouter une adresse ne ressuscite pas non plus son vote de dégel",async function(){
    const f=await loadFixture(fixture);await f.wallet.connect(f.alice).freeze("incident");
    await f.wallet.connect(f.emma).approveUnfreeze();await f.wallet.connect(f.alice).approveUnfreeze();
    await replace(f,f.emma,f.frank);await replace(f,f.frank,f.emma);
    await time.increaseTo(await f.wallet.keyTrustedAfter(f.emma.address));
    await f.wallet.connect(f.bruno).approveUnfreeze();expect(await f.wallet.frozen()).to.equal(true);
    await expect(f.wallet.connect(f.emma).approveUnfreeze()).to.emit(f.wallet,"Unfrozen");
  });
});
