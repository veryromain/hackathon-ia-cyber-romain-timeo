"""Prépare un dossier de démo hors chaîne pour le tableau de bord : exemple de Timéo + moteur + oracle.

    python -m dashboard.preparer_demo [--sans-llm]
    streamlit run dashboard/app.py -- --dossier dashboard/demo
"""
import argparse
import json
import shutil
from pathlib import Path

from oracle.oracle import traiter_page
from score.moteur import Moteur

ICI = Path(__file__).resolve().parent
ECH = ICI.parents[1] / "shared" / "echantillons"


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--sans-llm", action="store_true")
    args = a.parse_args()
    demo = ICI / "demo"
    demo.mkdir(exist_ok=True)
    shutil.copy(ECH / "events.exemple.jsonl", demo / "events.jsonl")
    m = Moteur(json.loads((ICI.parent / "config" / "carnet.exemple.json").read_text()))
    with open(demo / "alerts.jsonl", "w") as f:
        for l in (ECH / "events.exemple.jsonl").read_text().splitlines():
            al = m.traiter(json.loads(l))
            if al:
                f.write(json.dumps(al, ensure_ascii=False) + "\n")
    acc, _ = traiter_page(str(ICI.parent / "oracle" / "corpus_demo" / "01-forum-arnaque.html"), args.sans_llm)
    (demo / "flags.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in acc))
    print(f"démo prête dans {demo} : streamlit run dashboard/app.py -- --dossier {demo}")


if __name__ == "__main__":
    main()
