# -*- coding: utf-8 -*-
"""T11: 진술 머리·절·부록 D 항목 추출과 11.2 표 대조 (자리 찾기용)."""
import re, json, sys, glob, os
ROOT = r"C:\math\임시\주차함수_증명"
CH = os.path.join(ROOT, "장v2")
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리|가정|문제|추측)\s+\{\{(\w+):([\w\-]+)\}\}\s*(\((.*?)\))?\s*(\[(.*?)\])?\.?\*\*')
sec_re = re.compile(r'^###\s+(\d+(?:\.\d+)*)')
chap_files = sorted(glob.glob(os.path.join(CH, "장*.md")))
heads = {}
sections = {}
for f in chap_files:
    cur_sec = None
    cur_head = None
    with open(f, encoding='utf-8') as fh:
        for i, line in enumerate(fh, 1):
            m = sec_re.match(line)
            if m:
                cur_sec = m.group(1)
            m = head_re.match(line)
            if m:
                typ, ch, lab, _, name, _, mark = m.groups()
                key = f"{ch}:{lab}"
                heads[key] = dict(type=typ, file=os.path.basename(f), line=i, sec=cur_sec, name=name, mark=mark, text=line[:300])
D = {}
d_re = re.compile(r'^###\s+D\.\{\{D:([\w\-]+)\}\}\s+(.*)$')
for f in sorted(glob.glob(os.path.join(CH, "부록D_*.md"))):
    cur = None
    with open(f, encoding='utf-8') as fh:
        for i, line in enumerate(fh, 1):
            m = d_re.match(line)
            if m:
                cur = m.group(1)
                D[cur] = dict(file=os.path.basename(f), line=i, title=m.group(2), stmts=re.findall(r'\{\{(\w+):([\w\-]+)\}\}', m.group(2)))
                continue
            if cur and line.startswith('**'):
                mm = re.match(r'^\*\*(.+?)\.\*\*\s*(.*)$', line)
                if mm:
                    D[cur][mm.group(1)] = mm.group(2).strip()
json.dump(dict(heads=heads, D=D), open(os.path.join(ROOT, "대조v2", "수학검사2", "_T11_heads_D.json"), "w", encoding='utf-8'), ensure_ascii=False, indent=1)
print("heads", len(heads), "D", len(D))
# 11.2 표 대조
rows = []
with open(os.path.join(CH, "장11.md"), encoding='utf-8') as fh:
    lines = fh.readlines()
for i, line in enumerate(lines, 1):
    if line.startswith('| 부록 D.{{D:'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        if len(cells) < 6: cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append((i, cells))
for i, c in rows:
    dl = re.search(r'\{\{D:([\w\-]+)\}\}', c[0]).group(1)
    d = D.get(dl)
    if not d:
        print(f"L{i} D항목 없음: {dl}"); continue
    tab_stmts = re.findall(r'\{\{(\w+):([\w\-]+)\}\}', c[1])
    issues = []
    if [s for s in tab_stmts] != d['stmts']:
        issues.append(f"확인진술 불일치: 표 {tab_stmts} / D제목 {d['stmts']}")
    grade_D = d.get('산술 등급', '')
    issues.append(f"등급: 표「{c[2]}」 / D「{grade_D[:120]}」")
    # 쓰인 곳
    secs = sorted({heads.get(f'{a}:{b}', {}).get('sec', '?') for a, b in tab_stmts})
    issues.append(f"쓰인곳: 표「{c[3]}」 / 진술 절 {secs}")
    rec = d.get('독립 재계산', '')
    mbr = re.match(r'〔(.*?)〕\s*(.*)$', rec)
    if mbr:
        br_D, rest_D = mbr.group(1), mbr.group(2)
        br_T = c[4].strip('〔〕')
        if br_D != br_T:
            issues.append(f"꺾쇠 불일치:\n   표 {br_T}\n   D  {br_D}")
        # 본문 비교
        if rest_D != c[5]:
            # 간단 diff 위치
            k = 0
            while k < min(len(rest_D), len(c[5])) and rest_D[k] == c[5][k]: k += 1
            issues.append(f"서술 다름 @{k}: 표「…{c[5][max(0,k-40):k+80]}…」 / D「…{rest_D[max(0,k-40):k+80]}…」")
    else:
        issues.append(f"D 독립 재계산 줄 꺾쇠 없음: {rec[:100]}")
    print(f"\n## L{i} D:{dl} ({d['file']}:{d['line']})")
    for s in issues: print("  -", s)
