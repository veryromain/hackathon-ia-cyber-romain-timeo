from pathlib import Path
import subprocess,tempfile
repo=Path(__file__).resolve().parents[2]
scanner=repo/'ia-2/scripts/zero-secret.js'
with tempfile.TemporaryDirectory(prefix='scanner-',dir=None) as td:
 p=Path(td)
 def git(*args):subprocess.run(['git','-C',str(p),*args],check=True,capture_output=True)
 git('init');git('config','user.email','test@example.invalid');git('config','user.name','Synthetic scanner test')
 (p/'notes.md').write_text('# ZERO-SECRET : VERSION DE TEST SYNTHETIQUE\n',encoding='utf-8')
 git('add','notes.md');git('commit','-m','synthetic heading')
 def run():return subprocess.run(['node',str(scanner),str(p)],capture_output=True)
 assert run().returncode==0,'Le titre non secret est un faux positif'
 # Valeur fabriquée, uniquement dans le dépôt temporaire ; pas un credential.
 (p/'config.txt').write_text('PRIVATE_KEY='+'a'*32+'\n',encoding='utf-8');git('add','config.txt')
 assert run().returncode==1,'Une affectation sensible dans l’index doit être détectée'
 git('commit','-m','synthetic assignment');git('rm','config.txt');git('commit','-m','remove assignment')
 assert run().returncode==1,'La suppression ne doit pas masquer une fuite historique'
 print('Scanner : titre non secret accepté, affectation index détectée, historique conservé.')
