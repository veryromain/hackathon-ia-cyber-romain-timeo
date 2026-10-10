const scenarios={normal:{recipient:'Infrastructure RPC',amount:'2 400',score:12,verdict:'Sans friction',className:'normal',reason:'Prestataire déjà connu, montant habituel et aucune rafale de paiements.',approvals:'2 signatures sur 5',delay:'Aucun',detail:'Le garde conserve les exigences ordinaires du portefeuille. Ce scénario illustre un paiement normal ; aucune transaction n’est signée ou transmise.'},new:{recipient:'Nouveau prestataire',amount:'12 000',score:56,verdict:'Signature supplémentaire',className:'step-up',reason:'Ce destinataire apparaît pour la première fois. Une validation indépendante permet de vérifier ses coordonnées.',approvals:'3 signatures sur 5',delay:'Aucun délai de risque',detail:'Dans cet exemple, le seuil passe de 2 à 3 signatures. Le troisième signataire vérifie la demande avant de signer dans son propre portefeuille.'},risk:{recipient:'Destinataire signalé',amount:'95 000',score:93,verdict:'En attente',className:'hold',reason:'Une adresse signalée, un montant hors habitudes et plusieurs demandes rapprochées justifient une mise en attente.',approvals:'3 signatures sur 5',delay:'Selon votre politique',detail:'La mise en attente donne aux signataires le temps de vérifier les preuves. Le signalement peut être contesté ; le moniteur ne peut pas transférer vos fonds.'}};
const tabs=[...document.querySelectorAll('[data-scenario]')];function selectScenario(tab){const s=scenarios[tab.dataset.scenario];tabs.forEach(t=>{const active=t===tab;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1});document.querySelector('#panel').setAttribute('aria-labelledby',tab.id);for(const id of ['recipient','amount','reason','approvals','delay'])document.querySelector('#'+id).textContent=s[id];const verdict=document.querySelector('#verdict');verdict.textContent=s.verdict;verdict.className='status '+s.className;document.querySelector('#score').textContent=s.score+' / 100';document.querySelector('#bar').style.width=s.score+'%';document.querySelector('#bar').style.background=s.className==='hold'?'var(--orange)':s.className==='step-up'?'var(--blue)':'var(--green)';document.querySelector('#detail').textContent=s.detail;document.querySelector('#detail').hidden=true;document.querySelector('#explain').setAttribute('aria-expanded','false');}tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectScenario(tab));tab.addEventListener('keydown',e=>{let n;if(e.key==='ArrowRight'||e.key==='ArrowDown')n=(i+1)%tabs.length;if(e.key==='ArrowLeft'||e.key==='ArrowUp')n=(i+tabs.length-1)%tabs.length;if(e.key==='Home')n=0;if(e.key==='End')n=tabs.length-1;if(n!==undefined){e.preventDefault();tabs[n].focus();selectScenario(tabs[n])}})});document.querySelector('#explain').addEventListener('click',()=>{const detail=document.querySelector('#detail');detail.hidden=!detail.hidden;document.querySelector('#explain').setAttribute('aria-expanded',String(!detail.hidden))});selectScenario(tabs[0]);

