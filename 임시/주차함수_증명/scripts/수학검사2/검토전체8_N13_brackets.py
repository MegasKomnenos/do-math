# 11.2 표의 「재계산」 꺾쇠 괄호와 부록 D 항목의 독립 재계산 꺾쇠 괄호, 산술 등급, 확인 진술 라벨을 대조한다.
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/장v2/"
files = ["부록D_장7A.md","부록D_장7B.md","부록D_장8.md","부록D_장9.md","부록D_장10.md"]
entries = {}
for f in files:
    txt = open(root+f, encoding='utf-8').read()
    parts = re.split(r'^### D\.\{\{D:([^}]+)\}\}', txt, flags=re.M)
    for i in range(1, len(parts), 2):
        lab = parts[i]; body = parts[i+1]
        head = body.split('\n',1)[0]
        m = re.search(r'\*\*독립 재계산\.\*\*\s*〔([^〕]*)〕', body)
        g = re.search(r'\*\*산술 등급\.\*\*\s*(.*)', body)
        entries[lab] = dict(file=f, head=head.strip(), bracket=m.group(1) if m else None,
                            grade=g.group(1)[:200] if g else None,
                            headlabels=re.findall(r'\{\{(\d+:[^}]+)\}\}', head))
t11 = open(root+"장11.md", encoding='utf-8').read().split('\n')
rows = [l for l in t11 if l.startswith('| 부록 D.{{D:')]
for r in rows:
    cells = [c.strip() for c in r.strip().strip('|').split('|')]
    lab = re.search(r'\{\{D:([^}]+)\}\}', cells[0]).group(1)
    if lab not in entries: continue
    e = entries[lab]
    tb = re.search(r'〔([^〕]*)〕', cells[4])
    tb = tb.group(1) if tb else None
    rowlabels = re.findall(r'\{\{(\d+:[^}]+)\}\}', cells[1])
    print("==", lab, e['file'])
    if tb != e['bracket']:
        print("  BRACKET DIFF\n   11.2:", tb, "\n   D   :", e['bracket'])
    if rowlabels != e['headlabels']:
        print("  HEAD LABELS DIFF\n   11.2:", rowlabels, "\n   D   :", e['headlabels'])
    print("  11.2 grade:", cells[2], "| section:", cells[3])
    print("  D grade   :", e['grade'][:120])
    # 독립 재계산 서술 비교(꺾쇠 뒤 본문)
    body = open(root+e['file'], encoding='utf-8').read()
    m = re.search(r'\*\*독립 재계산\.\*\*\s*〔[^〕]*〕\s*(.*)', body.split('### D.{{D:'+lab+'}}')[1])
    dtext = m.group(1).split('\n')[0] if m else ''
    rtext = cells[5]
    if dtext != rtext:
        # find first differing position
        i = 0
        while i < min(len(dtext),len(rtext)) and dtext[i]==rtext[i]: i+=1
        print("  NARRATIVE DIFF at", i, "\n   D   :", dtext[max(0,i-60):i+100], "\n   11.2:", rtext[max(0,i-60):i+100])
