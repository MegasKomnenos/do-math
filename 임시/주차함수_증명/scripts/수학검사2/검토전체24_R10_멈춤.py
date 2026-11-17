# 부록 B의 기록에서 「멈춤 확률」이 나오는 자리의 글귀를 찍는다(부록 C 94행 확인용).
import re, io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
R = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
B = open(r'C:/math/임시/주차함수_증명/장v2/부록B.md', encoding='utf-8').read()
folders = re.findall(r'(?m)^[|] (r[0-9a-f]{7}) [|].*[|] `([0-9a-z]+)` [|]$', B)
for rid, fo in folders:
    for f in glob.glob(R+fo+'/**/*', recursive=True):
        if not (f.endswith('.md') or f.endswith('record.json')): continue
        try: t = open(f, encoding='utf-8').read()
        except Exception: continue
        js = [m.start() for m in re.finditer('멈춤 확률', t)]
        for j in js[:2]:
            print(f'[{rid}] {os.path.relpath(f, R+fo)} ({len(js)}곳): …' + t[max(0, j-150):j+130].replace('\n', ' ') + '…')
