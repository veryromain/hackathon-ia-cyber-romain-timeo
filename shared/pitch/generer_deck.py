# Génère le PowerPoint du pitch Breaker dans l'identité du site vitrine (ia-2/site-vitrine/dist/style.css).
# Usage : python3 shared/pitch/generer_deck.py  → shared/pitch/Breaker-pitch.pptx
# Les notes orateur (volet « Notes » de PowerPoint) portent le texte à dire, avec ROMAIN / TIMÉO et le chrono.
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import os

# --- Charte du site -----------------------------------------------------------
BG = RGBColor(0x07, 0x11, 0x1F)        # bleu nuit
INK = RGBColor(0xF6, 0xF9, 0xFC)       # titres
TEXT = RGBColor(0xE7, 0xED, 0xF4)
MUTED = RGBColor(0xA9, 0xB4, 0xC2)     # ≈ rgba(231,237,244,.7) sur le fond
FAINT = RGBColor(0x7F, 0x8B, 0x9B)
LINE = RGBColor(0x26, 0x33, 0x47)      # ≈ rgba(255,255,255,.11) sur le fond
GLASS = RGBColor(0x10, 0x1C, 0x2E)     # tuile « verre »
ACCENT = RGBColor(0xC7, 0xFA, 0x70)    # vert citron
ON_ACCENT = RGBColor(0x14, 0x20, 0x08)
BLUE = RGBColor(0xA8, 0xBF, 0xFF)      # signature supplémentaire
ORANGE = RGBColor(0xFF, 0xC4, 0x81)    # en attente
DISPLAY, BODY = "Manrope", "DM Sans"

W, H = Inches(13.333), Inches(7.5)
M = Inches(0.8)  # marge

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]
TOTAL_MAIN = 8


def rect(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, radius=None):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(0.75)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    return s


