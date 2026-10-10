"""Rapport d'incident (R4) : chronologie, montants, décisions, preuves, à partir des fichiers du relais.

Deux parties :
1. les FAITS, établis par le code à partir de events.jsonl / alerts.jsonl / flags.jsonl (jamais par le modèle) ;
2. la SYNTHÈSE, rédigée par Bedrock à partir de ces faits seulement, puis vérifiée : tout montant ou hash cité
   doit exister dans les faits, sinon on garde une synthèse écrite par le code.

Usage : python -m score.rapport --dossier ../shared --sortie rapport-incident.md [--sans-llm]
"""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from .regles import UNITE, fmt

CONSIGNE = """Tu rédiges la synthèse d'un rapport d'incident de sécurité pour la direction d'une organisation qui gère
sa trésorerie sur la blockchain, et pour un auditeur. Règles strictes :
- utilise UNIQUEMENT les faits fournis ; n'invente ni chiffre, ni date, ni cause, ni identité ;
- cite les montants exactement comme fournis ; ne cite pas de hash de transaction (ils sont dans le rapport) ;
- 3 paragraphes courts, en français : (1) ce qui s'est passé, (2) comment le garde a réagi et ce que les signataires
  ont décidé, (3) ce qu'il reste à faire (vérifications humaines, signalement, revue des accès) ;
- ton factuel ; n'affirme pas que c'est une fraude si les faits disent seulement « annulé » ou « en attente ».
Réponds par le texte seul."""


def lire(f: Path):
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]


def heure(ts):
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M:%S")


def etablir_faits(events, alertes, flags):
    """Reconstruit l'incident : paiements signalés, leur sort, chronologie, montants, délais."""
    al = {a["payment_id"]: a for a in alertes}
    pay, chrono, gel = {}, [], []
    for e in events:
        d, t, pid = e.get("data", {}), e["type"], e.get("data", {}).get("payment_id")
        if t == "payment_proposed":
            pay[pid] = {**d, "proposé": e["timestamp"], "tx": e["tx_hash"], "sort": "en attente", "signalé": None, "approbations": []}
        elif pid in pay and t == "payment_approved":
            pay[pid]["approbations"].append((e["timestamp"], d.get("owner"), e["tx_hash"]))
        elif pid in pay and t == "risk_flagged":
            pay[pid]["signalé"] = (e["timestamp"], d.get("level"), d.get("reason"), e["tx_hash"], d.get("by"))
        elif pid in pay and t == "payment_executed":
            pay[pid]["sort"] = "exécuté"
            pay[pid]["fin"] = (e["timestamp"], e["tx_hash"])
        elif pid in pay and t == "payment_cancelled":
            pay[pid]["sort"] = "annulé"
            pay[pid]["fin"] = (e["timestamp"], e["tx_hash"], d.get("by"), d.get("reason"))
        if t in ("wallet_frozen", "wallet_unfrozen", "address_flagged", "address_unflagged", "owner_replaced", "threshold_changed"):
            gel.append((e["timestamp"], t, d, e["tx_hash"]))
        chrono.append((e["timestamp"], t, pid, e["tx_hash"], d))
    incident = [p for p in pay.values() if p["signalé"] or p["payment_id"] in al]
    tente = sum(int(p["amount"]) for p in incident)
    sorti = sum(int(p["amount"]) for p in incident if p["sort"] == "exécuté")
    delais = [p["signalé"][0] - p["proposé"] for p in incident if p["signalé"]]
    return {
        "paiements": incident, "alertes": al, "gel": gel, "chrono": chrono, "flags": flags,
        "tente": tente, "sorti": sorti, "protege": tente - sorti,
        "delai_max": max(delais) if delais else None,
        "debut": min((p["proposé"] for p in incident), default=None),
        "fin": max((p.get("fin", (p["proposé"],))[0] for p in incident), default=None),
    }


def faits_texte(f):
    """Les faits, formulés pour le modèle (et lisibles tels quels)."""
    L = [f"Période : du {heure(f['debut'])} au {heure(f['fin'])}." if f["debut"] else "Aucun paiement signalé.",
         f"Paiements signalés par le garde : {len(f['paiements'])}.",
         f"Montant total tenté : {fmt(f['tente'])}. Sorti : {fmt(f['sorti'])}. Protégé : {fmt(f['protege'])}."]
    if f["delai_max"] is not None:
        L.append(f"Délai maximal entre la proposition d'un paiement et son signalement : {f['delai_max']} s.")
    for p in sorted(f["paiements"], key=lambda p: p["proposé"]):
        a = f["alertes"].get(p["payment_id"])
        s = p["signalé"]
        L.append(f"- Paiement n° {p['payment_id']} : {fmt(int(p['amount']))} vers {p['to'][:6]}…{p['to'][-4:]}, libellé « {p.get('memo', '')} », "
                 f"proposé le {heure(p['proposé'])}, {len(p['approbations'])} approbation(s)"
                 + (f", signalé « {s[1]} » {s[0] - p['proposé']} s après ({s[2]})" if s else "")
                 + (f", raisons du moteur : {' ; '.join(r['detail'] for r in a['reasons'])}" if a else "")
                 + f". Sort : {p['sort']}" + (f" ({p['fin'][3]})" if p["sort"] == "annulé" and len(p["fin"]) > 3 else "") + ".")
    for ts, t, d, _ in f["gel"]:
        if t == "wallet_frozen":
            L.append(f"- Le {heure(ts)}, un signataire a gelé le portefeuille (motif : « {d.get('reason', '')} »).")
        elif t == "wallet_unfrozen":
            L.append(f"- Le {heure(ts)}, le portefeuille a été dégelé par plusieurs signataires.")
        elif t == "address_flagged":
            L.append(f"- Le {heure(ts)}, l'oracle a inscrit l'adresse {d.get('flagged', '')[:6]}… au registre (niveau {d.get('level')}).")
        elif t == "threshold_changed":
            L.append(f"- Le {heure(ts)}, le seuil de signatures est passé de {d.get('previous_threshold')} à {d.get('new_threshold')}.")
        elif t == "owner_replaced":
            L.append(f"- Le {heure(ts)}, un signataire a été remplacé.")
    for fl in f["flags"]:
        if not fl.get("remove"):
            L.append(f"- Signalement Web : {fl['address'][:6]}… ({fl.get('category')}, confiance {fl.get('confidence')}), source {fl.get('source_url')}, "
                     f"citation : « {fl.get('quote', '')[:160]} ».")
    return "\n".join(L)


