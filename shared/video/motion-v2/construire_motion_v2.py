#!/usr/bin/env python3
"""Construit la v2 du motion design de Breaker (livrable L1) : page animée + voix off + mp4.

Pipeline, dans cet ordre :
  1. --voix   : chaque phrase de la voix off est synthétisée avec Piper (voix française locale, hors ligne),
                les durées mesurées fixent la chronologie des plans (timeline.json), puis la piste complète est
                assemblée (voix-off.wav, voix-off.mp3).
  2. --html   : écrit motion-v2.html, une page 1920x1080 pilotée par window.seek(t) : chaque image est une
                fonction pure du temps, donc rendue à l'identique dans le navigateur et par le moteur de rendu.
                Ouverte dans Chrome, la page joue la vidéo avec la voix (Espace : lecture / pause, R : début,
                F : plein écran, flèches : plan précédent / suivant).
  3. --rendu  : capture chaque image à 30 i/s avec Playwright (Chrome installé sur la machine) puis encode
                motion-v2.mp4 avec ffmpeg (H.264 + voix AAC).
  --tout enchaîne les trois. Le style reprend la charte du site vitrine (ia-2/site-vitrine/dist/style.css) :
  bleu nuit, vert citron, verre, Manrope / DM Sans / IBM Plex Mono. Le rythme s'inspire des reels de motion
  design « typographie cinétique » : un ou deux mots géants par coupe, flou de mouvement, chiffres incarnés par
  des formes, HUD monospace, cercles concentriques, bandeau de texte répété.

Outils : piper-tts (uv tool install piper-tts), playwright (uv tool install playwright) + Google Chrome, ffmpeg.
Voix : ~/.local/share/piper-voices/fr_FR-siwis-medium.onnx (téléchargée automatiquement si absente).
Tous les chiffres viennent de démonstrations jouées (JOURNAL.md, shared/mesures.md, shared/plan-video-motion.md).
Vocabulaire fixé : signature en plus · mise en attente · Cosignataire ; jamais « bloqué », « l'IA bloque »,
« nous avons rejoué Drift », ni la clé de contrainte, ni un montant réel sauvé.
"""
import argparse, base64, json, os, shutil, subprocess, sys, urllib.request, wave

D = os.path.dirname(os.path.abspath(__file__))
MATIERE = os.path.dirname(D)                       # shared/video : fiches PNG de Timéo
VOIX = os.path.join(D, "voix")                     # segments wav (régénérables, ignorés par git)
FRAMES = os.path.join(D, "_frames")                # images du rendu (ignorées par git)
HTML_OUT = os.path.join(D, "motion-v2.html")
MP4_OUT = os.path.join(D, "motion-v2.mp4")
TIMELINE = os.path.join(D, "timeline.json")
FPS = 30
VOICE_DIR = os.path.expanduser("~/.local/share/piper-voices")
VOICE = os.environ.get("PIPER_MODEL", os.path.join(VOICE_DIR, "fr_FR-siwis-medium.onnx"))
VOICE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"
LENGTH_SCALE = os.environ.get("PIPER_LENGTH", "0.88")   # < 1 = débit un peu plus rapide

# ---------------------------------------------------------------------------------------------------------
# Les plans et la voix off. Chaque phrase est un segment ; les visuels sont calés sur le début de chaque
# segment (S.seg[i] dans le JavaScript). lead : silence après la coupe ; tail : tenue après la dernière phrase.
# ---------------------------------------------------------------------------------------------------------
# Version courte (11/10, 11 h 15) : 7 plans, cible 70 s. Drift corrigé : signataires trompés (pré-signature,
# conseil de sécurité à 2 sur 5, 1er avril 2026), aucune clé volée ; le rejeu Fuji reprend la cadence avec
# l'attaquant au seuil (2 signatures sur 5).
SCENES = [
    dict(id="hook", lead=0.25, tail=0.3, mention="", segs=[
        "Bybit : un milliard quatre cent soixante millions de dollars.",
        "Drift : deux cent quatre-vingts millions, trente et un retraits en douze minutes.",
        "Aucune clé volée : des signataires trompés ont validé.",
    ]),
    dict(id="marque", lead=0.2, tail=0.5, mention="", segs=[
        "Un multisig arrête une clé volée. Pas un mauvais paiement.",
        "Breaker se greffe sur votre coffre, et note chaque paiement avant son exécution.",
    ]),
    dict(id="attaque", lead=0.2, tail=1.0, mention="Avalanche Fuji · réseau de test · accéléré", segs=[
        "Trois virements urgents vers une adresse jamais vue : deux cent quatre-vingt mille cinq cents.",
        "En moins de dix secondes, chacun est mis en attente, inscrit sur la chaîne, et expliqué en français.",
        "Il manque une signature : rien ne part. Zéro sorti.",
    ]),
    dict(id="oracle", lead=0.2, tail=0.6, mention="Avalanche Fuji · accéléré : 2 min 10 en réel", segs=[
        "Le garde lit aussi le Web : adresse sous sanctions, l'attente reste, même avec trois signatures.",
    ]),
    dict(id="drift", lead=0.2, tail=1.0, mention="Avalanche Fuji · attaquant au seuil : 2 signatures sur 5", segs=[
        "La cadence de Drift, avec le même seuil : deux signatures sur cinq. Trente et un retraits, zéro sorti.",
    ]),
    dict(id="chiffres", lead=0.2, tail=0.6, mention="jeu de test final · formes de fraude jamais vues · données synthétiques", segs=[
        "Sur des fraudes jamais vues : quatre-vingt-onze pour cent des montants mis en attente.",
        "Trente jours d'essai, puis cent quarante-neuf euros par mois.",
    ]),
    dict(id="fin", lead=0.2, tail=2.2, mention="", segs=[
        "Prototype non audité, sur réseau de test. Breaker : gardez la main sur votre trésorerie.",
    ]),
]
GAP = 0.25  # silence entre deux phrases d'un même plan


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def wav_duration(path):
    with wave.open(path, "rb") as w:
        return w.getnframes() / w.getframerate(), w.getframerate(), w.getnchannels(), w.getsampwidth()


