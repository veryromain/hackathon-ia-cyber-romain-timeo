"""Évalue le moteur sur les jeux de Timéo (shared/donnees) : train puis test, à la suite (une seule histoire).

Usage : python -m eval.evaluer_donnees [--dossier ../shared/donnees]
Seul ce script lit les étiquettes. « Arrêtée » = hold ; « freinée » = step_up.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from score.moteur import Moteur

U = 10**18


def lire(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def evaluer(dossier: Path, verbeux=True):
    m = Moteur(json.loads((dossier / "carnet.json").read_text()))
    niveaux, montants, raisons = {}, {}, {}
    for f in ("train.events.jsonl", "test.events.jsonl"):
        for ev in lire(dossier / f):
            if ev["type"] == "payment_proposed":
                montants[ev["data"]["payment_id"]] = int(ev["data"]["amount"])
            a = m.traiter(ev)
            if a:
                niveaux[a["payment_id"]] = a["level"]
                raisons[a["payment_id"]] = [r["code"] for r in a["reasons"]]
    res = {}
    for jeu in ("train", "test"):
        par = defaultdict(lambda: {"n": 0, "hold": 0, "step_up": 0, "mt": 0, "mt_hold": 0, "mt_frein": 0})
        for lab in lire(dossier / f"{jeu}.labels.jsonl"):
            s = par[(lab["label"], lab["scenario"])]
            pid, niv = lab["payment_id"], niveaux.get(lab["payment_id"])
            s["n"] += 1
            s["mt"] += montants[pid]
            if niv:
                s[niv] += 1
                s["mt_frein"] += montants[pid]
                if niv == "hold":
                    s["mt_hold"] += montants[pid]
        res[jeu] = par
        if verbeux:
            print(f"\n=== {jeu.upper()} ===")
            for (label, scen), s in sorted(par.items()):
                print(f"  {label:<6} {scen:<24} n={s['n']:>4}  hold {s['hold'] / s['n']:>5.0%}  step_up {s['step_up'] / s['n']:>5.0%}"
                      f"  rien {(s['n'] - s['hold'] - s['step_up']) / s['n']:>5.0%}")
    t = res["test"]
    fr = [s for (l, _), s in t.items() if l == "fraud"]
    no = [s for (l, _), s in list(t.items()) + list(res["train"].items()) if l == "normal"]
    tot = lambda L, k: sum(s[k] for s in L)
    synth = {
        "fraudes_arretees": tot(fr, "hold") / tot(fr, "n"),
        "fraudes_freinees_ou_arretees": (tot(fr, "hold") + tot(fr, "step_up")) / tot(fr, "n"),
        "montant_fraude": tot(fr, "mt") / U, "montant_hold": tot(fr, "mt_hold") / U, "montant_frein": tot(fr, "mt_frein") / U,
        "faux_hold": tot(no, "hold") / tot(no, "n"), "step_up_normaux": tot(no, "step_up") / tot(no, "n"), "n_normaux": tot(no, "n"),
    }
    if verbeux:
        print(f"\n  FRAUDES (test)   arrêtées {synth['fraudes_arretees']:.0%} · freinées ou arrêtées {synth['fraudes_freinees_ou_arretees']:.0%}"
              f"  (n={tot(fr, 'n')})")
        print(f"  MONTANTS         {synth['montant_hold']:,.0f} mUSD mis en attente sur {synth['montant_fraude']:,.0f} proposés "
              f"({synth['montant_hold'] / synth['montant_fraude']:.0%}) ; freinés ou en attente : {synth['montant_frein'] / synth['montant_fraude']:.0%}")
        print(f"  NORMAUX (train+test)  mis en attente à tort {synth['faux_hold']:.1%} · signature en plus {synth['step_up_normaux']:.1%}"
              f"  (n={synth['n_normaux']})")
    return synth, niveaux, raisons


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--dossier", type=Path, default=Path(__file__).resolve().parents[2] / "shared" / "donnees")
    evaluer(a.parse_args().dossier)
