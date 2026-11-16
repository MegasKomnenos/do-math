# -*- coding: utf-8 -*-
"""README.md의 SHA-256 표와 critical_window_rerun/ 현행 파일을 대조한다. python -I 로 실행."""
import hashlib, re, os, sys
ROOT = r"C:\math\임시\주차함수_증명\원고_자료"
os.chdir(ROOT)
readme = open('README.md', encoding='utf-8').read()
rows = re.findall(r'^\| `(세션_재계산/critical_window_rerun/[^`]+)` \| `([0-9a-f]{64})` \|', readme, re.M)
print('README rows for critical_window_rerun:', len(rows))
bad = []; missing = []
for p, h in rows:
    if not os.path.exists(p):
        missing.append(p); continue
    hh = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if hh != h: bad.append((p, h[:12], hh[:12]))
print('missing files:', missing)
print('hash mismatches:', len(bad))
for b in bad: print('  ', b)
listed = set(p for p, _ in rows)
allf = []
for root, dirs, files in os.walk('세션_재계산/critical_window_rerun'):
    if '__pycache__' in root: continue
    for f in files:
        allf.append(os.path.join(root, f).replace(os.sep, '/'))
unl = [f for f in allf if f not in listed]
print('files present but not listed in README:', len(unl))
for f in unl: print('  ', f)
