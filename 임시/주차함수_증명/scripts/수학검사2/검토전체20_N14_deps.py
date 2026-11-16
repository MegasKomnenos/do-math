# -*- coding: utf-8 -*-
"""N14: 1.5절의 「…에 의존」 규칙 — 외부 입력(계산 증거·계산 보조·문헌 인용·의존)을 가진 진술을 증명이 인용하면 머리가 선언해야 한다 — 를 장 파일에서 센다."""
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
SD = os.path.join(ROOT, "scripts", "수학검사2")
heads = json.load(open(os.path.join(SD, "_N14_heads.json"), encoding='utf-8'))
H = {h['label']: h for h in heads}
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
CH = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
lines = {ch: open(os.path.join(ROOT, "장v2", ch + ".md"), encoding='utf-8').read().split('\n') for ch in CH}
KEY = ('계산 증거', '계산 보조', '문헌 인용', '에 의존')
def tainted(h):
    s = h.get('status') or ''
    return any(k in s for k in KEY)
E = {h['label'] for h in heads if tainted(h)}
print("외부 입력 표지를 가진 진술 수:", len(E), "/", len(heads))
out = []
for h in heads:
    if h['kind'] == '정의': continue
    line = lines[h['file']][h['line'] - 1]
    m = re.search(r'\[(.*?)\]\.\*\*', line)
    bracket = m.group(1) if m else ''
    declared = set(LAB.findall(bracket))
    stmt = set(LAB.findall(line)) - declared - {h['label']}
    cited = stmt | set(h['body_labels'])
    missing = sorted(l for l in cited if l in E and l not in declared)
    unseen = sorted(l for l in declared if l not in cited)
    if missing or unseen:
        out.append((h['label'], h['num'], h['sec'], missing, unseen, h.get('status')))
print("\n== 외부 입력 진술을 인용하면서 선언하지 않은 것(단순 언급 포함; 손 판정 필요) ==")
n = 0
for lab, num, sec, missing, unseen, st in out:
    if missing:
        n += 1
        print(f"{lab} ({num}, {sec}) 선언 밖 인용: {missing} | 지위: {st}")
print("개수:", n)
print("\n== 선언했으나 진술문·증명 어디서도 인용하지 않은 것 ==")
for lab, num, sec, missing, unseen, st in out:
    if unseen:
        print(f"{lab} ({num}, {sec}) 선언만: {unseen}")
