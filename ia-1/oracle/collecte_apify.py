"""Collecte Web réelle pour l'oracle, par Apify (conseil du mentor, 11 octobre).

Jusqu'ici l'oracle lisait des fichiers locaux ou une URL donnée à la main. Ce module ajoute l'étape qui
manquait : aller chercher de vraies pages, puis les passer dans l'oracle existant sans rien changer à ses
garde-fous (texte caché écarté, citation vérifiée mot pour mot, croisement des sources).

Deux façons de l'utiliser :
    # 1. lire des pages précises
    python -m oracle.collecte_apify --urls https://exemple.org/page --out ../shared/flags.jsonl
    # 2. partir d'une adresse : chercher ce que le Web en dit, puis lire les pages trouvées
    python -m oracle.collecte_apify --recherche 0x1234…abcd --out ../shared/flags.jsonl

Il faut un jeton Apify dans .env à la racine du dépôt : APIFY_TOKEN=…  (jamais dans Git).
Les pages collectées restent dans oracle/collecte_cache/, ignoré par Git : elles peuvent contenir des
pseudonymes et des accusations visant des personnes. Seules l'adresse, l'URL, la phrase citée et son
hash partent dans flags.jsonl, comme pour le reste de l'oracle.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from . import oracle

RACINE = Path(__file__).resolve().parents[2]
CACHE = Path(__file__).resolve().parent / "collecte_cache"
API = "https://api.apify.com/v2/acts/{acteur}/run-sync-get-dataset-items"
ACTEUR_PAGES = "apify~website-content-crawler"
ACTEUR_RECHERCHE = "apify~google-search-scraper"
MOTS_RECHERCHE = "scam OR arnaque OR phishing OR fraude OR hack"


def jeton() -> str:
    try:
        from dotenv import load_dotenv
        load_dotenv(RACINE / ".env")
    except ImportError:
        pass
    valeur = os.getenv("APIFY_TOKEN", "").strip()
    if not valeur:
        raise SystemExit("APIFY_TOKEN absent : ajoute une ligne APIFY_TOKEN=… dans .env à la racine du dépôt.")
    return valeur


def appeler_apify(acteur: str, entree: dict, delai_s: int = 300) -> list[dict]:
    """Lance un acteur Apify et attend ses résultats. Le jeton part dans l'en-tête, pas dans l'URL."""
    import httpx
    reponse = httpx.post(API.format(acteur=acteur), json=entree, timeout=delai_s,
                         headers={"Authorization": f"Bearer {jeton()}"})
    reponse.raise_for_status()
    return reponse.json()


def rechercher(adresse: str, maximum: int = 5) -> list[str]:
    """URL des pages qui parlent de cette adresse, d'après une recherche Web."""
    resultats = appeler_apify(ACTEUR_RECHERCHE, {
        "queries": f'"{adresse}" {MOTS_RECHERCHE}', "maxPagesPerQuery": 1, "resultsPerPage": maximum,
    })
    urls = []
    for page in resultats:
        for r in page.get("organicResults", []):
            if r.get("url") and r["url"] not in urls:
                urls.append(r["url"])
    return urls[:maximum]


def collecter(urls: list[str]) -> list[dict]:
    """Télécharge les pages. Chaque élément : {"url", "html"} ou {"url", "text"} si le HTML manque."""
    if not urls:
        return []
    return appeler_apify(ACTEUR_PAGES, {
        "startUrls": [{"url": u} for u in urls], "maxCrawlDepth": 0, "maxCrawlPages": len(urls), "saveHtml": True,
    })


def lire_pages(pages: list[dict], sans_llm: bool = False, maintenant: int | None = None) -> tuple[list, list]:
    """Passe les pages collectées dans l'oracle. La source reste l'URL réelle : c'est son hôte qui porte la réputation."""
    CACHE.mkdir(exist_ok=True)
    textes = {}
    for page in pages:
        url = page.get("url")
        if not url:
            continue
        if page.get("html"):
            fichier = CACHE / (hashlib.sha256(url.encode()).hexdigest()[:16] + ".html")
            fichier.write_text(page["html"], encoding="utf-8")
            textes[url] = oracle.texte_de(str(fichier))  # même nettoyage que pour une page locale
        elif page.get("text"):
            textes[url] = page["text"]
    (CACHE / "index.json").write_text(json.dumps(
        {"collecte_le": int(time.time()), "urls": sorted(textes)}, ensure_ascii=False, indent=2), encoding="utf-8")

    d_origine = oracle.texte_de
    oracle.texte_de = lambda source: textes[source] if source in textes else d_origine(source)
    candidats, rejets = [], []
    try:
        for url in textes:
            try:
                acceptes, rejetes = oracle.traiter_page(url, sans_llm, maintenant)
            except Exception as err:  # une page qui échoue ne doit pas arrêter la collecte
                print(f"✗ {url} : {err!r}", file=sys.stderr)
                continue
            candidats += acceptes
            rejets += rejetes
            print(f"{url[:70]:<70} accusations {len(acceptes)}  rejetées {len(rejetes)}", file=sys.stderr)
    finally:
        oracle.texte_de = d_origine
    return candidats, rejets


def main(argv=None):
    a = argparse.ArgumentParser(description="Collecte Web par Apify, puis lecture par l'oracle")
    a.add_argument("--urls", nargs="*", default=[], help="pages à lire")
    a.add_argument("--recherche", nargs="*", default=[], help="adresses 0x… : chercher ce que le Web en dit")
    a.add_argument("--max-pages", type=int, default=5, help="pages lues par adresse recherchée")
    a.add_argument("--out", type=Path, default=Path("flags.jsonl"))
    a.add_argument("--sans-llm", action="store_true", help="repli par mots-clés si Bedrock est injoignable")
    a.add_argument("--sans-croisement", action="store_true", help="publie chaque accusation sans exiger d'autres sources")
    args = a.parse_args(argv)

    urls = list(args.urls)
    for adresse in args.recherche:
        trouvees = rechercher(adresse, args.max_pages)
        print(f"recherche {adresse[:12]}… : {len(trouvees)} page(s)", file=sys.stderr)
        urls += [u for u in trouvees if u not in urls]
    if not urls:
        raise SystemExit("Aucune page à lire : donne --urls ou --recherche.")

    t0 = time.time()
    pages = collecter(urls)
    print(f"Apify : {len(pages)} page(s) collectée(s) en {time.time() - t0:.0f} s", file=sys.stderr)
    candidats, rejets = lire_pages(pages, args.sans_llm)
    publies, attente = (candidats, []) if args.sans_croisement else oracle.consolider(candidats)
    with open(args.out, "a", encoding="utf-8") as f:
        for x in publies:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    with open(args.out.with_name("flags-rejetes.jsonl"), "a", encoding="utf-8") as f:
        for x in rejets + attente:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    for x in publies:
        print(f"✓ PUBLIÉE {x['address'][:12]}… {x['level']} ({x['sources_count']} source(s)) {x['source_url'][:60]}", file=sys.stderr)
    for x in attente:
        print(f"⏸ EN ATTENTE {x['address'][:12]}… {x['detail']}", file=sys.stderr)


if __name__ == "__main__":
    main()
