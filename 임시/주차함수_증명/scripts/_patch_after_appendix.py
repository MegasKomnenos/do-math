# -*- coding: utf-8 -*-
"""부록 집필 회수 뒤 장부·작업 장부 반영(2026-11-12): Ξ→𝔛 잔존 행, 8장 ρ(m) 미사용, 7.2 국소 함수 글자(𝔤→𝖦), 식별자 규칙 확장, 사건 줄."""
import io


def rw(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


root = "임시/주차함수_증명"

p = root + "/장부_기호용어이름.md"
s = rw(p)
# (13) Ξ 잔존
n_xi = s.count(r"\Xi_d(y)") + s.count(r"\Xi^0_d") + s.count(r"\Xi^1_d")
s = s.replace(r"\Xi_d(y)", r"\mathfrak X_d(y)").replace(r"\Xi^0_d", r"\mathfrak X^0_d").replace(r"\Xi^1_d", r"\mathfrak X^1_d")
# (가) 판정 글자 수정
old = r"(가) 정리 AR 증명의 국소 함수 $G(N)$, $G'(N)$은 6.9·7.3의 가장 큰 나무 크기 $G$와 글자가 겹치므로 $\mathfrak g(N)$, $\mathfrak g'(N)$으로 바꾼다."
assert s.count(old) == 1, s.count(old)
s = s.replace(old, r"(가) 정리 AR 증명의 국소 함수 $G(N)$, $G'(N)$은 6.9·7.3의 가장 큰 나무 크기 $G$와 글자가 겹치므로 바꾼다. 처음 정한 $\mathfrak g(N)$은 5.5.6의 $\mathfrak g(\zeta)$와 다시 겹쳐(부록 집필 대조 어긋남 3) $\mathsf G(N)$, $\mathsf G'(N)$으로 확정한다(일관성 수리에서 적용).")
# (14) 8장 ρ(m) 미사용 — 2.8 표에 비고
old = "### 2.9 9장 보증"
assert s.count(old) == 1
s = s.replace(old, "비고(부록 집필 대조 어긋남 14): 2.8 본표의 $\\rho(m)$은 8장 본문에 쓰이지 않았다(부록 A에 싣지 않음). 2.8 본표의 $\\mathcal H_k(s)$도 본문 0회.\n\n" + old)
# 식별자 감사 규칙 5 보강
old = "5. 본문이 인용한 식별자 집합과 부록 B의 목록이 같다."
assert s.count(old) == 1
s = s.replace(old, "5. 본문이 인용한 식별자 집합과 부록 B의 목록이 같다. 식별자는 대괄호 안의 모든 `r`+7자리 토큰(지위 표지의 쌍반점 뒤 `[증명됨; rA, rB]`의 것 포함)을 센다(2026-11-12 확장; 이전 규칙은 `[rX]` 꼴만 세어 15개를 놓쳤다).")
wr(p, s)
print("장부: Ξ 치환 %d, (가) 글자, (14) 비고, 규칙 5" % n_xi)

p = root + "/작업_장부.md"
s = rw(p)
key = "- 2026-11-12 9장·부록 파견 둘("
i = s.index(key)
j = s.index("\n", i)
add = "\n".join([
    r"- 2026-11-12 부록 A·B·C 집필 회수(완료; A 153행, B 65행, C 98행; `장/부록A.md`·`부록B.md`·`부록C.md`, `대조/부록_집필대조.md`). 집필자 발견: 본문 식별자는 80개인데 불변식·부록B_자료 스크립트가 `[rX]` 꼴만 세어 65개였다(지위 표지 `[증명됨; rA, rB]`의 15개 누락) → 세션이 두 스크립트의 규칙을 「대괄호 안의 모든 r+7 토큰」으로 확장(히어독의 역슬래시 축약으로 `\b`가 백스페이스로 깨진 사고를 겪어 전후방 탐색으로 다시 씀; 교훈: 정규식·LaTeX가 든 패치는 Write 도구로 스크립트 파일을 만들어 실행). 재실행 결과 1–8장+부록+9장(집필 중) 식별자 84개. 부록 B에 보탤 19개(표지의 15 + 9장의 r0af7f41, r5c20a94, r77d0f73, r801ec22)는 9장 회수 뒤 부록 집필자 재개로 처리. 어긋남 14건(ζ 네 뜻, 7.2 $\mathfrak g(N)$ 대 5.5.6 $\mathfrak g(\zeta)$ 재충돌, 8장 $\mathsf H$ 두 뜻, 「창 행」·「네 가족」 정의 전 사용 등) → 일관성 수리자 `gp-fable-high` 파견(산출 `대조/일관성_수리.md`; 결정: 7.2 국소 함수는 $\mathsf G(N)$으로). 장부: Ξ→𝔛 잔존 행 정정, (가) 판정 글자 확정, (14) 비고, 감사 규칙 5 보강.",
])
s = s[:j + 1] + add + "\n" + s[j + 1:]
wr(p, s)
print("ledger appended")
