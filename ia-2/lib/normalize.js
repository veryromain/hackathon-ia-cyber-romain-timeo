// Traduit les journaux d'événements des contrats vers le format de shared/format-evenements.md.
// Utilisé par le relais (en direct) et par le générateur de jeux de données (hors ligne) :
// les deux produisent donc exactement les mêmes lignes.

const LEVELS = ["none", "step_up", "hold"];
const CHANGES = { 1: "replace_owner", 2: "change_threshold" };
const lower = (address) => address.toLowerCase();
const num = (value) => Number(value);

function createNormalizer({ provider, wallet, registry, assetAddress, chainId, startSeq = 0 }) {
  const walletAddress = lower(wallet.target);
  const registryAddress = registry ? lower(registry.target) : null;
  const configIds = new Set();
  const txFromCache = new Map();
  const blockTimeCache = new Map();
  let seq = startSeq;

  async function txFrom(hash) {
    if (!txFromCache.has(hash)) txFromCache.set(hash, lower((await provider.getTransaction(hash)).from));
    return txFromCache.get(hash);
  }

  async function blockTime(number) {
    if (!blockTimeCache.has(number)) blockTimeCache.set(number, (await provider.getBlock(number)).timestamp);
    return blockTimeCache.get(number);
  }

  function describeWallet(name, a) {
    switch (name) {
      case "PaymentProposed":
        return ["payment_proposed", {
          payment_id: num(a.id), proposer: lower(a.proposer), to: lower(a.to), token: lower(assetAddress),
          amount: a.amount.toString(), memo: a.memo,
          required_approvals: num(a.requiredApprovals), executable_after: num(a.executableAfter),
        }];
      case "ConfigProposed":
        configIds.add(num(a.id));
        return ["config_proposed", {
          proposal_id: num(a.id), change: CHANGES[num(a.kind)], proposer: lower(a.proposer),
          new_owner: num(a.kind) === 1 ? lower(a.target) : null,
          previous_owner: num(a.kind) === 1 ? lower(a.subject) : null,
          new_threshold: num(a.kind) === 2 ? num(a.value) : null,
          required_approvals: num(a.requiredApprovals), executable_after: num(a.executableAfter),
        }];
      case "Approved": {
        const config = configIds.has(num(a.id));
        return [config ? "config_approved" : "payment_approved", {
          [config ? "proposal_id" : "payment_id"]: num(a.id), owner: lower(a.owner),
          approvals: num(a.approvals), required_approvals: num(a.requiredApprovals),
        }];
      }
      case "RiskFlagged":
        return ["risk_flagged", {
          payment_id: num(a.id), level: LEVELS[num(a.level)], reason: a.reason, by: lower(a.by),
          required_approvals: num(a.requiredApprovals), executable_after: num(a.executableAfter),
        }];
      case "PaymentExecuted":
        return ["payment_executed", {
          payment_id: num(a.id), to: lower(a.to), token: lower(assetAddress),
          amount: a.amount.toString(), executor: lower(a.executor),
        }];
      case "Cancelled": {
        const config = configIds.has(num(a.id));
        return [config ? "config_cancelled" : "payment_cancelled", {
          [config ? "proposal_id" : "payment_id"]: num(a.id), by: lower(a.by), reason: a.reason,
        }];
      }
      case "OwnerReplaced":
        return ["owner_replaced", {
          previous_owner: lower(a.previousOwner), new_owner: lower(a.newOwner), key_expires_at: num(a.keyExpiresAt),
        }];
      case "ThresholdChanged":
        return ["threshold_changed", {
          previous_threshold: num(a.previousThreshold), new_threshold: num(a.newThreshold),
        }];
      case "Frozen":
        return ["wallet_frozen", { by: lower(a.by), reason: a.reason }];
      case "UnfreezeApproved":
        return ["unfreeze_approved", {
          owner: lower(a.owner), approvals: num(a.approvals), required_approvals: num(a.requiredApprovals),
        }];
      case "Unfrozen":
        return ["wallet_unfrozen", { by: lower(a.by) }];
      default:
        return null;
    }
  }

  function describeRegistry(name, a) {
    switch (name) {
      case "AddressFlagged":
        return ["address_flagged", {
          flagged: lower(a.flagged), level: LEVELS[num(a.level)], category: a.category,
          evidence_hash: a.evidenceHash, expires_at: num(a.expiresAt), by: lower(a.by),
        }];
      case "AddressUnflagged":
        return ["address_unflagged", { flagged: lower(a.flagged), by: lower(a.by) }];
      default:
        return null; // événements de rôles d'OpenZeppelin, sans intérêt pour le moteur
    }
  }

  /// @returns l'événement normalisé, ou null si le journal ne nous concerne pas.
  async function normalize(log) {
    const address = lower(log.address);
    let described = null;
    let contract = null;
    if (address === walletAddress) {
      const parsed = wallet.interface.parseLog(log);
      if (parsed) described = describeWallet(parsed.name, parsed.args);
      contract = "wallet";
    } else if (address === registryAddress) {
      const parsed = registry.interface.parseLog(log);
      if (parsed) described = describeRegistry(parsed.name, parsed.args);
      contract = "registry";
    }
    if (!described) return null;
    seq += 1;
    return {
      seq, chain_id: chainId, block: log.blockNumber, timestamp: await blockTime(log.blockNumber),
      tx_hash: log.transactionHash, log_index: log.index, tx_from: await txFrom(log.transactionHash),
      contract, address, type: described[0], data: described[1],
    };
  }

  /// Lit tous les journaux des deux contrats entre deux blocs, dans l'ordre de la chaîne.
  async function collect(fromBlock, toBlock) {
    const addresses = [wallet.target];
    if (registry) addresses.push(registry.target);
    const logs = await provider.getLogs({ address: addresses, fromBlock, toBlock });
    logs.sort((x, y) => x.blockNumber - y.blockNumber || x.index - y.index);
    const events = [];
    for (const log of logs) {
      const event = await normalize(log);
      if (event) events.push(event);
    }
    return events;
  }

  return { normalize, collect };
}

module.exports = { createNormalizer, LEVELS };
