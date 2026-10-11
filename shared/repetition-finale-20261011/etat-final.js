const path = require('path');
const fs = require('fs');
const hre = require(require.resolve('hardhat', { paths: [process.cwd()] }));
const { loadDeployment } = require(path.join(process.cwd(), 'lib', 'deployment'));
(async () => {
  const { info, wallet, musd } = await loadDeployment(hre);
  const count = Number(await wallet.proposalCount());
  const proposals = [];
  for (let id = 0; id < count; id++) {
    const p = await wallet.getProposal(id);
    proposals.push({id, target: p.target, value: p.value.toString(), risk: Number(p.risk), executed: p.executed, cancelled: p.cancelled, approvals: Number(await wallet.validApprovals(id)), required: Number(await wallet.requiredApprovals(id)), recipientBalance: (await musd.balanceOf(p.target)).toString()});
  }
  const state = {capturedAt: new Date().toISOString(), chainId: info.chain_id, wallet: info.wallet, treasury: (await musd.balanceOf(wallet.target)).toString(), frozen: await wallet.frozen(), proposals};
  fs.writeFileSync(path.join(__dirname, 'etat-final.json'), JSON.stringify(state, null, 2));
  console.log(JSON.stringify(state, null, 2));
})().catch(e => {console.error(e.shortMessage || e.message);process.exitCode=1;});