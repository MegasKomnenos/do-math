# -*- coding: utf-8 -*-
import re, json, os
base = r"C:\math\임시\주차함수_증명"
files = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
appx = ["부록A","부록B","부록C","부록D_장2","부록D_장3","부록D_장4","부록D_장5A","부록D_장7A","부록D_장7B","부록D_장8","부록D_장9"]
def rd(name):
    return open(os.path.join(base,"장v2",name+".md"),encoding="utf-8").read()
heads = json.load(open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_heads.json"),encoding="utf-8"))
hd = {h["label"][2:-2]:h for h in heads}
_cache={}
def lines(name):
    if name not in _cache: _cache[name]=rd(name).split("\n")
    return _cache[name]
def block(label):
    """머리 줄부터 다음 머리(또는 ## 절) 전까지: (진술 줄, 전체)"""
    h=hd[label]; L=lines(h["file"]); i=h["line"]-1
    j=i+1
    while j<len(L) and not re.match(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{",L[j]) and not L[j].startswith("#"):
        j+=1
    # 진술부: 머리 줄부터 '**증명' 전까지
    k=i+1
    while k<j and not L[k].startswith("**증명"):
        k+=1
    return "\n".join(L[i:k]), "\n".join(L[i:j])
chap_of_file={"장1":1,"장2":2,"장3":3,"장4":4,"장5A":5,"장5B":5,"장6":6,"장7A":7,"장7B":7,"장8":8,"장9":9,"장10":10,
 "부록D_장2":2,"부록D_장3":3,"부록D_장4":4,"부록D_장5A":5,"부록D_장7A":7,"부록D_장7B":7,"부록D_장8":8,"부록D_장9":9}
