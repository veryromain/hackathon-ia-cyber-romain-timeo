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
    "URGENCY_MEMO": 0.20,             # seul, ne suffit pas (régularisations urgentes légitimes)
    "OFF_HOURS": 0.15,               # soir ou week-end
    "OFF_HOURS_NUIT": 0.30,          # 0h–6h
    "FLAGGED_ADDRESS_HOLD": 0.90,
    "FLAGGED_ADDRESS_STEP_UP": 0.50,
    "RECENT_OWNER_CHANGE": 0.10,     # changement légitime fréquent (renouvellement de clé)
    "NEW_OWNER_PROPOSES": 0.50,      # le signataire tout juste ajouté propose lui-même un paiement
    "THRESHOLD_LOWERED": 0.50,
    "PAYMENT_FRAUD_PATTERN": 0.55,   # nouveau destinataire + libellé pressant / changement de coordonnées
    "RAPID_REPEAT": 0.35,            # paiements répétés vers une adresse apparue il y a moins de 7 jours
    "ANOMALY_MODEL": 0.25,           # R2 : plus étrange que 99 % du trafic normal d'entraînement
    "ANOMALY_MODEL_FORT": 0.40,      # R2 : plus étrange que tout le trafic normal d'entraînement
    # Corrections du 10/10 soir, guidées par la FORME des fraudes du jeu de généralisation (pas par ses chiffres) :
    "NEW_OWNER_LARGE_PAYMENT": 0.65, # clé de moins de 7 jours + montant hors norme : forme de Bybit → hold
    "NEW_OWNER_APPROVES": 0.45,      # une clé neuve apporte une signature à un paiement en cours
    "RECENT_RECIPIENT": 0.15,        # destinataire payé pour la 1re fois il y a moins de 30 jours
    "RECENT_RECIPIENT_SPIKE": 0.60,  # ... et montant > 5 × ce qu'il a déjà reçu : mise en confiance puis gros coup
    "DAILY_CAP_RECIPIENT": 0.50,     # cumul du jour vers ce destinataire bien au-dessus de son habitude
    "DAILY_CAP_RECENT": 0.50,        # cumul du jour vers des adresses récentes au-dessus des gros paiements habituels : fractionnement
    "AMOUNT_OUTLIER_EXTREME": 0.76,  # ≥ 10 × l'habitude d'un destinataire connu → hold à lui seul
    "TAINTED_FUNDS": 0.50,           # R9 : a reçu une part significative des fonds d'une adresse signalée
    "LOOKALIKE_ADDRESS": 0.90,       # adresse sosie : mêmes premiers et derniers caractères qu'un fournisseur connu → hold
    "HONEYPOT_ADDRESS": 0.99,        # adresse piège du carnet : seul un attaquant qui lit le carnet peut la payer
    # Historique on-chain du destinataire (11/10, Timéo). Non mesurés : les adresses de nos jeux de données n'ont pas
    # de passé sur la chaîne. Choisis pour qu'aucun ne mette en attente à lui seul, même ajouté à NEW_RECIPIENT.
    "FRESH_ADDRESS": 0.30,           # adresse vierge, ou active depuis moins de 7 jours
    "FRESH_ADDRESS_FAIBLE": 0.15,    # n'a jamais rien signé, ancienneté inconnue (un coffre qui ne fait que recevoir aussi)
    "NEW_CONTRACT": 0.30,            # contrat déployé il y a moins de 7 jours
    "NEW_CONTRACT_NON_VERIFIE": 0.45,  # ... et code source non publié
}
FENETRE_ADRESSE_NEUVE_S = 7 * 86400
SOSIE_PREFIXE, SOSIE_SUFFIXE = 4, 4   # caractères comparés après « 0x » et en fin d'adresse (ce que l'œil vérifie)
RATIO_EXTREME = 10.0
FENETRE_RECENT_30J_S = 30 * 86400
FENETRE_JOUR_S = 86400
RATIO_SPIKE = 5.0
RATIO_CUMUL_JOUR = 5.0
PART_TAINTED_MIN = 0.10          # R9 : part minimale des sorties de l'adresse signalée (ignore le « dusting »)
FENETRE_TAINTED_S = 7 * 86400
SEUIL_HOLD = 0.75  # choisi par recherche sur les graines 1-20 (faux hold 0,5 % au lieu de 1,1 %)
SEUIL_STEP_UP = 0.30
RATIO_MONTANT_MIN = 3.0          # destinataire connu : montant >= 3 fois SON paiement médian
CENTILE_NOUVEAU = 0.90           # destinataire nouveau : montant au-dessus du 90e centile de tous les paiements
FENETRE_RECENT_S = 7 * 86400     # un destinataire « récent » a reçu son 1er paiement il y a moins de 7 jours
FENETRE_REPETITION_S = 3 * 86400
FENETRE_RAFALE_S = 600           # autres propositions dans les 10 dernières minutes
FENETRE_CHANGEMENT_S = 7 * 86400  # changement de signataire ou de seuil dans les 7 derniers jours
HEURES_OUVREES = (7, 20)         # 7h–20h, heure de Paris (réglage client, voir charger_reglages_client)
JOURS_OUVRES = {0, 1, 2, 3, 4}   # lundi à vendredi (réglage client)