def text(slide, x, y, w, h, runs, size=18, color=TEXT, font=BODY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.15, tabular=False):
    """runs : str, ou liste de paragraphes ; un paragraphe = str ou liste de (texte, {opts})."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = runs if isinstance(runs, list) else [runs]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align; para.line_spacing = spacing
        segs = p if isinstance(p, list) else [(p, {})]
        for seg, o in segs:
            r = para.add_run(); r.text = seg
            f = r.font; f.name = o.get("font", font); f.size = Pt(o.get("size", size)); f.bold = o.get("bold", bold)
            f.color.rgb = o.get("color", color)
    return tb


def mark(slide, x, y, size=Inches(0.42), fill=ACCENT, letter=ON_ACCENT):
    """Le logo : un B dans un bloc à pans coupés (silhouette du site : polygon 0 0, 70% 0, 100% 26%, 100% 100%, 30% 100%, 0 74%)."""
    w, h = size, int(size * 38 / 34)
    pts = [(0, 0), (0.70, 0), (1, 0.26), (1, 1), (0.30, 1), (0, 0.74)]
    ff = slide.shapes.build_freeform(x + int(pts[0][0] * w), y + int(pts[0][1] * h), scale=1.0)
    ff.add_line_segments([(x + int(px * w), y + int(py * h)) for px, py in pts[1:]], close=True)
    s = ff.convert_to_shape()
    s.fill.solid(); s.fill.fore_color.rgb = fill; s.line.fill.background(); s.shadow.inherit = False
    text(slide, x, y + int(h * 0.08), w, int(h * 0.84), "B", size=int(size / Inches(0.42) * 15), color=letter, font=DISPLAY, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return s


def wordmark(slide, x, y, size=16, color=INK):
    text(slide, x, y, Inches(2), Inches(0.4), [[("breaker", {"color": color, "bold": True, "font": DISPLAY, "size": size}), (".", {"color": ACCENT, "bold": True, "font": DISPLAY, "size": size})]])


def base(title_eyebrow, number=None, annex=False, who=None):
    slide = prs.slides.add_slide(BLANK)
    rect(slide, 0, 0, W, H, fill=BG)
    # filigrane : la silhouette du logo, très discrète, en haut à droite
    mark(slide, W - Inches(3.2), -Inches(0.9), size=Inches(3.6), fill=RGBColor(0x0B, 0x17, 0x28), letter=RGBColor(0x0B, 0x17, 0x28))
    # pied de page
    mark(slide, M, H - Inches(0.62), size=Inches(0.26))
    wordmark(slide, M + Inches(0.36), H - Inches(0.67), size=13)
    if number is not None:
        text(slide, W - M - Inches(3), H - Inches(0.66), Inches(3), Inches(0.35), f"{number} / {TOTAL_MAIN}" if not annex else f"annexe {number}", size=11, color=FAINT, font=BODY, align=PP_ALIGN.RIGHT)
    # surtitre
    eyebrow_color = ORANGE if annex else ACCENT
    text(slide, M, Inches(0.55), W - 2 * M, Inches(0.35), [[(title_eyebrow[0].upper() + "  ", {"color": eyebrow_color, "bold": True, "size": 11, "font": BODY}), (title_eyebrow[1], {"color": MUTED, "size": 11, "font": BODY})]])
    if who:
        pill = rect(slide, W - M - Inches(1.5), Inches(0.5), Inches(1.5), Inches(0.38), fill=GLASS, line=LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
        text(slide, W - M - Inches(1.5), Inches(0.5), Inches(1.5), Inches(0.38), who, size=10, color=ACCENT, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    return slide


def title(slide, t, y=Inches(1.05), size=38, w=None):
    text(slide, M, y, w or (W - 2 * M - Inches(1.5)), Inches(1.6), t, size=size, color=INK, font=DISPLAY, bold=True, spacing=1.02)


def tiles(slide, items, y, h=Inches(1.6), cols=None, value_size=34):
    """items : (valeur, libellé, couleur)."""
    cols = cols or len(items); gap = Inches(0.22)
    w = int((W - 2 * M - gap * (cols - 1)) / cols)
    for i, (v, l, c) in enumerate(items):
        x = M + i * (w + gap)
        rect(slide, x, y, w, h, fill=GLASS, line=LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
        rect(slide, x, y, Inches(0.06), h, fill=c, shape=MSO_SHAPE.RECTANGLE)
        text(slide, x + Inches(0.3), y + Inches(0.22), w - Inches(0.5), Inches(0.7), v, size=value_size, color=c, font=DISPLAY, bold=True)
        text(slide, x + Inches(0.3), y + Inches(0.22) + Inches(0.72), w - Inches(0.5), h - Inches(1.0), l, size=12.5, color=MUTED, spacing=1.15)


def flow(slide, boxes, y, h=Inches(1.5), highlight=()):
    """boxes : (titre, sous-texte) ; flèches entre."""
    n = len(boxes); arrow_w = Inches(0.45); gap = Inches(0.12)
    w = int((W - 2 * M - (n - 1) * (arrow_w + 2 * gap)) / n)
    x = M
    for i, (t, s) in enumerate(boxes):
        hl = i in highlight
        rect(slide, x, y, w, h, fill=GLASS, line=ACCENT if hl else LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
        if hl:
            rect(slide, x, y, Inches(0.06), h, fill=ACCENT)
        text(slide, x + Inches(0.25), y + Inches(0.2), w - Inches(0.4), Inches(0.5), t, size=16, color=INK, font=DISPLAY, bold=True)
        text(slide, x + Inches(0.25), y + Inches(0.68), w - Inches(0.4), h - Inches(0.8), s, size=11.5, color=MUTED, spacing=1.15)
        x += w
        if i < n - 1:
            text(slide, x + gap, y + int(h / 2) - Inches(0.25), arrow_w, Inches(0.5), "→", size=22, color=ACCENT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            x += arrow_w + 2 * gap


def rows(slide, data, y, col_w, h_row=Inches(0.42), size=12.5, header=True):
    """Tableau sobre : lignes séparées par un filet. data[0] = en-têtes si header."""
    for r, row in enumerate(data):
        yy = y + r * h_row
        x = M
        for c, cell in enumerate(row):
            is_head = header and r == 0
            text(slide, x, yy + Inches(0.07), col_w[c] - Inches(0.15), h_row, cell, size=10 if is_head else size, color=FAINT if is_head else (INK if c == 0 else TEXT), font=BODY, bold=(c == 0 and not is_head), spacing=1.05)
            x += col_w[c]
        rect(slide, M, yy + h_row - Emu(6000), W - 2 * M, Emu(6000), fill=LINE)


def notes(slide, txt):
    slide.notes_slide.notes_text_frame.text = txt


def source(slide, s):
    text(slide, M, H - Inches(1.05), W - 2 * M, Inches(0.3), s, size=9.5, color=FAINT)


# =============================================================================
# 1. Titre — ROMAIN (accroche), TIMÉO (équipe)
s = base(("Breaker", "Secure Horizons · Track 1 Fintech Security · axe 2 SOC antifraude"), 1, who="ROMAIN")
mark(s, M, Inches(1.5), size=Inches(0.9))
wordmark(s, M + Inches(1.15), Inches(1.72), size=30)
title(s, "Le 21 février 2025, trois personnes ont signé le plus gros vol de l'histoire.", y=Inches(2.65), size=34, w=Inches(10.5))
text(s, M, Inches(4.75), Inches(9.5), Inches(1.0), [[("Elles pensaient signer un virement de routine. L'écran leur montrait un virement de routine. ", {}), ("1,46 milliard de dollars.", {"bold": True, "color": INK})]], size=18, color=MUTED)
text(s, M, Inches(5.85), Inches(11), Inches(0.5), "Une signature ne suffit pas à faire confiance.", size=20, color=ACCENT, font=DISPLAY, bold=True)
notes(s, """[0:00 → 0:30]  ROMAIN
« Le 21 février 2025, trois personnes ont signé le plus gros vol de l'histoire : un milliard quatre cent soixante millions de dollars. »
(silence, 2 secondes)
« Elles pensaient signer un virement de routine. L'écran leur montrait un virement de routine. »

