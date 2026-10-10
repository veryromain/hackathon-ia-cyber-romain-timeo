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


@st.fragment(run_every=2)
def tableau():
    events = lire(DOSSIER / "events.jsonl")
    alertes = {a["payment_id"]: a for a in lire(DOSSIER / "alerts.jsonl")}
    flags = [f for f in lire(DOSSIER / "flags.jsonl") if not f.get("remove")]
    pay, gel = etat_paiements(events)

    st.title("🛡️ Breaker — garde antifraude de la trésorerie")
    st.caption(f"Source : `{DOSSIER}` · mis à jour à {datetime.now():%H:%M:%S} · "
               "l'outil ne détient aucun fonds : il ajoute des signatures ou un délai, **les signataires décident**.")
    if gel:
        st.error("🧊 Portefeuille GELÉ par un signataire : aucun paiement ne peut partir.")

    risques = [pid for pid in pay if pid in alertes]
    protege = sum(int(pay[p]["amount"]) for p in risques if pay[p]["état"] != "💸 exécuté")
    c = st.columns(5)
    c[0].metric("Paiements proposés", len(pay))
    c[1].metric("🛑 Mis en attente", sum(1 for a in alertes.values() if a["level"] == "hold"))
    c[2].metric("✋ Signature en plus", sum(1 for a in alertes.values() if a["level"] == "step_up"))
    c[3].metric("Montant protégé", mutd(protege))
    c[4].metric("Adresses signalées (Web)", len({f["address"] for f in flags}))

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

    with st.expander("Journal de la chaîne (derniers événements)"):
        if events:
            df = pd.DataFrame([{"heure": heure(e["timestamp"]), "type": e["type"],
                                "paiement": e.get("data", {}).get("payment_id", ""),
                                "par": court(e.get("tx_from", "")), "tx": e["tx_hash"][:12] + "…"} for e in events[-40:][::-1]])
            st.dataframe(df, hide_index=True, use_container_width=True)


tableau()
