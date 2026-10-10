# DORA : ce qui est vérifié et ce qui ne l'est pas

Notes de Timéo (ia-2) pour le module conformité de Romain. Vérification faite par recherche web le 10 octobre 2026 vers 14h00. **Rien ici ne remplace la lecture des textes avant de coder les seuils.**

## Délais de notification (règlement délégué (UE) 2025/301, article 5)

| Rapport | Délai | Niveau de confiance |
|---|---|---|
| Notification initiale | Au plus tard 4 heures après le classement en incident majeur, et au plus tard 24 heures après la prise de connaissance de l'incident | Confirmé par une reproduction de l'article 5 |
| Rapport intermédiaire | 72 heures après la notification initiale | Source secondaire seulement, à lire dans le texte |
| Rapport final | 1 mois | Source secondaire seulement, à lire dans le texte |

Le compteur des 4 heures part du **classement** en incident majeur, pas de la détection. Retarder le classement pour gagner du temps est mal vu des superviseurs : c'est un argument pour notre outil, qui classe tout de suite.

## Classement en incident majeur (règlement délégué (UE) 2024/1772, articles 8 et 9)

Structure confirmée : un incident est majeur s'il touche des **services critiques** et remplit l'une des deux conditions suivantes :
- le seuil de perte de données ou d'accès non autorisé est atteint ;
- ou au moins **deux** des autres seuils de matérialité sont atteints.

Les six familles de critères de l'article 9 : clients et transactions touchés, réputation, durée et arrêt du service, étendue géographique, pertes de données, impact économique.

Incidents récurrents : deux incidents de même cause en 6 mois peuvent compter ensemble comme un incident majeur.

**Non confirmé (cité de mémoire, à vérifier) :** impact économique supérieur à 100 000 EUR ; durée supérieure à 24 heures, ou arrêt d'un service critique supérieur à 2 heures. Les seuils chiffrés sur les clients et les transactions n'ont pas été trouvés.

## Sources

- Texte officiel du règlement délégué 2024/1772 (classement) : https://eur-lex.europa.eu/eli/reg_del/2024/1772/oj/eng
- Article 5 du règlement délégué 2025/301 (délais) : https://advisera.com/cdr-2025-301/time-limits-for-the-initial-notification-and-for-the-intermediate-and-final-reports/
- Instructions opérationnelles des autorités européennes (modèles de rapport) : https://www.esma.europa.eu/sites/default/files/2026-09/DORA_Incident_reporting_-_Operational_instructions.pdf
- Autorité autrichienne FMA, page sur les incidents : https://www.fma.gv.at/en/dora-ict-related-incidents/
- Article 9 commenté : https://www.springlex.eu/en/packages/dora/rts-ic-regulation/article-9/

## Point à trancher avec le mentor

Un protocole DeFi pur n'est pas soumis à DORA (déjà noté dans `PLAN.md`). Le rapport doit donc être écrit du point de vue d'une entité régulée exposée au coffre, par exemple un prestataire crypto agréé MiCA.
