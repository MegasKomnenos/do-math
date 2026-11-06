import re
def blocks(path):
    s=open(path,encoding="utf-8").read()
    s=s[s.index("## 5. L 패킷 확정본"):s.index("## 6. 지적 처분표")]
    out=[]
    for part in re.split(r"\n### 편집 (\d+)\n", s)[1:][1::2]:
        tgt=re.search(r"- 대상: (L-\d{4})", part).group(1)
        anchor=re.search(r'- 기준점: "(.+?)"', part).group(1)
        op=re.search(r"- 조작: (\S+)", part).group(1).rstrip(".")
        q=[l[2:] if l.startswith("> ") else "" for l in part.split("\n") if l.startswith(">")]
        out.append((tgt,anchor,op,q,part))
    return out
eds=[("A",*e) for e in blocks("임시/dream-D0013/확정-A.md")]+[("B",*e) for e in blocks("임시/dream-D0013/확정-B.md")]
assert len(eds)==9,len(eds)
for src,tgt,anchor,op,q,part in eds:
    p=f"기억/layer3/{tgt}.md"; raw=open(p,encoding="utf-8",newline="").read()
    nl="\r\n" if "\r\n" in raw else "\n"; assert raw.count(anchor)==1,(tgt,anchor)
    pos=raw.index(anchor); text=nl.join(q)
    if op=="교체":
        assert len(q)==1; new=raw.replace(anchor,q[0]); where="replace"
    elif "목록 항목" in part:
        end=raw.find(nl,pos); new=raw[:end]+nl+text+raw[end:]; where="after list line"
    else:  # 뒤에 삽입 / 신설: after the anchor's paragraph
        end=raw.find(nl+nl,pos); new=raw[:end]+nl+nl+text+raw[end:]; where="after paragraph"
    open(p,"w",encoding="utf-8",newline="").write(new)
    after=new[new.index(text)+len(text):new.index(text)+len(text)+40].replace(nl,"/") if op!="교체" else ""
    print(src,tgt,op,where,"| next:",after)