TIMÉO
« Nous sommes Timéo et Romain. Breaker existe pour que ces trois personnes aient eu quelqu'un pour leur dire : attendez. »

Source : Bybit, 21/02/2025 (shared/business-probleme.md, fait 1).""")

# 2. Problème — ROMAIN (faits), TIMÉO (conséquence)
s = base(("Problème", "ce ne sont plus les contrats qu'on casse, ce sont les gens qu'on trompe au moment de signer"), 2, who="ROMAIN · TIMÉO")
title(s, "Les clés étaient valides. Les signataires, trompés.", size=36)
tiles(s, [("1,46 Md$", "Bybit, février 2025 : 3 signataires sur 6 valident une transaction que leur interface leur montre falsifiée", ORANGE),
          ("≈ 280 M$", "Drift, avril 2026 : des mois de fausses identités pour approcher les signataires, puis le multisig", ORANGE),
          ("3,4 Md$", "volés en 2025 (Chainalysis). Médiane d'un incident significatif : 1,3 M$ (TRM)", ORANGE)], y=Inches(2.75), h=Inches(1.75))
text(s, M, Inches(4.85), W - 2 * M, Inches(1.2), [[("Le coffre fait exactement ce qu'on lui demande. ", {"bold": True, "color": INK}), ("Il n'a aucune idée de ce qui est normal pour vous. Les grandes plateformes se paient des équipes et des outils dépositaires à partir de 36 000 $ par an. Les autres n'ont rien, à aucun prix.", {})]], size=17, color=MUTED)
source(s, "shared/business-probleme.md · TRM Labs 2025 · fireblocks.com/pricing")
notes(s, """[0:30 → 1:20]  ROMAIN
« Bybit, c'est trois signataires sur six, trompés par leur propre écran. Drift, en avril 2026 : 280 millions, après des mois où des attaquants ont construit de fausses identités pour approcher les signataires. En 2025, 3,4 milliards volés. Le point commun : ce ne sont plus les contrats qu'on casse, ce sont les gens qu'on trompe au moment de signer. »
(geste : mimer une signature)

TIMÉO
« Et le coffre, lui, fait exactement ce qu'on lui demande. Il vérifie les signatures, pas les intentions. Il n'a aucune idée de ce qui est normal pour vous. »

ROMAIN
« Conséquence : les grandes plateformes se paient des équipes de sécurité et des outils à 36 000 dollars par an. Les autres, l'immense majorité, n'ont rien, à aucun prix. »""")

# 3. Cible — ROMAIN
s = base(("Cible", "les organisations qui ont une trésorerie et pas d'équipe sécurité"), 3, who="ROMAIN")
title(s, "Pour les équipes compactes aux trésoreries importantes", size=36)
tiles(s, [("675", "protocoles avec plus de 10 M$ d'actifs gérés, toutes chaînes (API DeFiLlama, 11/10/2026)", INK),
          ("≈ 220", "DAO avec plus de 1 M$ de trésorerie (DeepDAO, T1 2026)", INK),
          ("32 – 121", "organisations adressables sur Avalanche : 22 protocoles > 10 M$, > 50 L1, 10 équipes sur Safe", ACCENT),
          ("675 – 895", "sur les chaînes EVM, borne basse : fonds et fondations exclus, faute de source", INK)], y=Inches(2.65), h=Inches(1.85), value_size=30)
text(s, M, Inches(4.85), W - 2 * M, Inches(1.1), [[("Protocoles, DAO, startups et fonds crypto : 1 à 10 M$ dans un Safe, zéro personne dont c'est le métier. ", {"color": INK, "bold": True}), ("Tous ont déjà un coffre : Safe sécurise 35 Md$ sur 61 millions de comptes. Aucun ne déplacera sa trésorerie pour un essai.", {})]], size=16, color=MUTED)
source(s, "shared/business-marche.md D1–D5 · Safe Foundation, rapport T1 2026")
notes(s, """[1:20 → 2:00]  ROMAIN
« Les autres, ce sont les équipes de protocoles, les DAO, les startups et les fonds crypto : une trésorerie de un à dix millions dans un coffre multi-signatures, le plus souvent un Safe, et zéro personne dont c'est le métier. Il y en a au moins 675 à 895 sur les chaînes compatibles Ethereum. Sur Avalanche, où nous sommes nés, entre 32 et 121. Ces chiffres viennent de l'API DeFiLlama lue hier et de DeepDAO ; les calculs sont dans le dépôt. »
(passer la main : « Timéo, qu'est-ce qu'on leur apporte ? »)

