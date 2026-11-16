# I12: 11.2절 표의 「재계산」·「독립 재계산」 열과 부록 D 「독립 재계산」 줄의 일치 검사 (2장–6장 항목)
import re,glob
D={}
for f in ["장v2/부록D_장2.md","장v2/부록D_장3.md","장v2/부록D_장4.md","장v2/부록D_장5A.md","장v2/부록D_장5B.md","장v2/부록D_장6.md"]:
    txt=open(f,encoding='utf-8').read()
    for m in re.finditer(r'### D\.\{\{D:([^}]+)\}\}(.*?)(?=\n### D\.|\Z)',txt,re.S):
        name=m.group(1); body=m.group(2)
        mm=re.search(r'\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*?)\n',body,re.S)
        gr=re.search(r'\*\*산술 등급\.\*\*\s*(.*?)\n',body,re.S)
        st=re.search(r'\*\*확인하는 진술\.\*\*',body)
        head=re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$',m.group(0).split('\n')[0].strip())
        D[name]=(mm.group(1),mm.group(2).strip(),gr.group(1).strip(),m.group(0).split('\n')[0])
tab=open("장v2/장11.md",encoding='utf-8').read()
rows=re.findall(r'^\| 부록 D\.\{\{D:([^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (〔[^〕]*〕) \| (.*?) \|\s*$',tab,re.M)
for name,stmt,grade,sec,br,ind in rows:
    if name not in D: continue
    b,t,g,h=D[name]
    t2=t.replace('이 문단 머리의 꺾쇠 괄호','「재계산」 열의 꺾쇠 괄호')
    print("==",name)
    print("  진술(표):",stmt,"| 머리(D):",h[h.find('('):])
    print("  등급(표):",grade,"| 등급(D):",g[:90])
    print("  꺾쇠 일치:",b==br, "| 서술 일치:", t2==ind)
    if t2!=ind:
        import difflib
        for l in difflib.ndiff([t2],[ind]):
            if l[0] in '+-?': print("   ",l[:300])
