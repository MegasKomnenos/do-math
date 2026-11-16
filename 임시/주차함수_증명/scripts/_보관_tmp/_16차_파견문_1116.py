# -*- coding: utf-8 -*-
"""16차 독립 검토 파견문(태그 E)과 16차 수리 공통 안내(태그 I) 1–3절을 15차 것에서 만든다. 2026-11-16.
태그: 검토 K–T·H·F, 수리 U–Z·R·A–C·J·G가 쓰였고 D는 부록 D 접미라 E(검토)·I(수리)를 쓴다(두 파견문에 E·I 토큰이 없음을 확인; 보충 E 물결은 11-16 04:xx의 세션 수리 이름이나 파일 이름에 차례 번호가 있어 겹치지 않는다).
공통 안내의 C50·C20·C1′·(G1)(G2)(5차 선례의 이름)는 작업자 태그가 아니므로 보호한다."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토15_파견문_1116.md", encoding="utf-8").read()
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("15차", "16차").replace("14차 수리", "15차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체15_F", "검토전체16_E")
s = re.sub(r"\| F(\d+[ab]?) \|", lambda m: "| E" + m.group(1) + " |", s)
s = s.replace("F11·F12·F13", "E11·E12·E13").replace("F14", "E14").replace("F1–F14", "E1–E14")
s = s.replace("`scripts/수학검사2/검토전체15_<태그>_*.py`", "`scripts/수학검사2/검토전체16_<태그>_*.py`")
s = re.sub(r"(?<![A-Za-z가-힣])F(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "E" + m.group(1), s)
io.open(ROOT + r"\전체_독립검토16_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "F 잔존", re.findall(r"(?<![A-Za-z가-힣])F\d", s), "15차 잔존", [s[max(0,m.start()-15):m.start()+10] for m in re.finditer("15차", s)])

c = io.open(ROOT + r"\전체검토15_수리_공통_1116.md", encoding="utf-8").read()
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(E1–E14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 15차(F1–F14) 뒤의 수리", "전체 독립 검토 16차(E1–E14) 뒤의 수리")
c = c.replace("이 문서는 15차 전체 검토의 지적을 반영하는", "이 문서는 16차 전체 검토의 지적을 반영하는")
c = c.replace("검토전체15_", "검토전체16_").replace("수리_전체15_", "수리_전체16_").replace("인계_전체15_", "인계_전체16_")
PROT = {"C50": "\u0001", "C20": "\u0002", "C1′": "\u0003", "(G1)(G2)": "\u0004"}
for k, v in PROT.items():
    c = c.replace(k, v)
c = re.sub(r"(?<![A-Za-z가-힣])G(\d+|D|L)(?=[^A-Za-z가-힣]|$)", lambda m: "I" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])G(\d+|D|L)(?=[가-힣·])", lambda m: "I" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])F(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "E" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])F(\d+[ab]?)(?=[가-힣·])", lambda m: "E" + m.group(1), c)
for k, v in PROT.items():
    c = c.replace(v, k)
c = c.replace("6차부터 14차까지", "6차부터 15차까지")
io.open(ROOT + r"\전체검토16_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
print("공통 ok", len(c), "G 잔존", re.findall(r"(?<![A-Za-z가-힣])G(\d+|D|L)\b", c), "F 잔존", len(re.findall(r"(?<![A-Za-z가-힣])F\d", c)),
      "15차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("15차", c)], "14차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("14차", c)],
      "I 토큰", sorted(set(re.findall(r"(?<![A-Za-z가-힣])I(\d+|D|L)\b", c))))
