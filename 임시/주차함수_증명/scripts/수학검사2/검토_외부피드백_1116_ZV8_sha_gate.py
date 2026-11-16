# -*- coding: utf-8 -*-
"""ZV8: 배포 직전의 관문 — 원고_자료/README.md의 SHA-256 표 둘(세션 재계산 2열 표, 파일 목록 4열 표)의 모든 행이
디스크의 파일과 일치하고 빠진 경로가 없으면 0, 하나라도 어긋나면 1을 돌려준다(어긋난 행을 모두 적는다).
ZV4의 대조 스크립트(검토_외부피드백_1116_ZV4_sha.py)와 같은 정규식을 쓰되 종료 코드로 판정만 한다.
python -I scripts/수학검사2/검토_외부피드백_1116_ZV8_sha_gate.py"""
import hashlib, os, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
MAT = os.path.join(ROOT, "원고_자료")
readme = open(os.path.join(MAT, 'README.md'), encoding='utf-8').read()
rows2 = re.findall(r'^\| `([^`]+)` \| `([0-9a-f]{64})` \|\s*$', readme, re.M)
rows4 = re.findall(r'^\| `([^`]+)` \| (.*?) \| ([^|]*?) \| `([0-9a-f]{64})` \|\s*$', readme, re.M)
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
bad = 0
for label, rows in (("세션 재계산", rows2), ("파일 목록", rows4)):
    seen = set(); ok = 0
    for r in rows:
        p, h = r[0], r[-1]
        if (p, h) in seen: continue
        seen.add((p, h))
        fp = os.path.join(MAT, p)
        if not os.path.exists(fp):
            print(f"[{label}] 경로 없음  {p}"); bad += 1; continue
        if sha(fp) != h:
            print(f"[{label}] 해시 불일치 {p}"); bad += 1
        else: ok += 1
    print(f"[{label}] 행 {len(rows)}, 고유 쌍 {len(seen)}, 일치 {ok}")
print("어긋남 합계:", bad)
sys.exit(1 if bad else 0)
