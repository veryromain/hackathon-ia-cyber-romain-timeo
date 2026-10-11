# Track 1 deliverable — DeFi incident detection and response PoC

## Goal

Create a blue-team proof of concept for treasury security in a DeFi environment. The objective is to detect and respond to a stealthy drain pattern in which an attacker abuses valid signing authority, manipulates signers, and triggers multiple withdrawals in a short time window.

## Solution

Breaker combines three layers:

1. On-chain transaction monitoring on Avalanche Fuji.
2. An explainable risk engine that scores abnormal value, new beneficiaries, rapid withdrawal sequences, and destination reputation.
3. A response flow that raises an alert, initiates a hold, and requires explicit human escalation before any final action.

The product is designed for a wallet governed by multiple signers, without giving the guard a unilateral veto. The final decision remains with the treasury team.

## Attack scenario

The scenario mirrors a Drift-style drain pattern:
- a malicious or spoofed transaction is proposed to signers;
- the value and beneficiary are unusual for the treasury;
- several transfers or quick withdrawals are attempted in a short burst;
- the operational control logic triggers a hold and demands validation.

## Flow of the PoC

- Event collection: wallet and transaction events are read from the chain and normalized.
- Pattern detection: the engine identifies atypical payment patterns, unusual recipients, and multiple rapid withdrawals.
- Risk scoring: scores are derived from value, source/destination history, prior reputation, and sequence anomalies.
- Response action: the system can place the transaction in a hold state, notify signers, and request additional verification.
- DORA / incident classification: a factual incident record is created for human review; regulatory classification must be validated by the client.

## Response playbook

1. Detect and triage the transaction.
2. Freeze or hold the suspicious flow before execution.
3. Notify all relevant signers with the evidence and risk explanation.
4. Require a second confirmation or a formal override path.
5. Preserve the trace on the chain and in logs for the incident review.
6. Record the incident in a concise, regulator-friendly report and document what failed, what was blocked, and what was allowed.

## Metrics and evidence

Measured on synthetic fraud scenarios during the hackathon:
- 90.9% of fraudulent amounts were put on hold; 31/40 fraudulent payments were held and 38/40 held or slowed.
- 0 mUSD exited the wallet during the live demo.
- Signal to signer alert time: ~5–6 seconds on Fuji.
- False-positive rate: ~5.1% on legitimate high-value first-time payments.

These results are not guaranteed on live production traffic, but they demonstrate the product’s practical detection and response capability in a controlled environment.

## Security and compliance framing

This project addresses the jurisdictional and operational concerns behind DORA and safe treasury governance:
- faster detection of financial operational incidents;
- better traceability and decision logging;
- a human-controlled escalation path;
- clearer evidence for post-incident review.

## Known limitations

- Prototype only; not yet external-audit certified.
- The live demo is on Avalanche Fuji testnet, not on production treasury infrastructure.
- The model focuses on a specific family of DeFi abuse patterns; it does not yet cover all fraud and operational risk scenarios.
- Legitimate first-time payments may still trigger a hold, so tuning remains necessary.

## Value to the jury

This PoC demonstrates a credible blue-team defense pattern: monitor abnormal DeFi treasury activity, explain what is risky, pause suspicious execution, and keep the human in the loop. It is balanced, demonstrable, and aligned with the track’s focus on detection, response, and recovery.


## Final submission references

The verified one-page PDF and detailed response playbook are in `shared/submit/` in the common project repository. Exact final counts: 40 fraudulent and 234 normal payments; 31 fraud hold, 7 fraud step_up, 2 missed; 12 normal hold. Synthetic data, no independent contract audit.