// --- Haut de page : trame interactive et flux de paiements ---
const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Trame de tuiles à pans coupés, la silhouette du logo. Les tuiles proches du curseur s'allument puis
// s'éteignent, un clic envoie une onde. Sous l'élément [data-cloud], des tuiles pleines forment le
// « nuage » sur lequel se posent les paiements.
function initField(canvas) {
  const host = canvas.parentElement;
  const ctx = canvas.getContext('2d');
  const PITCH = 46, SIZE = 38, CUT = 10, OFF = (PITCH - SIZE) / 2, REACH = 130;
  const LINE = 'rgba(255, 255, 255, .075)', ACCENT = '199, 250, 112', CLOUD = 'rgba(255, 255, 255, .06)'; // mêmes teintes que style.css
  const BLOBS = [[.5, .5, .54, .36], [.76, .2, .34, .24], [.22, .8, .3, .22]]; // centre et rayons, en parts de la zone
  let cols = 0, rows = 0, heat = new Float32Array(0), cloud = new Uint8Array(0);
  let pointer = null, waves = [], frame = 0, last = 0;

  function tile(x, y) {
    ctx.beginPath();
    ctx.moveTo(x, y); ctx.lineTo(x + SIZE - CUT, y); ctx.lineTo(x + SIZE, y + CUT);
    ctx.lineTo(x + SIZE, y + SIZE); ctx.lineTo(x + CUT, y + SIZE); ctx.lineTo(x, y + SIZE - CUT);
    ctx.closePath();
  }

  function draw() {
    ctx.clearRect(0, 0, cols * PITCH, rows * PITCH);
    ctx.lineWidth = 1;
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const i = r * cols + c, hot = heat[i];
      tile(c * PITCH + OFF + .5, r * PITCH + OFF + .5);
      if (cloud[i]) { ctx.fillStyle = CLOUD; ctx.fill(); }
      if (hot > .01) {
        ctx.fillStyle = `rgba(${ACCENT}, ${.22 * hot})`; ctx.fill();
        ctx.strokeStyle = `rgba(${ACCENT}, ${.15 + .55 * hot})`; ctx.stroke();
      } else if (!cloud[i]) { ctx.strokeStyle = LINE; ctx.stroke(); }
    }
  }

  function measure() {
    const w = host.clientWidth, h = host.clientHeight, ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(w * ratio); canvas.height = Math.round(h * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    cols = Math.ceil(w / PITCH) + 1; rows = Math.ceil(h / PITCH) + 1;
    heat = new Float32Array(cols * rows); cloud = new Uint8Array(cols * rows);
    const zone = host.querySelector('[data-cloud]');
    if (zone) {
      const a = host.getBoundingClientRect(), b = zone.getBoundingClientRect();
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
        const x = (c + .5) * PITCH - (b.left - a.left), y = (r + .5) * PITCH - (b.top - a.top);
        if (BLOBS.some(([cx, cy, rx, ry]) => ((x / b.width - cx) / rx) ** 2 + ((y / b.height - cy) / ry) ** 2 <= 1)) cloud[r * cols + c] = 1;
      }
    }
    draw();
  }

  function step(now) {
    const fade = calm ? 0 : Math.exp(-Math.min(now - last, 50) / 420);
    last = now;
    waves = waves.filter(w => now - w.t < 1100);
    let alive = false;
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const i = r * cols + c, x = (c + .5) * PITCH, y = (r + .5) * PITCH;
      let v = heat[i] * fade;
      if (pointer) {
        const d = Math.hypot(x - pointer.x, y - pointer.y);
        if (d < REACH) v = Math.max(v, (1 - d / REACH) ** 1.6);
      }
      for (const w of waves) {
        const age = now - w.t, d = Math.abs(Math.hypot(x - w.x, y - w.y) - age * .55);
        if (d < 34) v = Math.max(v, (1 - d / 34) * (1 - age / 1100));
      }
      heat[i] = v;
      if (v > .01) alive = true;
    }
    draw();
    frame = alive || waves.length ? requestAnimationFrame(step) : 0;
  }
  function wake() { if (!frame) { last = performance.now(); frame = requestAnimationFrame(step); } }

  const at = e => { const b = host.getBoundingClientRect(); return { x: e.clientX - b.left, y: e.clientY - b.top }; };
  const release = () => { pointer = null; wake(); };
  host.addEventListener('pointermove', e => { pointer = at(e); wake(); });
  host.addEventListener('pointerleave', release);
  host.addEventListener('pointercancel', release);
  host.addEventListener('pointerup', e => { if (e.pointerType !== 'mouse') release(); });
  host.addEventListener('pointerdown', e => { if (!calm) { waves.push({ ...at(e), t: performance.now() }); wake(); } });
  new ResizeObserver(measure).observe(host);
  canvas.style.backgroundImage = 'none';
}
document.querySelectorAll('canvas.field').forEach(initField);

// Flux de paiements : chacun arrive, attend le verdict du garde, puis laisse la place au suivant.
// Adresses de test du déploiement Fuji ou inventées ; montants de la démo.
const PAYMENTS = [
  { name: 'Prestataire habituel', address: '0x3f79…9438', amount: '3 150', state: 'normal' },
  { name: 'Adresse jamais vue', address: '0xa3Cd…F126', amount: '95 000', state: 'hold' },
  { name: 'Hébergement cloud', address: '0x8007…A508', amount: '2 400', state: 'normal' },
  { name: 'Nouveau prestataire', address: '0x51b2…c07e', amount: '12 000', state: 'step-up' },
  { name: 'Audit de sécurité', address: '0x7c1e…04bd', amount: '8 600', state: 'normal' },
  { name: 'Adresse signalée', address: '0x6253…c352', amount: '4 800', state: 'hold' },
];
const VERDICTS = {
  normal: { label: 'Sans friction', sigs: '2/2' },
  'step-up': { label: 'Signature supplémentaire', sigs: '2/3' },
  hold: { label: 'En attente', sigs: '2/3' },
};
const PERSON = '<svg viewBox="0 0 12 12"><circle cx="6" cy="3.6" r="2.3"/><path d="M1.6 11c.3-2.6 2-4 4.4-4s4.1 1.4 4.4 4z"/></svg>';
const INKS = [['#16283f', '#c7fa70'], ['#c7fa70', '#142008'], ['#1b3557', '#a8bfff'], ['#ffc481', '#1a1206'], ['#a8bfff', '#0b1626']];

