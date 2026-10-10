"""Générateur de trafic synthétique pour valider le moteur de score (en attendant T4/T5 de Timéo).

Produit events.jsonl + labels.jsonl au format de shared/format-evenements.md :
- trafic normal sur N jours : salaires, fournisseurs récurrents, nouveaux fournisseurs légitimes,
  grosses factures annuelles, paiements tardifs, remplacement légitime d'un signataire ;
- fraudes (8 scénarios), dont des cas volontairement difficiles.

Usage : python eval/generateur.py --graine 1 --jours 60 --sortie /tmp/train
"""
import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")
U = 10**18


class Gen:
    def __init__(self, graine, jours, echelle=1.0):
        self.r = random.Random(graine)
        self.jours, self.echelle = jours, echelle
        self.debut = datetime(2026, 9, 1, 9, 0, tzinfo=PARIS)
        self.items = []  # (timestamp, ordre, type, data, label|None, scenario)
        self.pid = 0
        self.owners = [self.adr() for _ in range(5)]
        self.wallet, self.token = self.adr(), self.adr()
        self.monitor, self.oracle = self.adr(), self.adr()
        self.payroll = self.adr()
        self.fournisseurs = [(self.adr(), self.r.uniform(800, 15000) * echelle, self.r.choice([7, 14, 30]))
                             for _ in range(8)]
        self.carnet = [self.payroll] + [f[0] for f in self.fournisseurs]

    def adr(self):
        return "0x" + "".join(self.r.choice("0123456789abcdef") for _ in range(40))

    def tx(self):
        return "0x" + "".join(self.r.choice("0123456789abcdef") for _ in range(64))

    def heure_ouvree(self, jour, tard=False):
        d = self.debut + timedelta(days=jour)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        h = self.r.uniform(20.0, 21.5) if tard else self.r.uniform(8.5, 18.5)
        return int(d.replace(hour=int(h), minute=int((h % 1) * 60)).timestamp())

    def paiement(self, t, to, montant, memo, label="normal", scen="", executer=True, proposer=None):
        self.pid += 1
        pid, p = self.pid, proposer or self.r.choice(self.owners)
        self.items.append((t, 0, "payment_proposed", {"payment_id": pid, "proposer": p, "to": to, "token": self.token,
                           "amount": str(int(montant * U)), "memo": memo, "required_approvals": 2,
                           "executable_after": t + 60}, label, scen))
        if executer:
            self.items.append((t + self.r.randint(300, 7200), 1, "payment_executed",
                               {"payment_id": pid, "to": to, "token": self.token, "amount": str(int(montant * U)),
                                "executor": p}, None, None))
        return pid

    def normal(self):
        for m in range(0, self.jours, 30):  # salaires mensuels
            self.paiement(self.heure_ouvree(m + 27), self.payroll, 48200 * self.echelle * self.r.uniform(0.97, 1.03),
                          f"Salaires mois {m // 30 + 1}", scen="payroll")
        for adr, base, freq in self.fournisseurs:  # fournisseurs récurrents
            for j in range(self.r.randint(0, freq), self.jours, freq):
                self.paiement(self.heure_ouvree(j, tard=self.r.random() < 0.05), adr, base * self.r.uniform(0.8, 1.2),
                              self.r.choice(["Facture", "Facture mensuelle", "Prestation", "Abonnement"]),
                              scen="recurring_supplier")
        for _ in range(max(2, self.jours // 10)):  # nouveaux fournisseurs légitimes
            adr, j = self.adr(), self.r.randint(5, self.jours - 1)
            montant = self.r.uniform(1500, 15000) * self.echelle
            self.paiement(self.heure_ouvree(j), adr, montant, "Acompte nouveau prestataire", scen="new_supplier")
            if self.r.random() < 0.5:
                self.paiement(self.heure_ouvree(min(j + 14, self.jours - 1)), adr, montant, "Facture", scen="new_supplier_repeat")
        for _ in range(2):  # grosse facture annuelle à un fournisseur connu
            adr, base, _ = self.r.choice(self.fournisseurs)
            self.paiement(self.heure_ouvree(self.r.randint(10, self.jours - 1)), adr, base * self.r.uniform(6, 12),
                          "Licence annuelle", scen="annual_invoice")
        j = self.r.randint(10, self.jours - 10)  # remplacement légitime d'un signataire (renouvellement de clé)
        nouveau = self.adr()
        self.items.append((self.heure_ouvree(j), 0, "owner_replaced",
                           {"previous_owner": self.owners[0], "new_owner": nouveau, "key_expires_at": 0}, None, None))

    def fraudes(self):
        r, inconnu = self.r, self.adr
        urg = ["URGENT confidentiel - acquisition, ne pas en parler", "Urgent : nouveau RIB du fournisseur",
               "Paiement immédiat demandé par la direction", "Confidentiel - opération spéciale"]
        def nuit(j):
            d = self.debut + timedelta(days=j)
            return int(d.replace(hour=r.randint(1, 5), minute=r.randint(0, 59)).timestamp())
        jours = r.sample(range(3, self.jours - 3), 8)
        # 1. signataires trompés, rafale
        t = self.heure_ouvree(jours[0]) if r.random() < 0.5 else nuit(jours[0])
        memo = r.choice(urg)
        for k in range(3):
            self.paiement(t + k * r.randint(20, 60), inconnu(), r.uniform(80000, 100000) * self.echelle, memo,
                          "fraud", "tricked_signers_burst", executer=False)
        # 2. clé volée : un gros paiement la nuit, libellé neutre
        self.paiement(nuit(jours[1]), inconnu(), r.uniform(50000, 90000) * self.echelle, "Facture",
                      "fraud", "stolen_key", executer=False)
        # 3. goutte-à-goutte : petits montants vers la même adresse, en heures ouvrées (cas difficile)
        cible = inconnu()
        for k in range(5):
            self.paiement(self.heure_ouvree(jours[2] + k // 2), cible, r.uniform(2000, 5000) * self.echelle,
                          "Prestation conseil", "fraud", "slow_drip", executer=True)
        # 4. seuil abaissé puis paiement
        t = self.heure_ouvree(jours[3])
        self.items.append((t, 0, "threshold_changed", {"previous_threshold": 2, "new_threshold": 1}, None, None))
        self.paiement(t + 3600, inconnu(), r.uniform(30000, 60000) * self.echelle, "Facture", "fraud", "threshold_lowered",
                      executer=False)
        # 5. signataire remplacé puis vidage
        t = self.heure_ouvree(jours[4])
        pirate = inconnu()
        self.items.append((t, 0, "owner_replaced", {"previous_owner": self.owners[1], "new_owner": pirate,
                                                    "key_expires_at": 0}, None, None))
        self.paiement(t + 86400, inconnu(), r.uniform(40000, 80000) * self.echelle, "Règlement", "fraud",
                      "owner_replaced_then_drain", executer=False, proposer=pirate)
        # 6. adresse signalée par l'oracle, montant et libellé banals
        t = self.heure_ouvree(jours[5])
        adr = inconnu()
        self.items.append((t - 7200, 0, "address_flagged", {"flagged": adr, "level": "hold", "category": "scam_report",
                                                            "evidence_hash": self.tx(), "expires_at": t + 30 * 86400},
                           None, None))
        self.paiement(t, adr, r.uniform(3000, 8000) * self.echelle, "Facture", "fraud", "flagged_address", executer=False)
        # 7. fraude au président, un seul paiement moyen
        self.paiement(self.heure_ouvree(jours[6]), inconnu(), r.uniform(15000, 30000) * self.echelle, r.choice(urg),
                      "fraud", "ceo_fraud_single", executer=False)
        # 8. usurpation de fournisseur : montant habituel, « nouveau RIB » (cas difficile)
        adr0, base, _ = r.choice(self.fournisseurs)
        self.paiement(self.heure_ouvree(jours[7]), inconnu(), base * r.uniform(0.9, 1.1),
                      "Facture - changement de coordonnées bancaires", "fraud", "vendor_impersonation", executer=False)

    def ecrire(self, dossier: Path):
        dossier.mkdir(parents=True, exist_ok=True)
        self.items.sort(key=lambda x: (x[0], x[1]))
        with open(dossier / "events.jsonl", "w") as ev, open(dossier / "labels.jsonl", "w") as lab:
            for seq, (t, _, typ, data, label, scen) in enumerate(self.items, 1):
                frm = data.get("proposer") or data.get("executor") or self.owners[0]
                ev.write(json.dumps({"seq": seq, "chain_id": 31337, "block": 1000 + seq, "timestamp": t,
                                     "tx_hash": self.tx(), "log_index": 0, "tx_from": frm,
                                     "contract": "registry" if typ.startswith("address_") else "wallet",
                                     "address": self.wallet, "type": typ, "data": data}) + "\n")
                if label:
                    lab.write(json.dumps({"payment_id": data["payment_id"], "label": label, "scenario": scen}) + "\n")
        (dossier / "carnet.json").write_text(json.dumps(self.carnet))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--graine", type=int, default=1)
    a.add_argument("--jours", type=int, default=60)
    a.add_argument("--echelle", type=float, default=1.0, help="multiplie tous les montants (test de généralisation)")
    a.add_argument("--sortie", type=Path, required=True)
    args = a.parse_args()
    g = Gen(args.graine, args.jours, args.echelle)
    g.normal()
    g.fraudes()
    g.ecrire(args.sortie)


if __name__ == "__main__":
    main()
