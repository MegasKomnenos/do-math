# -*- coding: utf-8 -*-
"""19차 독립 검토 파견문(태그 M)과 19차 수리 공통 안내(태그 X) 1–3절을 18차 것에서 만든다. 2026-11-16.
파일 이름에 차례 번호가 있어 겹치지 않는 7차의 글자(M 검토·X 수리)를 다시 쓴다.
공통 안내의 C50·C20·C1′·(G1)(G2)와 「5차 V2 실측」은 작업자 태그가 아니므로 보호한다."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명\파견"

s = io.open(ROOT + r"\전체_독립검토18_파견문_1116.md", encoding="utf-8").read()
s = re.sub(r"^# .*$", lambda m: m.group(0).replace("18차", "19차").replace("17차 수리", "18차 수리"), s, count=1, flags=re.M)
s = s.replace("검토전체18_L", "검토전체19_M")
s = re.sub(r"\| L(\d+[ab]?) \|", lambda m: "| M" + m.group(1) + " |", s)
s = s.replace("L11·L12·L13", "M11·M12·M13").replace("L14", "M14").replace("L1–L14", "M1–M14")
s = s.replace("`scripts/수학검사2/검토전체18_<태그>_*.py`", "`scripts/수학검사2/검토전체19_<태그>_*.py`")
s = re.sub(r"(?<![A-Za-z가-힣])L(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "M" + m.group(1), s)
io.open(ROOT + r"\전체_독립검토19_파견문_1116.md", "w", encoding="utf-8", newline="\n").write(s)
print("파견문 ok", len(s), "L 잔존", re.findall(r"(?<![A-Za-z가-힣])L\d", s), "18차 잔존", [s[max(0,m.start()-15):m.start()+10] for m in re.finditer("18차", s)])

c = io.open(ROOT + r"\전체검토18_수리_공통_1116.md", encoding="utf-8").read()
i = c.find("## 4. ")
assert i > 0
c = c[:i] + "## 4. 이번 차례의 배정 메모(세션이 보고를 훑어 적은 임자와 주의; 판정이 아니다)\n\n(M1–M14 보고 회수 뒤 작성)\n"
c = c.replace("전체 독립 검토 18차(L1–L14) 뒤의 수리", "전체 독립 검토 19차(M1–M14) 뒤의 수리")
c = c.replace("이 문서는 18차 전체 검토의 지적을 반영하는", "이 문서는 19차 전체 검토의 지적을 반영하는")
c = c.replace("검토전체18_", "검토전체19_").replace("수리_전체18_", "수리_전체19_").replace("인계_전체18_", "인계_전체19_")
PROT = {"C50": "\u0001", "C20": "\u0002", "C1′": "\u0003", "(G1)(G2)": "\u0004", "5차 V2 실측": "\u0005"}
for k, v in PROT.items():
    c = c.replace(k, v)
c = re.sub(r"(?<![A-Za-z가-힣])W(\d+|D|L)(?=[^A-Za-z가-힣]|$)", lambda m: "X" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])W(\d+|D|L)(?=[가-힣·])", lambda m: "X" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])L(\d+[ab]?)(?=[^A-Za-z가-힣]|$)", lambda m: "M" + m.group(1), c)
c = re.sub(r"(?<![A-Za-z가-힣])L(\d+[ab]?)(?=[가-힣·])", lambda m: "M" + m.group(1), c)
for k, v in PROT.items():
    c = c.replace(v, k)
c = c.replace("6차부터 17차까지", "6차부터 18차까지")
io.open(ROOT + r"\전체검토19_수리_공통_1116.md", "w", encoding="utf-8", newline="\n").write(c)
print("공통 ok", len(c), "W 잔존", re.findall(r"(?<![A-Za-z가-힣])W(\d+|D|L)\b", c), "L 잔존", len(re.findall(r"(?<![A-Za-z가-힣])L\d", c)),
      "18차 잔존", [c[max(0,m.start()-15):m.start()+10] for m in re.finditer("18차", c)], "X 토큰", sorted(set(re.findall(r"(?<![A-Za-z가-힣])X(\d+|D|L)\b", c))))
