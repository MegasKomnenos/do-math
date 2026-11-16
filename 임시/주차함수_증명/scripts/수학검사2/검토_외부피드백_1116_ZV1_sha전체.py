# -*- coding: utf-8 -*-
"""README.md의 SHA-256 표 전체(모든 행)를 현행 파일과 대조한다. python -I 로 실행."""
import hashlib, re, os
ROOT = r"C:\math\임시\주차함수_증명\원고_자료"
os.chdir(ROOT)
readme = open('README.md', encoding='utf-8').read()
rows = re.findall(r'^\| `([^`]+)` \| `([0-9a-f]{64})` \|', readme, re.M)
print('README SHA rows total:', len(rows))
bad = []; missing = []
for p, h in rows:
    if not os.path.exists(p):
        missing.append(p); continue
    hh = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if hh != h: bad.append((p, h[:16], hh[:16]))
print('missing files:', len(missing))
for m in missing: print('  MISSING', m)
print('hash mismatches:', len(bad))
for b in bad: print('  MISMATCH', b)
