"""Mesure l'oracle sur le corpus synthétique (R8b) : précision, rappel, pièges déjoués.

Usage : python -m eval.evaluer_oracle --corpus oracle/corpus --jeu test [--sans-llm] [--parallele 4]
"""
import argparse
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import oracle.oracle as O


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", type=Path, default=Path("oracle/corpus"))
    p.add_argument("--jeu", default="test", choices=["dev", "test"])
    p.add_argument("--sans-llm", action="store_true")
    p.add_argument("--parallele", type=int, default=4)
    a = p.parse_args()
    verite = [json.loads(l) for l in open(a.corpus / "verite.jsonl") if l.strip()]
    verite = [v for v in verite if v["jeu"] == a.jeu]
    pages = sorted({v["page"] for v in verite})

    def run(pg):
        acc, _ = O.traiter_page(pg, a.sans_llm)
        return pg, {x["address"] for x in acc}

    with ThreadPoolExecutor(a.parallele) as ex:
        signalees = dict(ex.map(run, pages))

    vp = fp = fn = vn = 0
    par_type = defaultdict(Counter)
    erreurs = []
    for v in verite:
        signale = v["address"] in signalees[v["page"]]
        doit = v["expected"] == "accepted"
        vp += signale and doit; fn += doit and not signale; fp += signale and not doit; vn += (not signale) and not doit
        par_type[v["type"]]["juste" if signale == doit else "faux"] += 1
        if signale != doit:
            erreurs.append(f"{v['type']:<18} {'signalée à tort' if signale else 'ratée'}  {Path(v['page']).name}")
    print(f"Jeu {a.jeu} : {len(pages)} pages, {len(verite)} adresses — moteur : {'mots-clés' if a.sans_llm else getattr(O.analyser_bedrock, 'modele', 'Bedrock')}")
    for t, c in sorted(par_type.items()):
        print(f"  {t:<18} juste {c['juste']:>3}/{c['juste'] + c['faux']}")
    prec = vp / (vp + fp) if vp + fp else 1.0
    rap = vp / (vp + fn) if vp + fn else 1.0
    print(f"\n  PRÉCISION {prec:.0%} (adresses signalées qui devaient l'être) · RAPPEL {rap:.0%} (accusations trouvées)"
          f" · fausses accusations {fp}/{fp + vn}")
    for e in erreurs:
        print("   ✗", e)


if __name__ == "__main__":
    main()
