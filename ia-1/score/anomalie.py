"""Modèle d'anomalie (R2) : un Isolation Forest appris sur le trafic normal, en complément des règles.

Chaque paiement proposé est décrit par quelques caractéristiques, calculées avec ce que le moteur sait AVANT
ce paiement. Le modèle apprend la forme du trafic normal (jeu d'entraînement, sans fraude) ; un paiement
plus étrange que presque tous ceux de l'entraînement reçoit la raison ANOMALY_MODEL.

Entraîner : python -m score.anomalie --events ../shared/donnees/train.events.jsonl \
                --carnet ../shared/donnees/carnet.json --sortie modeles/anomalie.joblib
"""
import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from statistics import median

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from . import regles

# La nouveauté du destinataire n'est PAS une caractéristique : la règle NEW_RECIPIENT la compte déjà
# (essai sur train : avec elle, les nouveaux fournisseurs légitimes étaient mis en attente 50 % plus souvent).
NOMS = ["log_montant", "log_ratio_habituel", "heure", "weekend", "log_secondes_depuis_precedent",
        "propositions_10_min", "jours_depuis_changement_signataire", "libelle_urgent", "paiements_meme_dest_3_jours"]


def caracteristiques(p, etat):
    """Vecteur décrivant le paiement p, à partir de l'état AVANT ce paiement."""
    t = datetime.fromtimestamp(p["timestamp"], regles.FUSEAU)
    hist = etat.montants_par_dest.get(p["to"])
    if hist:
        ref = median(hist)
    elif etat.montants_payes:
        ref = regles.centile(etat.montants_payes, regles.CENTILE_NOUVEAU)
    else:
        ref = p["amount"] or 1
    props = list(etat.propositions.values())
    precedents = [p["timestamp"] - q["timestamp"] for q in props if q["timestamp"] <= p["timestamp"]]
    changements = [p["timestamp"] - c[0] for c in etat.changements_signataires if c[0] <= p["timestamp"]]
    return [
        math.log10(max(p["amount"], 1) / regles.UNITE + 1),
        math.log2(max(p["amount"], 1) / max(ref, 1)),
        t.hour + t.minute / 60,
        float(t.weekday() >= 5),
        math.log1p(min(precedents) if precedents else 86400 * 30),
        float(sum(1 for d in precedents if d <= regles.FENETRE_RAFALE_S)),
        min(min(changements) / 86400, 30.0) if changements else 30.0,
        float(bool(regles.MOTS_URGENCE.search(p.get("memo") or ""))),
        float(sum(1 for q in props if q["to"] == p["to"] and 0 < p["timestamp"] - q["timestamp"] <= regles.FENETRE_REPETITION_S)),
    ]


class ModeleAnomalie:
    def __init__(self, foret, seuil_alerte, seuil_fort):
        self.foret, self.seuil_alerte, self.seuil_fort = foret, seuil_alerte, seuil_fort

    def etrangete(self, x):
        return float(-self.foret.score_samples(np.array([x]))[0])  # plus c'est haut, plus c'est étrange

    def raison(self, p, etat):
        x = caracteristiques(p, etat)
        e = self.etrangete(x)
        if e < self.seuil_alerte:
            return None
        poids = regles.POIDS["ANOMALY_MODEL_FORT"] if e >= self.seuil_fort else regles.POIDS["ANOMALY_MODEL"]
        # Les deux caractéristiques les plus éloignées de la médiane d'entraînement, pour l'explication.
        ecarts = np.abs((np.array(x) - self.mediane) / self.echelle)
        top = [NOMS[i] for i in np.argsort(-ecarts)[:2]]
        return regles.Raison("ANOMALY_MODEL", f"paiement atypique pour ce portefeuille (surtout : {', '.join(top)})",
                             [p["tx_hash"]], poids)


def entrainer(events, carnet, graine=0):
    from .moteur import Moteur  # import local : évite l'import circulaire
    m = Moteur(carnet)
    X = []
    for ev in events:
        if ev["type"] == "payment_proposed":
            d = ev["data"]
            p = {**d, "to": d["to"].lower(), "proposer": d.get("proposer", "").lower(), "amount": int(d["amount"]),
                 "timestamp": ev["timestamp"], "tx_hash": ev["tx_hash"]}
            X.append(caracteristiques(p, m.etat))
        m.traiter(ev)
    X = np.array(X)
    foret = IsolationForest(n_estimators=300, random_state=graine).fit(X)
    scores = -foret.score_samples(X)
    # Seuils fixés sur l'entraînement : ~1 % des paiements normaux dépassent le seuil d'alerte, aucun le seuil fort.
    modele = ModeleAnomalie(foret, float(np.quantile(scores, 0.99)), float(scores.max()) * 1.02)
    modele.mediane = np.median(X, axis=0)
    modele.echelle = np.quantile(X, 0.75, axis=0) - np.quantile(X, 0.25, axis=0) + 1e-6
    return modele, len(X)


def main():
    a = argparse.ArgumentParser(description="Entraîne le modèle d'anomalie (R2) sur du trafic normal")
    a.add_argument("--events", required=True, type=Path)
    a.add_argument("--carnet", type=Path)
    a.add_argument("--sortie", type=Path, default=Path("modeles/anomalie.joblib"))
    args = a.parse_args()
    events = [json.loads(l) for l in open(args.events) if l.strip()]
    carnet = json.loads(args.carnet.read_text()) if args.carnet else []
    modele, n = entrainer(events, carnet)
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modele, args.sortie)
    print(f"modèle appris sur {n} paiements normaux → {args.sortie} "
          f"(seuil d'alerte {modele.seuil_alerte:.3f}, seuil fort {modele.seuil_fort:.3f})")


if __name__ == "__main__":
    main()
