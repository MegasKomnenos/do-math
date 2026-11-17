import re, sys, json, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = [o for o in json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8')) if not o['proof']]
H = {o['label']: o for o in heads}
cnt = Counter(o['sec'] for o in heads)
L = open(W+"구조표_v2.md", encoding='utf-8').read().split('\n')
chap = None
for ln, line in enumerate(L, 1):
    m = re.match(r'^## (\d+)\.', line)
    if m: chap = int(m.group(1))
    if line.startswith('## 부록') or line.startswith('## 설계'): chap = None
    # braced labels
    for m in re.finditer(r'\{\{(\d+):([^}]+)\}\}', line):
        ch, nm = m.groups()
        k = f"{ch}:{nm}"
        k9 = f"9:{nm}" if ch == '10' else k
        if ch == '9' and chap != 10 and False: pass
        if k9 not in H:
            print('BRACED-DEAD', ln, 'chap', chap, k, '…', line[max(0,m.start()-60):m.end()+40].replace('\n',' '))
        elif ch == '9':
            print('BRACED-9(현행 접두)', ln, 'chap', chap, k)
    # unbraced backticked labels that are live
    for m in re.finditer(r'`(\d+):([A-Za-z][^`]*)`', line):
        ch, nm = m.groups(); k = f"{ch}:{nm}"; k9 = f"9:{nm}" if ch == '10' else k
        if k9 in H and not (ch=='9'): print('UNBRACED-LIVE', ln, k)
        if ch=='9' and k in H: print('UNBRACED-9-LIVE?', ln, k)
    if chap and line.startswith('|') and re.match(r'^\| (\d+\.\d+)', line):
        sec = re.match(r'^\| (\d+\.\d+)', line).group(1)
        fins = re.findall(r'진술 (?:수 )?(\d+)→(\d+)', line)
        cur_sec = sec
        if chap == 10: cur_sec = '9.' + sec.split('.')[1]
        if chap == 11: cur_sec = '10.' + sec.split('.')[1]
        if chap == 9: cur_sec = None
        last = fins[-1][1] if fins else None
        keep = re.findall(r'진술 (\d+) 그대로', line)
        if keep: last = keep[-1] if (not fins or line.rfind('그대로') > line.rfind('→')) else last
        print('ROW', ln, 'sec', sec, '→현행', cur_sec, '| 표의 마지막 진술 수:', last, '| 현행 수:', cnt.get(cur_sec) if cur_sec else '-', '' if (last is None or cur_sec is None or int(last)==cnt.get(cur_sec,0)) else '  <<< DIFF')
