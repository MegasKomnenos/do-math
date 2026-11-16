# -*- coding: utf-8 -*-
"""외부 교정 셋째 묶음(오식·기호 미통일) 가운데 세션이 원문 대조로 확인한 항목을 본문 조각에 반영한다. 멱등.
각 치환은 기대 횟수를 적고, 어긋나면 멈춘다(None은 횟수만 보고)."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv

EDITS = [
    # 3.3 정리(로그오목성의 실패) 증명: 첨자 h → I
    ("장v2/장3.md", r"T^{(n)}_hT^{(n)}_{3I}", r"T^{(n)}_IT^{(n)}_{3I}", 1),
    # 4.3·5.6: 옛 글자 W_j → Wi_j (k 앞에 붙은 자리만 남아 있었다)
    ("장v2/장4.md", r"kW_2", r"k\mathrm{Wi}_2", 7),
    ("장v2/장4.md", r"kW_1", r"k\mathrm{Wi}_1", 3),
    ("장v2/장5B.md", r"kW_2", r"k\mathrm{Wi}_2", 3),
    ("장v2/장5B.md", r"kW_1", r"k\mathrm{Wi}_1", 1),
    # 4.3 보조정리(Gauss 계수의 경계) 증명 끝: ∎와 줄바꿈
    ("장v2/장4.md", "$11/2$보다 크다. **첫 조각의 환원.**", "$11/2$보다 크다. ∎\n\n**첫 조각의 환원.**", 1),
    # 5.2 정리(양의 원천 표현): 기록 글자 D_d → sd_d
    ("장v2/장5A.md", r"D_{n-m-1}(k+1)", r"\mathrm{sd}_{n-m-1}(k+1)", 2),
    ("장v2/장5A.md", r"D_{n-m-1}(k)", r"\mathrm{sd}_{n-m-1}(k)", 2),
    # 5.2 보조정리(고정 크기 응답) (나): 1차 글자 V_i → fs_i
    ("장v2/장5A.md", r"\frac{V_i}{n-i}", r"\frac{\mathrm{fs}_i}{n-i}", 1),
    # (다)·역수 형태: 1차 글자 tilde V의 반쪽 치환 tilde fs → fs'
    ("장v2/장5A.md", r"\tilde{\mathrm{fs}}", r"\mathrm{fs}'", None),
    # 타일 합은 모두 mathcal V (fs는 인수 없는 고정 크기 응답에만)
    ("장v2/장5A.md", r"($\mathrm{fs}_0:=1$)", r"($\mathcal V_0:=1$)", 1),
    ("장v2/장5A.md", r"\mathcal V_d=(1+q_d)\mathrm{fs}_{d-1}+\sum_{j\ge2}\mathrm{tw}_j\mathrm{fs}_{d-j}",
     r"\mathcal V_d=(1+q_d)\mathcal V_{d-1}+\sum_{j\ge2}\mathrm{tw}_j\mathcal V_{d-j}", 1),
    ("장v2/장5A.md", r"\mathrm{fs}_{r-1}(", r"\mathcal V_{r-1}(", None),
    # fs'_d의 정의 자리는 (다)의 증명 하나로
    ("장v2/장5A.md", r"$\mathrm{fs}'_d:=\Gamma_d(y;n)/(n)_d$는 $\mathrm{fs}'_0=1$과",
     r"$\mathrm{fs}'_d=\Gamma_d(y;n)/(n)_d$(보조정리 {{5:fixed-size-response}}(다)의 증명에서 둔 글자)는 $\mathrm{fs}'_0=1$과", 1),
    # 5.5.7·5.5.9: 1차 글자 H → hov
    ("장v2/장5B.md", r"H(\rho_0,Q_{\mathrm w})", r"\mathrm{hov}(\rho_0,Q_{\mathrm w})", 3),
    # 7.2: 가중치 글자 G → Psi; 모멘트 판정 통계는 mathcal T_k (J^S_k는 자기일관 상계의 절단 정수)
    ("장v2/장7A.md", r"\mathbb E_GZ_y", r"\mathbb E_\Psi Z_y", 1),
    ("장v2/장7A.md", r"\mathbb E^{\sigma}_{n,k}[\mathcal J^{\mathrm S}_k]", r"\mathbb E^{\sigma}_{n,k}[\mathcal T_k]", 2),
    # 7.4 보조정리(Green 원자) 머리: 잘린 식별자
    ("장v2/장7B.md", "[r8d685]", "[r8d6850a]", 1),
    # 7.7 정리(둘째 층의 한 걸음 항등식) 증명: 분할 무게는 이탤릭 w
    ("장v2/장7B.md", r"k\mathrm w_{2k}A_{2k,k-1}", r"kw_{2k}A_{2k,k-1}", 1),
]


def main():
    texts = {}
    for rel, old, new, expect in EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel)
        if s is None:
            s = io.open(p, encoding="utf-8").read()
        n = s.count(old)
        if n == 0:
            if new in s:
                print(f"{rel}: 이미 반영 — {old[:40]}")
                continue
            print(f"{rel}: 원문 없음 — {old[:60]}")
            sys.exit(1)
        if expect is not None and n != expect:
            print(f"{rel}: 횟수 어긋남 {n}≠{expect} — {old[:60]}")
            sys.exit(1)
        s = s.replace(old, new)
        texts[rel] = s
        print(f"{rel}: {n}곳 — {old[:50]} → {new[:50]}")
    if DRY:
        print("(dry) 쓰지 않음")
        return
    for rel, s in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
    print("기록함:", ", ".join(texts))


if __name__ == "__main__":
    main()