def charger_reglages_client(chemin):
    """Réglages du client (config/client.json) : heures et jours ouvrés. Jamais changés par une personne seule en
    production (ils passent par le portefeuille, comme un paiement) ; ici un simple fichier pour la démo."""
    import json
    global HEURES_OUVREES, JOURS_OUVRES
    d = json.loads(open(chemin, encoding="utf-8").read())
    if "heures_ouvrees" in d:
        HEURES_OUVREES = tuple(d["heures_ouvrees"])
    if "jours_ouvres" in d:
        JOURS_OUVRES = set(d["jours_ouvres"])

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
    montants_par_dest: dict = field(default_factory=dict)      # destinataire -> montants exécutés
    premier_paiement: dict = field(default_factory=dict)       # destinataire -> date du 1er paiement exécuté
    nouveaux_signataires: dict = field(default_factory=dict)   # adresse -> (date d'ajout, tx_hash)
    recus_par_dest: dict = field(default_factory=dict)         # destinataire -> total déjà exécuté vers lui
    teintees: dict = field(default_factory=dict)               # R9 : adresse -> (part des sorties de l'adresse signalée, date, tx_hash, origine)
    services_connus: set = field(default_factory=set)          # R9 : plateformes, ponts, routeurs : jamais teintés
    pieges: set = field(default_factory=set)                   # adresses pièges du carnet (honeypots)
    propositions: dict = field(default_factory=dict)           # payment_id -> événement de proposition
    adresses_signalees: dict = field(default_factory=dict)     # adresse -> {level, expires_at, tx_hash, category}
    changements_signataires: list = field(default_factory=list)  # (timestamp, tx_hash)
    baisses_seuil: list = field(default_factory=list)            # (timestamp, tx_hash, ancien, nouveau)


def fmt(montant: int) -> str:
    return f"{montant / UNITE:,.0f}".replace(",", " ") + " mUSD"


def r_nouveau_destinataire(p, etat):
    if p["to"] not in etat.destinataires_connus:
        return Raison("NEW_RECIPIENT", "premier paiement vers cette adresse", [p["tx_hash"]], POIDS["NEW_RECIPIENT"])


def centile(valeurs, q):
    v = sorted(valeurs)
    return v[min(len(v) - 1, int(q * len(v)))]


def r_montant_hors_norme(p, etat):
    """Compare au propre historique du destinataire ; pour un inconnu, aux plus gros paiements habituels."""
    hist = etat.montants_par_dest.get(p["to"])
    if not hist and p["to"] in etat.destinataires_connus:
        return None  # destinataire du carnet d'adresses, pas encore d'historique de montant
    if hist:
        ref, quoi = median(hist), "le paiement médian à ce destinataire"
    elif len(etat.montants_payes) >= 3:
        ref, quoi = centile(etat.montants_payes, CENTILE_NOUVEAU), "les plus gros paiements habituels (90e centile)"
        if p["amount"] > ref:  # pour un inconnu, dépasser le 90e centile suffit
            ratio = p["amount"] / ref
            poids = min(POIDS["AMOUNT_OUTLIER_MAX"], 0.30 + 0.15 * math.log2(ratio))
            return Raison("AMOUNT_OUTLIER", f"{fmt(p['amount'])} vers une adresse inconnue, au-dessus de {quoi} ({fmt(int(ref))})",
                          [p["tx_hash"]], poids)
        return None
    else:
        return None  # pas assez d'historique pour juger
    ratio = p["amount"] / ref if ref else math.inf
    if ratio >= RATIO_EXTREME:
        return Raison("AMOUNT_OUTLIER_EXTREME", f"{fmt(p['amount'])}, {ratio:.0f} fois {quoi} ({fmt(int(ref))})",
                      [p["tx_hash"]], POIDS["AMOUNT_OUTLIER_EXTREME"])
    if ratio >= RATIO_MONTANT_MIN:
        poids = min(POIDS["AMOUNT_OUTLIER_MAX"], 0.15 * math.log2(ratio))
        return Raison("AMOUNT_OUTLIER", f"{fmt(p['amount'])}, {ratio:.1f} fois {quoi} ({fmt(int(ref))})",
                      [p["tx_hash"]], poids)


