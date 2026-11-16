# -*- coding: utf-8 -*-
"""심사 X6 — 장별 분량 지형: 행 수·글자 수·진술 수(종류별)·증명 행 수·긴 증명 목록·주 정리 비도달 진술의 분량."""
import json, os, re
from collections import Counter, defaultdict
ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, '장v2')
g = json.load(open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_graph.json'), encoding='utf-8'))
stmts = g['statements']
R = set(g['reach_main'])
num = {}; cnt = {}
for s in stmts:
    ch = s['label'].split(':')[0]
    if ch == 'D': continue
    cnt[ch] = cnt.get(ch, 0) + 1
    num[s['label']] = f"{ch}.{cnt[ch]}"
FILES = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md","부록A.md","부록B.md","부록C.md"] + sorted(f for f in os.listdir(CH) if f.startswith('부록D_'))
out = []
out.append('파일\t행\t글자\t진술\t정의\t정리\t명제\t보조\t따름\t증명행\t증명행(비도달)\t비도달진술')
tot = Counter()
for f in FILES:
    txt = open(os.path.join(CH, f), 'rb').read().decode('utf-8')
    lines = txt.split('\n')
    ss = [s for s in stmts if s['file'] == f]
    kinds = Counter(s['kind'] for s in ss)
    pl = sum(s['proof_lines'] for s in ss)
    dead = [s for s in ss if s['label'] not in R and s['kind'] != '정의']
    pld = sum(s['proof_lines'] for s in dead)
    out.append(f"{f}\t{len(lines)}\t{len(txt)}\t{len(ss)}\t{kinds['정의']}\t{kinds['정리']}\t{kinds['명제']}\t{kinds['보조정리']}\t{kinds['따름정리']}\t{pl}\t{pld}\t{len(dead)}")
    tot['행'] += len(lines); tot['글자'] += len(txt); tot['진술'] += len(ss); tot['증명행'] += pl
out.append(f"합계\t{tot['행']}\t{tot['글자']}\t{tot['진술']}\t\t\t\t\t\t{tot['증명행']}")
out.append('')
out.append('# 증명이 긴 진술 상위 40 (증명 행 수; 미룬 증명 포함)')
for s in sorted(stmts, key=lambda s: -s['proof_lines'])[:40]:
    out.append(f"{s['proof_lines']}\t{num.get(s['label'],'')}\t{s['kind']}\t{s['label']}\t{s['name'][:40]}\t{s['file']}:{s['line']}\t{'도달' if s['label'] in R else '비도달'}")
out.append('')
out.append('# 글자 수로 잰 진술 본문(머리~증명 끝, 미룬 증명 포함) 상위 30')
def body_chars(s):
    lines = open(os.path.join(CH, s['file']), encoding='utf-8').read().split('\n')
    t = '\n'.join(lines[s['line']-1:s['body_end']])
    for f, a, b in s['deferred']:
        t += '\n'.join(open(os.path.join(CH, f), encoding='utf-8').read().split('\n')[a-1:b])
    return len(t)
bc = {s['label']: body_chars(s) for s in stmts}
for s in sorted(stmts, key=lambda s: -bc[s['label']])[:30]:
    out.append(f"{bc[s['label']]}\t{num.get(s['label'],'')}\t{s['kind']}\t{s['label']}\t{s['name'][:40]}\t{s['file']}:{s['line']}")
out.append('')
# 장별 진술 본문 글자 합과 산문(진술 밖) 글자 합
out.append('# 장별 진술 본문 글자 합 / 전체 글자 (나머지가 산문·절 머리·표)')
for f in FILES:
    txt = open(os.path.join(CH, f), 'rb').read().decode('utf-8')
    ss = [s for s in stmts if s['file'] == f]
    sb = sum(bc[s['label']] for s in ss)
    out.append(f"{f}\t{sb}\t{len(txt)}\t{sb/len(txt):.2f}")
json.dump({k: v for k, v in bc.items()}, open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_bodychars.json'), 'w', encoding='utf-8'), ensure_ascii=False)
open(os.path.join(ROOT, 'scripts/구조압축/심사_X6_volume.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
