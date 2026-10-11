"""Tableau de bord des signataires (R5) — Streamlit.

Lit les fichiers vivants du relais (events.jsonl, alerts.jsonl, flags.jsonl) et se rafraîchit tout seul.
    streamlit run dashboard/app.py                          # dossier ../shared (démo en direct avec le relais)
    streamlit run dashboard/app.py -- --dossier dashboard/demo   # démo hors chaîne (python -m dashboard.preparer_demo)
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import time
import uuid

U = 10**18
ICI = Path(__file__).resolve().parent
EXPLORATEUR = {43113: "https://testnet.snowtrace.io/tx/"}
NIVEAUX = {"hold": ("🛑 Mise en attente", "#c62828"), "step_up": ("✋ Signature en plus", "#ef6c00")}


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--dossier", type=Path, default=Path(os.getenv("BREAKER_DOSSIER", ICI.parents[1] / "shared")))
    return p.parse_known_args(sys.argv[1:])[0]


def lire(f: Path):
    if not f.exists():
        return []
    out = []
    for l in f.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:
            pass
    return out


def court(adr):
    return f"{adr[:6]}…{adr[-4:]}" if adr else "?"


def mutd(x):
    return f"{int(x) / U:,.0f}".replace(",", " ") + " mUSD"


def heure(ts):
    return datetime.fromtimestamp(ts).strftime("%d/%m %H:%M:%S")


def lien_tx(h, chain):
    base = EXPLORATEUR.get(chain)
    return f"[{h[:10]}…]({base}{h})" if base else f"`{h[:10]}…`"


def deploiement(dossier: Path):
    """Signataires du déploiement (ia-2/deployments/<réseau>.json) : pour choisir « je suis… » dans la démo."""
    candidats = [Path(os.environ["BREAKER_DEPLOIEMENT"])] if os.getenv("BREAKER_DEPLOIEMENT") else \
        [dossier.parents[0] / "ia-2" / "deployments" / n for n in ("localhost.json", "fuji.json")]
    for f in candidats:
        if f.exists():
            try:
                d = json.loads(f.read_text())
                return {f"Signataire {i + 1} ({court(o)})": o for i, o in enumerate(d.get("owners", []))}
            except (OSError, json.JSONDecodeError):
                pass
    return {}


def ecrire_action(dossier: Path, **a):
    a = {"id": f"act-{datetime.utcnow():%Y-%m-%dT%H:%M:%SZ}-{uuid.uuid4().hex[:4]}", "created_at": int(time.time()), **a}
    with open(dossier / "actions.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(a, ensure_ascii=False) + "\n")
    return a["id"]


def contester(dossier: Path, adresse: str):
    with open(dossier / "flags.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"address": adresse, "remove": True}) + "\n")


def retours(dossier: Path):
    """Jugement des signataires sur chaque alerte (vraie / fausse) : la matière du rapport mensuel et de la précision mesurée."""
    return {r["payment_id"]: r for r in lire(dossier / "retours.jsonl")}


def juger(dossier: Path, payment_id, verdict, by):
    with open(dossier / "retours.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"payment_id": payment_id, "verdict": verdict, "by": by, "at": int(time.time())}) + "\n")


def signaler_pour_tous(dossier: Path, p: dict, pid, by):
    """Immunité collective : une fraude annulée chez un client devient un signalement, avec la transaction annulée pour preuve."""
    import hashlib
    quote = f"Paiement n° {pid} de {mutd(p['amount'])} vers cette adresse annulé par un signataire après alerte du garde (tx {p['tx']})."
    source = f"client-verifie://{court(by)}/paiement/{pid}"
    f = {"address": p["to"].lower(), "level": "hold", "category": "scam_report", "confidence": 0.9, "sources_count": 1,
         "source_url": source, "quote": quote, "evidence_hash": "0x" + hashlib.sha256(f"{source}\n{quote}".encode()).hexdigest(),
         "expires_at": int(time.time()) + 30 * 86400}
    with open(dossier / "flags.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(f, ensure_ascii=False) + "\n")


def etats_actions(dossier: Path):
    res = {r["id"]: r for r in lire(dossier / "actions-resultats.jsonl")}
    return [(a, res.get(a["id"])) for a in lire(dossier / "actions.jsonl")]


def etat_paiements(events):
    pay, gel = {}, False
    for e in events:
        d, t = e.get("data", {}), e["type"]
        pid = d.get("payment_id")
        if t == "payment_proposed":
            pay[pid] = {**d, "proposé": e["timestamp"], "état": "en cours", "tx": e["tx_hash"], "chain": e.get("chain_id")}
        elif pid in pay and t == "payment_executed":
            pay[pid]["état"] = "💸 exécuté"
        elif pid in pay and t == "payment_cancelled":
            pay[pid]["état"] = "✅ annulé"
        elif pid in pay and t == "risk_flagged":
            pay[pid]["sur la chaîne"] = d.get("level")
        elif t == "wallet_frozen":
            gel = True
        elif t == "wallet_unfrozen":
            gel = False
    return pay, gel


st.set_page_config(page_title="Breaker — garde de trésorerie", page_icon="🛡️", layout="wide")
DOSSIER = args().dossier
SIGNATAIRES = deploiement(DOSSIER)
with st.sidebar:
    st.header("Je suis…")
    MOI = st.selectbox("Signataire", list(SIGNATAIRES) or ["(aucun déploiement trouvé)"], label_visibility="collapsed")
    MOI_ADR = SIGNATAIRES.get(MOI)
    st.caption("Démo : les clics écrivent dans `shared/actions.jsonl`, un exécuteur signe avec la clé de test du signataire. "
               "En production, vous signeriez avec votre propre portefeuille.")
    st.divider()
    if MOI_ADR:
        motif = st.text_input("Motif", "Alerte du garde, vérification en cours")
        c1, c2 = st.columns(2)
        if c1.button("🧊 Geler", use_container_width=True):
            ecrire_action(DOSSIER, action="freeze", by=MOI_ADR, reason=motif)
            st.toast("Gel demandé")
        if c2.button("🔓 Dégeler", use_container_width=True):
            ecrire_action(DOSSIER, action="unfreeze", by=MOI_ADR)
            st.toast("Dégel approuvé par vous")


@st.fragment(run_every=2)
def tableau():
    events = lire(DOSSIER / "events.jsonl")
    alertes = {a["payment_id"]: a for a in lire(DOSSIER / "alerts.jsonl")}
    toutes = lire(DOSSIER / "flags.jsonl")
    retirees = {f["address"] for f in toutes if f.get("remove")}
    flags = [f for f in toutes if not f.get("remove") and f["address"] not in retirees]
    pay, gel = etat_paiements(events)

    st.title("🛡️ Breaker — garde antifraude de la trésorerie")
    st.caption(f"Source : `{DOSSIER}` · mis à jour à {datetime.now():%H:%M:%S} · "
               "**Breaker n'est pas un coffre** : il se greffe sur votre multisig (ici, un coffre de démonstration qui tient lieu de votre Safe) "
               "et ne détient aucun fonds : il ajoute des signatures ou un délai, **les signataires décident**.")
    if gel:
        st.error("🧊 Portefeuille GELÉ par un signataire : aucun paiement ne peut partir.")

    risques = [pid for pid in pay if pid in alertes]
    protege = sum(int(pay[p]["amount"]) for p in risques if pay[p]["état"] != "💸 exécuté")
    juges = retours(DOSSIER)
    vraies = sum(1 for r in juges.values() if r["verdict"] == "vraie")
    fausses = sum(1 for r in juges.values() if r["verdict"] == "fausse")
    c = st.columns(6)
    c[0].metric("Paiements proposés", len(pay))
    c[1].metric("🛑 Mis en attente", sum(1 for a in alertes.values() if a["level"] == "hold"))
    c[2].metric("✋ Signature en plus", sum(1 for a in alertes.values() if a["level"] == "step_up"))
    c[3].metric("Montant protégé", mutd(protege))
    c[4].metric("Adresses signalées (Web)", len({f["address"] for f in flags}))
    c[5].metric("Précision jugée", f"{vraies / (vraies + fausses):.0%}" if vraies + fausses else "—",
                help=f"{vraies} alerte(s) jugée(s) vraie(s), {fausses} fausse(s), par les signataires. C'est la mesure chez le client (rapport mensuel).")

    gauche, droite = st.columns([3, 2])
    with gauche:
        st.subheader("Paiements à examiner")
        if not risques:
            st.info("Aucun paiement suspect pour l'instant.")
        for pid in sorted(risques, key=lambda p: -pay[p]["proposé"]):
            a, p = alertes[pid], pay[pid]
            titre, couleur = NIVEAUX.get(a["level"], (a["level"], "#555"))
            with st.container(border=True):
                st.markdown(f"<span style='color:{couleur};font-weight:700'>{titre}</span> · score **{a['score']:.2f}** · "
                            f"paiement n° {pid} · {p['état']}", unsafe_allow_html=True)
                st.markdown(f"**{mutd(p['amount'])}** vers `{court(p['to'])}` — « {p.get('memo', '')} » "
                            f"· proposé le {heure(p['proposé'])} par `{court(p.get('proposer'))}`")
                st.write(a.get("explanation", ""))
                for r in a["reasons"]:
                    preuves = " ".join(lien_tx(h, p["chain"]) for h in r.get("evidence", [])[:3])
                    st.markdown(f"- `{r['code']}` — {r['detail']} {preuves}")
                j = juges.get(pid)
                if j:
                    st.caption(f"Jugée **{'✔ vraie' if j['verdict'] == 'vraie' else '✖ fausse'} alerte** par `{court(j['by'])}` le {heure(j['at'])}")
                elif MOI_ADR:
                    v1, v2, _ = st.columns([1, 1, 3])
                    if v1.button("👍 Vraie alerte", key=f"v{pid}", use_container_width=True):
                        juger(DOSSIER, pid, "vraie", MOI_ADR)
                        st.toast("Merci : alerte jugée vraie")
                    if v2.button("👎 Fausse alerte", key=f"f{pid}", use_container_width=True):
                        juger(DOSSIER, pid, "fausse", MOI_ADR)
                        st.toast("Merci : alerte jugée fausse (le réglage s'affinera)")
                if MOI_ADR and p["état"] == "✅ annulé" and p["to"].lower() not in {f["address"] for f in flags}:
                    if st.button("📣 Signaler cette adresse pour tous les clients", key=f"sig{pid}",
                                 help="Immunité collective : la transaction annulée sert de preuve ; le signalement reste contestable et expire dans 30 jours"):
                        signaler_pour_tous(DOSSIER, p, pid, MOI_ADR)
                        st.toast("Adresse signalée au registre, avec la transaction annulée pour preuve")
                if MOI_ADR and p["état"] == "en cours":
                    # Idée 3 : « ce que vous signez vraiment » — la transaction décodée, et le signataire retape la fin de l'adresse.
                    st.markdown(f"<div style='font-family:monospace;font-size:12.5px;opacity:.85'>Vous signeriez : <b>wallet.approve({pid})</b> → "
                                f"à l'exécution, transfert de <b>{mutd(p['amount'])}</b> vers <b>{p['to']}</b></div>", unsafe_allow_html=True)
                    saisie = st.text_input("Pour signer, retapez les 4 derniers caractères du destinataire", key=f"chk{pid}", max_chars=4,
                                           placeholder="ex. " + p["to"][-4:][:2] + "··", help="Contre la signature en aveugle (cas Bybit) et les adresses sosies")
                    ok_saisie = saisie.strip().lower() == p["to"][-4:].lower()
                    b1, b3, b2, _ = st.columns([1, 1, 1, 2])
                    if b1.button("✅ Valider (signer)", key=f"ok{pid}", use_container_width=True, disabled=not ok_saisie):
                        ecrire_action(DOSSIER, action="approve", payment_id=pid, by=MOI_ADR)
                        st.toast(f"Signature demandée pour le paiement {pid}")
                    if b3.button("▶️ Exécuter", key=f"ex{pid}", use_container_width=True, disabled=not ok_saisie, help="Une fois les signatures réunies et le délai écoulé"):
                        ecrire_action(DOSSIER, action="execute", payment_id=pid, by=MOI_ADR)
                        st.toast(f"Exécution demandée pour le paiement {pid}")
                    if b2.button("🛑 Annuler", key=f"no{pid}", use_container_width=True):
                        ecrire_action(DOSSIER, action="cancel", payment_id=pid, by=MOI_ADR, reason="Demande non confirmée par un autre canal")
                        st.toast(f"Annulation demandée pour le paiement {pid}")
    with droite:
        st.subheader("🌐 Signalées sur le Web (oracle)")
        if not flags:
            st.info("Aucune adresse signalée.")
        for f in flags[::-1]:
            with st.container(border=True):
                st.markdown(f"`{court(f['address'])}` · **{f['level']}** · {f.get('category', '')} · confiance {f.get('confidence', '?')}")
                st.markdown(f"> {f.get('quote', '')}")
                exp = datetime.fromtimestamp(f["expires_at"]).strftime("%d/%m/%Y") if f.get("expires_at") else "?"
                st.caption(f"Source : {f.get('source_url', '?')} · preuve `{f.get('evidence_hash', '')[:14]}…` · expire le {exp}")
                if st.button("⚖️ Contester ce signalement", key=f"ct{f['address']}"):
                    contester(DOSSIER, f["address"])
                    st.toast("Contestation envoyée : le signalement sera retiré du registre")

    actions = etats_actions(DOSSIER)
    if actions:
        with st.expander(f"Actions des signataires ({len(actions)})", expanded=True):
            for a, r in actions[::-1][:8]:
                etat = "⏳ en attente" if not r else ("✔ fait " + lien_tx(r["tx_hash"], 43113 if DOSSIER.name != "demo" else None)
                                                   if r["status"] == "done" else f"✖ {r.get('error', '')}")
                st.markdown(f"- `{a['action']}` {('paiement ' + str(a['payment_id'])) if a.get('payment_id') is not None else ''} "
                            f"par `{court(a.get('by', ''))}` — {etat}")

    with st.expander("Journal de la chaîne (derniers événements)"):
        if events:
            df = pd.DataFrame([{"heure": heure(e["timestamp"]), "type": e["type"],
                                "paiement": str(e.get("data", {}).get("payment_id", "")),
                                "par": court(e.get("tx_from", "")), "tx": e["tx_hash"][:12] + "…"} for e in events[-40:][::-1]])
            st.dataframe(df, hide_index=True, use_container_width=True)


tableau()
