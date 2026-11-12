# -*- coding: utf-8 -*-
"""독해 3 수리 C의 뒤처리: 명제 coupling-ineq의 지위를 비형식 증명으로, 9.1 「진술만」 표에 여섯 행 추가, 라벨 등록."""
import io


def rw(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


root = "임시/주차함수_증명"

# 1. 장6 표지
p = root + "/장/장6.md"
s = rw(p)
old = "(세 용량 개수의 결합 부등식; 기록 [r39ba7c1]의 결합 부등식) [증명됨; r39ba7c1].**"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "(세 용량 개수의 결합 부등식; 기록 [r39ba7c1]의 결합 부등식) [비형식 증명; r39ba7c1].**")
wr(p, s)
print("장6 coupling-ineq 지위 → 비형식 증명")

# 2. 장9 9.1 표에 여섯 행(7장 첫 행 앞에)
p = root + "/장/장9.md"
lines = rw(p).split("\n")
idx = None
for i, ln in enumerate(lines):
    if ln.startswith("| 정리 {{new:7:theorem-F-prime}}"):
        idx = i
        break
assert idx is not None
rows = [
    "| 명제 {{new:6:coupling-ineq}} (세 용량 개수의 결합 부등식; 6.2절) | 비형식 증명 | 증명 전부(모양별 국소 부등식, 연결성, 방향 평균 항등식, Jensen) | [r39ba7c1] §4.1a와 별도 증명 파일 §1–2 |",
    "| 6.7절 표의 임계 창 앞쪽 조각($k\\ge3131$, $14\\le m-k\\le m^{2/3}/2$에서 $U_k(m)>0$) | 비형식 증명 | 증명 전부 | [r7e03176] §8.5 따름정리 W′, [r29c10cd] §7.5 명제 W |",
    "| 6.7절 표의 먼 창 조각($k\\ge10001$, $m^{2/3}/2<m-k<1.4k^{2/3}-1$) | 비형식 증명 | 증명 전부 | [r9bf2dc6] §5.1 |",
    "| 6.7절 표의 작은 $k$의 벌크 조각($3131\\le k\\le10000$, $m^{2/3}/2<m-k$, $m\\le2k-2$) | 비형식 증명, 계산 보조 | 증명 전부 | [r9bf2dc6] §5.2 |",
    "| 6.7절 표의 첫 층의 끝 조각($k\\ge9$에서 $V_{2k-1},V_{2k}>0$) | 비형식 증명, 정리 {{old:정리 4.5}}에 의존 | 증명 전부 | [r29c10cd] §7.2 명제 E(가) |",
    "| 6.7절 표의 창 위쪽 조각($k\\ge10001$, $k-1+1.4k^{2/3}\\le m\\le2k$) | 비형식 증명, 계산 보조 | 증명 전부 | [r29c10cd] §7.2 명제 E(나) |",
]
lines[idx:idx] = rows
wr(p, "\n".join(lines))
print("장9 9.1 표 +6행")

# 3. 라벨 등록
p = root + "/파견/라벨.md"
s = rw(p)
old = "| (정리 B‴는 `{{old:정리 6.23}}`) | | 6.9 |"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, old + "\n| `{{new:6:coupling-ineq}}` | 세 용량 개수의 결합 부등식(기록 [r39ba7c1]; 독해 3 수리에서 세움, 진술만) | 6.2 |")
wr(p, s)
print("라벨 등록")
