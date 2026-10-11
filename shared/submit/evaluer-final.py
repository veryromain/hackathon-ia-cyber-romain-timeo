"""Rejoue le jeu final sans appels externes, sans ajuster les seuils."""
from pathlib import Path
import sys, json
from collections import defaultdict
repo=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(repo/'ia-1'))
from score.moteur import Moteur
from score.anomalie import entrainer
d=repo/'shared/donnees'
def lire(n): return [json.loads(l) for l in (d/n).read_text(encoding='utf-8').splitlines() if l.strip()]
carnet=json.loads((d/'carnet.json').read_text(encoding='utf-8'))
model,_=entrainer(lire('train.events.jsonl'),carnet)
m=Moteur(carnet,model)
levels={}; amounts={}
for phase in ('train','test','holdout','final'):
    for e in lire(phase+'.events.jsonl'):
        if e['type']=='payment_proposed': amounts[e['data']['payment_id']]=int(e['data']['amount'])
        a=m.traiter(e)
        if a: levels[a['payment_id']]=a['level']
tot=defaultdict(lambda:defaultdict(int))
for l in lire('final.labels.jsonl'):
    s=tot[l['label']]; pid=l['payment_id']; level=levels.get(pid,'none')
    s['n']+=1; s[level]+=1; s['amount']+=amounts[pid]
    if level=='hold': s['amount_hold']+=amounts[pid]
f,n=tot['fraud'],tot['normal']
result={'synthetic':True,'training':'train only','evaluation':'final; after train/test/holdout replay','counts':dict(tot),
 'fraud_hold_percent':100*f['hold']/f['n'],'fraud_friction_percent':100*(f['hold']+f['step_up'])/f['n'],
 'fraud_amount_hold_percent':100*f['amount_hold']/f['amount'],'normal_hold_percent':100*n['hold']/n['n']}
out=Path(__file__).parent/'final-metrics-replay.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
