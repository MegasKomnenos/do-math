# -*- coding: utf-8 -*-
"""13차 독립 검토 파견문(태그 T)과 13차 수리 공통 안내(태그 C) 1–3절을 12차 것에서 만든다. 2026-11-16."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토12_파견문_1116.md", encoding="utf-8").read()
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("12차", "13차").replace("11차 수리", "12차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체12_S", "검토전체13_T")
s = re.sub(r"\| S(\d+[ab]?) \|", lambda m: "| T" + m.group(1) + " |", s)
s = s.replace("S11·S12·S13", "T11·T12·T13").replace("S14", "T14").replace("S1–S14", "T1–T14")
s = s.replace("`scripts/수학검사2/검토전체12_<태그>_*.py`", "`scripts/수학검사2/검토전체13_<태그>_*.py`")
io.open(ROOT + r"\전체_독립검토13_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "S 잔존", len(re.findall(r"\bS\d", s)), "12차 잔존", [s[max(0,m.start()-15):m.start()+10] for m in re.finditer("12차", s)])

c = io.open(ROOT + r"\전체검토12_수리_공통_1116.md", encoding="utf-8").read()
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(T1–T14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 12차(S1–S14) 뒤의 수리", "전체 독립 검토 13차(T1–T14) 뒤의 수리")
c = c.replace("이 문서는 12차 전체 검토의 지적을 반영하는", "이 문서는 13차 전체 검토의 지적을 반영하는")
c = c.replace("검토전체12_", "검토전체13_").replace("수리_전체12_", "수리_전체13_").replace("인계_전체12_", "인계_전체13_")
c = re.sub(r"(?<![A-Za-z가-힣])B(\d+|D|L)(?=[^A-Za-z가-힣]|$)", lambda m: "C" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])B(\d+|D|L)(?=[가-힣·])", lambda m: "C" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])S(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "T" + m.group(1) + "" if False else "T" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])S(\d+[ab]?)(?=[가-힣·])", lambda m: "T" + m.group(1), c)
c = c.replace("6차부터 11차까지", "6차부터 12차까지")
io.open(ROOT + r"\전체검토13_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
print("공통 ok", len(c), "B 잔존", len(re.findall(r"(?<![A-Za-z가-힣])B(\d+|D|L)\b", c)), "S 잔존", len(re.findall(r"(?<![A-Za-z가-힣])S\d", c)), "12차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("12차", c)])
