# -*- coding: utf-8 -*-
# 1.1의 그리스 변수(\nu, \ell)와 1.2의 \lambda가 장별로 몇 번 나오는지, 10장의 k·\ell·\nu 문맥.
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
for tok in [r"\\nu(?![A-Za-z])", r"\\ell(?![A-Za-z])", r"\\lambda(?![A-Za-z])"]:
    out={}
    for f in files+[a for a in appx if a.startswith("부록D")]:
        n=len(re.findall(tok,rd(f)))
        if n: out[f]=n
    print(tok,out)
t=rd("장10")
for m in re.finditer(r"\\ell(?![A-Za-z])|\\nu(?![A-Za-z])|(?<![A-Za-z\\{:\-])k(?![A-Za-z}\-])",t):
    ln=t.count("\n",0,m.start())+1
    print(ln,t[max(0,m.start()-70):m.end()+50].replace("\n"," "))