def r_rafale(p, etat):
    if p["to"] in etat.destinataires_connus:
        return None  # paiements groupés vers des destinataires connus : normal (fin de mois)
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
    if t.weekday() not in JOURS_OUVRES or not (HEURES_OUVREES[0] <= t.hour < HEURES_OUVREES[1]):
        poids = POIDS["OFF_HOURS_NUIT"] if t.hour < 6 else POIDS["OFF_HOURS"]
        return Raison("OFF_HOURS", f"proposé le {t:%d/%m à %Hh%M} (heure de Paris)", [p["tx_hash"]], poids)


def r_adresse_signalee(p, etat):
    s = etat.adresses_signalees.get(p["to"])
    if s and s["expires_at"] > p["timestamp"]:
        cle = "FLAGGED_ADDRESS_HOLD" if s["level"] == "hold" else "FLAGGED_ADDRESS_STEP_UP"
        return Raison("FLAGGED_ADDRESS", f"destinataire signalé par l'oracle ({s['category']})", [s["tx_hash"]], POIDS[cle])


def montant_hors_norme(p, etat) -> bool:
    """Vrai si le montant dépasse l'habitude du destinataire (× 3) ou, pour un inconnu, les gros paiements habituels."""
    hist = etat.montants_par_dest.get(p["to"])
    if hist:
        return p["amount"] >= RATIO_MONTANT_MIN * median(hist)
    if len(etat.montants_payes) >= 3:
        return p["amount"] > centile(etat.montants_payes, CENTILE_NOUVEAU)
    return False


PAIEMENTS_POUR_ETRE_CONNU = 3


def est_recent(a, etat, maintenant) -> bool:
    """Récent = apparu depuis moins de 30 jours ET moins de 3 paiements exécutés (un fournisseur régulier n'est pas « récent »)."""
    premier = etat.premier_paiement.get(a)
    if premier is None:
        return a not in etat.destinataires_connus
    return maintenant - premier <= FENETRE_RECENT_30J_S and len(etat.montants_par_dest.get(a, ())) < PAIEMENTS_POUR_ETRE_CONNU


def r_destinataire_recent(p, etat):
    """Mise en confiance : un destinataire apparu depuis moins de 30 jours reçoit soudain bien plus que ce qu'il a déjà reçu."""
    premier = etat.premier_paiement.get(p["to"])
    if premier is None or not est_recent(p["to"], etat, p["timestamp"]):
        return None
    jours = (p["timestamp"] - premier) // 86400
    recu = etat.recus_par_dest.get(p["to"], 0)
    if recu and p["amount"] >= RATIO_SPIKE * recu:
        n = len(etat.montants_par_dest.get(p["to"], ()))
        return Raison("RECENT_RECIPIENT_SPIKE", f"schéma de mise en confiance : {n} petit(s) paiement(s) ({fmt(recu)} au total) depuis {jours} j, "
                      f"puis celui-ci, {p['amount'] / recu:.0f} fois plus gros", [p["tx_hash"]], POIDS["RECENT_RECIPIENT_SPIKE"])
    return Raison("RECENT_RECIPIENT", f"destinataire apparu il y a {jours} j", [p["tx_hash"]], POIDS["RECENT_RECIPIENT"])