// Petit blason tiré de l'adresse : 5 cases sur 5, symétrique, deux teintes de la charte.
function crest(address) {
  let hash = 2166136261;
  for (const ch of address) hash = Math.imul(hash ^ ch.charCodeAt(0), 16777619) >>> 0;
  const [back, front] = INKS[hash % INKS.length];
  let cells = '';
  for (let y = 0; y < 5; y++) for (let x = 0; x < 3; x++) {
    if (!((hash >>> (y * 3 + x + 3)) & 1)) continue;
    cells += `<rect x="${x}" y="${y}" width="1" height="1"/>`;
    if (x < 2) cells += `<rect x="${4 - x}" y="${y}" width="1" height="1"/>`;
  }
  return `<svg viewBox="0 0 5 5" shape-rendering="crispEdges"><rect width="5" height="5" fill="${back}"/><g fill="${front}">${cells}</g></svg>`;
}

function initStream(list) {
  const slots = [...list.children];
  let next = 0;
  // Les minuteries s'arrêtent quand l'onglet est caché et reprennent à son retour.
  const later = (ms, fn) => setTimeout(() => {
    if (!document.hidden) return fn();
    document.addEventListener('visibilitychange', function resume() {
      if (document.hidden) return;
      document.removeEventListener('visibilitychange', resume);
      fn();
    });
  }, ms);

  function fill(slot, p) {
    slot.innerHTML = `<span class="avatar">${crest(p.address)}</span>`
      + `<div class="who"><strong>${p.name}</strong><code>${p.address}</code></div>`
      + `<div class="what"><strong>${p.amount} <small>mUSD</small></strong><span class="sigs">${PERSON}<b>2/2</b></span></div>`
      + '<span class="status pending">Analyse en cours</span>';
  }
  function judge(slot, p) {
    const verdict = VERDICTS[p.state], status = slot.querySelector('.status'), sigs = slot.querySelector('.sigs');
    status.className = 'status ' + p.state;
    status.textContent = verdict.label;
    sigs.querySelector('b').textContent = verdict.sigs;
    sigs.classList.toggle('raised', verdict.sigs !== '2/2');
  }

  if (calm) { // pas de défilement : trois paiements fixes, un par réponse
    [PAYMENTS[0], PAYMENTS[3], PAYMENTS[1]].forEach((p, i) => { fill(slots[i], p); judge(slots[i], p); });
    return;
  }

  function show(slot) {
    const p = PAYMENTS[next++ % PAYMENTS.length];
    fill(slot, p);
    slot.classList.add('no-anim');
    slot.classList.remove('is-out');
    void slot.offsetWidth; // repart du bas sans rejouer la sortie
    slot.classList.remove('no-anim');
    slot.classList.add('is-in');
    later(1300, () => judge(slot, p));
    later(6000, () => {
      slot.classList.remove('is-in');
      slot.classList.add('is-out');
      later(700, () => show(slot));
    });
  }
  list.classList.add('js-stream');
  slots.forEach((slot, i) => later(250 + i * 1900, () => show(slot)));
}
document.querySelectorAll('.stream').forEach(initStream);

// --- Cartes en verre : un reflet suit le curseur, et les cartes s'inclinent légèrement vers lui ---
function initGlass(card) {
  const tilts = card.matches('.stat, .card'); // les grands panneaux ne s'inclinent pas
  const reach = Math.min(6, 1900 / card.offsetWidth); // degrés : moins d'angle sur une carte large
  card.addEventListener('pointermove', e => {
    const b = card.getBoundingClientRect(), x = (e.clientX - b.left) / b.width, y = (e.clientY - b.top) / b.height;
    card.style.setProperty('--mx', x * 100 + '%');
    card.style.setProperty('--my', y * 100 + '%');
    card.style.setProperty('--lit', 1);
    if (!tilts || calm || e.pointerType !== 'mouse') return;
    card.classList.add('tilting');
    card.style.setProperty('--ry', ((x - .5) * 2 * reach).toFixed(2) + 'deg');
    card.style.setProperty('--rx', ((.5 - y) * 2 * reach).toFixed(2) + 'deg');
  });
  card.addEventListener('pointerleave', () => {
    for (const name of ['--lit', '--rx', '--ry']) card.style.removeProperty(name);
    setTimeout(() => { if (!card.matches(':hover')) card.classList.remove('tilting'); }, 400); // une fois la carte revenue à plat
  });
}
document.querySelectorAll('.stat, .card, .dashboard, .closing-panel, .tabs button').forEach(initGlass);
