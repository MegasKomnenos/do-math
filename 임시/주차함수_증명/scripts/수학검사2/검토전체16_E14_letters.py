# -*- coding: utf-8 -*-
"""E14: 수식 안 맨 글자(이탤릭) 출현을 센다. 장부 1.1·1.3·6절의 「X장에는 맨 글자 ...가 없다」류 주장 확인."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
BS = chr(92)
CMD = re.compile(BS+BS+r'(?:mathfrak|mathsf|mathrm|mathcal|mathbb|operatorname|text|mathbf|mathscr)\s*(?:\{[^}]*\}|[A-Za-z])')
ANY = re.compile(BS+BS+r'[A-Za-z]+')
def math_spans(txt):
    for m in re.finditer(r'\$\$(.+?)\$\$|\$(.+?)\$', txt, re.S):
        yield m.start(), (m.group(1) or m.group(2))
def standalone(letter, f):
    txt=open(f"{ROOT}/장v2/{f}.md",encoding='utf-8').read()
    hits=[]
    if letter.startswith(BS):
        pat=re.compile(re.escape(letter)+r'(?![A-Za-z])')
        for pos,s in math_spans(txt):
            s2=CMD.sub(' ', s)
            if pat.search(s2): hits.append((txt.count("\n",0,pos)+1, s.strip()[:80]))
        return hits
    pat=re.compile(r'(?<![A-Za-z])'+re.escape(letter)+r'(?![A-Za-z])')
    for pos,s in math_spans(txt):
        s2=CMD.sub(' ', s); s2=ANY.sub(' ', s2)
        if pat.search(s2):
            hits.append((txt.count("\n",0,pos)+1, s.strip()[:80]))
    return hits
G = lambda name: BS+name
checks=[('m','장4','1.1: 4장에는 이탤릭 m이 나오지 않는다'),('u','장7A','1.1: 7장에 맨 글자 u 없음'),('u','장7B','1.1: 7장에 맨 글자 u 없음'),('u','장8','1.1: 8장에 맨 글자 u 없음'),('t','장11','1.1: 11장에 맨 글자 t 없음'),('N','장5A','6절: 5장에 대문자 N 없음'),('N','장5B','6절: 5장에 대문자 N 없음'),('X','장5A','6절: 5A 국소 X 없음'),('X','장5B','6절: 5B 국소 X'),('X','장6','6절: 장6 국소 X 없음'),('G','장7A','1.3 7.3: 7A 이탤릭 G'),('G','장7B','1.3 7.3: 7B 이탤릭 G'),('L','장5A','1.3 5.2: 1.2 사슬 길이 L은 5장이 쓰지 않는다'),('L','장5B','1.3 5.5: L은 5.5절이 쓰지 않는다'),('f','장5A','1.3: 1.2 밀도 f는 5장에 나오지 않는다'),('f','장5B','(같음)'),('f','장6','1.3 6.5: 밀도 f는 6장에 나오지 않는다'),('f','장9','1.3 9.1: 밀도 f는 9장에 나오지 않는다'),('g','장4','1.3 4.3: 1.2 g(x)는 4장에 나오지 않음'),(G('tau'),'장6','1.3 6.5: 6장에 전역 τ 없음(국소만)'),(G('xi'),'장5A','1.3: 1.2 ξ는 5장에서 쓰이지 않음'),(G('xi'),'장5B','(같음)'),(G('xi'),'장6','1.3 6.3: 1.2 ξ는 6장에 나오지 않음'),(G('xi'),'장7A','1.3 7.1: 1.2 ξ는 7장에서 쓰이지 않음'),(G('xi'),'장7B','(같음)'),('F','장10','1.3 10.6: 1.2 숲 F는 10장에 나오지 않음'),(G('gamma'),'장7A','1.3 7.3: 7장 여유 그리스 γ·ς는 이제 7장이 쓰지 않는다'),(G('gamma'),'장7B','(같음)'),(G('varsigma'),'장7A','(같음)'),(G('varsigma'),'장7B','(같음)'),('N','장4','6절: 4.3 Euler–Maclaurin 상한 N(허용)'),('V','장7A','1.3 7.3: 2차 V를 ψ_G로 바꿈'),('V','장7B','1.2 V(x) 7장 씀'),('T','장6','1.3 6.5: 6장 T는 실수 용량 연장(국소)'),('m','장10','1.1 m 쓰이는 장에 10 포함'),('u','장2','1.1 u 2장'),('u','장6','1.1 u 6장'),('u','장9','1.1 u 9장'),('u','장5A','1.1: 5장의 맨 u는 생성함수·적분의 임시 변수'),('u','장5B','(같음)'),('r','장8','0절 R1: 8.2의 합 지표 r'),('r','장3','1.1 r 쓰이는 장(1,2,4,5,9,11) — 3장 없음'),('r','장6','1.1 r — 6장 없음'),('r','장7A','1.1 r — 7장 없음(7.4 국소 지표 r 허용)'),('r','장7B','(같음)'),('r','장10','1.1 r — 10장 없음')]
for letter,f,claim in checks:
    h=standalone(letter,f)
    print(f"== {claim} [{f}, {letter}]: {len(h)} hits")
    for x in h[:8]: print("   ", x)
