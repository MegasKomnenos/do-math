# 장1·장2가 인용한 라벨 {{X:label}}이 해당 장 파일에 진술 머리로 존재하는지, 인용한 종류(정리/명제/...)가 머리의 종류와 같은지 본다.
import re, glob, os, sys
root=r"C:\math\임시\주차함수_증명\장v2"
files={os.path.basename(p)[:-3]:p for p in glob.glob(os.path.join(root,"*.md"))}
# 라벨 정의 수집: **종류 {{X:label}} ...**  (정의, 정리, 명제, 보조정리, 따름정리, 문제, 가설 등)
defs={}
for name,p in files.items():
    txt=open(p,encoding="utf-8").read()
    for m in re.finditer(r"\*\*(정의|정리|명제|보조정리|따름정리|문제|추측|가설|관찰|예)\s+\{\{([^}:]+):([^}]+)\}\}",txt):
        defs[(m.group(2),m.group(3))]=(m.group(1),name)
out=[]
for ch in ["장1","장2"]:
    txt=open(files[ch],encoding="utf-8").read()
    lines=txt.split("\n")
    for i,l in enumerate(lines,1):
        for m in re.finditer(r"(정의|정리|명제|보조정리|따름정리|문제|D)?\.?\s*\{\{([^}:]+):([^}]+)\}\}",l):
            kind,X,lab=m.group(1),m.group(2),m.group(3)
            key=(X,lab)
            if X=="D":
                # 부록 D 라벨: 부록D_장*.md 안에 "{{D:lab}}" 존재 여부
                found=[n for n,p in files.items() if n.startswith("부록D") and ("{{D:%s}}"%lab) in open(p,encoding="utf-8").read()]
                if not found: out.append(f"{ch}:{i} D 라벨 없음 {{{{D:{lab}}}}}")
                continue
            if key not in defs:
                out.append(f"{ch}:{i} 정의 없는 라벨 {{{{{X}:{lab}}}}} (인용 종류 {kind})")
            else:
                dk,dn=defs[key]
                # 정의 머리가 아닌 자기 자신 선언은 건너뜀
                if l.startswith("**") and ("{{%s:%s}}"%(X,lab)) in l and dn==ch and kind==dk and l.find("{{%s:%s}}"%(X,lab))<40:
                    continue
                if kind and kind!=dk:
                    out.append(f"{ch}:{i} 종류 불일치 {{{{{X}:{lab}}}}} 인용={kind} 정의={dk}({dn})")
out.append(f"정의된 라벨 수={len(defs)}")
open(sys.argv[1],"w",encoding="utf-8").write("\n".join(out)+"\n")
