"""Compare alerts.jsonl à labels.jsonl (la vérité). Seul ce script lit les étiquettes."""
import json
import sys

alerts = {json.loads(l)["payment_id"]: json.loads(l) for l in open(sys.argv[1]) if l.strip()}
labels = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
vp = fp = fn = vn = 0
for lab in labels:
    a = alerts.get(lab["payment_id"])
    niveau = a["level"] if a else "—"
    fraude = lab["label"] == "fraud"
    attrape = niveau == "hold"
    vp += fraude and attrape; fn += fraude and not attrape
    fp += (not fraude) and attrape; vn += (not fraude) and not attrape
    print(f"paiement {lab['payment_id']:>3}  {lab['label']:<6} {lab['scenario']:<24} → {niveau}")
print(f"\nFraudes mises en attente : {vp}/{vp + fn} · Paiements normaux mis en attente (faux positifs) : {fp}/{fp + vn}")
