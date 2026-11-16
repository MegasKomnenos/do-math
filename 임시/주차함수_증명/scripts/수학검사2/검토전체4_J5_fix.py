p="대조v2/수학검사2/검토전체4_J5.md"
s=open(p,encoding="utf-8").read()
start=s.index("**J5-2-1 [문면]**")
end=s.index("그 밖은 없음. 보조정리 `{{6:old-7-19}}`")
new=open("scripts/수학검사2/검토전체4_J5_fix.txt",encoding="utf-8").read()
s=s[:start]+new+s[end:]
open(p,"w",encoding="utf-8").write(s)
print("replaced")