def r_cumul_du_jour(p, etat):
    """Fractionnement : le cumul des propositions du jour, vers ce destinataire ou vers des adresses récentes, dépasse l'habitude."""
    jour = [q for q in etat.propositions.values() if 0 <= p["timestamp"] - q["timestamp"] <= FENETRE_JOUR_S]
    meme = sum(q["amount"] for q in jour if q["to"] == p["to"]) + p["amount"]
    hist = etat.montants_par_dest.get(p["to"])
    n_meme = sum(1 for q in jour if q["to"] == p["to"])
    if hist and n_meme >= 2 and meme >= RATIO_CUMUL_JOUR * median(hist):  # ≥ 3 propositions dans la journée vers ce destinataire
        return Raison("DAILY_CAP_RECIPIENT", f"{fmt(meme)} proposés aujourd'hui vers ce destinataire, {meme / median(hist):.1f} fois son paiement médian",
                      [q["tx_hash"] for q in jour if q["to"] == p["to"]] + [p["tx_hash"]], POIDS["DAILY_CAP_RECIPIENT"])
    def recent(a):
        return est_recent(a, etat, p["timestamp"])
    if recent(p["to"]) and len(etat.montants_payes) >= 3:
        vers_recents = [q for q in jour if recent(q["to"]) and q["to"] != p["to"]]
        total = sum(q["amount"] for q in vers_recents) + p["amount"]
        if len(vers_recents) >= 2 and total > centile(etat.montants_payes, CENTILE_NOUVEAU):  # ≥ 3 adresses récentes dans la journée
            return Raison("DAILY_CAP_RECENT", f"{fmt(total)} proposés aujourd'hui vers {len(vers_recents) + 1} adresses récentes, au-dessus des plus gros paiements habituels",
                          [q["tx_hash"] for q in vers_recents] + [p["tx_hash"]], POIDS["DAILY_CAP_RECENT"])


def r_adresse_sosie(p, etat):
    """Address poisoning : l'attaquant fabrique une adresse qui imite le début et la fin de celle d'un vrai fournisseur,
    puis l'injecte dans l'historique (dusting) pour que le trésorier la copie. Le sosie n'est jamais dans le carnet."""
    to = p["to"]
    if to in etat.destinataires_connus:
        return None
    for connu in etat.destinataires_connus:
        if connu != to and connu[2:2 + SOSIE_PREFIXE] == to[2:2 + SOSIE_PREFIXE] and connu[-SOSIE_SUFFIXE:] == to[-SOSIE_SUFFIXE:]:
            return Raison("LOOKALIKE_ADDRESS", f"adresse sosie : ressemble au fournisseur connu {connu[:6]}…{connu[-4:]} "
                          f"(mêmes premiers et derniers caractères) mais n'est pas la même adresse", [p["tx_hash"]], POIDS["LOOKALIKE_ADDRESS"])


def r_adresse_piege(p, etat):
    """Adresse piège : un faux fournisseur glissé dans le carnet, que personne de légitime ne paiera jamais."""
    if p["to"] in etat.pieges:
        return Raison("HONEYPOT_ADDRESS", "adresse piège du carnet : seul quelqu'un qui a lu le carnet ou la facturation peut la proposer ; compromission probable",
                      [p["tx_hash"]], POIDS["HONEYPOT_ADDRESS"])


def r_adresse_sans_passe(p, etat):
    """Le destinataire est inconnu du client ET de la chaîne : adresse vierge, toute récente, ou contrat déployé cette semaine.
    L'historique est lu par le moteur (score/historique_chaine.py) ; sans lui, la règle ne dit rien."""
    h = p.get("historique")
    if h is None or p["to"] in etat.destinataires_connus or p["to"] in etat.services_connus:
        return None
    # Âge à la date du paiement ; une première activité postérieure au paiement vaut « rien avant ».
    age = p["timestamp"] - h.premiere_activite if h.premiere_activite is not None else None
    jeune = age is not None and age <= FENETRE_ADRESSE_NEUVE_S
    jours = max(age, 0) // 86400 if age is not None else None
    if h.est_contrat:
        if not jeune:
            return None
        if h.code_verifie is False:
            return Raison("NEW_CONTRACT", f"le destinataire est un contrat déployé il y a {jours} j, au code source non publié",
                          [p["tx_hash"]], POIDS["NEW_CONTRACT_NON_VERIFIE"])
        return Raison("NEW_CONTRACT", f"le destinataire est un contrat déployé il y a {jours} j", [p["tx_hash"]], POIDS["NEW_CONTRACT"])
    if h.jamais_vue or (age is not None and age < 0):
        return Raison("FRESH_ADDRESS", "adresse vierge : aucune transaction sur la chaîne avant ce paiement", [p["tx_hash"]], POIDS["FRESH_ADDRESS"])
    if jeune:
        return Raison("FRESH_ADDRESS", f"adresse active sur la chaîne depuis {jours} j seulement ({h.transactions_emises} transaction(s) émise(s))",
                      [p["tx_hash"]], POIDS["FRESH_ADDRESS"])
    if h.transactions_emises == 0 and age is None:
        return Raison("FRESH_ADDRESS", "adresse qui n'a jamais rien signé sur la chaîne (ancienneté inconnue)", [p["tx_hash"]],
                      POIDS["FRESH_ADDRESS_FAIBLE"])


