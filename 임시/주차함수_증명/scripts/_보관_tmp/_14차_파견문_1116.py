# -*- coding: utf-8 -*-
"""14차 독립 검토 파견문(태그 H)과 14차 수리 공통 안내(태그 J) 1–3절을 13차 것에서 만든다. 2026-11-16.
태그 선택: 검토 K·L·M·N·O·P·Q·S·T, 수리 U·V·W·X·Y·Z·R·A·B·C, 보충 E·G·ZV·ZJ·ZM이 이미 쓰였고 D는 부록 D 작업자 접미, I는 1·l과 헷갈려 H(검토)·J(수리)를 쓴다.
공통 안내의 C50·C20(5차 선례의 상수 이름)·C1′(글자 규칙 이름)은 작업자 태그가 아니므로 보호한다."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토13_파견문_1116.md", encoding="utf-8").read()
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("13차", "14차").replace("12차 수리", "13차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체13_T", "검토전체14_H")
s = re.sub(r"\| T(\d+[ab]?) \|", lambda m: "| H" + m.group(1) + " |", s)
s = s.replace("T11·T12·T13", "H11·H12·H13").replace("T14", "H14").replace("T1–T14", "H1–H14")
s = s.replace("`scripts/수학검사2/검토전체13_<태그>_*.py`", "`scripts/수학검사2/검토전체14_<태그>_*.py`")
s = re.sub(r"(?<![A-Za-z가-힣])T(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "H" + m.group(1), s)
io.open(ROOT + r"\전체_독립검토14_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "T 잔존", re.findall(r"(?<![A-Za-z가-힣])T\d", s), "13차 잔존", [s[max(0,m.start()-15):m.start()+10] for m in re.finditer("13차", s)])

c = io.open(ROOT + r"\전체검토13_수리_공통_1116.md", encoding="utf-8").read()
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(H1–H14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 13차(T1–T14) 뒤의 수리", "전체 독립 검토 14차(H1–H14) 뒤의 수리")
c = c.replace("이 문서는 13차 전체 검토의 지적을 반영하는", "이 문서는 14차 전체 검토의 지적을 반영하는")
c = c.replace("검토전체13_", "검토전체14_").replace("수리_전체13_", "수리_전체14_").replace("인계_전체13_", "인계_전체14_")
# 보호: 작업자 태그가 아닌 C 토큰
PROT = {"C50": "\u0001", "C20": "\u0002", "C1′": "\u0003"}
for k, v in PROT.items():
    c = c.replace(k, v)
c = re.sub(r"(?<![A-Za-z가-힣])C(\d+|D|L)(?=[^A-Za-z가-힣]|$)", lambda m: "J" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])C(\d+|D|L)(?=[가-힣·])", lambda m: "J" + m.group(1), c)
for k, v in PROT.items():
    c = c.replace(v, k)
c = re.sub(r"(?<![A-Za-z가-힣])T(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "H" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])T(\d+[ab]?)(?=[가-힣·])", lambda m: "H" + m.group(1), c)
c = c.replace("6차부터 12차까지", "6차부터 13차까지")
io.open(ROOT + r"\전체검토14_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
left_C = [c[max(0,m.start()-10):m.start()+6] for m in re.finditer(r"(?<![A-Za-z가-힣])C(\d+|D|L)\b", c)]
print("공통 ok", len(c), "C 잔존", left_C, "T 잔존", len(re.findall(r"(?<![A-Za-z가-힣])T\d", c)), "13차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("13차", c)], "12차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("12차", c)])
