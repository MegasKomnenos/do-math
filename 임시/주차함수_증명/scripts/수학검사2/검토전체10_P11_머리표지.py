# -*- coding: utf-8 -*-
"""11.2 표의 진술들의 머리 표지를 뽑고, 11.3 표의 「계산 진술과 산술 등급」 열과 대조할 자료를 만든다."""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
J = json.load(open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체10_P11_heads.json", encoding='utf-8'))
heads, D = J['heads'], J['D']
ch11 = open(r"C:\math\임시\주차함수_증명\장v2\장11.md", encoding='utf-8').read()
# 11.2 표에 적힌 진술 -> (D 항목, 등급)
tab = {}
for ln in ch11.split('\n'):
    if ln.startswith('| 부록 D.{{D:'):
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        lab = re.search(r'\{\{D:([^}]+)\}\}', c[0]).group(1)
        for s in re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', c[1]):
            tab.setdefault(s, []).append((lab, c[2]))
print("=== 11.2 표의 진술과 머리 표지 ===")
for s, lst in tab.items():
    h = heads.get(s)
    print(f"\n{s}  <- {lst}")
    print("   머리:", (h['rest'][:400] if h else '머리 없음'), f"({h['file']}:{h['line']})" if h else '')
# 계산 보조/계산 증거를 단 머리 전부
print("\n\n=== 계산 보조·계산 증거를 단 머리 전부 ===")
for s, h in heads.items():
    if '계산' in h['rest']:
        mark = '표에 있음' if s in tab else '** 11.2 표에 없음 **'
        print(f"{s} [{mark}] {h['rest'][:300]}")
