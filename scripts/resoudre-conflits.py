"""Résout automatiquement les conflits Git sur JOURNAL.md et SUIVI.md (écrits par Romain et Timéo en même temps).

- JOURNAL.md : on garde les deux entrées, la nôtre au-dessus.
- SUIVI.md : ligne par ligne (clé = 1re colonne du tableau), on garde le statut le plus avancé
  (✅ > ✂️ > 🔄 > ⬜) ; les lignes présentes d'un seul côté sont conservées.
Usage : python3 scripts/resoudre-conflits.py JOURNAL.md SUIVI.md
Renvoie 1 s'il reste des marqueurs de conflit.
"""
import sys

RANG = {"✅": 3, "✂️": 2, "🔄": 1, "⬜": 0}


def rang(ligne):
    statut = ligne.rstrip().rstrip("|").split("|")[-1] if ligne.startswith("|") else ""
    return max([v for k, v in RANG.items() if k in statut] or [-1])


def cle(ligne):
    return ligne.split("|")[1].strip() if ligne.startswith("|") else ligne[:30]


def resoudre(texte, journal):
    lignes, out, i = texte.split("\n"), [], 0
    while i < len(lignes):
        if not lignes[i].startswith("<<<<<<<"):
            out.append(lignes[i])
            i += 1
            continue
        j = next(n for n in range(i, len(lignes)) if lignes[n].startswith("======="))
        k = next(n for n in range(j, len(lignes)) if lignes[n].startswith(">>>>>>>"))
        amont, nous = lignes[i + 1:j], lignes[j + 1:k]  # pendant un rebase : HEAD = amont (GitHub), l'autre = notre commit
        if journal:
            out += nous + amont
        else:
            dict_nous = {cle(l): l for l in nous}
            for l in amont:
                n = dict_nous.pop(cle(l), None)
                if l.startswith("**Dernière mise à jour"):
                    out.append(n or l)
                else:
                    out.append(n if n is not None and rang(n) > rang(l) else l)
            out += list(dict_nous.values())
        i = k + 1
    return "\n".join(out)


reste = False
for chemin in sys.argv[1:]:
    t = open(chemin, encoding="utf-8").read()
    if "<<<<<<<" in t:
        t = resoudre(t, journal=chemin.endswith("JOURNAL.md"))
        open(chemin, "w", encoding="utf-8").write(t)
    reste |= "<<<<<<<" in t or ">>>>>>>" in t
sys.exit(1 if reste else 0)
