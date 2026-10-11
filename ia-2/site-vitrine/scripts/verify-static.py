"""Fail closed on unexpected public files or known secrets. Never print matches."""
import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path
from urllib.parse import quote

PUBLIC = {'index.html', 'app.js', 'style.css'}
PATTERNS = [rb'(?:AKIA|ASIA)[A-Z0-9]{16}', rb'(?:ABSK|bedrock-api-key-)[A-Za-z0-9+/=_-]{20,}',
            rb'apify_api_[A-Za-z0-9]{20,}', rb'sk-(?:ant-)?[A-Za-z0-9_-]{24,}',
            rb'(?:ghp|gho|ghs|ghu|github_pat)_[A-Za-z0-9_]{20,}',
            rb'-----BEGIN [A-Z ]*PRIVATE KEY-----']

def secrets(envfiles, walletdir):
    values = []
    if envfiles:
        from dotenv import dotenv_values
        for filename in envfiles:
            if not Path(filename).is_file():
                raise ValueError('Known-secret environment file missing')
            values.extend(v for k, v in dotenv_values(filename).items()
                          if v and re.search(r'KEY|TOKEN|PASSWORD|SECRET|MNEMONIC', k))
    if walletdir:
        script = "const fs=require('fs'),d=require('dotenv').parse(fs.readFileSync('.env')),{ethers}=require('ethers');if(!d.FUJI_MNEMONIC)process.exit(1);process.stdout.write(JSON.stringify(Array.from({length:20},(_,i)=>ethers.HDNodeWallet.fromPhrase(d.FUJI_MNEMONIC,undefined,`m/44'/60'/0'/0/${i}`).privateKey)));"
        result = subprocess.run(['node', '-e', script], cwd=walletdir, capture_output=True, check=True)
        values.extend(json.loads(result.stdout))
    variants = set()
    for value in values:
        b = value.encode()
        variants.update([b, quote(value, safe='').encode(), base64.b64encode(b),
                         b.hex().encode(), json.dumps(value)[1:-1].encode()])
        if value.startswith('0x'):
            variants.add(value[2:].encode())
        words = value.split()
        if len(words) >= 12:
            variants.update(' '.join(words[i:i+3]).encode() for i in range(len(words)-2))
        elif len(value) >= 40:
            variants.update(value[i:i+20].encode() for i in range(0, len(value)-19, 20))
    return [v for v in variants if len(v) >= 16]

def inspect(objects, variants):
    problems = []
    for name, data in objects.items():
        if any(v in data for v in variants) or any(re.search(p, data) for p in PATTERNS):
            problems.append({'file':name, 'reason':'secret detected; value redacted'})
    return problems

def html_matches(body, source):
    if body == source:
        return True, False
    # Cloudflare inserts its JavaScript detection script with per-request values.
    # Remove only one identifiable platform script; every original byte must remain.
    candidates = list(re.finditer(rb'<script>\(function\(\)\{function c\(\).*?</script>', body, re.S))
    if len(candidates) != 1:
        return False, False
    script = candidates[0]
    if (len(script[0]) > 4096 or b'__CF$cv$params' not in script[0]
            or b'/cdn-cgi/challenge-platform/scripts/jsd/main.js' not in script[0]):
        return False, False
    cleaned = body[:script.start()] + body[script.end():]
    return cleaned == source, True

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', required=True)
    p.add_argument('--archive')
    p.add_argument('--env', action='append', default=[])
    p.add_argument('--wallet-tool-dir')
    p.add_argument('--live-json', action='store_true')
    p.add_argument('--report')
    a = p.parse_args()
    root = Path(a.source).resolve()
    objects = {}
    for f in root.rglob('*'):
        if f.is_symlink():
            raise ValueError('Public directory contains a symlink')
        if f.is_file():
            objects[f.relative_to(root).as_posix()] = f.read_bytes()
    if set(objects) != PUBLIC:
        raise ValueError('Public directory must contain exactly index.html, app.js, style.css')
    variants = secrets(a.env, a.wallet_tool_dir)
    problems = inspect(objects, variants)
    js = objects['app.js']
    if re.search(rb'\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|localStorage|sessionStorage|eval|ethereum|process\.env|import\.meta\.env)\b', js):
        problems.append({'file':'app.js', 'reason':'Static-only boundary changed'})
    if re.search(rb'<form\b|<script[^>]+src=["\']https?://', objects['index.html']):
        problems.append({'file':'index.html', 'reason':'Static-only boundary changed'})
    archive_files = []
    if a.archive:
        with tarfile.open(a.archive, 'r:gz') as t:
            members = t.getmembers()
            if any(not (m.isfile() or m.isdir()) for m in members):
                raise ValueError('Archive contains links or unsupported entries')
            files = {m.name:t.extractfile(m).read() for m in members if m.isfile()}
        expected = {'dist/'+name for name in PUBLIC} | {'dist/.openai/hosting.json'}
        if set(files) != expected or len([m for m in members if m.isfile()]) != len(expected):
            raise ValueError('Unexpected archive entries')
        config = json.loads(files['dist/.openai/hosting.json'])
        if set(config) != {'project_id','static'} or config['static'] != {'directory':'dist'}:
            raise ValueError('Unexpected deployment metadata')
        for name in PUBLIC:
            if files['dist/'+name] != objects[name]:
                raise ValueError('Archive differs from validated source')
        problems.extend(inspect(files, variants))
        archive_files = sorted(files)
    live = []
    if a.live_json:
        responses = json.load(sys.stdin)
        for r in responses:
            body = base64.b64decode(r.pop('body'))
            path = r['path']
            if path in ['/', '/app.js', '/style.css']:
                name = 'index.html' if path == '/' else path[1:]
                matched, injected = html_matches(body, objects[name]) if name == 'index.html' else (body == objects[name],False)
                r['matches_source'] = r['status'] == 200 and matched
                r['platform_script_added'] = injected
                if not r['matches_source']:
                    problems.append({'file':path, 'reason':'Live response differs from source'})
            else:
                fallback, injected = html_matches(body, objects['index.html'])
                r['file_not_exposed'] = r['status'] == 404 or (r['status'] == 200 and fallback)
                r['homepage_fallback'] = r['status'] == 200 and fallback
                if not r['file_not_exposed']:
                    problems.append({'file':path, 'reason':'Sensitive path response unexpected'})
            problems.extend(inspect({path:body}, variants))
            r['sha256'] = hashlib.sha256(body).hexdigest()
            r['bytes'] = len(body)
            live.append(r)
    result = {'ok':not problems, 'public_files':sorted(objects), 'archive_files':archive_files,
              'known_secret_variants':len(variants), 'findings':problems, 'live':live,
              'manifest':{k:hashlib.sha256(v).hexdigest() for k,v in objects.items()}}
    if a.report:
        Path(a.report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not problems else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        # Subprocess output and secret values are deliberately never printed.
        print(json.dumps({'ok':False, 'error_type':type(e).__name__}))
        sys.exit(1)
