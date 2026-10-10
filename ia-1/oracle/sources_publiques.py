"""Sources publiques en lecture seule pour l'oracle (décision B1 §3) : listes d'adresses publiées POUR être réutilisées.

- OFAC (sanctions du Trésor américain) : adresses « Digital Currency Address - ETH » de la liste SDN, telles qu'extraites
  et publiées par le dépôt ouvert 0xB10C/ofac-sanctioned-digital-currency-addresses (format EVM = Avalanche C-Chain).
- ScamSniffer : base publique d'adresses de phishing (dépôt scamsniffer/scam-database).
On ne scrape rien, on ne juge rien : on charge, on cite la source, on date, on fait expirer (30 jours).

Sorties :
- shared/listes-publiques.jsonl : TOUTES les adresses (lues hors chaîne par le moteur, option --listes-publiques) ;
- shared/flags.jsonl (option --publier N) : N adresses par source inscrites au registre on-chain par le relais, pour la démo.

Usage : python -m oracle.sources_publiques [--publier 2] [--hors-ligne]
"""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
CACHE = Path(__file__).resolve().parent / "sources_cache"
ADRESSE = re.compile(r"0x[a-fA-F0-9]{40}")
DUREE_S = 30 * 86400
SOURCES = {
    "ofac": {
        "url": "https://raw.githubusercontent.com/0xB10C/ofac-sanctioned-digital-currency-addresses/lists/sanctioned_addresses_ETH.txt",
        "page": "https://home.treasury.gov/policy-issues/financial-sanctions/specially-designated-nationals-and-blocked-persons-list-sdn-human-readable-lists",
        "category": "sanctions", "confidence": 0.98, "level": "hold",
        "quote": "Adresse figurant sur la liste SDN de l'OFAC (sanctions), extraction publique du dépôt 0xB10C.",
    },
    "scamsniffer": {
        "url": "https://raw.githubusercontent.com/scamsniffer/scam-database/main/blacklist/address.json",
        "page": "https://github.com/scamsniffer/scam-database",
        "category": "phishing", "confidence": 0.9, "level": "hold",
        "quote": "Adresse figurant dans la base publique d'adresses de phishing de ScamSniffer.",
    },
}


def telecharger(nom: str, hors_ligne=False) -> str:
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{nom}.txt"
    if not hors_ligne:
        import httpx
        try:
            r = httpx.get(SOURCES[nom]["url"], timeout=30, follow_redirects=True)
            r.raise_for_status()
            f.write_text(r.text, encoding="utf-8")
        except Exception as err:
            print(f"{nom} : téléchargement impossible ({err!r}), cache utilisé si présent")
    return f.read_text(encoding="utf-8") if f.exists() else ""


def adresses_de(texte: str) -> list[str]:
    return sorted({a.lower() for a in ADRESSE.findall(texte)})


def entree(nom: str, adr: str, maintenant: int) -> dict:
    s = SOURCES[nom]
    preuve = "0x" + hashlib.sha256(f"{s['url']}\n{s['quote']}\n{adr}".encode()).hexdigest()
    return {"address": adr, "level": s["level"], "category": s["category"], "confidence": s["confidence"], "sources_count": 1,
            "source_url": s["url"], "source": nom, "quote": s["quote"], "evidence_hash": preuve,
            "retrieved_at": maintenant, "expires_at": maintenant + DUREE_S}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--publier", type=int, default=0, help="N adresses par source à écrire dans shared/flags.jsonl (registre on-chain)")
    a.add_argument("--hors-ligne", action="store_true")
    a.add_argument("--sortie", type=Path, default=RACINE / "shared" / "listes-publiques.jsonl")
    a.add_argument("--flags", type=Path, default=RACINE / "shared" / "flags.jsonl")
    args = a.parse_args()
    maintenant = int(time.time())
    total, publies = 0, 0
    with open(args.sortie, "w", encoding="utf-8") as out:
        for nom in SOURCES:
            adresses = adresses_de(telecharger(nom, args.hors_ligne))
            for adr in adresses:
                out.write(json.dumps(entree(nom, adr, maintenant), ensure_ascii=False) + "\n")
            total += len(adresses)
            if args.publier:
                with open(args.flags, "a", encoding="utf-8") as ff:
                    for adr in adresses[:args.publier]:
                        ff.write(json.dumps(entree(nom, adr, maintenant), ensure_ascii=False) + "\n")
                        publies += 1
            print(f"{nom:<12} {len(adresses):>6} adresses  ({SOURCES[nom]['category']}, confiance {SOURCES[nom]['confidence']})")
    print(f"→ {total} adresses dans {args.sortie}" + (f" ; {publies} publiées dans {args.flags} (registre on-chain)" if publies else ""))


if __name__ == "__main__":
    main()
