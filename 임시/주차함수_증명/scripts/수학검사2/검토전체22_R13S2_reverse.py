# 역방향 점검: 장 파일에서 바탕 기호로(첨자·윗첨자 꼬리표가 아니라) 쓰인 \mathrm{이름}·\mathsf·\mathfrak·\mathcal 토큰이
# 둘 이상의 장에 나오는데 장부 1.2 표(48–287행)의 첫 칸에 없는 것을 뽑는다. 후보일 뿐이고 판정은 원문을 읽어서 한다.
import sys, io, re, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
FILES = ["장1","장2","부록D_장2","장3","부록D_장3","장4","부록D_장4","장5A","장5B","부록D_장5A","장6","장7A","장7B","부록D_장7A","부록D_장7B","장8","부록D_장8","장9","부록D_장9","장10"]
def chap(f): return re.search(r'장(\d+)', f).group(1)
mode = sys.argv[1]  # mathrm | mathsf | mathfrak | mathcal
BS = chr(92)
pat = re.compile('(.{0,2})' + BS + BS + mode + ('[{]([A-Za-z]+)[}]' if mode=='mathrm' else '(?:[{]([A-Za-z]+)[}]| ?([A-Za-z]))'))
use = collections.defaultdict(lambda: collections.Counter())
for f in FILES:
    t = open(W+"장v2/"+f+".md", encoding='utf-8').read()
    for m in pat.finditer(t):
        pre = m.group(1)
        name = m.group(2) or (m.group(3) if mode!='mathrm' else None)
        if pre.endswith('^{') or pre.endswith('_{') or pre.endswith('^') or pre.endswith('_'): continue
        use[name][chap(f)] += 1
L = open(W+"장부_v2.md", encoding='utf-8').read().split('\n')
first = ' '.join(l.split('|')[1] for l in L[47:287] if l.startswith('|') and len(l.split('|'))>2)
for name, c in sorted(use.items(), key=lambda kv: -len(kv[1])):
    if len(c) < 2: continue
    key = BS+mode+'{'+name+'}' if mode=='mathrm' else None
    if mode=='mathrm': inl = key in first
    else: inl = (BS+mode+' '+name in first) or (BS+mode+'{'+name+'}' in first)
    if not inl:
        print(name, dict(c))
