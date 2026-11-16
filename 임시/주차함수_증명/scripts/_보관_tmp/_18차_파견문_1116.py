# -*- coding: utf-8 -*-
"""18차 독립 검토 파견문(태그 L)과 18차 수리 공통 안내(태그 W) 1–3절을 17차 것에서 만든다. 2026-11-16.
파일 이름에 차례 번호가 있어 겹치지 않는 6차의 글자(L 검토·W 수리)를 다시 쓴다.
공통 안내의 C50·C20·C1′·(G1)(G2)와 「5차 V2 실측」은 작업자 태그가 아니므로 보호한다."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토17_파견문_1116.md", encoding="utf-8").read()
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("17차", "18차").replace("16차 수리", "17차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체17_K", "검토전체18_L")
s = re.sub(r"\| K(\d+[ab]?) \|", lambda m: "| L" + m.group(1) + " |", s)
s = s.replace("K11·K12·K13", "L11·L12·L13").replace("K14", "L14").replace("K1–K14", "L1–L14")
s = s.replace("`scripts/수학검사2/검토전체17_<태그>_*.py`", "`scripts/수학검사2/검토전체18_<태그>_*.py`")
s = re.sub(r"(?<![A-Za-z가-힣])K(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "L" + m.group(1), s)
io.open(ROOT + r"\전체_독립검토18_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "K 잔존", re.findall(r"(?<![A-Za-z가-힣])K\d", s), "17차 잔존", [s[max(0,m.start()-15):m.start()+10] for m in re.finditer("17차", s)])

c = io.open(ROOT + r"\전체검토17_수리_공통_1116.md", encoding="utf-8").read()
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(L1–L14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 17차(K1–K14) 뒤의 수리", "전체 독립 검토 18차(L1–L14) 뒤의 수리")
c = c.replace("이 문서는 17차 전체 검토의 지적을 반영하는", "이 문서는 18차 전체 검토의 지적을 반영하는")
c = c.replace("검토전체17_", "검토전체18_").replace("수리_전체17_", "수리_전체18_").replace("인계_전체17_", "인계_전체18_")
PROT = {"C50": "\u0001", "C20": "\u0002", "C1′": "\u0003", "(G1)(G2)": "\u0004", "5차 V2 실측": "\u0005"}
for k, v in PROT.items():
    c = c.replace(k, v)
c = re.sub(r"(?<![A-Za-z가-힣])V(\d+|D|L)(?=[^A-Za-z가-힣]|$)", lambda m: "W" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])V(\d+|D|L)(?=[가-힣·])", lambda m: "W" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])K(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "L" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])K(\d+[ab]?)(?=[가-힣·])", lambda m: "L" + m.group(1), c)
for k, v in PROT.items():
    c = c.replace(v, k)
c = c.replace("6차부터 16차까지", "6차부터 17차까지")
io.open(ROOT + r"\전체검토18_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
print("공통 ok", len(c), "V 잔존", re.findall(r"(?<![A-Za-z가-힣])V(\d+|D|L)\b", c), "K 잔존", len(re.findall(r"(?<![A-Za-z가-힣])K\d", c)),
      "17차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("17차", c)], "W 토큰", sorted(set(re.findall(r"(?<![A-Za-z가-힣])W(\d+|D|L)\b", c))))
