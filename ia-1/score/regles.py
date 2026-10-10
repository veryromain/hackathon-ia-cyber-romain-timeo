"""Règles de détection du moteur de score (R1).

Chaque règle regarde un paiement proposé et l'historique du portefeuille, et renvoie
une raison (code, détail lisible, transactions de preuve) avec un poids entre 0 et 1.
Les poids se combinent en « OU bruité » : score = 1 - produit(1 - poids).
"""
import math
import re
from dataclasses import dataclass, field
from datetime import datetime
from statistics import median
from zoneinfo import ZoneInfo

UNITE = 10**18  # montants en unités de base, 18 décimales
FUSEAU = ZoneInfo("Europe/Paris")

# Réglages, à calibrer sur le trafic normal d'entraînement (R2), jamais sur le test.
POIDS = {
    "NEW_RECIPIENT": 0.35,
    "AMOUNT_OUTLIER_MAX": 0.6,
    "BURST": 0.40,
    "URGENCY_MEMO": 0.30,
    "OFF_HOURS": 0.15,
    "FLAGGED_ADDRESS_HOLD": 0.90,
    "FLAGGED_ADDRESS_STEP_UP": 0.50,
    "RECENT_OWNER_CHANGE": 0.30,
    "THRESHOLD_LOWERED": 0.50,
}
SEUIL_HOLD = 0.70
SEUIL_STEP_UP = 0.30
RATIO_MONTANT_MIN = 3.0          # montant >= 3 fois le paiement médian
FENETRE_RAFALE_S = 600           # autres propositions dans les 10 dernières minutes
FENETRE_CHANGEMENT_S = 7 * 86400  # changement de signataire ou de seuil dans les 7 derniers jours
HEURES_OUVREES = (7, 20)         # 7h–20h, heure de Paris, du lundi au vendredi

MOTS_URGENCE = re.compile(
    r"urgent|confidentiel|secret|discr[eè]t|ne pas en parler|imm[ée]diat|"
    r"nouveau (rib|iban|compte|portefeuille|wallet)|changement de coordonn[ée]es",
    re.IGNORECASE,
)


@dataclass
class Raison:
    code: str
    detail: str
    preuves: list
    poids: float


@dataclass
class EtatPortefeuille:
    """Ce que le moteur sait du portefeuille, construit uniquement à partir des événements."""
    destinataires_connus: set = field(default_factory=set)
    montants_payes: list = field(default_factory=list)         # montants des paiements exécutés
    propositions: dict = field(default_factory=dict)           # payment_id -> événement de proposition
    adresses_signalees: dict = field(default_factory=dict)     # adresse -> {level, expires_at, tx_hash, category}
    changements_signataires: list = field(default_factory=list)  # (timestamp, tx_hash)
    baisses_seuil: list = field(default_factory=list)            # (timestamp, tx_hash, ancien, nouveau)


def fmt(montant: int) -> str:
    return f"{montant / UNITE:,.0f}".replace(",", " ") + " mUSD"


def r_nouveau_destinataire(p, etat):
    if p["to"] not in etat.destinataires_connus:
        return Raison("NEW_RECIPIENT", "premier paiement vers cette adresse", [p["tx_hash"]], POIDS["NEW_RECIPIENT"])


def r_montant_hors_norme(p, etat):
    if len(etat.montants_payes) < 2:
        return None  # pas assez d'historique pour juger
    ref = median(etat.montants_payes)
    ratio = p["amount"] / ref if ref else math.inf
    if ratio >= RATIO_MONTANT_MIN:
        poids = min(POIDS["AMOUNT_OUTLIER_MAX"], 0.15 * math.log2(ratio))
        return Raison("AMOUNT_OUTLIER", f"{fmt(p['amount'])}, {ratio:.1f} fois le paiement médian ({fmt(int(ref))})",
                      [p["tx_hash"]], poids)


def r_rafale(p, etat):
    autres = [q for q in etat.propositions.values()
              if q["payment_id"] != p["payment_id"] and 0 <= p["timestamp"] - q["timestamp"] <= FENETRE_RAFALE_S]
    if autres:
        duree = p["timestamp"] - min(q["timestamp"] for q in autres)
        return Raison("BURST", f"{len(autres) + 1} paiements proposés en {duree} s",
                      [q["tx_hash"] for q in autres] + [p["tx_hash"]], POIDS["BURST"])


def r_libelle_urgent(p, etat):
    m = MOTS_URGENCE.search(p.get("memo") or "")
    if m:
        return Raison("URGENCY_MEMO", f"libellé pressant ou secret (« {m.group(0)} »)", [], POIDS["URGENCY_MEMO"])


def r_hors_heures(p, etat):
    t = datetime.fromtimestamp(p["timestamp"], FUSEAU)
    if t.weekday() >= 5 or not (HEURES_OUVREES[0] <= t.hour < HEURES_OUVREES[1]):
        return Raison("OFF_HOURS", f"proposé le {t:%a %d/%m à %Hh%M} (heure de Paris)", [p["tx_hash"]], POIDS["OFF_HOURS"])


def r_adresse_signalee(p, etat):
    s = etat.adresses_signalees.get(p["to"])
    if s and s["expires_at"] > p["timestamp"]:
        cle = "FLAGGED_ADDRESS_HOLD" if s["level"] == "hold" else "FLAGGED_ADDRESS_STEP_UP"
        return Raison("FLAGGED_ADDRESS", f"destinataire signalé par l'oracle ({s['category']})", [s["tx_hash"]], POIDS[cle])


def r_changement_recent(p, etat):
    recents = [c for c in etat.changements_signataires if 0 <= p["timestamp"] - c[0] <= FENETRE_CHANGEMENT_S]
    if recents:
        h = (p["timestamp"] - recents[-1][0]) // 3600
        return Raison("RECENT_OWNER_CHANGE", f"signataire remplacé il y a {h} h", [c[1] for c in recents], POIDS["RECENT_OWNER_CHANGE"])


def r_seuil_abaisse(p, etat):
    recents = [b for b in etat.baisses_seuil if 0 <= p["timestamp"] - b[0] <= FENETRE_CHANGEMENT_S]
    if recents:
        b = recents[-1]
        return Raison("THRESHOLD_LOWERED", f"seuil de signatures abaissé de {b[2]} à {b[3]}", [b[1]], POIDS["THRESHOLD_LOWERED"])


REGLES = [r_adresse_signalee, r_nouveau_destinataire, r_montant_hors_norme, r_rafale,
          r_libelle_urgent, r_hors_heures, r_changement_recent, r_seuil_abaisse]