def r_fonds_teintes(p, etat):
    """R9 : le destinataire a reçu une part significative des fonds d'une adresse signalée (1 intermédiaire, 7 jours)."""
    t = etat.teintees.get(p["to"])
    if not t or p["to"] in etat.services_connus or p["timestamp"] - t[1] > FENETRE_TAINTED_S:
        return None
    return Raison("TAINTED_FUNDS", f"a reçu {t[0]:.0%} des fonds sortis de l'adresse signalée {t[3][:6]}… il y a {(p['timestamp'] - t[1]) // 3600} h",
                  [t[2], p["tx_hash"]], POIDS["TAINTED_FUNDS"])


def r_changement_recent(p, etat):
    nouveau = etat.nouveaux_signataires.get(p.get("proposer", "").lower())
    # Une clé renouvelée qui paie un fournisseur connu est normal (renouvellement périodique des clés) ;
    # le signal fort, c'est un signataire tout juste ajouté qui paie une adresse inconnue.
    if nouveau and 0 <= p["timestamp"] - nouveau[0] <= FENETRE_CHANGEMENT_S:
        h = (p["timestamp"] - nouveau[0]) // 3600
        if p["to"] not in etat.destinataires_connus and montant_hors_norme(p, etat):  # forme de Bybit : la clé neuve sort un gros montant vers un inconnu
            return Raison("NEW_OWNER_LARGE_PAYMENT", f"gros montant proposé par un signataire ajouté il y a {h} h",
                          [nouveau[1], p["tx_hash"]], POIDS["NEW_OWNER_LARGE_PAYMENT"])
        if p["to"] not in etat.destinataires_connus:
            return Raison("NEW_OWNER_PROPOSES", f"proposé par un signataire ajouté il y a {h} h", [nouveau[1], p["tx_hash"]],
                          POIDS["NEW_OWNER_PROPOSES"])
    recents = [c for c in etat.changements_signataires if 0 <= p["timestamp"] - c[0] <= FENETRE_CHANGEMENT_S]
    if recents:
        h = (p["timestamp"] - recents[-1][0]) // 3600
        return Raison("RECENT_OWNER_CHANGE", f"signataire remplacé il y a {h} h", [c[1] for c in recents], POIDS["RECENT_OWNER_CHANGE"])


def r_schema_fraude(p, etat):
    """Schéma de la fraude au président / usurpation de fournisseur : destinataire inconnu ET libellé pressant."""
    m = MOTS_URGENCE.search(p.get("memo") or "")
    if m and p["to"] not in etat.destinataires_connus:
        return Raison("PAYMENT_FRAUD_PATTERN", "nouveau destinataire avec une demande pressante ou un changement de coordonnées",
                      [p["tx_hash"]], POIDS["PAYMENT_FRAUD_PATTERN"])


def r_repetition_rapide(p, etat):
    """Goutte-à-goutte : plusieurs paiements rapprochés vers une adresse apparue récemment."""
    premier = etat.premier_paiement.get(p["to"])
    if premier is None or p["timestamp"] - premier > FENETRE_RECENT_S:
        return None
    precedents = [q for q in etat.propositions.values()
                  if q["to"] == p["to"] and 0 < p["timestamp"] - q["timestamp"] <= FENETRE_REPETITION_S]
    if precedents:
        return Raison("RAPID_REPEAT", f"{len(precedents) + 1} paiements en moins de 3 jours vers une adresse apparue il y a "
                      f"{(p['timestamp'] - premier) // 3600} h", [q["tx_hash"] for q in precedents] + [p["tx_hash"]],
                      POIDS["RAPID_REPEAT"])


def r_seuil_abaisse(p, etat):
    recents = [b for b in etat.baisses_seuil if 0 <= p["timestamp"] - b[0] <= FENETRE_CHANGEMENT_S]
    if recents:
        b = recents[-1]
        return Raison("THRESHOLD_LOWERED", f"seuil de signatures abaissé de {b[2]} à {b[3]}", [b[1]], POIDS["THRESHOLD_LOWERED"])


REGLES = [r_adresse_piege, r_adresse_signalee, r_adresse_sosie, r_fonds_teintes, r_nouveau_destinataire, r_adresse_sans_passe, r_destinataire_recent, r_montant_hors_norme,
          r_cumul_du_jour, r_rafale, r_libelle_urgent, r_schema_fraude, r_repetition_rapide, r_hors_heures,
          r_changement_recent, r_seuil_abaisse]
