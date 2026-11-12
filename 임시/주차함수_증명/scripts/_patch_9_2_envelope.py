# -*- coding: utf-8 -*-
"""독해 2 수리 B의 9.2 제안 적용: 정리 W·B′·B‴ 행에 탈출 봉투 y-감소성의 수치 확인과 검토의 「남은 엄밀성 지점」 판단을 적는다."""
import io

p = "임시/주차함수_증명/장/장9.md"
lines = io.open(p, encoding="utf-8").read().split("\n")
done = {"W": 0, "B": 0, "B3": 0, "stmt": 0}
for i, ln in enumerate(lines):
    if ln.startswith("| 배정밀도 평가, 인증 아님 | 정리 {{new:6:theorem-W}} (6.9절) |"):
        cells = ln.split(" | ")
        assert len(cells) >= 5, len(cells)
        cells[2] = cells[2] + r"; 원천 봉투 $Q^{\mathrm{env}}$의 표 구성이 기대는 탈출 쪽 봉투의 $y$-감소성과 여섯 조각의 $k$-단조성은 여섯 $k$($6600$–$10^{12}$), $y\in[0.2,6]$의 $20$만 칸 배정밀도 확인과 기록의 미분 논증"
        cells[4] = cells[4].rstrip(" |") + r"; 검토는 봉투 탈출 부분의 $y$-감소성을 남은 엄밀성 지점으로 적음 |"
        lines[i] = " | ".join(cells)
        done["W"] += 1
    elif ln.startswith("| 배정밀도 평가, 인증 아님 | 정리 {{new:6:theorem-B-prime}} (6.9절) |") or ln.startswith("| 배정밀도 평가, 인증 아님 | 정리 {{old:정리 6.23}} (6.9절) |"):
        cells = ln.split(" | ")
        assert len(cells) >= 5, len(cells)
        cells[4] = cells[4].rstrip(" |") + r"; 봉투의 $y$-감소성은 정리 {{new:6:theorem-W}} 행과 같음 |"
        lines[i] = " | ".join(cells)
        done["B" if "B-prime" in ln else "B3"] += 1
    elif ln.startswith("| 정리 {{new:6:theorem-W}} (창의 수준 질량 하계; 6.9절) |") and "원천 봉투" in ln:
        lines[i] = ln.replace(r"원천 봉투 $Q^{\mathrm{env}}$의 식과 표", r"원천 봉투 $Q^{\mathrm{env}}$의 식과 표(탈출 쪽 봉투의 $y$-감소성은 수치 확인)", 1)
        done["stmt"] += 1
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print(done)
assert done["W"] == 1 and done["B"] == 1 and done["B3"] == 1, done