Si question sur la méthode : comptage par seuil de TVL, hypothèse H1 (protocole > 10 M$ ⇒ trésorerie ≥ 1 M$), script reproductible dans shared/business-marche.md § 5.""")

# 4. Solution — TIMÉO
s = base(("Solution", "Breaker n'est pas un coffre"), 4, who="TIMÉO")
title(s, "Vous avez déjà le coffre. Il vous manque quelqu'un qui regarde.", size=34)
flow(s, [("Votre Safe", "vos signataires, votre adresse, votre historique : rien ne bouge"),
         ("Guard Breaker", "appelé avant chaque paiement : signature en plus, attente, gel, probation des clés"),
         ("Moteur Breaker", "règles sur votre historique · modèle d'anomalie · oracle Web · listes OFAC · explication en français"),
         ("Vos signataires", "décident, toujours. L'unanimité lève tout.")], y=Inches(2.5), h=Inches(1.7), highlight=(1, 2))
y3 = Inches(4.4)
for i, (k, t, d, c) in enumerate([("1", "Regarde", "Bénéficiaire nouveau ? Montant 4× vos habitudes ? Trois paiements en dix minutes ? Adresse sosie, fonds souillés, sanctions ?", ACCENT),
                                   ("2", "Explique", "En français, pour des non-experts : « premier paiement à cette adresse, montant quatre fois supérieur à vos habitudes ».", BLUE),
                                   ("3", "Freine", "Une signature de plus, ou une attente. Jamais un blocage définitif : le pire bug possible est un faux ralentissement.", ORANGE)]):
    w = int((W - 2 * M - Inches(0.4)) / 3); x = M + i * (w + Inches(0.2))
    text(s, x, y3, Inches(0.5), Inches(0.6), k, size=30, color=c, font=DISPLAY, bold=True)
    text(s, x + Inches(0.55), y3 + Inches(0.05), w - Inches(0.6), Inches(0.4), t, size=16, color=INK, font=DISPLAY, bold=True)
    text(s, x + Inches(0.55), y3 + Inches(0.45), w - Inches(0.6), Inches(1.1), d, size=11.5, color=MUTED)
text(s, M, Inches(5.85), W - 2 * M, Inches(0.5), [[("Et protège la personne : ", {"bold": True, "color": INK}), ("clé d'identité pour révoquer seul sa clé volée · clé de contrainte qui dit « oui » à l'écran et gèle en silence · probation des clés neuves.", {})]], size=13.5, color=MUTED)
source(s, "shared/ce-que-breaker-est.md · ia-1/score/regles.py · ia-2/contracts/TreasuryGuard.sol")
notes(s, """[2:00 → 3:00]  TIMÉO
« Breaker n'est pas un coffre. C'est une garde qui se greffe sur le coffre que vous avez déjà, et qui fait trois choses.
Un : elle regarde chaque paiement avec ce qu'elle a appris de votre historique. Ce bénéficiaire est-il nouveau ? Ce montant est-il normal ? Pourquoi trois paiements en dix minutes ? Pourquoi “urgent” ? Elle vérifie aussi l'adresse sur le Web et sur les listes de sanctions.
Deux : elle explique, en français, à des gens qui ne sont pas experts : “premier paiement à cette adresse, montant quatre fois supérieur à vos habitudes”.
Trois : elle freine. Une signature de plus, ou une attente. Jamais un blocage définitif : l'unanimité de vos signataires lève tout.
Et parce que l'attaque vise la personne, chaque signataire a une clé d'identité, gardée à part, pour révoquer seul sa clé volée ; et une clé de contrainte, qui dit oui à l'écran mais gèle en silence si on le force. »