def synthese_code(f):
    n = len(f["paiements"])
    annules = sum(1 for p in f["paiements"] if p["sort"] == "annulé")
    return (f"{n} paiement(s) ont été signalés par le garde entre le {heure(f['debut'])} et le {heure(f['fin'])}, "
            f"pour un total de {fmt(f['tente'])}. {fmt(f['sorti'])} sont sortis ; {fmt(f['protege'])} ont été protégés. "
            f"{annules} paiement(s) ont été annulés par les signataires. Les vérifications humaines (contact du demandeur par un autre canal, "
            f"revue des accès des signataires, contestation ou confirmation des signalements) restent à documenter.") if n else "Aucun incident."


def verifier(texte, f):
    if not texte or len(texte) > 3000:
        return False
    if re.search(r"0x[a-fA-F0-9]{10,}", texte):
        return False  # pas de hash dans la synthèse
    montants_ok = {fmt(int(p["amount"])) for p in f["paiements"]} | {fmt(f["tente"]), fmt(f["sorti"]), fmt(f["protege"])}
    for m in re.findall(r"\d[\d  ]*\d mUSD", texte):
        if m.replace(" ", " ") not in montants_ok:
            return False  # un montant qui n'est pas dans les faits
    return True


def generer(dossier: Path, sans_llm=False):
    events, alertes, flags = lire(dossier / "events.jsonl"), lire(dossier / "alerts.jsonl"), lire(dossier / "flags.jsonl")
    f = etablir_faits(events, alertes, flags)
    faits = faits_texte(f)
    synthese, modele = synthese_code(f), "code"
    if not sans_llm and f["paiements"]:
        try:
            from commun import bedrock
            t = bedrock.texte_de(bedrock.converse(CONSIGNE, faits, max_tokens=900)).strip()
            if verifier(t, f):
                synthese, modele = t, bedrock.modele_utilise
        except Exception:
            pass
    preuves = []
    for p in sorted(f["paiements"], key=lambda p: p["proposé"]):
        preuves.append(f"| {p['payment_id']} | proposition | `{p['tx']}` |")
        if p["signalé"]:
            preuves.append(f"| {p['payment_id']} | signalement {p['signalé'][1]} | `{p['signalé'][3]}` |")
        if "fin" in p:
            preuves.append(f"| {p['payment_id']} | {p['sort']} | `{p['fin'][1]}` |")
    for ts, t, d, h in f["gel"]:
        preuves.append(f"| — | {t} | `{h}` |")
    for fl in f["flags"]:
        preuves.append(f"| — | signalement Web {fl['address'][:10]}… | preuve `{fl.get('evidence_hash', '')}` |")
    chrono = "\n".join(f"| {heure(ts)} | {t} | {pid if pid is not None else ''} |" for ts, t, pid, _, _ in f["chrono"])
    return f"""# Rapport d'incident — garde de trésorerie Breaker

*Généré le {datetime.now():%d/%m/%Y %H:%M}. Faits établis par le code à partir des événements de la chaîne ; synthèse rédigée par {modele}, vérifiée (aucun montant ni hash hors des faits).*

## 1. Synthèse

{synthese}

## 2. Chiffres clés

| | |
|---|---|
| Paiements signalés | {len(f['paiements'])} |
| Montant tenté | {fmt(f['tente'])} |
| Montant sorti | {fmt(f['sorti'])} |
| **Montant protégé** | **{fmt(f['protege'])}** |
| Délai maximal de signalement | {f['delai_max'] if f['delai_max'] is not None else '—'} s |

## 3. Faits

{faits}

## 4. Preuves (vérifiables sur l'explorateur de la chaîne)

| Paiement | Événement | Transaction / preuve |
|---|---|---|
{chr(10).join(preuves)}

## 5. Chronologie complète

| Heure | Événement | Paiement |
|---|---|---|
{chrono}

## 6. Suites à donner (humaines)

- [ ] Contacter le demandeur de chaque paiement signalé par un autre canal et consigner la réponse.
- [ ] Si une clé de signataire est suspectée : la remplacer, puis dégeler le portefeuille.
- [ ] Confirmer ou contester les signalements d'adresses (registre).
- [ ] Classer l'incident (impact, clients touchés) et, si l'organisation est régulée, notifier dans les délais applicables.
"""


def main():
    a = argparse.ArgumentParser(description="Rapport d'incident (R4)")
    a.add_argument("--dossier", type=Path, default=Path(__file__).resolve().parents[2] / "shared")
    a.add_argument("--sortie", type=Path, default=Path("rapport-incident.md"))
    a.add_argument("--sans-llm", action="store_true")
    args = a.parse_args()
    args.sortie.write_text(generer(args.dossier, args.sans_llm), encoding="utf-8")
    print(f"rapport écrit : {args.sortie}")


if __name__ == "__main__":
    main()
