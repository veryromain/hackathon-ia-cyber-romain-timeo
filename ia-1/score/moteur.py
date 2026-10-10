"""Moteur de score (R1) : lit events.jsonl, écrit alerts.jsonl.

Usage :
    python -m score.moteur --events ../shared/echantillons/events.exemple.jsonl --out alerts.jsonl \
        --carnet config/carnet.exemple.json
    python -m score.moteur --events ../shared/events.jsonl --out ../shared/alerts.jsonl --suivre   # en direct

Ne lit jamais labels.jsonl.
"""
import argparse
import json
import sys
import time
from pathlib import Path

from . import regles
from .regles import REGLES, EtatPortefeuille, Raison


class Moteur:
    def __init__(self, carnet=None, modele=None, expliquer=False, services=None, notifier=None):
        self.etat = EtatPortefeuille()
        self.modele = modele  # modèle d'anomalie (R2), facultatif
        self.expliquer = expliquer  # R3 : explication rédigée par Bedrock, avec repli sur le texte à trous
        self.niveaux = {}  # payment_id -> dernier niveau émis (un niveau ne peut que monter)
        self.notifier = notifier  # P5 : fonction(alerte, paiement) appelée à chaque mise en attente
        self.etat.sorties_signalees, self.etat.recus_de_signalee = {}, {}
        for a in services or []:
            self.etat.services_connus.add(a.lower())
        # Carnet d'adresses du client (fournisseurs et comptes déjà connus) : évite le démarrage à froid.
        for adresse in carnet or []:
            self.etat.destinataires_connus.add(adresse.lower())

    def traiter(self, ev: dict):
        """Met à jour l'état ; renvoie une alerte (dict) si l'événement est un paiement proposé jugé risqué."""
        t, d, e = ev["type"], ev.get("data", {}), self.etat
        if t == "payment_proposed":
            p = {**d, "to": d["to"].lower(), "proposer": d.get("proposer", ev.get("tx_from", "")).lower(),
                 "amount": int(d["amount"]),
                 "timestamp": ev["timestamp"], "tx_hash": ev["tx_hash"]}
            alerte = self.noter(p)
            e.propositions[p["payment_id"]] = p
            # Les règles ne regardent que les 3 derniers jours : on oublie le reste (mémoire et vitesse constantes).
            limite = p["timestamp"] - max(regles.FENETRE_REPETITION_S, regles.FENETRE_JOUR_S)
            for vieux in [k for k, q in e.propositions.items() if q["timestamp"] < limite]:
                del e.propositions[vieux]
            return alerte
        if t == "payment_approved":
            # Une clé de moins de 7 jours apporte sa signature à un paiement encore en cours : on re-note, le niveau ne peut que monter.
            nouveau = e.nouveaux_signataires.get((d.get("owner") or "").lower())
            p = e.propositions.get(pid := d.get("payment_id"))
            # Seulement si le paiement est DÉJÀ signalé (step_up) : une clé neuve ne doit pas pouvoir apporter la signature manquante.
            if (p and nouveau and 0 <= ev["timestamp"] - nouveau[0] <= regles.FENETRE_CHANGEMENT_S
                    and self.niveaux.get(pid) == "step_up" and p["to"] not in e.destinataires_connus):
                h = (ev["timestamp"] - nouveau[0]) // 3600
                extra = Raison("NEW_OWNER_APPROVES", f"signature apportée par un signataire ajouté il y a {h} h", [nouveau[1], ev["tx_hash"]],
                               regles.POIDS["NEW_OWNER_APPROVES"])
                alerte = self.noter(p, [extra])
                if alerte and alerte["level"] == "hold":
                    return alerte
            return None
        if t == "token_transfer":
            # R9 : sorties de fonds d'une adresse signalée → ses destinataires sont « teintés » à hauteur de leur part.
            src, dst = (d.get("from") or "").lower(), (d.get("to") or "").lower()
            if src in e.adresses_signalees:
                e.sorties_signalees[src] = e.sorties_signalees.get(src, 0) + int(d.get("amount", 0))  # toutes les sorties comptent
                if dst not in e.services_connus:  # ... mais une plateforme n'est jamais teintée
                    e.recus_de_signalee[(src, dst)] = e.recus_de_signalee.get((src, dst), 0) + int(d.get("amount", 0))
                # Les parts de TOUS les destinataires de cette adresse sont recalculées (une grosse sortie dilue les autres).
                for (s_, d_), recu in e.recus_de_signalee.items():
                    if s_ != src:
                        continue
                    part = recu / e.sorties_signalees[src]
                    if part >= regles.PART_TAINTED_MIN:
                        prev = e.teintees.get(d_)
                        e.teintees[d_] = (part, prev[1] if prev else ev["timestamp"], prev[2] if prev else ev["tx_hash"], src)
                    else:
                        e.teintees.pop(d_, None)
            return None
        if t == "payment_executed":
            to, montant = d["to"].lower(), int(d["amount"])
            if to not in e.destinataires_connus:  # les adresses du carnet ne sont jamais « récentes »
                e.premier_paiement.setdefault(to, ev["timestamp"])
            e.destinataires_connus.add(to)
            e.montants_payes.append(montant)
            e.montants_par_dest.setdefault(to, []).append(montant)
            e.recus_par_dest[to] = e.recus_par_dest.get(to, 0) + montant
        elif t == "address_flagged":
            e.adresses_signalees[d["flagged"].lower()] = {
                "level": d["level"], "expires_at": d["expires_at"],
                "category": d.get("category", "?"), "tx_hash": ev["tx_hash"]}
        elif t == "address_unflagged":
            e.adresses_signalees.pop(d["flagged"].lower(), None)
        elif t == "owner_replaced":
            e.changements_signataires.append((ev["timestamp"], ev["tx_hash"]))
            e.nouveaux_signataires[d["new_owner"].lower()] = (ev["timestamp"], ev["tx_hash"])
        elif t == "threshold_changed" and d["new_threshold"] < d["previous_threshold"]:
            e.baisses_seuil.append((ev["timestamp"], ev["tx_hash"], d["previous_threshold"], d["new_threshold"]))
        return None

    def noter(self, p: dict, extras=()):
        raisons: list[Raison] = [r for r in (regle(p, self.etat) for regle in REGLES) if r] + list(extras)
        if self.modele:
            r = self.modele.raison(p, self.etat)
            if r:
                raisons.append(r)
        reste = 1.0
        for r in raisons:
            reste *= 1 - r.poids
        score = round(1 - reste, 2)
        niveau = "hold" if score >= regles.SEUIL_HOLD else "step_up" if score >= regles.SEUIL_STEP_UP else None
        if not niveau:
            return None
        raisons.sort(key=lambda r: -r.poids)
        alerte = {
            "payment_id": p["payment_id"],
            "created_at": int(time.time()),
            "score": score,
            "level": niveau,
            "reasons": [{"code": r.code, "detail": r.detail, "evidence": r.preuves} for r in raisons],
            "explanation": explication(niveau, raisons),
        }
        if self.expliquer:
            from .explication import expliquer
            alerte["explanation"] = expliquer(alerte, p, alerte["explanation"])
        self.niveaux[p["payment_id"]] = niveau
        if self.notifier and niveau == "hold":
            try:
                self.notifier(alerte, p)
            except Exception as err:  # jamais bloquant
                print(f"notification impossible : {err!r}", file=sys.stderr)
        return alerte


