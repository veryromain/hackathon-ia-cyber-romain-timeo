"""Notification des signataires à chaque mise en attente (P5, version minimale décidée en B1 §4).

Canaux, tous facultatifs et cumulables, configurés par variables d'environnement (.env à la racine, jamais dans Git) :
- macOS : bannière de notification (osascript) — le canal de la démo, aucun réglage ;
- e-mail : SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASSWORD, NOTIF_EMAIL_TO (séparés par des virgules) ;
- Telegram : TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.
Chaque notification est aussi journalisée dans shared/notifications.jsonl (preuve pour le rapport).
Une panne d'un canal n'arrête jamais le moteur.
"""
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

from .regles import fmt

RACINE = Path(__file__).resolve().parents[2]


def message(alerte: dict, paiement: dict) -> tuple[str, str]:
    niveau = "MISE EN ATTENTE" if alerte["level"] == "hold" else "signature en plus"
    titre = f"Breaker — {niveau} : paiement n° {alerte['payment_id']}"
    corps = (f"{fmt(int(paiement['amount']))} vers {paiement['to'][:6]}…{paiement['to'][-4:]} — « {paiement.get('memo') or ''} »\n"
             f"{alerte.get('explanation', '')}")
    return titre, corps


def _macos(titre, corps):
    if platform.system() != "Darwin":
        return False
    court = corps.split("\n")[0][:180].replace('"', "'")
    subprocess.run(["osascript", "-e", f'display notification "{court}" with title "{titre}" sound name "Submarine"'],
                   check=True, capture_output=True, timeout=5)
    return True


def _email(titre, corps):
    hote, dest = os.getenv("SMTP_HOST"), os.getenv("NOTIF_EMAIL_TO")
    if not hote or not dest:
        return False
    import smtplib
    from email.message import EmailMessage
    m = EmailMessage()
    m["Subject"], m["From"], m["To"] = titre, os.getenv("SMTP_USER", "breaker@localhost"), dest
    m.set_content(corps + "\n\nTableau de bord : http://localhost:8599")
    with smtplib.SMTP(hote, int(os.getenv("SMTP_PORT", "587")), timeout=10) as s:
        s.starttls()
        if os.getenv("SMTP_USER"):
            s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD", ""))
        s.send_message(m)
    return True


def _telegram(titre, corps):
    jeton, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not jeton or not chat:
        return False
    import httpx
    httpx.post(f"https://api.telegram.org/bot{jeton}/sendMessage", timeout=10,
               json={"chat_id": chat, "text": f"🛡️ {titre}\n{corps}"}).raise_for_status()
    return True


CANAUX = {"macos": _macos, "email": _email, "telegram": _telegram}


def notifier(alerte: dict, paiement: dict, journal: Path | None = None, seulement_hold=True) -> list[str]:
    """Envoie sur chaque canal disponible ; renvoie la liste des canaux qui ont réussi."""
    if seulement_hold and alerte["level"] != "hold":
        return []
    titre, corps = message(alerte, paiement)
    reussis, erreurs = [], {}
    for nom, f in CANAUX.items():
        try:
            if f(titre, corps):
                reussis.append(nom)
        except Exception as err:  # un canal en panne ne doit pas bloquer les autres ni le moteur
            erreurs[nom] = str(err)[:120]
    if journal:
        with open(journal, "a", encoding="utf-8") as fj:
            fj.write(json.dumps({"payment_id": alerte["payment_id"], "level": alerte["level"], "at": int(time.time()),
                                 "canaux": reussis, "erreurs": erreurs, "titre": titre}, ensure_ascii=False) + "\n")
    if erreurs:
        print(f"notification : canaux en erreur {erreurs}", file=sys.stderr)
    return reussis
