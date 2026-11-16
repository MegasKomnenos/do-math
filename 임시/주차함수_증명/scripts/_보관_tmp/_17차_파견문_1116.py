# -*- coding: utf-8 -*-
"""17차 독립 검토 파견문(태그 K)과 17차 수리 공통 안내(태그 V) 1–3절을 16차 것에서 만든다. 2026-11-16.
알파벳 홑글자 태그가 D 하나(부록 D 접미)만 남아, 파일 이름에 차례 번호가 있어 겹치지 않는 5차의 글자(K 검토·V 수리)를 다시 쓴다.
공통 안내의 C50·C20·C1′·(G1)(G2)와 「5차 V2 실측」은 작업자 태그가 아니므로 보호한다."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토16_파견문_1116.md", encoding="utf-8").read()
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("16차", "17차").replace("15차 수리", "16차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체16_E", "검토전체17_K")
s = re.sub(r"\| E(\d+[ab]?) \|", lambda m: "| K" + m.group(1) + " |", s)
s = s.replace("E11·E12·E13", "K11·K12·K13").replace("E14", "K14").replace("E1–E14", "K1–K14")
s = s.replace("`scripts/수학검사2/검토전체16_<태그>_*.py`", "`scripts/수학검사2/검토전체17_<태그>_*.py`")
s = re.sub(r"(?<![A-Za-z가-힣])E(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "K" + m.group(1), s)
io.open(ROOT + r"\전체_독립검토17_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "E 잔존", re.findall(r"(?<![A-Za-z가-힣])E\d", s), "16차 잔존", [s[max(0,m.start()-15):m.start()+10] for m in re.finditer("16차", s)])

c = io.open(ROOT + r"\전체검토16_수리_공통_1116.md", encoding="utf-8").read()
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(K1–K14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 16차(E1–E14) 뒤의 수리", "전체 독립 검토 17차(K1–K14) 뒤의 수리")
c = c.replace("이 문서는 16차 전체 검토의 지적을 반영하는", "이 문서는 17차 전체 검토의 지적을 반영하는")
c = c.replace("검토전체16_", "검토전체17_").replace("수리_전체16_", "수리_전체17_").replace("인계_전체16_", "인계_전체17_")
PROT = {"C50": "\u0001", "C20": "\u0002", "C1′": "\u0003", "(G1)(G2)": "\u0004", "5차 V2 실측": "\u0005"}
for k, v in PROT.items():
    c = c.replace(k, v)
c = re.sub(r"(?<![A-Za-z가-힣])I(\d+|D|L)(?=[^A-Za-z가-힣]|$)", lambda m: "V" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])I(\d+|D|L)(?=[가-힣·])", lambda m: "V" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])E(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "K" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])E(\d+[ab]?)(?=[가-힣·])", lambda m: "K" + m.group(1), c)
for k, v in PROT.items():
    c = c.replace(v, k)
c = c.replace("6차부터 15차까지", "6차부터 16차까지")
io.open(ROOT + r"\전체검토17_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
print("공통 ok", len(c), "I 잔존", re.findall(r"(?<![A-Za-z가-힣])I(\d+|D|L)\b", c), "E 잔존", len(re.findall(r"(?<![A-Za-z가-힣])E\d", c)),
      "16차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("16차", c)], "V 토큰", sorted(set(re.findall(r"(?<![A-Za-z가-힣])V(\d+|D|L)\b", c))))
