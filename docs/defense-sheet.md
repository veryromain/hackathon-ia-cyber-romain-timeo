# Breaker — Defense Sheet

## Threat scenario addressed

This project addresses a DeFi treasury compromise pattern in which valid signer keys are not necessarily enough to prevent loss. The risk is a manipulated or malicious payment flow: a signer is deceived, a transaction appears legitimate, and multiple withdrawals are executed in a short burst. This is aligned with the Drift-style drain pattern observed in real incidents, where the wallet logic itself was correct but the operational control layer failed.

## What the product defends

- Multi-signature treasury wallets operating on Avalanche Fuji.
- High-value payment flows and rapid withdrawal sequences.
- New or unexpected beneficiaries, abnormal values, and suspicious destination reputations.
- Human decision-making under pressure, where the signer may be manipulated or misled by a spoofed UI or social-engineering flow.

## NIST CSF 2.0 coverage

- Detect: continuous monitoring of abnormal transaction values, unusual beneficiaries, and rapid multi-withdrawal patterns.
- Respond: hold the suspicious transaction, escalate to the signers, and preserve evidence for review.
- Recover: keep the decision trail for post-incident review and governance follow-up.

## ATT&CK / ATLAS / OWASP mapping

- MITRE ATT&CK: phishing/social engineering, manipulation of legitimate workflow, and execution of malicious or misleading financial actions.
- MITRE ATLAS: unsafe automation and model-assisted decisioning in operational finance contexts.
- OWASP Top 10 for Agentic Applications: excessive agency, insufficient verification before action, and over-trust in a single automated signal.

Breaker reduces this risk by adding an explainable second layer of verification before execution, while keeping the final decision under human control.

## Metrics achieved

On synthetic fraud scenarios during the hackathon:
- 90.9% of fraudulent amounts were put on hold; 31/40 fraudulent payments were held and 38/40 held or slowed.
- 0 mUSD exited the wallet during the live demo.
- Detection and alerting occurred in ~5–6 seconds on Avalanche Fuji.
- Legitimate false positives were limited to ~5.1% for high-value first-time payments.

## Known limitations

- Results are measured on synthetic data, not production treasury traffic.
- Validation is done on the Fuji testnet, not on live production infrastructure.
- This is a targeted defense against a specific class of DeFi drain patterns, not a universal solution for all financial compromise scenarios.
- Human governance remains necessary; the system does not replace signer accountability or legal approval procedures.

## Business value

Breaker is designed for crypto-native teams, protocols, and treasuries with small security operations. It creates a practical control layer that explains risk clearly, slows dangerous execution, and gives teams a defendable response path without fully automating trust.


## Final submission references

The verified one-page PDF and detailed response playbook are in `shared/submit/` in the common project repository. Exact final counts: 40 fraudulent and 234 normal payments; 31 fraud hold, 7 fraud step_up, 2 missed; 12 normal hold. Synthetic data, no independent contract audit.