Si question « vous êtes un module de Safe ? » : « Le multisig de la démo tient lieu du Safe du client ; le portage en Guard + Module de Safe est en feuille de route, 6 à 8 semaines. »""")

# 5. Démo & preuves — TIMÉO
s = base(("Démo & preuves", "mesuré, avant d'être affirmé : une seule fois, sur un jeu préparé à l'aveugle par l'autre membre"), 5, who="TIMÉO")
title(s, "Sur Avalanche Fuji : 280 500 tentés, zéro sorti.", size=34)
tiles(s, [("95 %", "des fraudes freinées ou arrêtées, formes jamais vues", ACCENT),
          ("91 %", "des montants frauduleux mis en attente (1,12 M sur 1,23 M)", ACCENT),
          ("5,1 %", "de paiements légitimes retardés : gros premiers paiements ; 0 % sur les récurrents", ORANGE),
          ("5 – 6 s", "pour signaler, sur 30 s d'examen · 0,002 $ de gas par alerte", BLUE)], y=Inches(2.3), h=Inches(1.8), value_size=32)
tiles(s, [("100 %", "oracle Web : précision et rappel sur 35 adresses · 7 injections déjouées", INK),
          ("0 · 50 · 7 000", "détection grave (Slither) · tests · appels aléatoires, 0 invariant violé", INK),
          ("synthétique", "données fabriquées par nous · contrat pas encore audité par un tiers", ORANGE)], y=Inches(4.35), h=Inches(1.6), value_size=24)
source(s, "shared/mesures.md § 1 · shared/audit-contrat.md · explorateur Fuji : adresses dans ia-2/deployments/fuji.json")
notes(s, """[3:00 → 3:50]  TIMÉO
« Tout ça tourne sur Avalanche Fuji, et vous allez le voir. »
→ LANCER LA VIDÉO (2 à 3 min) ou la démo live. Pendant la vidéo, Timéo commente ; Romain surveille le chrono.
« Les chiffres, mesurés une seule fois sur un jeu de fraudes que Romain a préparé à l'aveugle : 95 % des fraudes freinées ou arrêtées, 91 % des montants frauduleux mis en attente, 5,1 % de paiements légitimes retardés, tous de gros premiers paiements. Sur Fuji : 280 500 tentés, zéro sorti, signalement en 5 secondes, 0,002 dollar de gas par alerte. L'oracle Web : 100 % sur 35 adresses, 7 injections déjouées. Le contrat : zéro détection grave à l'analyse statique, 50 tests, 7 000 appels aléatoires sans qu'une seule promesse soit violée. »

