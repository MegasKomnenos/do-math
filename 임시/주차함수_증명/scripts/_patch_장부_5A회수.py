# -*- coding: utf-8 -*-
"""작업 장부: 5A 회수와 2차 대조 파견, 시험 조립·불변식 결과 항목을 더한다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()

ENTRY = (
    "- 2026-11-12 23:2x **5A 회수와 2차 대조 파견; 시험 조립**: 5A 집필(fable-high, 118분; 압축 한 번) — `장v2/장5A.md`(207KB; 5.1–5.4, 진술 48 = 파견 47 + `{{5:witness-position-bound}}`; 비형식 증명 14·계산 증거 3), `부록D_장5A.md`(항목 8; exact-n20000에 증인 위치 경계의 확인 (ㅂ) 추가), `대조v2/장5A_집필대조.md`. "
    "중대 사항: 증인 위치 경계의 출처는 [r19de912](mode-formula-crosscheck; [r7e03176] §8은 인용), 봉우리 한 칸은 [r59c82d7] C20; 기록 사이 어긋남 셋(정리 5.13 결함 다섯·여백 0.00156, 정리 5.1 (ㄴ) 비엄격, 정리 5.3 「최적 시작점」은 오목성에만); 작성자 판단 17단계 중 머리 표지는 green-connection 하나. "
    "의존지도에 더할 간선: `{{5:old-5-10}}`→`{{5:SR-implies-QR}}`, `{{5:old-5-15}}`→`{{5:cover-edge}}`(나), `{{5:kernel-sandwich}}`→kernel-C-bound·kernel-bounds·sign-sandwich(명세 재빌드 때 세션). 사전 후속(최종 정리 때): 묶음 387 $z_\\ast\\to r_\\ast$ 제안, 387 $\\iota$와 384 $\\iota$ 겹침, 379 $\\theta_k\\to\\vartheta_j$, 국소 글자 약 190개 합침. "
    "5A 2차 대조 파견(gp-fable-high; `대조v2/장5A_2차대조.md`; 특별 지시 여섯: 작성자 판단 17단계 전수, 결정 38 지위 재판정(FKG·Lambert W는 표준), 2장 전제 $n\\ge2r+1$·4장·6장 접합, 사전 190글자, 기록 어긋남 셋, 식별자·등급 꼴). "
    "**시험 조립**(`scripts/조립_v2.py --out 대조v2/_시험조립_2320.md`, 5A 포함 전 10장): 라벨 427 전부 해소, 부록 D 45항목, [todo] 0; 문제 1 — 라벨 중복 `{{5:weight-envelope}}`(5A 5.4 [r13b0b8f] 등록 라벨 vs 5B 5.5 [r8a9b11e] U2; 5B 쪽을 바꿈 → 5B 재개 항목). "
    "불변식 v2 실패 19: 식별자 짧은 꼴 `ra7615a`(4장 e-integral; 폴더 ra7615a0…)·`r9e782`(7A seed-transfer; 폴더 r9e782f5…) → 전 파일 치환 대상(결정 39와 같은 꼴), 7A 「검토가 고친」 둘(정정 이력), 7B 산술 등급 이름 셋(「binary64 바깥 부풀림 구간 산술; 정확 유리수」·「정확 유리수」×2), 6장 small-k-bulk 「계산 증거(정리 5.1의 인증 자료)」, 8장 보조정리 명시 경계 「표준(Robbins, Euler–Maclaurin)」(세션이 「표준」으로), 번호 중복(라벨 중복의 귀결), 부록 B 부재(아직 생성 전). "
    "검사기 거짓 양성 셋: 「사슬 밖의 꼭짓점」(수학적 쓰임) 3건, 「다른 결과로 닫히지 않는」(7.81·9장 실질 잔여 정의) 2건, 「…에 의존」 절을 낯선 낱말로 세는 참고 목록 — 검사기를 좁힌다."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "5A 회수와 2차 대조 파견" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
# 현재 상태의 배경 파견 줄: 5A 집필 → 5A 2차 대조
s = s.replace("배경 파견(23:1x): 5A 집필(a25a6ba133fe1200a), ", "배경 파견(23:2x): 5A 2차 대조(파견 23:2x), ")
s = s.replace("(집필 13조각 중 12 회수; 1·2·3·4·8·10장 완료, 9장 수정 중, 6·5B·7B·7A 2차 대조 중, 5A 집필 중)", "(집필 13조각 전부 회수; 1·2·3·4·8·10장 완료, 9장 수정 중, 6·5B·7B·7A·5A 2차 대조 중)")
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md (5A 회수)")
