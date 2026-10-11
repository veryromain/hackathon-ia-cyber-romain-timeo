# Construit la première version du motion design (livrable L1) : shared/video/motion-v1.html
# Suit les 7 plans de shared/plan-video-motion.md (Timéo), avec la matière réelle de shared/video/.
# Usage : python3 shared/video/construire_motion.py ; puis ouvrir motion-v1.html dans Chrome (plein écran, F) et
# enregistrer l'écran (⌘⇧5 sur Mac) pour obtenir le mp4. Espace : pause ; ← → : plan précédent / suivant ; R : début.
import base64, os
D = os.path.dirname(os.path.abspath(__file__))
def img(n):
    with open(os.path.join(D, n), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

HTML = r'''<title>Breaker, la démonstration</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Manrope:wght@500;600;800&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Identité du site vitrine (ia-2/site-vitrine/dist/style.css). Scène 16:9 centrée ; sous-titres = voix off. */
:root{--bg:#07111f;--ink:#f6f9fc;--text:#e7edf4;--muted:rgba(231,237,244,.7);--faint:rgba(231,237,244,.52);--line:rgba(255,255,255,.11);
--accent:#c7fa70;--on-accent:#142008;--green:#c7fa70;--blue:#a8bfff;--orange:#ffc481;--red:#ff6b6b;
--glass:linear-gradient(135deg,rgba(255,255,255,.11),rgba(255,255,255,.03) 46%,rgba(255,255,255,.07));--glass-edge:rgba(255,255,255,.14);
--display:'Manrope','DM Sans',system-ui,sans-serif;--body:'DM Sans',system-ui,sans-serif;--mono:'IBM Plex Mono',ui-monospace,Menlo,monospace}
html,body{height:100%;margin:0;background:#000;color:var(--text);font-family:var(--body)}
body{color-scheme:dark;display:flex;align-items:center;justify-content:center;overflow:hidden}
#stage{position:relative;width:min(100vw,177.78vh);aspect-ratio:16/9;background:var(--bg);overflow:hidden;font-size:calc(min(100vw,177.78vh)/72)}
.scene{position:absolute;inset:0;padding:5% 6%;opacity:0;transition:opacity .5s;display:flex;flex-direction:column;justify-content:center;gap:1.2em}
.scene.on{opacity:1}
.el{opacity:0;transform:translateY(.6em);transition:opacity .6s,transform .6s}
.el.on{opacity:1;transform:none}
h1,h2{font-family:var(--display);margin:0;letter-spacing:-.02em;line-height:1.05;text-wrap:balance}
h1{font-size:3.2em;font-weight:800;color:var(--ink)} h2{font-size:2.1em;font-weight:800;color:var(--ink)}
.big{font-size:4.4em;font-weight:800;font-family:var(--display);color:var(--ink);line-height:1}
.big.acc{color:var(--accent)} .big.org{color:var(--orange)}
.sub{color:var(--muted);font-size:1.25em;max-width:34em}
.mono{font-family:var(--mono)}
.card{background:var(--glass);border:1px solid var(--glass-edge);border-radius:.6em;padding:1em 1.2em;box-shadow:inset 0 1px 0 rgba(255,255,255,.2)}
.row{display:flex;gap:1em;align-items:center;flex-wrap:wrap}
.badge{display:inline-block;font-family:var(--mono);font-size:.8em;padding:.25em .6em;border-radius:.4em;border:1px solid var(--line);color:var(--muted)}
.badge.ok{color:var(--on-accent);background:var(--green);border-color:transparent}
.badge.hold{color:#2a1a00;background:var(--orange);border-color:transparent}
.badge.step{color:#101a3a;background:var(--blue);border-color:transparent}
.pay{display:grid;grid-template-columns:1fr auto;gap:.4em 1.5em;align-items:center;padding:.8em 1.1em;border-radius:.6em;border:1px solid var(--line);background:rgba(255,255,255,.03)}
.pay b{font-family:var(--display);font-size:1.5em;color:var(--ink)} .pay small{color:var(--faint);font-family:var(--mono);font-size:.85em}
.pay .st{text-align:right}
.term{font-family:var(--mono);font-size:.95em;line-height:1.5;white-space:pre-wrap;color:var(--text);background:#040a14;border:1px solid var(--line);border-radius:.6em;padding:1em 1.2em;min-height:9em}
.term .k{color:var(--accent)} .term .o{color:var(--orange)} .term .b{color:var(--blue)} .term .d{color:var(--faint)} .term .r{color:var(--red)}
.fiche{position:absolute;right:6%;top:8%;height:84%;border-radius:.6em;box-shadow:0 30px 60px -20px rgba(0,0,0,.8);border:1px solid var(--glass-edge);background:#fff}
.fiche img{height:100%;width:auto;display:block;border-radius:.6em}
.hl{background:rgba(199,250,112,.25);outline:2px solid var(--accent);border-radius:.2em;padding:0 .15em}
.mention{position:absolute;top:3.5%;right:6%;font-family:var(--mono);font-size:.8em;color:var(--faint);border:1px solid var(--line);padding:.3em .7em;border-radius:.4em;opacity:0;transition:opacity .4s}
.mention.on{opacity:1}
.brand{display:flex;align-items:center;gap:.5em;font-family:var(--display);font-weight:800;font-size:2.2em;color:var(--ink)}
.brand i{color:var(--accent);font-style:normal}
.mark{width:1.1em;height:1.23em;display:inline-block}
.sub-bar{position:absolute;left:0;right:0;bottom:0;padding:1em 6% 1.6em;background:linear-gradient(transparent,rgba(7,17,31,.95) 40%);font-size:1.25em;color:var(--ink);text-align:center;min-height:3.5em;text-wrap:balance}
.sub-bar span{background:rgba(0,0,0,.45);padding:.15em .5em;border-radius:.3em;box-decoration-break:clone}
.prog{position:absolute;left:0;bottom:0;height:.25em;background:var(--accent);width:0}
.counter{font-family:var(--display);font-weight:800;font-size:3.2em;color:var(--ink);font-variant-numeric:tabular-nums}
.bar{height:1.2em;border-radius:.6em;background:rgba(255,255,255,.06);border:1px solid var(--line);overflow:hidden;position:relative}
.bar i{position:absolute;left:0;top:0;bottom:0;width:0;background:repeating-linear-gradient(90deg,var(--orange) 0 2.9%,transparent 2.9% 3.226%)}
.ticks{display:flex;justify-content:space-between;font-family:var(--mono);font-size:.8em;color:var(--faint)}
.hud{position:absolute;left:6%;top:3.5%;font-family:var(--mono);font-size:.8em;color:var(--faint)}
.help{position:fixed;left:1em;bottom:1em;font:12px var(--mono);color:#889;background:#0b1626;padding:.4em .7em;border-radius:4px;border:1px solid #223}
@media (prefers-reduced-motion:reduce){.el,.scene{transition:none}}
</style>
<div id="stage">
<div class="hud" id="hud">plan 1 / 7 · 0:00</div>
<div class="mention" id="mention"></div>

<!-- 1. Le problème -->
<section class="scene" data-start="0">
  <div class="el" data-t="0.3"><div class="big org">Bybit · 1,46 Md$</div></div>
  <div class="el" data-t="2.2"><div class="big org">Drift · 280 M$</div></div>
  <div class="el" data-t="4.5"><h1>Les clés étaient valides.<br>Les signataires, trompés.</h1></div>
  <div class="el" data-t="9.5"><div class="brand"><svg class="mark" viewBox="0 0 34 38"><path d="M1 1h22.6L33 10.4V37H10.4L1 27.6z" fill="#c7fa70" stroke="#c7fa70" stroke-width="2" stroke-linejoin="round"/><path d="M10.5 9h7.25a5.25 5.25 0 0 1 0 10.5H10.5zM10.5 17.5h8.25a5.75 5.75 0 0 1 0 11.5H10.5z" fill="#142008"/><path d="M14.5 12.6h3.1a1.65 1.65 0 0 1 0 3.3h-3.1zM14.5 21.6h4.1a1.9 1.9 0 0 1 0 3.8h-4.1z" fill="#c7fa70"/></svg>breaker<i>.</i></div><div class="sub">La garde antifraude qui se greffe sur votre coffre.</div></div>
</section>

<!-- 2. Paiement normal -->
<section class="scene" data-start="15" data-mention="Avalanche Fuji · réseau de test · accéléré">
  <div class="el" data-t="0.2"><h2>Un paiement habituel passe sans friction.</h2></div>
  <div class="el pay" data-t="1"><div><b>3 150 mUSD</b> → Prestataire habituel <small>0x3f79…9438</small><br><small>paiement 9 · « Facture mensuelle »</small></div><div class="st"><span class="badge ok">aucun risque</span><br><small id="p9sig">1 / 2 signatures</small></div></div>
  <div class="el" data-t="4"><div class="row"><span class="badge step">2 / 2 signatures</span><span class="badge">délai d'examen 30 s</span><span class="badge ok" id="p9ok">exécuté 39 s après la proposition</span></div></div>
  <div class="el" data-t="8"><div class="sub mono">tx 0xf63a4366…5f5219 · testnet.snowtrace.io</div></div>
</section>

<!-- 3. L'attaque : 280 500 mUSD -->
<section class="scene" data-start="35" data-mention="Avalanche Fuji · réseau de test · accéléré">
  <div class="el" data-t="0.2"><h2>Trois paiements vers une adresse jamais vue.</h2></div>
  <div class="el pay" data-t="1" style="max-width:52%"><div><b>95 000 mUSD</b> → <small>0x2dd0…76f6</small><br><small>paiement 10 · « URGENT - virement confidentiel, acquisition en cours »</small></div><div class="st"><span class="badge hold">mise en attente · 10 s</span></div></div>
  <div class="el pay" data-t="3" style="max-width:52%"><div><b>93 500 mUSD</b> → <small>0x2dd0…76f6</small><br><small>paiement 11</small></div><div class="st"><span class="badge hold">mise en attente · 7 s</span></div></div>
  <div class="el pay" data-t="5" style="max-width:52%"><div><b>92 000 mUSD</b> → <small>0x2dd0…76f6</small><br><small>paiement 12 · « Opération confidentielle validée par la direction »</small></div><div class="st"><span class="badge hold">mise en attente · 9 s</span></div></div>
  <div class="el" data-t="7" style="max-width:52%"><div class="row"><span class="counter">280 500 mUSD</span><span class="sub">proposés par deux signataires trompés</span></div></div>
  <div class="el fiche" data-t="9"><img src="IMG10" alt="Fiche du paiement 10 : mise en attente, score 0,88, explication en français"></div>
  <div class="el" data-t="22" style="max-width:52%"><div class="row"><span class="badge step">2 signatures sur 3</span><span class="sub">il manque une signature : rien ne part</span></div></div>
  <div class="el" data-t="30" style="max-width:52%"><div class="row"><span class="badge hold">gel</span><span class="badge">annulé ×3</span><span class="counter" style="color:var(--accent)">0 mUSD sorti</span></div></div>
</section>

<!-- 4. L'oracle lit le Web -->
<section class="scene" data-start="75" data-mention="Avalanche Fuji · accéléré : 2 min 10 en réel">
  <div class="el" data-t="0.2"><h2>Le garde lit aussi le Web.</h2></div>
  <div class="el" data-t="0.8" style="max-width:52%"><div class="term" id="term4"></div></div>
  <div class="el fiche" data-t="13"><img src="IMG13" alt="Fiche du paiement 13 : adresse sanctionnée, score 0,97"></div>
  <div class="el" data-t="18" style="max-width:52%"><div class="row"><span class="badge hold">25 000 mUSD · attente maintenue malgré 3 signatures</span><span class="badge">annulé</span></div></div>
</section>

<!-- 5. Cosignataire -->
<section class="scene" data-start="100" data-mention="chaîne de test locale · mode Cosignataire (Premium)">
  <div class="el" data-t="0.2"><h2>En mode Cosignataire, un agent tient une signature.</h2></div>
  <div class="el" data-t="0.8"><div class="term" id="term5"></div></div>
  <div class="el" data-t="15"><div class="sub">Il simule chaque paiement, puis signe ou s'abstient, et dit pourquoi. Vos signataires gardent le dernier mot.</div></div>
</section>

<!-- 6. La cadence de Drift -->
<section class="scene" data-start="120" data-mention="Avalanche Fuji · avec le seuil de clés volées (2 sur 5)">
  <div class="el" data-t="0.2"><h2>La cadence de Drift, rejouée : 31 retraits en 12 minutes.</h2></div>
  <div class="el" data-t="1"><div class="bar"><i id="drift"></i></div><div class="ticks"><span>01:26:29</span><span>285 000 mUSD tentés</span><span>01:38:39</span></div></div>
  <div class="el" data-t="1.5"><div class="row"><span class="counter" id="dcount">0</span><span class="sub">retraits proposés et approuvés par les deux clés volées</span></div></div>
  <div class="el" data-t="11"><div class="row"><span class="counter" style="color:var(--accent)">0 exécuté · 0 mUSD sorti</span><span class="sub">chaque retrait mis en attente : 2 signatures sur 3</span></div></div>
</section>

<!-- 7. Les chiffres -->
<section class="scene" data-start="135">
  <div class="el" data-t="0.2"><div class="row" style="gap:2.5em"><div><div class="big acc">91 %</div><div class="sub">des montants frauduleux mis en attente</div></div><div><div class="big org">5,1 %</div><div class="sub">de paiements légitimes retardés</div></div><div><div class="big acc">0 mUSD</div><div class="sub">sorti en démonstration</div></div></div></div>
  <div class="el" data-t="5"><div class="sub mono">Mesuré sur des fraudes dont le garde n'avait jamais vu la forme · prototype non audité · données synthétiques · réseau de test</div></div>
  <div class="el" data-t="9"><div class="brand"><svg class="mark" viewBox="0 0 34 38"><path d="M1 1h22.6L33 10.4V37H10.4L1 27.6z" fill="#c7fa70" stroke="#c7fa70" stroke-width="2" stroke-linejoin="round"/><path d="M10.5 9h7.25a5.25 5.25 0 0 1 0 10.5H10.5zM10.5 17.5h8.25a5.75 5.75 0 0 1 0 11.5H10.5z" fill="#142008"/><path d="M14.5 12.6h3.1a1.65 1.65 0 0 1 0 3.3h-3.1zM14.5 21.6h4.1a1.9 1.9 0 0 1 0 3.8h-4.1z" fill="#c7fa70"/></svg>breaker<i>.</i></div><h1>Une signature ne suffit pas à faire confiance.</h1></div>
</section>

<div class="sub-bar"><span id="subtitle"></span></div>
<div class="prog" id="prog"></div>
</div>
<div class="help">espace : pause · ← → : plans · R : début · F : plein écran · 2 min 30</div>

<script>
// ---- Voix off (sous-titres), en secondes depuis le début. Même texte que shared/video/voix-off.md.
var SUBS = [
 [0.5,"Bybit, un milliard quatre cent soixante millions. Drift, deux cent quatre-vingts millions."],
 [5,"Dans les deux cas, personne n'a volé de clé au moment du paiement. Des signataires ont validé."],
 [10,"Breaker est la garde antifraude qui se greffe sur le coffre que vous avez déjà."],
 [15.5,"Un paiement habituel, vers un prestataire connu : deux signatures, trente secondes d'examen."],
 [22,"Il passe sans friction, trente-neuf secondes après la proposition. Tout est vérifiable sur l'explorateur."],
 [35.5,"Deux signataires trompés proposent trois paiements vers une adresse jamais vue : deux cent quatre-vingt mille."],
 [43,"En sept à dix secondes, le garde met chaque paiement en attente, l'inscrit sur la chaîne, et explique pourquoi, en français."],
 [52,"Nouveau destinataire, montants hors norme, trois paiements en deux minutes, un libellé qui insiste sur l'urgence et le secret."],
 [59,"Il demande une signature de plus. Il en manque une : rien ne part."],
 [66,"Un signataire alerté gèle le coffre et annule. Zéro sorti sur deux cent quatre-vingt mille."],
 [75.5,"Le garde lit aussi le Web. Un paiement de vingt-cinq mille vers une adresse nouvelle : d'abord une signature en plus."],
 [84,"Puis il cherche, lit trois pages, retient une citation exacte : cette adresse est sur la liste des sanctions."],
 [92,"L'adresse est inscrite au registre. Même avec trois signatures, l'attente reste : le paiement est annulé."],
 [100.5,"En mode Cosignataire, un agent tient une signature. Il simule chaque paiement, puis signe ou s'abstient, et dit pourquoi."],
 [109,"Une facture habituelle : il cosigne. Soixante pour cent de la trésorerie d'un coup : il refuse. Un inconnu : il attend un humain de plus."],
 [116,"Vos signataires gardent le dernier mot."],
 [120.5,"Nous avons rejoué la cadence de Drift : trente et un retraits en douze minutes, approuvés par deux clés volées."],
 [130,"Chacun mis en attente. Zéro exécuté, zéro sorti sur deux cent quatre-vingt-cinq mille."],
 [135.5,"Mesuré sur des fraudes dont le garde n'avait jamais vu la forme : quatre-vingt-onze pour cent des montants mis en attente, cinq pour cent de paiements légitimes retardés."],
 [143,"Prototype de hackathon, non audité, sur réseau de test. Breaker. Une signature ne suffit pas à faire confiance."]
];
var TERM4 = [
 [0,"<span class='d'>$ python -m agent.agent --mode cosignataire --web …</span>\n<span class='d'>paiement 1 · 25 000 mUSD → 0x098b…2f96</span>\n"],
 [1.5,"agent · paiement 1 · immédiate · <span class='b'>freiner</span> · signature en plus · 6,2 s\n"],
 [3.5,"<span class='d'>recherche Web…</span>\n  lu : etherscan.io/address/0x098B…2f96\n"],
 [5.5,"  lu : x.com/chainalysis/status/1514645222…\n"],
 [7,"  lu : basescan.org/address/0x098B…2f96\n"],
 [9,"accusation retenue (sanctions, 2 sources) :\n  <span class='hl'>« OFAC added a new ETH address to Lazarus Group's SDN entry : 0x098B716B…2f96 »</span>\n"],
 [12,"agent · paiement 1 · après Web · <span class='o'>refuser</span> · mise en attente, signature refusée · 4,7 s\n"],
 [16,"<span class='d'>Durée réelle : 2 min 10. Aucune signature écrite par l'agent.</span>"]
];
var TERM5 = [
 [0,"<span class='d'>$ npm run agent:local</span>\nTrésorerie : 1 000 000 mUSD · agent cosignataire 0x15d3…6A65 · seuil 2 sur 3\n\n"],
 [2,"1. Facture habituelle à un fournisseur du carnet · 3 200 mUSD\n   l'agent <span class='k'>A COSIGNÉ</span> · risque : aucun · 2/2 signatures · 6,8 s → exécuté\n\n"],
 [6,"2. Même fournisseur, mais 60 % de la trésorerie d'un coup · 600 000 mUSD\n   l'agent <span class='o'>N'A PAS SIGNÉ</span> · mise en attente · 1/3 · 5,4 s → « 60 % de la trésorerie et 188 fois l'habitude »\n\n"],
 [10,"3. Destinataire jamais vu · 4 800 mUSD\n   l'agent <span class='b'>N'A PAS SIGNÉ</span> · signature en plus · 1/3 · 5,8 s → mis en attente tant qu'un humain de plus ne signe pas\n\n"],
 [13,"Sorti : 3 200 mUSD (la facture habituelle). Non signés par l'agent, annulés : 2."]
];
var scenes=[].slice.call(document.querySelectorAll('.scene')), TOTAL=150, t=0, playing=true, last=null;
var mention=document.getElementById('mention'), hud=document.getElementById('hud'), prog=document.getElementById('prog'), subtitle=document.getElementById('subtitle');
function sceneIndex(tt){var i=0;scenes.forEach(function(s,k){if(tt>=+s.dataset.start)i=k;});return i;}
function typed(el,lines,rel){var h='';lines.forEach(function(l){if(rel>=l[0])h+=l[1];});if(el.innerHTML!==h)el.innerHTML=h;}
function render(){
  var si=sceneIndex(t);
  scenes.forEach(function(s,k){
    var on=k===si; s.classList.toggle('on',on);
    var rel=t-(+s.dataset.start);
    s.querySelectorAll('.el').forEach(function(e){e.classList.toggle('on',on&&rel>=+e.dataset.t);});
  });
  var s=scenes[si], rel=t-(+s.dataset.start);
  mention.textContent=s.dataset.mention||''; mention.classList.toggle('on',!!s.dataset.mention);
  var sub='';SUBS.forEach(function(x){if(t>=x[0])sub=x[1];}); subtitle.textContent=sub;
  if(si===3)typed(document.getElementById('term4'),TERM4,rel-0.8);
  if(si===4)typed(document.getElementById('term5'),TERM5,rel-0.8);
  if(si===5){var p=Math.min(1,Math.max(0,(rel-1)/9));document.getElementById('drift').style.width=(p*100)+'%';document.getElementById('dcount').textContent=Math.round(p*31);}
  if(si===1){document.getElementById('p9sig').textContent=rel>=4?'2 / 2 signatures':'1 / 2 signatures';}
  var m=Math.floor(t/60), sec=Math.floor(t%60); hud.textContent='plan '+(si+1)+' / 7 · '+m+':'+(sec<10?'0':'')+sec+(playing?'':' · pause');
  prog.style.width=(t/TOTAL*100)+'%';
}
function tick(now){if(last===null)last=now;var dt=(now-last)/1000;last=now;if(playing){t=Math.min(TOTAL,t+dt);if(t>=TOTAL)playing=false;}render();requestAnimationFrame(tick);}
document.addEventListener('keydown',function(e){
  if(e.key===' '){e.preventDefault();playing=!playing;}
  else if(e.key==='ArrowRight'){var i=Math.min(scenes.length-1,sceneIndex(t)+1);t=+scenes[i].dataset.start;}
  else if(e.key==='ArrowLeft'){var i=sceneIndex(t);var rel=t-(+scenes[i].dataset.start);t=+scenes[rel<1.5?Math.max(0,i-1):i].dataset.start;}
  else if(e.key==='r'||e.key==='R'){t=0;playing=true;}
  else if(e.key==='f'||e.key==='F'){var st=document.getElementById('stage');if(document.fullscreenElement)document.exitFullscreen();else if(st.requestFullscreen)st.requestFullscreen();}
});
document.addEventListener('click',function(){playing=!playing;});
requestAnimationFrame(tick);
</script>
'''
out = HTML.replace("IMG10", img("plan3-fiche-paiement-10.png")).replace("IMG13", img("plan4-fiche-paiement-13-sanctions.png"))
dst = os.path.join(D, "motion-v1.html")
open(dst, "w").write(out)
print("écrit", dst, len(out) // 1024, "Ko")
