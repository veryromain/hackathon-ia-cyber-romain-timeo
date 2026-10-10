"""Évalue le moteur de score de ia-1 sur le jeu de généralisation (shared/donnees/holdout.*).

Le moteur lit train, test puis holdout à la suite (une seule histoire) ; seules les étiquettes du
holdout sont comptées. Règles seules : le modèle d'anomalie R2 n'est pas chargé ici.

Usage, depuis ia-1 (pour que le moteur soit importable) :
    python ../ia-2/scripts/evaluer-holdout.py            # sous Windows : PYTHONUTF8=1 devant
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "ia-1"))
from score.moteur import Moteur  # noqa: E402

DONNEES = RACINE / "shared" / "donnees"
U = 10**18


def lire(nom):
    return [json.loads(ligne) for ligne in open(DONNEES / nom, encoding="utf-8") if ligne.strip()]


def main():
    moteur = Moteur(json.loads((DONNEES / "carnet.json").read_text(encoding="utf-8")), None)
    niveaux, raisons, montants, executes = {}, {}, {}, set()
    for fichier in ("train.events.jsonl", "test.events.jsonl", "holdout.events.jsonl"):
        for ev in lire(fichier):
            d = ev["data"]
            if ev["type"] == "payment_proposed":
                montants[d["payment_id"]] = int(d["amount"]) / U
            elif ev["type"] == "payment_executed":
                executes.add(d["payment_id"])
            alerte = moteur.traiter(ev)
            if alerte:
                niveaux[alerte["payment_id"]] = alerte["level"]
                raisons[alerte["payment_id"]] = [r["code"] for r in alerte["reasons"]]

    par = defaultdict(lambda: {"n": 0, "hold": 0, "step_up": 0, "mt": 0.0, "mt_hold": 0.0, "mt_base": 0.0, "raisons": defaultdict(int)})
    for lab in lire("holdout.labels.jsonl"):
        cle = (lab["label"], lab["scenario"] + ("/" + lab["stage"] if lab.get("stage") else ""))
        s, pid = par[cle], lab["payment_id"]
        niveau = niveaux.get(pid)
        s["n"] += 1
        s["mt"] += montants[pid]
        s["mt_base"] += montants[pid] if pid in executes else 0  # sorti sans aucune alerte du moniteur
        if niveau:
            s[niveau] += 1
            s["mt_hold"] += montants[pid] if niveau == "hold" else 0
            for code in raisons[pid]:
                s["raisons"][code] += 1

    print(f"{'':7}{'scénario':34}{'n':>4}{'hold':>6}{'step_up':>8}{'rien':>6}   proposé  sorti sans moniteur   raisons les plus fréquentes")
    tot = defaultdict(lambda: defaultdict(float))
    for (label, scenario), s in sorted(par.items()):
        rien = s["n"] - s["hold"] - s["step_up"]
        top = ", ".join(c for c, _ in sorted(s["raisons"].items(), key=lambda kv: -kv[1])[:3])
        print(f"{label:7}{scenario:34}{s['n']:>4}{s['hold']:>6}{s['step_up']:>8}{rien:>6}{s['mt']:>10,.0f}{s['mt_base']:>12,.0f}            {top}")
        for k in ("n", "hold", "step_up", "mt", "mt_hold", "mt_base"):
            tot[label][k] += s[k]
    f, n = tot["fraud"], tot["normal"]
    print()
    print(f"FRAUDES  (n={f['n']:.0f})  arrêtées (hold) {100 * f['hold'] / f['n']:.0f} %  ·  freinées ou arrêtées {100 * (f['hold'] + f['step_up']) / f['n']:.0f} %  ·  manquées {100 * (f['n'] - f['hold'] - f['step_up']) / f['n']:.0f} %")
    print(f"MONTANTS frauduleux : {f['mt']:,.0f} mUSD proposés, {f['mt_hold']:,.0f} mis en attente ({100 * f['mt_hold'] / f['mt']:.0f} %) ; sans moniteur, {f['mt_base']:,.0f} étaient sortis")
    print(f"NORMAUX  (n={n['n']:.0f})  mis en attente à tort {100 * n['hold'] / n['n']:.1f} %  ·  signature en plus {100 * n['step_up'] / n['n']:.1f} %")


if __name__ == "__main__":
    main()