# ---------------------------------------------------------------------------------------------------------
# 1. Voix off
# ---------------------------------------------------------------------------------------------------------
def etape_voix():
    if not shutil.which("piper"):
        sys.exit("piper introuvable : uv tool install piper-tts (ou pipx install piper-tts)")
    if not os.path.exists(VOICE):
        os.makedirs(os.path.dirname(VOICE), exist_ok=True)
        for suffix in ("", ".json"):
            print("téléchargement de la voix", VOICE + suffix)
            urllib.request.urlretrieve(VOICE_URL + suffix, VOICE + suffix)
    os.makedirs(VOIX, exist_ok=True)
    t = 0.0
    timeline = dict(fps=FPS, scenes=[])
    sr = None
    for si, sc in enumerate(SCENES):
        rel = sc["lead"]
        segs = []
        for ki, text in enumerate(sc["segs"]):
            out = os.path.join(VOIX, f"{si:02d}-{ki:02d}.wav")
            stamp = os.path.join(VOIX, f"{si:02d}-{ki:02d}.txt")
            if not (os.path.exists(out) and os.path.exists(stamp) and open(stamp).read() == text + LENGTH_SCALE):
                run(["piper", "-m", VOICE, "-f", out, "--length-scale", LENGTH_SCALE, "--sentence-silence", "0.22"],
                    input=text.encode("utf-8"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                open(stamp, "w").write(text + LENGTH_SCALE)
            dur, sr_, ch, sw = wav_duration(out)
            assert ch == 1 and sw == 2, "wav mono 16 bits attendu"
            sr = sr or sr_
            segs.append(dict(text=text, rel=round(rel, 3), start=round(t + rel, 3), dur=round(dur, 3), file=out))
            rel += dur + GAP
        sdur = rel - GAP + sc["tail"]
        timeline["scenes"].append(dict(id=sc["id"], mention=sc["mention"], start=round(t, 3), dur=round(sdur, 3), segs=segs))
        t += sdur
    timeline["total"] = round(t + 0.5, 3)
    json.dump(timeline, open(TIMELINE, "w"), ensure_ascii=False, indent=1)
    # Piste complète : silence + segments collés à leur instant.
    n = int(timeline["total"] * sr) + sr
    buf = bytearray(n * 2)
    for sc in timeline["scenes"]:
        for sg in sc["segs"]:
            with wave.open(sg["file"], "rb") as w:
                data = w.readframes(w.getnframes())
            off = int(sg["start"] * sr) * 2
            buf[off:off + len(data)] = data
    wav_out = os.path.join(D, "voix-off.wav")
    with wave.open(wav_out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(buf))
    # mp3 normalisé pour la page HTML (petit) ; le mp4 repart du wav.
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav_out, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-ar", "44100", "-b:a", "112k", os.path.join(D, "voix-off.mp3")])
    m, s = divmod(int(timeline["total"]), 60)
    print(f"voix off : {len(timeline['scenes'])} plans, durée totale {m}:{s:02d}")
    for sc in timeline["scenes"]:
        print(f"  {sc['start']:6.1f}s  {sc['id']:<13} {sc['dur']:5.1f}s")
    return timeline


# ---------------------------------------------------------------------------------------------------------
# 2. La page animée
# ---------------------------------------------------------------------------------------------------------
def b64(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


HTML = r'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>Breaker, la démonstration (motion v2)</title>
<style>__POLICES__</style>
<style>
:root{--bg:#07111f;--ink:#f6f9fc;--text:#e7edf4;--muted:rgba(231,237,244,.7);--faint:rgba(231,237,244,.52);--line:rgba(255,255,255,.11);
--accent:#c7fa70;--on-accent:#142008;--blue:#a8bfff;--orange:#ffc481;--red:#ff6b6b;
--glass:linear-gradient(135deg,rgba(255,255,255,.11),rgba(255,255,255,.03) 46%,rgba(255,255,255,.07));--glass-edge:rgba(255,255,255,.14);
--display:'Manrope','DM Sans',system-ui,sans-serif;--body:'DM Sans',system-ui,sans-serif;--mono:'IBM Plex Mono',ui-monospace,Menlo,monospace}
html,body{margin:0;height:100%;background:#000;overflow:hidden}
#stage{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0;background:var(--bg);color:var(--text);font-family:var(--body);overflow:hidden;-webkit-font-smoothing:antialiased}
.aurora i{position:absolute;border-radius:50%;filter:blur(110px)}
.aurora i:nth-child(1){width:900px;height:900px;left:-250px;top:-350px;background:rgba(199,250,112,.20)}
.aurora i:nth-child(2){width:1000px;height:1000px;right:-350px;top:100px;background:rgba(28,150,140,.30)}
.aurora i:nth-child(3){width:800px;height:800px;left:500px;bottom:-500px;background:rgba(52,96,214,.36)}
.field{position:absolute;inset:0;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='26' height='26'%3E%3Ccircle cx='13' cy='13' r='1.5' fill='%23ffffff' fill-opacity='.14'/%3E%3C/svg%3E");-webkit-mask-image:radial-gradient(ellipse at 70% 40%,#000,rgba(0,0,0,.5) 50%,transparent 85%);mask-image:radial-gradient(ellipse at 70% 40%,#000,rgba(0,0,0,.5) 50%,transparent 85%)}
#rings{position:absolute;inset:0;width:1920px;height:1080px;pointer-events:none}
#ticker{position:absolute;left:0;right:0;top:470px;white-space:nowrap;font:800 150px/1 var(--display);letter-spacing:-.04em;color:var(--orange);opacity:0;pointer-events:none}
#ticker.lime{color:var(--accent)}
#flash{position:absolute;inset:0;background:var(--accent);opacity:0;pointer-events:none;mix-blend-mode:screen}
#grain{position:absolute;inset:0;width:1920px;height:1080px;opacity:.07;pointer-events:none;mix-blend-mode:overlay}
.scene{position:absolute;inset:0;display:none}
.scene.on{display:block}
.el{position:absolute;opacity:0;will-change:transform,opacity,filter}
.k1{font:800 190px/.95 var(--display);letter-spacing:-.045em;color:var(--ink);white-space:nowrap}
.k2{font:800 120px/.98 var(--display);letter-spacing:-.04em;color:var(--ink);white-space:nowrap}
.k3{font:800 78px/1 var(--display);letter-spacing:-.03em;color:var(--ink);white-space:nowrap}
.h{font:600 60px/1.08 var(--display);letter-spacing:-.025em;color:var(--ink);text-wrap:balance}
.sub{font:400 32px/1.35 var(--body);color:var(--muted)}
.mono{font:500 26px/1.4 var(--mono);color:var(--faint)}
.lime{color:var(--accent)} .amber{color:var(--orange)} .sky{color:var(--blue)}
.chip{display:inline-block;font:500 28px/1 var(--mono);padding:16px 24px;border-radius:14px;border:1px solid var(--glass-edge);background:rgba(255,255,255,.05);color:var(--muted);white-space:nowrap}
.chip.ok{background:var(--accent);color:var(--on-accent);border-color:transparent}
.chip.hold{background:var(--orange);color:#2a1a00;border-color:transparent}
.chip.step{background:var(--blue);color:#101a3a;border-color:transparent}
.chip.big{font-size:40px;padding:22px 34px;border-radius:18px}
.card.solid{background:var(--glass),#0d1a2b}
.card{background:var(--glass);border:1px solid var(--glass-edge);border-radius:24px;box-shadow:inset 0 1px 0 rgba(255,255,255,.24),0 26px 50px -22px rgba(0,0,0,.7);padding:34px 40px}
.pay{width:860px;display:grid;grid-template-columns:1fr auto;gap:10px 30px;align-items:center}
.pay b{font:800 54px/1 var(--display);letter-spacing:-.02em;color:var(--ink)} .pay small{font:400 24px/1.3 var(--mono);color:var(--faint)}
.pay .who{font:500 30px/1.2 var(--body);color:var(--text)} .pay .st{text-align:right;display:flex;flex-direction:column;gap:10px;align-items:flex-end}
.term{width:1000px;min-height:420px;font:500 26px/1.55 var(--mono);color:var(--text);background:#040a14;border:1px solid var(--line);border-radius:22px;padding:30px 36px;white-space:pre-wrap}
.term .k{color:var(--accent)} .term .o{color:var(--orange)} .term .b{color:var(--blue)} .term .d{color:var(--faint)}
.term .hl{background:rgba(199,250,112,.22);outline:2px solid var(--accent);border-radius:4px;padding:0 4px}
.fiche{border-radius:18px;overflow:hidden;background:#fff;box-shadow:0 40px 80px -30px rgba(0,0,0,.85);border:1px solid var(--glass-edge)}
.fiche img{display:block;width:100%;height:auto}
.fiche i{position:absolute;border:4px solid var(--accent);border-radius:10px;background:rgba(199,250,112,.12);box-shadow:0 0 0 6px rgba(199,250,112,.18)}
.brand{display:flex;align-items:center;gap:26px;font:800 150px/1 var(--display);letter-spacing:-.05em;color:var(--ink);white-space:nowrap}
.brand i{font-style:normal;color:var(--accent)}
.mark{display:block}
.blob{position:absolute;border-radius:50%;background:radial-gradient(circle at 35% 30%,rgba(255,196,129,.95),rgba(255,196,129,.55) 55%,rgba(255,196,129,.25) 100%);box-shadow:0 60px 120px -40px rgba(255,196,129,.6)}
.blob.lime{background:radial-gradient(circle at 35% 30%,rgba(199,250,112,.95),rgba(199,250,112,.5) 55%,rgba(199,250,112,.2))}
.key{width:150px;height:150px;border-radius:40px;background:var(--glass);border:1px solid var(--glass-edge);display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,.24)}
.key svg{width:80px;height:80px}
.check{position:absolute;right:-18px;top:-18px;width:60px;height:60px;border-radius:50%;background:var(--accent);color:var(--on-accent);display:flex;align-items:center;justify-content:center;font:800 40px/1 var(--display)}
.pill{font:800 64px/1 var(--display);letter-spacing:-.03em;padding:34px 54px;border-radius:999px;white-space:nowrap}
.pill.ok{background:var(--accent);color:var(--on-accent)} .pill.step{background:var(--blue);color:#101a3a} .pill.hold{background:var(--orange);color:#2a1a00}
.bars{display:flex;gap:9px;align-items:flex-end;height:260px}
.bars i{display:block;width:40px;height:100%;border-radius:8px;background:rgba(255,255,255,.06);border:1px solid var(--line);position:relative;overflow:hidden}
.bars i b{position:absolute;left:0;right:0;bottom:0;height:0;background:var(--orange)}
.bars i.wait{border-color:var(--accent);box-shadow:inset 0 0 0 2px var(--accent)}
.row{display:flex;gap:18px;align-items:center}
.dec{width:1400px;display:grid;grid-template-columns:1fr auto;gap:8px 30px;align-items:center;padding:28px 36px}
.dec b{font:800 46px/1 var(--display);letter-spacing:-.02em;color:var(--ink)} .dec span{font:400 28px/1.3 var(--body);color:var(--muted)}
.gauge{width:900px;height:22px;border-radius:11px;background:rgba(255,255,255,.07);border:1px solid var(--line);overflow:hidden}
.gauge b{display:block;height:100%;width:0;background:var(--accent)}
.hud{position:absolute;left:60px;top:40px;font:500 22px/1 var(--mono);color:var(--faint);letter-spacing:.04em}
.hud2{position:absolute;right:60px;top:40px;font:500 22px/1 var(--mono);color:var(--faint);letter-spacing:.04em;text-align:right}
.mention{position:absolute;right:60px;top:78px;font:500 22px/1 var(--mono);color:var(--faint);border:1px solid var(--line);padding:9px 16px;border-radius:10px;opacity:0;background:rgba(7,17,31,.6)}
.subbar{position:absolute;left:0;right:0;bottom:0;padding:30px 200px 44px;text-align:center;font:500 34px/1.3 var(--body);color:var(--ink);text-wrap:balance;background:linear-gradient(transparent,rgba(7,17,31,.9) 55%)}
.subbar span{background:rgba(0,0,0,.5);padding:6px 16px;border-radius:10px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.prog{position:absolute;left:0;bottom:0;height:6px;background:var(--accent);width:0}
.help{position:fixed;left:14px;bottom:12px;font:12px var(--mono);color:#889;background:#0b1626;padding:6px 10px;border-radius:4px;border:1px solid #223;z-index:9}
</style></head><body>
<svg width="0" height="0" style="position:absolute"><defs>
<symbol id="mark" viewBox="0 0 34 38"><path d="M1 1h22.6L33 10.4V37H10.4L1 27.6z" fill="#c7fa70" stroke="#c7fa70" stroke-width="2" stroke-linejoin="round"/><path d="M10.5 9h7.25a5.25 5.25 0 0 1 0 10.5H10.5zM10.5 17.5h8.25a5.75 5.75 0 0 1 0 11.5H10.5z" fill="#142008"/><path d="M14.5 12.6h3.1a1.65 1.65 0 0 1 0 3.3h-3.1zM14.5 21.6h4.1a1.9 1.9 0 0 1 0 3.8h-4.1z" fill="#c7fa70"/></symbol>
<symbol id="key" viewBox="0 0 24 24"><path d="M14.5 3a6.5 6.5 0 1 0 5.7 9.6L21 13.4V16l2 0v2h-2v2h-2v2h-3v-5.2l-2.4-2.4A6.5 6.5 0 0 0 14.5 3zm0 3a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5z" fill="#f6f9fc"/></symbol>
<filter id="noise"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>
</defs></svg>
<div id="stage">
<div class="aurora"><i id="au1"></i><i id="au2"></i><i id="au3"></i></div>
<div class="field"></div>
<div id="ticker"></div>
<svg id="rings"></svg>

<!-- 1. Le problème -->
<section class="scene" id="s-hook">
  <div class="blob el" id="h-blob1" style="left:1100px;top:160px;width:720px;height:720px"></div>
  <div class="blob el" id="h-blob2" style="left:1420px;top:560px;width:330px;height:330px"></div>
  <div class="el mono" id="h-l1" style="left:120px;top:300px">BYBIT · 21 FÉVRIER 2025 · 3 SIGNATAIRES SUR 6 TROMPÉS</div>
  <div class="el k1 amber" id="h-n1" style="left:112px;top:350px">1,46 Md$</div>
  <div class="el mono" id="h-l2" style="left:120px;top:600px">DRIFT · 1ER AVRIL 2026 · 31 RETRAITS EN 12 MINUTES</div>
  <div class="el k1 amber" id="h-n2" style="left:112px;top:650px">280 M$</div>
  <div class="el bars" id="h-bars" style="left:1000px;top:640px;height:160px"></div>
  <div class="el k1" id="h-w1" style="left:112px;top:260px">Aucune clé volée.</div>
  <div class="el k2 amber" id="h-w2" style="left:120px;top:500px">Des signataires<br>trompés ont validé.</div>
</section>

<!-- 2. La marque -->
<section class="scene" id="s-marque">
  <div class="el key" id="m-k1" style="left:120px;top:250px"><svg><use href="#key"/></svg><div class="check el" id="m-c1">✓</div></div>
  <div class="el key" id="m-k2" style="left:310px;top:250px"><svg><use href="#key"/></svg><div class="check el" id="m-c2">✓</div></div>
  <div class="el key" id="m-k3" style="left:500px;top:250px"><svg><use href="#key"/></svg><div class="check el" id="m-c3">✓</div></div>
  <div class="el h" id="m-t1" style="left:120px;top:470px;width:1000px">Un multisig arrête une clé volée.</div>
  <div class="el k2 amber" id="m-t2" style="left:120px;top:600px">Pas un mauvais paiement.</div>
  <div class="el card pay solid" id="m-pay" style="left:1060px;top:250px;width:720px"><div><b>95 000 mUSD</b><br><span class="who">→ adresse jamais vue</span></div><div class="st"><span class="chip ok">2 / 2 signatures</span><span class="chip">validé de bonne foi</span></div></div>
  <div class="el" id="m-logo" style="left:120px;top:250px"><svg class="mark" width="190" height="212"><use href="#mark"/></svg></div>
  <div class="el brand" id="m-brand" style="left:350px;top:275px">breaker<i>.</i></div>
  <div class="el sub" id="m-tag" style="left:120px;top:520px;width:1400px;font-size:40px;color:var(--text)">La garde antifraude qui se greffe sur le coffre que vous avez déjà.</div>
  <div class="el h" id="m-h1" style="left:120px;top:640px;width:1600px;font-size:76px">Chaque paiement noté<br><span class="lime">avant</span> d'être exécuté.</div>
</section>

<!-- 3. L'attaque -->
<section class="scene" id="s-attaque">
  <div class="el h" id="a-t" style="left:120px;top:140px;width:1100px">Trois virements vers une adresse <span class="amber">jamais vue</span>.</div>
  <div class="el card pay solid" id="a-p1" style="left:120px;top:320px;width:900px;padding:24px 36px"><div><b>95 000 mUSD</b> <small>→ 0x2dd0…76f6</small><br><small>« URGENT · virement confidentiel »</small></div><div class="st"><span class="chip hold el" id="a-h1" style="position:relative">mise en attente · 10 s</span></div></div>
  <div class="el card pay solid" id="a-p2" style="left:120px;top:500px;width:900px;padding:24px 36px"><div><b>93 500 mUSD</b> <small>→ 0x2dd0…76f6</small><br><small>paiement 11</small></div><div class="st"><span class="chip hold el" id="a-h2" style="position:relative">mise en attente · 7 s</span></div></div>
  <div class="el card pay solid" id="a-p3" style="left:120px;top:680px;width:900px;padding:24px 36px"><div><b>92 000 mUSD</b> <small>→ 0x2dd0…76f6</small><br><small>« Opération validée par la direction »</small></div><div class="st"><span class="chip hold el" id="a-h3" style="position:relative">mise en attente · 9 s</span></div></div>
  <div class="el k2 amber" id="a-sum" style="left:1120px;top:420px">0</div>
  <div class="el sub" id="a-suml" style="left:1125px;top:560px;width:700px">mUSD proposés par deux signataires trompés</div>
  <div class="el fiche" id="a-fiche" style="left:1120px;top:130px;width:680px"><img src="__IMG10__" alt=""><i style="left:2%;top:17%;width:96%;height:30%"></i></div>
  <div class="el k1 sky" id="a-sig" style="left:112px;top:220px">2 / 3</div>
  <div class="el h" id="a-sigl" style="left:120px;top:440px;width:1400px">signatures. Il en manque une : <span class="sky">rien ne part</span>.</div>
  <div class="el k1 lime" id="a-zero" style="left:112px;top:280px;font-size:300px">0 mUSD</div>
  <div class="el h" id="a-zerol" style="left:120px;top:630px;width:1500px">sorti, sur <span class="amber">280 500</span> proposés.</div>
</section>

<!-- 4. L'oracle -->
<section class="scene" id="s-oracle">
  <div class="el h" id="o-t" style="left:120px;top:140px;width:1200px">Le garde lit aussi <span class="lime">le Web</span>.</div>
  <div class="el term" id="o-term" style="left:120px;top:270px;min-height:380px"></div>
  <div class="el k2 amber" id="o-sanc" style="left:1180px;top:290px;font-size:110px">SANCTIONS</div>
  <div class="el chip step" id="o-c1" style="left:1180px;top:450px">inscrite au registre · on-chain</div>
  <div class="el chip hold" id="o-c2" style="left:1180px;top:540px">3 / 3 signatures · attente maintenue</div>
  <div class="el chip" id="o-c3" style="left:1180px;top:630px">25 000 mUSD · annulé</div>
</section>

<!-- 5. La cadence de Drift -->
<section class="scene" id="s-drift">
  <div class="el h" id="d-t" style="left:120px;top:130px;width:1200px">La cadence de Drift :<br><span class="amber">31 retraits en 12 minutes</span>.</div>
  <div class="el bars" id="d-bars" style="left:120px;top:320px;height:240px"></div>
  <div class="el mono" id="d-tk" style="left:120px;top:580px;width:1520px;display:flex;justify-content:space-between"><span>01:26:29</span><span>285 000 mUSD tentés · attaquant au seuil : 2 signatures sur 5</span><span>01:38:39</span></div>
  <div class="el k2 amber" id="d-count" style="left:1300px;top:150px;text-align:right;width:500px">0</div>
  <div class="el k2 lime" id="d-zero" style="left:120px;top:660px">0 mUSD sorti.</div>
  <div class="el h" id="d-zl" style="left:120px;top:800px;width:1600px;font-size:48px">Chaque retrait mis en attente : il manque la signature que l'attaquant n'a pas.</div>
</section>

<!-- 6. Les chiffres -->
<section class="scene" id="s-chiffres">
  <div class="el k1 lime" id="f-91" style="left:112px;top:150px;font-size:300px">0 %</div>
  <div class="el sub" id="f-91l" style="left:120px;top:470px;width:800px;font-size:36px">des montants frauduleux mis en attente</div>
  <div class="el k2 amber" id="f-51" style="left:1150px;top:200px">5,1 %</div>
  <div class="el sub" id="f-51l" style="left:1155px;top:340px;width:650px">de paiements légitimes retardés</div>
  <div class="el chip ok big" id="f-e1" style="left:1150px;top:480px">30 jours d'essai gratuit</div>
  <div class="el chip big" id="f-e2" style="left:1150px;top:590px">puis dès 149 € / mois</div>
</section>

<!-- 7. Fin -->
<section class="scene" id="s-fin">
  <div class="el mono" id="z-fine" style="left:120px;top:150px;width:1750px;line-height:1.6">PROTOTYPE DE HACKATHON · NON AUDITÉ · DONNÉES SYNTHÉTIQUES · RÉSEAU DE TEST AVALANCHE FUJI</div>
  <div class="el" id="z-logo" style="left:120px;top:300px"><svg class="mark" width="190" height="212"><use href="#mark"/></svg></div>
  <div class="el brand" id="z-brand" style="left:350px;top:325px">breaker<i>.</i></div>
  <div class="el h" id="z-h" style="left:120px;top:580px;width:1500px;font-size:88px">Gardez la main<br>sur votre <span class="lime">trésorerie</span>.</div>
  <div class="el sub" id="z-s" style="left:120px;top:830px;width:1500px">Construit pour Avalanche. Pensé pour les signataires.</div>
</section>

<svg id="grain"><rect width="100%" height="100%" filter="url(#noise)"/></svg>
<div id="flash"></div>
<div class="hud" id="hud">BREAKER · DÉMONSTRATION · 00:00:00</div>
<div class="hud2">1920 × 1080 · 30 i/s · SECURE HORIZONS 2026</div>
<div class="mention" id="mention"></div>
<div class="subbar"><span id="subtitle"></span></div>
<div class="prog" id="prog"></div>
</div>
<div class="help" id="help">Espace : lecture / pause · ← → : plans · R : début · F : plein écran · S : sous-titres</div>
<audio id="voice" src="__AUDIO__" preload="auto"></audio>
<script>
var TL = __TIMELINE__;
var $ = function(id){ return document.getElementById(id); };
var clamp = function(x,a,b){ return Math.max(a, Math.min(b, x)); };
var eo = function(p){ return 1 - Math.pow(1 - p, 4); };                     // sortie franche
var eb = function(p){ var c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); }; // léger rebond
var prog = function(rel, at, dur){ return clamp((rel - at) / (dur || .45), 0, 1); };
var fmt = function(n){ return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' '); };
function put(el, o, x, y, s, b){ el.style.opacity = o; el.style.transform = 'translate(' + x + 'px,' + y + 'px) scale(' + s + ')'; el.style.filter = b > .05 ? 'blur(' + b + 'px)' : 'none'; }
// Sorties : après `until`, l'élément s'efface en 0,25 s, avec un léger flou et un zoom.
function exitp(rel, until){ return until == null ? 0 : prog(rel, until, .25); }
// Entrées. slam : un mot géant qui claque (zoom arrière + flou de mouvement). rise : montée douce. slide : glisse latérale. pop : rebond.
function slam(el, rel, at, until, from){ var p = prog(rel, at, .5), e = eo(p), q = exitp(rel, until); from = from || 1.7;
  put(el, p <= 0 ? 0 : clamp(p * 5, 0, 1) * (1 - q), 0, (1 - e) * 10, from + (1 - from) * e + .05 * q, (1 - e) * 18 + q * 12); }
function rise(el, rel, at, until, dy){ var p = prog(rel, at, .6), e = eo(p), q = exitp(rel, until);
  put(el, e * (1 - q), 0, (1 - e) * (dy == null ? 50 : dy), 1 + .04 * q, (1 - e) * 8 + q * 10); }
function slide(el, rel, at, until, dx){ var p = prog(rel, at, .55), e = eo(p), q = exitp(rel, until);
  put(el, e * (1 - q), (1 - e) * (dx == null ? -140 : dx), 0, 1 + .04 * q, (1 - e) * 10 + q * 10); }
function pop(el, rel, at, until){ var p = prog(rel, at, .38), e = eb(p), q = exitp(rel, until);
  put(el, p <= 0 ? 0 : (1 - q), 0, 0, (.5 + .5 * e) * (1 + .05 * q), q * 8); }
function count(el, rel, at, dur, to, suffix){ var p = eo(prog(rel, at, dur)); el.textContent = fmt(p * to) + (suffix || ''); }
var RINGS = [];
function ring(cx, cy, age, color){ if (age > 0 && age < 1.3) RINGS.push([cx, cy, age, color]); }
function ticker(rel, on, text, lime){ var t = $('ticker'); t.className = lime ? 'lime' : ''; if (!on){ t.style.opacity = 0; return; }
  if (t.dataset.text !== text){ t.dataset.text = text; var s = ''; for (var i = 0; i < 8; i++) s += text + ' · '; t.textContent = s; }
  t.style.opacity = .13; t.style.transform = 'translateX(' + (-((rel * 260) % 1800)) + 'px)'; }
function bars(id, n){ var el = $(id); if (el.children.length) return; for (var i = 0; i < n; i++){ var b = document.createElement('i'); b.innerHTML = '<b></b>'; el.appendChild(b); } }
function typed(el, lines, rel){ var h = ''; lines.forEach(function(l){ if (rel >= l[0]) h += l[1]; }); if (el.dataset.h !== h){ el.dataset.h = h; el.innerHTML = h; } }

var TERM = [
 [0.1, "<span class='d'>$ python -m agent.agent --mode cosignataire --web …</span>\n<span class='d'>paiement 1 · 25 000 mUSD → 0x098b…2f96 · destinataire nouveau</span>\n"],
 [0.6, "agent · immédiat · <span class='b'>freiner</span> · signature en plus · 6,2 s\n"],
 [1.1, "<span class='d'>recherche Web…</span>\n"],
 [1.4, "  lu : etherscan.io/address/0x098B…2f96\n"],
 [1.6, "  lu : x.com/chainalysis/status/1514645222…\n"],
 [1.8, "  lu : basescan.org/address/0x098B…2f96\n"],
 [2.2, "accusation retenue (sanctions, 2 sources) :\n  <span class='hl'>« OFAC added a new ETH address to Lazarus Group's SDN entry : 0x098B716B…2f96 »</span>\n"],
 [3.3, "agent · après lecture du Web · <span class='o'>refuser</span> · mise en attente · 4,7 s\n"]
];

var DRAW = {
 hook: function(rel, S){ var a = S.seg[0], b = S.seg[1], c = S.seg[2];
  bars('h-bars', 31);
  var p1 = eo(prog(rel, a + .15, .9)); put($('h-blob1'), p1 * .9 * (1 - exitp(rel, c)), 0, 0, .2 + .8 * p1, 0);
  rise($('h-l1'), rel, a, c); slam($('h-n1'), rel, a + .15, c);
  var p2 = eo(prog(rel, b + .3, .8)); put($('h-blob2'), p2 * .9 * (1 - exitp(rel, c)), 0, 0, .2 + .8 * p2, 0);
  rise($('h-l2'), rel, b, c); slam($('h-n2'), rel, b + .15, c);
  rise($('h-bars'), rel, b + 1.3, c, 20); var ch = $('h-bars').children; for (var i = 0; i < 31; i++) ch[i].firstChild.style.height = (prog(rel, b + 1.4 + i * .05, .15) * 100) + '%';
  slam($('h-w1'), rel, c + .05); slam($('h-w2'), rel, c + 1.2);
  ring(960, 540, rel - (c + 1.2), '#ffc481'); },

 marque: function(rel, S){ var a = S.seg[0], b = S.seg[1];
  pop($('m-k1'), rel, a, b); pop($('m-k2'), rel, a + .1, b); pop($('m-k3'), rel, a + .2, b);
  pop($('m-c1'), rel, a + .5, b); pop($('m-c2'), rel, a + .6, b); pop($('m-c3'), rel, a + .7, b);
  rise($('m-t1'), rel, a + .1, b); slide($('m-pay'), rel, a + 1.2, b, 160); slam($('m-t2'), rel, a + 1.9, b);
  slam($('m-logo'), rel, b, null, 2.2); slam($('m-brand'), rel, b + .15, null, 1.4); rise($('m-tag'), rel, b + .6);
  slam($('m-h1'), rel, b + 2.3, null, 1.3); ring(960, 540, rel - b, '#c7fa70'); },

 attaque: function(rel, S){ var a = S.seg[0], b = S.seg[1], c = S.seg[2];
  rise($('a-t'), rel, a, c); slide($('a-p1'), rel, a + .3, c); slide($('a-p2'), rel, a + .5, c); slide($('a-p3'), rel, a + .7, c);
  rise($('a-sum'), rel, a + 1.6, b + 1.5); count($('a-sum'), rel, a + 1.7, 1.4, 280500); rise($('a-suml'), rel, a + 1.8, b + 1.5, 20);
  pop($('a-h1'), rel, b + .3, c); pop($('a-h2'), rel, b + .55, c); pop($('a-h3'), rel, b + .8, c);
  ring(880, 390, rel - (b + .3), '#ffc481'); ring(880, 570, rel - (b + .55), '#ffc481'); ring(880, 750, rel - (b + .8), '#ffc481');
  ticker(rel, rel >= b + .3 && rel < c, 'MISE EN ATTENTE', false);
  slide($('a-fiche'), rel, b + 1.7, c, 200);
  slam($('a-sig'), rel, c, c + 1.9); rise($('a-sigl'), rel, c + .4, c + 1.9);
  slam($('a-zero'), rel, c + 2.0, null, 2.4); rise($('a-zerol'), rel, c + 2.4); ring(760, 430, rel - (c + 2.0), '#c7fa70'); ring(760, 430, rel - (c + 2.15), '#c7fa70'); },

 oracle: function(rel, S){ var a = S.seg[0];
  rise($('o-t'), rel, a); rise($('o-term'), rel, a + .1); typed($('o-term'), TERM, rel - a);
  slam($('o-sanc'), rel, a + 2.3); ring(1500, 340, rel - (a + 2.3), '#ffc481');
  pop($('o-c1'), rel, a + 3.0); pop($('o-c2'), rel, a + 3.9); pop($('o-c3'), rel, a + 4.8); },

 drift: function(rel, S){ var a = S.seg[0], z = a + S.d[0] - 1.1; bars('d-bars', 31);
  rise($('d-t'), rel, a); rise($('d-bars'), rel, a + .3, null, 20); rise($('d-tk'), rel, a + .4, null, 10);
  var ch = $('d-bars').children, n = 0;
  for (var i = 0; i < 31; i++){ var p = prog(rel, a + .5 + i * .085, .18); ch[i].firstChild.style.height = (p * (45 + ((i * 37) % 55))) + '%'; if (p >= 1) n++; ch[i].className = rel >= a + .7 + i * .085 ? 'wait' : ''; }
  rise($('d-count'), rel, a + .4); $('d-count').textContent = n + ' / 31';
  ticker(rel, rel >= a + .8, 'MISE EN ATTENTE', false);
  slam($('d-zero'), rel, z); ring(500, 720, rel - z, '#c7fa70'); rise($('d-zl'), rel, z + .5); },

 chiffres: function(rel, S){ var a = S.seg[0], b = S.seg[1];
  rise($('f-91'), rel, a + .2); count($('f-91'), rel, a + .3, 1.6, 91, ' %'); rise($('f-91l'), rel, a + .4, null, 20);
  slam($('f-51'), rel, a + 2.4); rise($('f-51l'), rel, a + 2.6, null, 20);
  pop($('f-e1'), rel, b + .1); ring(1450, 520, rel - (b + .1), '#c7fa70'); pop($('f-e2'), rel, b + 1.3); },

 fin: function(rel, S){ var a = S.seg[0];
  rise($('z-fine'), rel, a, null, 20);
  slam($('z-logo'), rel, a + 2.6, null, 2.2); slam($('z-brand'), rel, a + 2.75, null, 1.4); ring(960, 540, rel - (a + 2.6), '#c7fa70');
  slam($('z-h'), rel, a + 3.3, null, 1.3); rise($('z-s'), rel, a + 4.3, null, 20); }
};
var ORDER = ['hook','marque','attaque','oracle','drift','chiffres','fin'];
var SECS = ORDER.map(function(k){ return $('s-' + k); });
var showSubs = !/[?&]sub=0/.test(location.search);

function sceneAt(t){ var i = 0; TL.scenes.forEach(function(s, k){ if (t >= s.start) i = k; }); return i; }
function render(t){
  var si = sceneAt(t), sc = TL.scenes[si], rel = t - sc.start;
  var S = { seg: sc.segs.map(function(s){ return s.rel; }), d: sc.segs.map(function(s){ return s.dur; }), dur: sc.dur };
  SECS.forEach(function(sec, k){ sec.classList.toggle('on', k === si); });
  RINGS = [];
  DRAW[ORDER[si]](rel, S);
  // fin de plan : fondu court avec flou ; début de plan : éclair vert (pas sur le premier)
  var q = prog(rel, sc.dur - .22, .22); var sec = SECS[si];
  sec.style.opacity = 1 - q; sec.style.filter = q > 0 ? 'blur(' + (q * 14) + 'px)' : 'none'; sec.style.transform = 'scale(' + (1 + q * .03) + ')';
  $('flash').style.opacity = si > 0 ? .45 * (1 - prog(rel, 0, .2)) : 0;
  if (!(ORDER[si] === 'attaque' || ORDER[si] === 'drift')) ticker(rel, false);
  var h = ''; RINGS.forEach(function(r){ var a = r[2]; h += '<circle cx="' + r[0] + '" cy="' + r[1] + '" r="' + (eo(a / 1.3) * 1100) + '" fill="none" stroke="' + r[3] + '" stroke-width="' + (4 * (1 - a / 1.3)) + '" opacity="' + (.8 * (1 - a / 1.3)) + '"/>'; });
  if ($('rings').dataset.h !== h){ $('rings').dataset.h = h; $('rings').innerHTML = h; }
  // lumières de fond : dérive lente, déterministe
  $('au1').style.transform = 'translate(' + (Math.sin(t / 9) * 60) + 'px,' + (Math.cos(t / 11) * 40) + 'px)';
  $('au2').style.transform = 'translate(' + (Math.cos(t / 10) * -70) + 'px,' + (Math.sin(t / 8) * 50) + 'px)';
  $('au3').style.transform = 'translate(' + (Math.sin(t / 7) * 50) + 'px,' + (Math.cos(t / 9) * -40) + 'px)';
  $('grain').style.opacity = .06 + .02 * ((Math.floor(t * 30) % 3) / 2);
  // HUD, mention, sous-titres, progression
  var tc = Math.max(0, t), m = Math.floor(tc / 60), s = Math.floor(tc % 60), f = Math.floor((tc % 1) * 30);
  $('hud').textContent = 'BREAKER · DÉMONSTRATION · PLAN ' + (si + 1) + '/' + TL.scenes.length + ' · 0' + m + ':' + (s < 10 ? '0' : '') + s + ':' + (f < 10 ? '0' : '') + f;
  $('mention').textContent = sc.mention || ''; $('mention').style.opacity = sc.mention ? eo(prog(rel, .3, .4)) : 0;
  var sub = ''; if (showSubs) sc.segs.forEach(function(x){ if (rel >= x.rel && rel < x.rel + x.dur + .35) sub = x.text; });
  $('subtitle').textContent = sub; $('subtitle').style.opacity = sub ? 1 : 0;
  $('prog').style.width = (t / TL.total * 100) + '%';
}
window.seek = function(t){ render(clamp(t, 0, TL.total)); return true; };
// Mise à l'échelle dans la fenêtre du navigateur.
function fit(){ var k = Math.min(innerWidth / 1920, innerHeight / 1080); var st = $('stage'); st.style.transform = 'scale(' + k + ')'; st.style.left = ((innerWidth - 1920 * k) / 2) + 'px'; st.style.top = ((innerHeight - 1080 * k) / 2) + 'px'; }
addEventListener('resize', fit); fit();
// Lecture dans le navigateur, synchronisée sur la voix.
var voice = $('voice'), playing = false, t = 0, last = null, RENDER = /[?&]render=1/.test(location.search);
function loop(now){ if (last === null) last = now; var dt = (now - last) / 1000; last = now;
  if (playing){ t = voice.readyState >= 2 && !voice.paused ? voice.currentTime : Math.min(TL.total, t + dt); if (t >= TL.total){ playing = false; voice.pause(); } }
  render(t); requestAnimationFrame(loop); }
function go(tt){ t = clamp(tt, 0, TL.total); try { voice.currentTime = t; } catch(e){} }
document.addEventListener('keydown', function(e){
  if (e.key === ' '){ e.preventDefault(); playing = !playing; if (playing){ if (t >= TL.total) go(0); voice.play().catch(function(){}); } else voice.pause(); }
  else if (e.key === 'ArrowRight'){ go(TL.scenes[Math.min(TL.scenes.length - 1, sceneAt(t) + 1)].start); }
  else if (e.key === 'ArrowLeft'){ var i = sceneAt(t); go(TL.scenes[t - TL.scenes[i].start < 1.5 ? Math.max(0, i - 1) : i].start); }
  else if (e.key === 'r' || e.key === 'R'){ go(0); }
  else if (e.key === 's' || e.key === 'S'){ showSubs = !showSubs; }
  else if (e.key === 'f' || e.key === 'F'){ if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen(); }
});
if (RENDER){ $('help').style.display = 'none'; voice.removeAttribute('src'); render(0); } else requestAnimationFrame(loop);
</script></body></html>
'''


POLICES = os.path.join(D, "polices")
UR = {"latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
      "latin-ext": "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF"}
FAM = {"manrope": "Manrope", "dm-sans": "DM Sans", "ibm-plex-mono": "IBM Plex Mono"}


def polices_css():
    """Polices du site embarquées dans la page (aucun accès réseau au rendu ni à la projection)."""
    css = []
    for f in sorted(os.listdir(POLICES)):
        if not f.endswith(".woff2"): continue
        base = f[:-len("-normal.woff2")]
        for fam in FAM:
            if base.startswith(fam + "-"):
                sub, w = base[len(fam) + 1:].rsplit("-", 1)
                css.append("@font-face{font-family:'%s';font-weight:%s;font-style:normal;font-display:block;src:url(%s) format('woff2');unicode-range:%s}"
                           % (FAM[fam], w, b64(os.path.join(POLICES, f), "font/woff2"), UR[sub]))
    return "\n".join(css)


def etape_html(timeline):
    out = (HTML.replace("__POLICES__", polices_css()).replace("__TIMELINE__", json.dumps(timeline, ensure_ascii=False))
           .replace("__IMG10__", b64(os.path.join(MATIERE, "plan3-fiche-paiement-10.png"), "image/png"))
           .replace("__IMG13__", b64(os.path.join(MATIERE, "plan4-fiche-paiement-13-sanctions.png"), "image/png"))
           .replace("__AUDIO__", b64(os.path.join(D, "voix-off.mp3"), "audio/mpeg")))
    ancien = open(HTML_OUT, encoding="utf-8").read() if os.path.exists(HTML_OUT) else None
    open(HTML_OUT, "w", encoding="utf-8").write(out)
    if ancien != out and os.path.isdir(FRAMES):
        shutil.rmtree(FRAMES)   # la page a changé : les images déjà rendues ne sont plus valables
        print("page modifiée : images du rendu précédent supprimées")
    print("écrit", HTML_OUT, len(out) // 1024, "Ko")


# ---------------------------------------------------------------------------------------------------------
# 3. Rendu image par image puis encodage
# ---------------------------------------------------------------------------------------------------------
RENDU = r'''
import os, sys, time
from playwright.sync_api import sync_playwright
html, outdir, fps, total = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
n = int(total * fps) + 1
os.makedirs(outdir, exist_ok=True)
with sync_playwright() as p:
    try:
        b = p.chromium.launch(channel="chrome", args=["--disable-gpu-vsync", "--force-device-scale-factor=1"])
    except Exception:
        b = p.chromium.launch(args=["--disable-gpu-vsync", "--force-device-scale-factor=1"])
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    pg.goto("file://" + html + "?render=1")
    pg.wait_for_function("document.fonts.status === 'loaded'", timeout=30000)
    pg.evaluate("document.getElementById('stage').style.transform='none';document.getElementById('stage').style.left='0';document.getElementById('stage').style.top='0'")
    t0 = time.time()
    for i in range(n):
        f = os.path.join(outdir, "f%05d.jpg" % i)
        if os.path.exists(f): continue
        pg.evaluate("window.seek(%f)" % (i / fps))
        pg.screenshot(path=f, type="jpeg", quality=92, clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
        if i % 300 == 0: print("image %d / %d  (%.0f s)" % (i, n, time.time() - t0), flush=True)
    b.close()
print("rendu :", n, "images")
'''


def etape_rendu(timeline):
    rendu_py = os.path.join(D, "_rendre_images.py")
    open(rendu_py, "w").write(RENDU)
    if shutil.which("uvx"):
        cmd = ["uvx", "--from", "playwright", "python", rendu_py]
    else:
        cmd = [sys.executable, rendu_py]
    run(cmd + [HTML_OUT, FRAMES, str(FPS), str(timeline["total"])])
    run(["ffmpeg", "-loglevel", "error", "-stats", "-y", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "f%05d.jpg"),
         "-i", os.path.join(D, "voix-off.wav"), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", MP4_OUT])
    # Vignette : la scène de marque.
    brand = next(s for s in timeline["scenes"] if s["id"] == "marque")
    tt = brand["start"] + brand["segs"][1]["rel"] + 3.5
    run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(tt), "-i", MP4_OUT, "-frames:v", "1", os.path.join(D, "motion-v2-vignette.jpg")])
    print("écrit", MP4_OUT, os.path.getsize(MP4_OUT) // (1024 * 1024), "Mo")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--voix", action="store_true"); ap.add_argument("--html", action="store_true")
    ap.add_argument("--rendu", action="store_true"); ap.add_argument("--tout", action="store_true")
    a = ap.parse_args()
    if not (a.voix or a.html or a.rendu or a.tout):
        ap.print_help(); sys.exit(0)
    tl = None
    if a.voix or a.tout:
        tl = etape_voix()
    if a.html or a.rendu or a.tout:
        tl = tl or json.load(open(TIMELINE))
    if a.html or a.tout:
        etape_html(tl)
    if a.rendu or a.tout:
        etape_rendu(tl)
