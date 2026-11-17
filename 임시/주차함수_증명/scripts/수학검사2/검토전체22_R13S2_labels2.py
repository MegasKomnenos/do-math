# 장부 행 범위의 모든 {{라벨}}을 뽑아 머리 목록에 없는 것만 보인다(식 라벨인지 죽은 라벨인지).
import sys, io, re, json, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8'))
H = {o['label']: o for o in heads if not o['proof']}
L = open(W+"장부_v2.md", encoding='utf-8').read().split('\n')
txt = {os.path.basename(p)[:-3]: open(p, encoding='utf-8').read() for p in glob.glob(W+"장v2/*.md")}
a, b = int(sys.argv[1]), int(sys.argv[2]); n = 0
for ln in range(a, b+1):
    for m in re.finditer(r'\{\{([^}]+)\}\}', L[ln-1]):
        n += 1; lab = m.group(1)
        if lab not in H:
            where = {f: t.count('{{'+lab+'}}') for f, t in txt.items() if '{{'+lab+'}}' in t}
            ctx = L[ln-1][max(0, m.start()-40):m.end()+20]
            print(ln, lab, 'NOT HEAD', where, '|', ctx)
print('total label mentions', n)