ROMAIN (une phrase, pour l'honnêteté)
« Données synthétiques, contrat pas encore audité par un tiers : on le dit avant qu'on nous le demande. »

Si le chrono dépasse 3:50 ici : couper la phrase sur l'oracle.""")

# 6. Offre — ROMAIN
s = base(("Offre", "Safe Pro vend des règles que vous écrivez ; nous détectons ce que vous n'avez pas prévu"), 6, who="ROMAIN")
title(s, "Un prix affiché, selon la taille de votre trésorerie", size=36)
gap = Inches(0.2); w = int((W - 2 * M - 3 * gap) / 4); y = Inches(2.45); h = Inches(2.0)
for i, (n, p, u, d, star) in enumerate([("Observation", "0 €", "30 jours", "détection et explications en lecture seule, rapport de fin d'observation", False),
                                        ("Essentiel", "149 €", "/ mois", "< 1 M$ · friction, explications, listes publiques, notifications", False),
                                        ("Standard", "449 €", "/ mois", "1 à 10 M$ · + oracle Web, traçage, sosies, clé d'identité, rapport mensuel", True),
                                        ("Premium", "990 €", "/ mois", "> 10 M$ · + mode cosignataire, réglages sur mesure, support · Entreprise sur devis", False)]):
    x = M + i * (w + gap)
    rect(s, x, y, w, h, fill=GLASS, line=ACCENT if star else LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    text(s, x + Inches(0.3), y + Inches(0.22), w - Inches(0.5), Inches(0.4), n, size=13, color=ACCENT if star else MUTED, bold=True)
    text(s, x + Inches(0.3), y + Inches(0.6), w - Inches(0.5), Inches(0.7), [[(p, {"size": 34, "font": DISPLAY, "bold": True, "color": INK}), ("  " + u, {"size": 12, "color": FAINT})]])
    text(s, x + Inches(0.3), y + Inches(1.3), w - Inches(0.5), Inches(0.7), d, size=11.5, color=MUTED)
rows(s, [["Pourquoi 449 €", ""],
         ["Perte annuelle évitée", "9,5 % d'incidents (TRM ÷ population) × 1,3 M$ médiane × 91 % d'efficacité ≈ 112 k$/an  (22 k$ à périmètre restreint)"],
         ["Prix / valeur", "5 400 €/an = 5 % de la perte évitée (règle : ≤ 10 %)"],
         ["Repère du client · coût marginal", "Safe Pro Business 669 €/mois (règles à écrire) · Fireblocks 999 $/mois (dépositaire) · coût marginal ≈ 1,2 $/client/mois"]],
     y=Inches(4.65), col_w=[Inches(3.2), W - 2 * M - Inches(3.2)], h_row=Inches(0.36), size=11.5)
source(s, "shared/business-prix.md · shared/business-safe-et-differenciation.md · safe.global/pricing (8/10/2026)")
notes(s, """[3:50 → 4:20]  ROMAIN
« Safe vient de lancer Safe Pro : 669 euros par mois pour des règles que vous écrivez vous-même. Nous, nous détectons ce que vous n'avez pas prévu, et nous l'expliquons.
Observation gratuite 30 jours : rien ne change à vos paiements. Puis 149, 449 ou 990 euros par mois selon la trésorerie, sans engagement.
449 euros, c'est 5 % de la perte annuelle que vous évitez, calculée avec les taux d'incidents de TRM et notre efficacité mesurée. »

Différence en une phrase si on nous la demande : « Vous avez déjà le coffre. Il vous manque quelqu'un qui regarde chaque paiement et vous dit, en français, quand quelque chose ne colle pas. »""")

# 7. Marché — ROMAIN
s = base(("Mise sur le marché", "aucun pourcentage de part de marché : un entonnoir, chaque étape sourcée"), 7, who="ROMAIN")
title(s, "Première année : 62 organisations présentées, 3 à 6 clients payants.", size=32)
flow(s, [("62 contactables", "Retro9000 30 + équipes de L1 10 + protocoles > 10 M$ sur Avalanche 22, présentées par l'écosystème"),
         ("31 en observation", "× 50 % : hypothèse H4, la seule non sourcée, mesurée dès octobre (± 12 points)"),
         ("3 à 6 payants", "× 8,9 – 18,5 % : conversion essai → payant du SaaS B2B sans carte bancaire")], y=Inches(2.4), h=Inches(1.5), highlight=(2,))
rows(s, [["Quand", "Jalon"],
         ["oct. 2026", "dépôt public · ≥ 10 organisations en observation · dossier subvention"],
         ["nov. – déc.", "portage en Guard + Module de Safe · mesure de H4 · faux positifs réels < 5 %"],
         ["janv. 2027", "contrat gelé, audit externe, puis premiers clients payants"],
         ["mars 2027", "même code sur une 2e chaîne EVM : marché × 6 à 8"],
         ["fin 2027 – mi-2028", "point mort : 17 clients Standard (7 300 €/mois de coûts fixes) ; plus tôt avec un client Premium"]],
     y=Inches(4.1), col_w=[Inches(2.6), W - 2 * M - Inches(2.6)], h_row=Inches(0.34), size=11.5)
source(s, "shared/business-marche.md § 3 · shared/business-mise-sur-le-marche.md § 3 et 3 bis")
notes(s, """[4:20 → 4:45]  ROMAIN
« Première année : 62 organisations présentées par l'écosystème Avalanche, la moitié en observation, 3 à 6 clients payants selon les taux de conversion du SaaS B2B. L'audit externe avant le premier euro. Puis le même code sur les autres chaînes compatibles : point mort à 17 clients, entre fin 2027 et mi-2028, plus tôt avec un seul client Premium. »

Si on a droit à 4 min seulement : sauter cette slide, les chiffres sont en annexe.
Si « pourquoi si peu ? » : « Parce qu'on ne prend que ce que l'entonnoir sourcé donne. L'année 1 sert aux références et aux données réelles. »""")

# 8. Équipe, limites, suite — TIMÉO (limites), ROMAIN (clôture)
s = base(("Équipe · limites · suite", "36 heures"), 8, who="TIMÉO · ROMAIN")
title(s, "Conçu pour être vérifié, pas pour être cru.", size=36)
colw = int((W - 2 * M - Inches(0.4)) / 2)
text(s, M, Inches(2.5), colw, Inches(0.4), "Ce qu'on ne cache pas", size=14, color=ORANGE, bold=True)
text(s, M, Inches(2.95), colw, Inches(2.4), ["•  Données synthétiques : une organisation fictive, trois mois de trafic.", "•  Contrat non audité par un tiers ; réseau de test.", "•  Le multisig de la démo tient lieu du Safe du client : le greffon reste à écrire.", "•  Aucun client interrogé, aucun prix validé par le marché."], size=14, color=TEXT, spacing=1.35)
x2 = M + colw + Inches(0.4)
text(s, x2, Inches(2.5), colw, Inches(0.4), "Les 90 prochains jours", size=14, color=ACCENT, bold=True)
text(s, x2, Inches(2.95), colw, Inches(2.4), ["•  Dès ce mois-ci : 10 organisations en observation gratuite, présentées par l'écosystème Avalanche.", "•  Portage en Guard + Module de Safe · notifications · rejeu de Bybit et Drift sur données réelles.", "•  Audit externe financé par subvention, avant le premier euro."], size=14, color=TEXT, spacing=1.35)
rect(s, M, Inches(5.45), Inches(0.08), Inches(0.75), fill=ACCENT)
text(s, M + Inches(0.3), Inches(5.4), W - 2 * M, Inches(0.9), "Vos fonds. Vos signataires. Votre dernier mot.", size=26, color=INK, font=DISPLAY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, M + Inches(0.3), Inches(6.15), W - 2 * M, Inches(0.4), "Romain, business · Timéo, technique · github.com/veryromain/hackathon-ia-cyber-romain-timeo", size=11, color=FAINT)
notes(s, """[4:45 → 5:00]  TIMÉO
« Ce qu'on ne cache pas : données synthétiques, contrat pas encore audité, le multisig de la démo tient lieu du Safe du client. Ce qu'il nous reste : le greffon Safe, l'audit, et surtout de vraies données. »

ROMAIN
« Dès ce mois-ci, dix organisations en observation gratuite. Breaker : vos fonds, vos signataires, votre dernier mot. Merci. »
(regarder le jury, s'arrêter ; les annexes A1 à A4 servent aux questions)""")

# ---- Annexes -------------------------------------------------------------------
s = base(("Annexe A1 · Conformité", "DORA, MiCA, LCB-FT, AI Act, et comment un auditeur vérifie"), "A1", annex=True, who="ROMAIN")
title(s, "Nous ne détenons jamais de fonds. Chaque décision est sur la chaîne, avec ses raisons.", size=28)
rows(s, [["Cadre", "Ce que ça implique pour Breaker", "Preuve"],
         ["MiCA", "Aucune fonction ne peut transférer sans les signatures humaines du client : hors garde d'actifs. Nous sommes éditeur d'un outil, pas dépositaire.", "seul safeTransfer dans execute, quorum requis ; invariant I1"],
         ["DORA", "Pour un client régulé, Breaker est un prestataire tiers de services TIC (à confirmer, mentor KPMG). Le rapport d'incident pré-rempli aide à classer et déclarer dans les délais (règl. délégué 2025/301).", "ia-1/score/rapport.py · shared/dora-notes.md"],
         ["LCB-FT", "Listes OFAC et ScamSniffer consultées ; refus pur des adresses sanctionnées activable par le client dans son contrat : ce n'est pas nous qui bloquons.", "ia-1/oracle/sources_publiques.py · code FLAGGED_ADDRESS"],
         ["AI Act", "Le modèle de langage n'explique que : il ne décide rien. Règles lisibles, chaque alerte cite ses codes ; garde-fous contre l'injection ; validation humaine toujours.", "ia-1/score/explication.py · regles.py"],
         ["Auditabilité", "Chaque signalement est un événement on-chain avec ses raisons ; l'oracle ne retient une accusation que s'il retrouve la citation exacte et en inscrit le hash. Tout se rejoue depuis le dépôt.", "RiskRegistry · evidence_hash · scenario_*.js"]],
     y=Inches(2.3), col_w=[Inches(1.6), Inches(6.9), W - 2 * M - Inches(8.5)], h_row=Inches(0.66), size=11)
notes(s, "ROMAIN répond aux questions de conformité ; TIMÉO complète sur la preuve technique (événements on-chain, hash de preuve).")

s = base(("Annexe A2 · Playbook de réponse", "qui est alerté, ce qui est automatique, ce qui reste humain"), "A2", annex=True, who="TIMÉO")
title(s, "Automatique : regarder, expliquer, freiner. Humain : décider, toujours.", size=28)
rows(s, [["Niveau", "Déclencheur", "Automatique", "Humain", "Alerté"],
         ["Aucun", "bénéficiaire connu, montant habituel", "journalisé : score et raisons", "signatures normales", "—"],
         ["Signature en plus (≥ 0,30)", "nouveau bénéficiaire, montant inhabituel, « urgent », hors heures", "exige une signature de plus ; explication en français", "un signataire supplémentaire relit « ce que vous signez »", "tous les signataires (tableau de bord, e-mail / Telegram)"],
         ["Mise en attente (≥ 0,75)", "rafale, adresse signalée, fonds souillés, sosie, nouveau signataire qui pousse un gros paiement", "attente (180 s en démo, 24 h en réel) + signature en plus ; rapport d'incident pré-rempli", "vérifier, annuler, ou lever à l'unanimité ; juger vraie / fausse alerte", "tous les signataires + responsable désigné"],
         ["Gel", "clé compromise, signature sous contrainte", "clé d'identité : révocation immédiate par la victime seule ; clé de contrainte : gel silencieux, alerte privée", "remplacer la clé, dégeler à la majorité des clés saines", "canal privé aux autres signataires, jamais on-chain"]],
     y=Inches(2.3), col_w=[Inches(1.9), Inches(2.7), Inches(2.9), Inches(2.4), W - 2 * M - Inches(9.9)], h_row=Inches(0.78), size=10.5)
notes(s, "TIMÉO présente le playbook ; les seuils sont ceux de ia-1/score/regles.py (SEUIL_STEP_UP 0,30 ; SEUIL_HOLD 0,75).")

s = base(("Annexe A3 · Sécurité du contrat", "chaque phrase est vérifiable en une commande"), "A3", annex=True, who="TIMÉO")
title(s, "Pas encore audité par un tiers. Voici ce qu'on a fait à la place, et ce que ça vaut.", size=28)
tiles(s, [("0", "détection haute ou moyenne (Slither 0.11, solc 0.8.24)", ACCENT), ("50", "tests unitaires (npx hardhat test)", INK), ("6 926", "appels aléatoires, 300 séquences, 8 types d'acteurs", INK), ("0", "invariant violé sur les 6 promesses du contrat (I1–I6)", ACCENT)], y=Inches(2.4), h=Inches(1.6))
text(s, M, Inches(4.3), W - 2 * M, Inches(1.8), ["•  L'architecture borne le risque : aucune fonction, pas même la nôtre, ne transfère sans les signatures du client. Le pire bug possible est un faux ralentissement.", "•  Code public, licence MIT, commandes dans shared/audit-contrat.md.", "•  Audit externe avant le premier client payant ; surface d'environ 500 lignes, sans garde de fonds."], size=14, color=TEXT, spacing=1.35)
notes(s, "TIMÉO. Ne jamais dire « audité » sans « par nous-mêmes », ni « aucune vulnérabilité » (dire : aucune détectée par ces méthodes). Pas de montant d'audit comme si on avait un devis.")

s = base(("Annexe A4 · Les chiffres et leurs sources", "rien d'arbitraire"), "A4", annex=True, who="ROMAIN")
title(s, "Chaque nombre dit à l'oral a une source externe ou un calcul explicite.", size=28)
rows(s, [["Chiffre", "Source ou calcul"],
         ["8 694 · 1 359 · 675 protocoles", "API DeFiLlama api.llama.fi/protocols, lue le 11/10/2026 ; seuils TVL > 0, > 1 M$, > 10 M$"],
         ["561 · 71 · 22 sur Avalanche", "même API, champ chainTvls.Avalanche"],
         ["≈ 220 DAO > 1 M$", "DeepDAO (T1 2026), via DAO Times / eco.com ; à confirmer sur deepdao.io"],
         ["35,25 Md$ · 61 M comptes", "Safe Foundation, rapport T1 2026 (23/04/2026)"],
         ["189 € · 669 € · 999 $", "safe.global/pricing (Safe Pro, 8/10/2026) · fireblocks.com/pricing"],
         ["≈ 150 incidents · 1,3 M$ médiane", "TRM Labs 2025 ; CertiK : > 700 incidents, médiane 104 k$ (périmètre plus large)"],
         ["8,9 % – 18,5 %", "conversion essai → payant SaaS B2B sans carte : ChartMogul (200 produits), First Page Sage (86 entreprises)"],
         ["95 % · 91 % · 5,1 %", "jeu final préparé à l'aveugle, 40 fraudes, 234 paiements légitimes (shared/mesures.md)"],
         ["0,002 $ · 1,2 $", "gas mesuré sur Fuji (shared/frais-gas.md) · Bedrock Opus 4.8 à 5 $ / 25 $ par million de tokens"]],
     y=Inches(2.3), col_w=[Inches(3.4), W - 2 * M - Inches(3.4)], h_row=Inches(0.37), size=11)
notes(s, "ROMAIN. Si un chiffre est contesté : donner la source, et dire ce qui est hypothèse (H1 à H11, nommées dans les documents).")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Breaker-pitch.pptx")
prs.save(out)
print("écrit", out, "-", len(prs.slides), "slides")
