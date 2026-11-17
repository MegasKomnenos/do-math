# -*- coding: utf-8 -*-
# 5절 둘째 열의 전역 기호마다, 그 장의 파일에 그 글자의 고정 문자열(여러 철자)이 있는지 센다.
# 0건인 것만 사람이 원문을 열어 확인할 후보로 찍는다. 아울러 1.2 「쓰이는 장」의 각 장에도 같은 셈을 한다(인수 'used').
import sys, io, re, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
t12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t12)
BS=chr(92)
FILES = {1:['장1'],2:['장2','부록D_장2'],3:['장3','부록D_장3'],4:['장4','부록D_장4'],5:['장5A','장5B','부록D_장5A'],6:['장6'],
         7:['장7A','장7B','부록D_장7A','부록D_장7B'],8:['장8','부록D_장8'],9:['장9','부록D_장9'],10:['장10']}
TXT = {ch: '\n'.join(io.open('장v2/%s.md'%f,encoding='utf-8').read() for f in fs) for ch,fs in FILES.items()}
def split_variants(cell):
    s = cell.strip().strip('$')
    out=[]; depth=0; cur=''
    for chx in s:
        if chx in '({[': depth+=1
        if chx in ')}]': depth-=1
        if chx==',' and depth==0:
            out.append(cur.strip()); cur=''
        else: cur+=chx
    out.append(cur.strip())
    return [v for v in out if v]
def spellings(v):
    # 인수 괄호 앞까지를 핵으로 삼고 철자 변형을 만든다
    core = v
    m = re.search(r'\((?![^)]*\)\s*[_^])', core)
    # 꼬리표 꼴 (G)_d, (\star)(n) 은 그대로
    if not core.startswith('('):
        # 첫 '(' 가 인수의 시작이면 자른다
        i = core.find('(')
        if i>0: core = core[:i]
    c=set([core])
    def add(x): c.add(x)
    for x in list(c):
        add(re.sub(r'\^\{(\w)\}', r'^\1', x)); add(re.sub(r'_\{(\w)\}', r'_\1', x))
        add(x.replace('^'+BS+'prime',"'")); add(x.replace('^{'+BS+'prime}',"'"))
        add(x.replace(BS+'ast','*')); add(x.replace('^'+BS+'ast','^*'))
    for x in list(c):
        add(re.sub(r'\^(\w)(?!\w)', r'^{\1}', x))
    # 첨자 글자가 달라질 수 있으므로 마지막 아래첨자를 떼어 낸 꼴도
    for x in list(c):
        y = re.sub(r'_\{[^{}]*\}$','',x); y = re.sub(r'_[A-Za-z0-9]$','',y); y=re.sub(r'_'+re.escape(BS)+r'[A-Za-z]+$','',y)
        if y!=x and len(y)>=2: add(y+'_')
    return sorted(c, key=len, reverse=True)
mode = sys.argv[1] if len(sys.argv)>1 else 'def'
rows = t12.table(49,288)
def chap_of_sec(s):
    m = re.match(r'\s*(\d+)\.', s); return int(m.group(1)) if m else None
for ln,c in rows:
    defch = chap_of_sec(c[3]); used = sorted(set(int(x) for x in re.findall(r'\d+', c[4].split('(')[0])))
    targets = [defch] if mode=='def' else used
    for v in split_variants(c[0]):
        sp = spellings(v)
        for ch in targets:
            n = sum(TXT[ch].count(s) for s in sp[:1])
            tot = [(s, TXT[ch].count(s)) for s in sp]
            if all(k==0 for _,k in tot):
                print('0건: 1.2 %d행 %s 의 변형 %s — 장 %d; 찾은 철자 %s'%(ln,c[0],v,ch,[s for s,_ in tot]))