def explication(niveau, raisons):
    """Texte à trous ; R3 le remplacera par une explication Bedrock, en gardant ce texte en secours."""
    faits = " ; ".join(r.detail for r in raisons)
    action = ("Mis en attente : vérifiez la demande par un autre canal (appel au demandeur) avant de signer."
              if niveau == "hold" else "Une signature supplémentaire est demandée.")
    return f"Paiement inhabituel : {faits}. {action}"


def charger_services(chemin: Path) -> list[str]:
    """shared/services-connus.json : liste d'adresses, ou {"services": [{"address": …}]}, ou {"adresses": […]}."""
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if isinstance(d, list):
        return [str(a).lower() for a in d]
    if "services" in d:
        return [str(x["address"] if isinstance(x, dict) else x).lower() for x in d["services"]]
    return [str(a).lower() for a in d.get("adresses", [])]


def lire(chemin: Path, suivre: bool):
    with open(chemin) as f:
        while True:
            ligne = f.readline()
            if ligne:
                if ligne.strip():
                    try:
                        yield json.loads(ligne)
                    except json.JSONDecodeError:
                        print(f"ligne ignorée (JSON invalide) : {ligne[:80]!r}", file=sys.stderr)
            elif suivre:
                time.sleep(0.5)
            else:
                return


def main(argv=None):
    a = argparse.ArgumentParser(description="Moteur de score Breaker (R1)")
    a.add_argument("--events", required=True, type=Path)
    a.add_argument("--out", required=True, type=Path)
    a.add_argument("--carnet", type=Path, help="JSON : liste des adresses déjà connues du client")
    a.add_argument("--suivre", action="store_true", help="continue de lire le fichier quand il grossit (mode direct)")
    a.add_argument("--modele", type=Path, help="modèle d'anomalie appris (R2), ex. modeles/anomalie.joblib")
    a.add_argument("--expliquer", action="store_true", help="R3 : explication rédigée par Bedrock (partage de connexion)")
    a.add_argument("--services", type=Path, help="R9 : JSON des adresses de services connus (plateformes, ponts), jamais teintées")
    a.add_argument("--client", type=Path, help="réglages du client (config/client.json) : heures et jours ouvrés")
    a.add_argument("--notifier", action="store_true", help="P5 : notification à chaque mise en attente (macOS, e-mail, Telegram selon .env)")
    args = a.parse_args(argv)

    carnet = json.loads(args.carnet.read_text()) if args.carnet else []
    modele = None
    if args.modele:
        import joblib
        modele = joblib.load(args.modele)
    services = charger_services(args.services) if args.services else []
    if args.client:
        regles.charger_reglages_client(args.client)
    notif = None
    if args.notifier:
        from dotenv import load_dotenv
        from .notifier import notifier as _n
        load_dotenv(Path(__file__).resolve().parents[2] / ".env")
        journal = args.out.with_name("notifications.jsonl")
        notif = lambda a, p: _n(a, p, journal)
    moteur = Moteur(carnet, modele, args.expliquer, services, notif)
    with open(args.out, "a" if args.suivre else "w") as sortie:
        for ev in lire(args.events, args.suivre):
            try:
                alerte = moteur.traiter(ev)
            except (KeyError, TypeError, ValueError) as err:  # un événement incomplet ne doit jamais arrêter le moteur
                print(f"événement ignoré (seq {ev.get('seq')}) : {err!r}", file=sys.stderr)
                continue
            if alerte:
                sortie.write(json.dumps(alerte, ensure_ascii=False) + "\n")
                sortie.flush()
                codes = ",".join(r["code"] for r in alerte["reasons"])
                print(f"paiement {alerte['payment_id']:>3} → {alerte['level']:<8} score {alerte['score']:.2f}  [{codes}]",
                      file=sys.stderr)


if __name__ == "__main__":
    main()
