# -*- coding: utf-8 -*-
"""15차 독립 검토 파견문(태그 F)과 15차 수리 공통 안내(태그 G) 1–3절을 14차 것에서 만든다. 2026-11-16.
태그: 검토 K–T·H, 수리 U–Z·R·A·B·C·J가 쓰였고 D는 부록 D 접미, I는 1·l과 헷갈려 F(검토)·G(수리)를 쓴다(G7a·G7b는 6차 보충의 이름이나 차례 번호가 달라 파일 이름이 겹치지 않는다).
공통 안내의 C50·C20·C1′·(G1)(G2)(5차 선례의 이름)는 작업자 태그가 아니므로 보호한다."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토14_파견문_1116.md", encoding="utf-8").read()
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("14차", "15차").replace("13차 수리", "14차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체14_H", "검토전체15_F")
s = re.sub(r"\| H(\d+[ab]?) \|", lambda m: "| F" + m.group(1) + " |", s)
s = s.replace("H11·H12·H13", "F11·F12·F13").replace("H14", "F14").replace("H1–H14", "F1–F14")
s = s.replace("`scripts/수학검사2/검토전체14_<태그>_*.py`", "`scripts/수학검사2/검토전체15_<태그>_*.py`")
s = re.sub(r"(?<![A-Za-z가-힣])H(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "F" + m.group(1), s)
io.open(ROOT + r"\전체_독립검토15_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "H 잔존", re.findall(r"(?<![A-Za-z가-힣])H\d", s), "14차 잔존", [s[max(0,m.start()-15):m.start()+10] for m in re.finditer("14차", s)])

c = io.open(ROOT + r"\전체검토14_수리_공통_1116.md", encoding="utf-8").read()
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(F1–F14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 14차(H1–H14) 뒤의 수리", "전체 독립 검토 15차(F1–F14) 뒤의 수리")
c = c.replace("이 문서는 14차 전체 검토의 지적을 반영하는", "이 문서는 15차 전체 검토의 지적을 반영하는")
c = c.replace("검토전체14_", "검토전체15_").replace("수리_전체14_", "수리_전체15_").replace("인계_전체14_", "인계_전체15_")
PROT = {"C50": "\u0001", "C20": "\u0002", "C1′": "\u0003", "(G1)(G2)": "\u0004"}
for k, v in PROT.items():
    c = c.replace(k, v)
c = re.sub(r"(?<![A-Za-z가-힣])J(\d+|D|L)(?=[^A-Za-z가-힣]|$)", lambda m: "G" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])J(\d+|D|L)(?=[가-힣·])", lambda m: "G" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])H(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "F" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])H(\d+[ab]?)(?=[가-힣·])", lambda m: "F" + m.group(1), c)
for k, v in PROT.items():
    c = c.replace(v, k)
c = c.replace("6차부터 13차까지", "6차부터 14차까지")
io.open(ROOT + r"\전체검토15_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
print("공통 ok", len(c), "J 잔존", re.findall(r"(?<![A-Za-z가-힣])J(\d+|D|L)\b", c), "H 잔존", len(re.findall(r"(?<![A-Za-z가-힣])H\d", c)),
      "14차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("14차", c)], "13차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("13차", c)],
      "G 토큰", sorted(set(re.findall(r"(?<![A-Za-z가-힣])G(\d+|D|L)\b", c))))
