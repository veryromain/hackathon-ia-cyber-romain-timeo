"""Banc d'essai du moteur de score : plusieurs graines, résultats par scénario.

Usage : python -m eval.banc --graines 1-20 [--echelle 1.0] [--jours 60]
Fraude « arrêtée » = hold. Fraude « freinée » = step_up (une signature de plus).
"""
import argparse
import json
import tempfile
import time
from collections import defaultdict
from pathlib import Path

from eval.generateur import Gen
from score.moteur import Moteur


def evaluer(graines, jours=60, echelle=1.0, verbeux=True):
    par_scen = defaultdict(lambda: {"n": 0, "hold": 0, "step_up": 0})
    n_ev, duree = 0, 0.0
    for g in graines:
        gen = Gen(g, jours, echelle)
        gen.normal()
        gen.fraudes()
        with tempfile.TemporaryDirectory() as d:
            gen.ecrire(Path(d))
            events = [json.loads(l) for l in open(Path(d) / "events.jsonl")]
            labels = {json.loads(l)["payment_id"]: json.loads(l) for l in open(Path(d) / "labels.jsonl")}
            carnet = json.loads((Path(d) / "carnet.json").read_text())
        m = Moteur(carnet)
        t0 = time.perf_counter()
        niveaux = {}
        for ev in events:
            a = m.traiter(ev)
            if a:
                niveaux[a["payment_id"]] = a["level"]
        duree += time.perf_counter() - t0
        n_ev += len(events)
        for pid, lab in labels.items():
            s = par_scen[(lab["label"], lab["scenario"])]
            s["n"] += 1
            niv = niveaux.get(pid)
            if niv:
                s[niv] += 1

    tot = {k: {"n": 0, "hold": 0, "step_up": 0} for k in ("fraud", "normal")}
    lignes = []
    for (label, scen), s in sorted(par_scen.items()):
        for k in ("n", "hold", "step_up"):
            tot[label][k] += s[k]
        lignes.append(f"  {label:<6} {scen:<26} n={s['n']:>4}   hold {s['hold'] / s['n']:>5.0%}   "
                      f"step_up {s['step_up'] / s['n']:>5.0%}   rien {(s['n'] - s['hold'] - s['step_up']) / s['n']:>5.0%}")
    f, n = tot["fraud"], tot["normal"]
    res = {
        "fraudes_arretees": f["hold"] / f["n"],
        "fraudes_freinees_ou_arretees": (f["hold"] + f["step_up"]) / f["n"],
        "faux_positifs_hold": n["hold"] / n["n"],
        "friction_normale_step_up": n["step_up"] / n["n"],
        "evenements_par_s": n_ev / duree if duree else 0,
    }
    if verbeux:
        print("\n".join(lignes))
        print(f"\n  FRAUDES  arrêtées (hold) {res['fraudes_arretees']:.0%} · freinées ou arrêtées "
              f"{res['fraudes_freinees_ou_arretees']:.0%}   (n={f['n']})")
        print(f"  NORMAUX  mis en attente à tort {res['faux_positifs_hold']:.1%} · signature en plus "
              f"{res['friction_normale_step_up']:.1%}   (n={n['n']})")
        print(f"  VITESSE  {res['evenements_par_s']:,.0f} événements/s")
    return res


def plage(txt):
    a, b = txt.split("-")
    return range(int(a), int(b) + 1)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--graines", default="1-20", type=plage)
    p.add_argument("--jours", type=int, default=60)
    p.add_argument("--echelle", type=float, default=1.0)
    a = p.parse_args()
    evaluer(a.graines, a.jours, a.echelle)
