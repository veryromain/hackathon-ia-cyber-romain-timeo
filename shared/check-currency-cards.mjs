import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const folder = new URL('../sites/breaker/dist/', import.meta.url);
const html = fs.readFileSync(new URL('index.html', folder), 'utf8');
const css = fs.readFileSync(new URL('style.css', folder), 'utf8');
const code = fs.readFileSync(new URL('app.js', folder), 'utf8').split('const scenarios=')[0];
const elements = [...html.matchAll(/<(span|s)\b[^>]*data-eur="([\d.]+)"/g)].map(m => ({
  tagName: m[1].toUpperCase(), dataset: {eur:m[2]},
  replaceChildren(...nodes) { this.output=nodes.map(n=>n.textContent).join(''); },
  setAttribute(name,value) { this[name]=value; },
}));
const inputs = ['pay-usdc','pay-eur','pay-usd'].map(id=>({id,addEventListener(event,fn){this.change=fn;}}));
let chosen=inputs[0];
const note={}, quote={};
const pricing={dataset:{},querySelectorAll(s){return s==='[data-eur]'?elements:inputs;},querySelector(s){return s.includes(':checked')?chosen:s==='[data-quote-currency]'?quote:note;}};
vm.runInNewContext(code,{Intl,document:{querySelector:()=>pricing,createElement:()=>({}),createTextNode:textContent=>({textContent})}});
const find=value=>elements.find(e=>e.dataset.eur===String(value));
const output=value=>find(value).output.replace(/[\u00a0\u202f]/g,' ');
assert.equal(output(149),'166,97 USDC');
assert.equal(output('134.10'),'150,27 USDC');
assert.equal(output('1609.20'),'1 803,27 USDC');
assert.equal(output('178.80'),'200,36 USDC');
chosen=inputs[1];chosen.change();
assert.equal(output(149),'149 €');
assert.equal(output('134.10'),'134 €');
assert.equal(output('1609.20'),'1 609 €');
assert.equal(output('178.80'),'179 €');
chosen=inputs[2];chosen.change();
assert.equal(output(149),'166,97 $');
assert.equal(output('134.10'),'150,27 $');
assert.equal(output('1609.20'),'1 803,27 $');
assert.equal(output('178.80'),'200,36 $');
assert.equal(quote.textContent,'Devis en dollars américains');
assert.match(note.textContent,/09\/10\/2026/);
chosen=inputs[0];chosen.change();
assert.equal(output(149),'166,97 USDC'); // switching back never compounds conversion
assert.equal(elements.length,16); // free trial + five amounts per paid card
assert.ok(css.includes('#bill-year:checked ~ .cards .monthly'));
assert.ok(css.includes('#bill-month:checked ~ .cards .annual'));
console.log('Currency changes, annual totals, savings and round trip: OK.');
