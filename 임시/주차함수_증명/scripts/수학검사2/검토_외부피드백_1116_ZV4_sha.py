# -*- coding: utf-8 -*-
"""ZV4: 원고_자료/README.md의 SHA-256 표 둘(세션 재계산 2열 표, 파일 목록 4열 표)을 디스크와 대조한다.
빠진 파일은 원고_자료 전체와 대조v2/보관_재계산_옛판_1116 아래에서 같은 SHA의 파일을 찾아 '이동'인지 본다.
python -I scripts/수학검사2/검토_외부피드백_1116_ZV4_sha.py"""
import hashlib, re, os, sys, collections
ROOT = r"C:\math\임시\주차함수_증명"
MAT = os.path.join(ROOT, "원고_자료")
ARCH = os.path.join(ROOT, "대조v2", "보관_재계산_옛판_1116")
readme = open(os.path.join(MAT, 'README.md'), encoding='utf-8').read()
rows2 = re.findall(r'^\| `([^`]+)` \| `([0-9a-f]{64})` \|\s*$', readme, re.M)
rows4 = re.findall(r'^\| `([^`]+)` \| (.*?) \| ([^|]*?) \| `([0-9a-f]{64})` \|\s*$', readme, re.M)
print('2열 표(세션 재계산) 행:', len(rows2), ' 4열 표(파일 목록) 행:', len(rows4))
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def check(rows, label):
    ok = 0; bad = []; missing = []
    seen = set()
    for r in rows:
        p, h = r[0], r[-1]
        key = (p, h)
        if key in seen: continue
        seen.add(key)
        fp = os.path.join(MAT, p)
        if not os.path.exists(fp): missing.append((p, h)); continue
        hh = sha(fp)
        if hh == h: ok += 1
        else: bad.append((p, h, hh))
    print(f'[{label}] 고유 (경로,SHA) 쌍 {len(seen)}: 일치 {ok}, 해시 불일치 {len(bad)}, 경로 없음 {len(missing)}')
    for p, h, hh in bad: print('  MISMATCH', p, '표', h[:12], '디스크', hh[:12])
    return bad, missing
bad2, miss2 = check(rows2, '세션 재계산')
bad4, miss4 = check(rows4, '파일 목록')
# 빠진 파일을 SHA로 찾기
need = {h: p for p, h in miss2 + miss4}
if need:
    found = collections.defaultdict(list)
    for base in (MAT, ARCH):
        for dp, dn, fn in os.walk(base):
            for f in fn:
                fp = os.path.join(dp, f)
                try:
                    if os.path.getsize(fp) > 400 * 1024 * 1024: continue
                    hh = sha(fp)
                except OSError: continue
                if hh in need: found[hh].append(os.path.relpath(fp, ROOT))
    for p, h in miss2 + miss4:
        print('  MISSING', p, '->', found.get(h, ['(같은 SHA 파일 없음)']))
# 디스크에는 있으나 표에 없는 파일(세션_재계산 아래만, 계산 폴더 제외)
listed = set(r[0] for r in rows2) | set(r[0] for r in rows4)
skip = ('critical_window_rerun', 'icert_py_full', 'moment_cert_iv')
unlisted = []
for dp, dn, fn in os.walk(os.path.join(MAT, '세션_재계산')):
    for f in fn:
        rel = os.path.relpath(os.path.join(dp, f), MAT).replace(os.sep, '/')
        if any(s in rel for s in skip): continue
        if rel.endswith(('.pyc',)) or '__pycache__' in rel: continue
        if rel not in listed: unlisted.append(rel)
print('표에 없는 세션_재계산 파일(돌고 있는 계산 폴더 제외):', len(unlisted))
for u in sorted(unlisted)[:80]: print('  UNLISTED', u)
