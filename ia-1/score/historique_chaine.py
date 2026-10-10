"""Historique on-chain du destinataire : ce que la chaîne elle-même sait d'une adresse jamais payée par le client.

NEW_RECIPIENT dit « nous ne l'avons jamais payée ». Ce module ajoute « et la chaîne non plus ne la connaît pas » :
une adresse sans aucune transaction, ou un contrat déployé la veille et au code non publié.

Deux sources, publiques et sans clé :
    - le nœud (RPC) : nombre de transactions émises, contrat ou non ;
    - l'explorateur (API au format Etherscan, Routescan pour Avalanche) : date de la première activité,
      code du contrat vérifié ou non. Facultatif : sans lui, l'âge reste inconnu.

Usage seul :
    python -m score.historique_chaine 0x… [--reseau fuji|avalanche]

Jamais bloquant : si le réseau ne répond pas, le moteur note le paiement sans ce signal.
Limite connue : un nouveau fournisseur honnête a souvent une adresse neuve lui aussi. Le signal freine, il ne bloque pas seul.
"""
import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass

RESEAUX = {
    "fuji": ("https://api.avax-test.network/ext/bc/C/rpc",
             "https://api.routescan.io/v2/network/testnet/evm/43113/etherscan/api"),
    "avalanche": ("https://api.avax.network/ext/bc/C/rpc",
                  "https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api"),
}
DELAI_S = 5.0


@dataclass
class Historique:
    adresse: str
    transactions_emises: int            # nonce : 0 = cette adresse n'a jamais rien signé
    est_contrat: bool
    premiere_activite: int | None = None  # date Unix de la première transaction reçue ou émise ; None = inconnue
    jamais_vue: bool = False            # l'explorateur a répondu et ne connaît aucune transaction pour cette adresse
    code_verifie: bool | None = None    # contrat : code source publié sur l'explorateur ; None = inconnu


def _rpc(rpc: str, appels: list) -> list:
    import httpx
    lot = [{"jsonrpc": "2.0", "id": i, "method": m, "params": p} for i, (m, p) in enumerate(appels)]
    reponses = httpx.post(rpc, json=lot, timeout=DELAI_S).json()
    return [r["result"] for r in sorted(reponses, key=lambda r: r["id"])]


def _explorateur(api: str, **params) -> list | None:
    """Résultat de l'API de l'explorateur ; None si elle ne répond pas (à ne pas confondre avec « aucune transaction »)."""
    import httpx
    for essai in range(2):  # l'API gratuite limite le débit : un second essai après une seconde
        try:
            d = httpx.get(api, params=params, timeout=DELAI_S).json()
            if isinstance(d.get("result"), list):
                return d["result"]
        except Exception:
            pass
        if essai == 0:
            time.sleep(1)
    return None


def _date_de_creation(adresse: str, rpc: str, explorateur: str) -> int | None:
    """Date de déploiement d'un contrat : l'explorateur donne la transaction, le nœud donne l'heure de son bloc."""
    creation = _explorateur(explorateur, module="contract", action="getcontractcreation", contractaddresses=adresse)
    if not creation or not creation[0].get("txHash"):
        return None
    (tx,) = _rpc(rpc, [("eth_getTransactionByHash", [creation[0]["txHash"]])])
    if not tx:
        return None
    (bloc,) = _rpc(rpc, [("eth_getBlockByNumber", [tx["blockNumber"], False])])
    return int(bloc["timestamp"], 16) if bloc else None


def lire(adresse: str, rpc: str, explorateur: str | None = None) -> Historique:
    nonce, code = _rpc(rpc, [("eth_getTransactionCount", [adresse, "latest"]), ("eth_getCode", [adresse, "latest"])])
    h = Historique(adresse.lower(), int(nonce, 16), code not in ("0x", "0x0", ""))
    if not explorateur:
        return h
    if h.est_contrat:
        h.premiere_activite = _date_de_creation(adresse, rpc, explorateur)
        source = _explorateur(explorateur, module="contract", action="getsourcecode", address=adresse)
        if source:
            h.code_verifie = bool(source[0].get("SourceCode"))
        return h
    # Transactions natives seulement : une adresse qui n'a reçu que des jetons n'y apparaît pas.
    premieres = _explorateur(explorateur, module="account", action="txlist", address=adresse, page=1, offset=1, sort="asc")
    if premieres:
        h.premiere_activite = int(premieres[0]["timeStamp"])
    elif premieres == []:
        h.jamais_vue = h.transactions_emises == 0
    return h


class Lecteur:
    """Ce que le moteur appelle pour un destinataire inconnu. Garde les réponses en mémoire ; ne lève jamais d'erreur."""

    def __init__(self, rpc: str, explorateur: str | None = None, duree_cache_s: int = 600):
        self.rpc, self.explorateur, self.duree_cache_s = rpc, explorateur, duree_cache_s
        self.cache = {}

    def __call__(self, adresse: str) -> Historique | None:
        adresse = adresse.lower()
        vu = self.cache.get(adresse)
        if vu and time.time() - vu[0] < self.duree_cache_s:
            return vu[1]
        try:
            h = lire(adresse, self.rpc, self.explorateur)
        except Exception as err:
            print(f"historique on-chain indisponible pour {adresse[:10]}… : {err!r}", file=sys.stderr)
            return None
        self.cache[adresse] = (time.time(), h)
        return h


def lecteur_pour(reseau_ou_rpc: str, explorateur: str | None = None) -> Lecteur:
    """« fuji », « avalanche », ou l'URL d'un nœud (alors sans explorateur, sauf s'il est donné)."""
    if reseau_ou_rpc in RESEAUX:
        rpc, api = RESEAUX[reseau_ou_rpc]
        return Lecteur(rpc, explorateur or api)
    return Lecteur(reseau_ou_rpc, explorateur)


def main(argv=None):
    a = argparse.ArgumentParser(description="Historique on-chain d'une adresse")
    a.add_argument("adresses", nargs="+")
    a.add_argument("--reseau", default="fuji", help="fuji, avalanche, ou l'URL d'un nœud")
    args = a.parse_args(argv)
    lecteur = lecteur_pour(args.reseau)
    for adresse in args.adresses:
        h = lecteur(adresse)
        print(json.dumps(asdict(h) if h else {"adresse": adresse, "erreur": "indisponible"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
