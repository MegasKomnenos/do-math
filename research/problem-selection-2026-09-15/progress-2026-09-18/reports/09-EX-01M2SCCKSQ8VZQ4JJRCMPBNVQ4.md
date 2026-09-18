## 수행 범위
과제 TK-01M2SBJK5NPH3NVAJXRQ3ZH4BC(revision 1)가 요구한 범위를 모두 수행했다. 검증된 정의 위에서 A 0 ℓ = 1과 모든 n, ℓ에 대한 누적 점화식을 Lean 4 코어로 증명했다.

## 읽은 입력과 재사용
- KN-01M2SA578QCVM7AACS831J3HYE(verified, usable_as_k=true): Lean 원문 전체를 추출해(work/Base.lean) 수정 없이 제출 원문 앞부분에 넣었다. 앞부분이 원 lean_code와 바이트 단위로 같음은 스크립트로 확인했다. 정의 A·PF·park·firstFree와 정리 firstFree_eq_some·firstFree_eq_none·mem_lists를 증명에 직접 사용했다.
- S2 정리 3.7의 식과 논증: source:선행연구와-시작-자료.md §2와 source:fullread-core.md를 읽었다. 형식 증명은 그 마지막 차 논증을 따른다. 원 PDF(source:interval-rational-parking-2024.pdf)는 다시 판독하지 않았고, 식 대조는 위 독해 기록에 기댔다.
- KN-01M2SAA8DM1HJ3EPNDB8M60MT5(candidate): 자연어 논증을 안내받는 데만 읽었고, 형식 결과의 의존성에는 넣지 않았다.

## 산출
- work/ParkingRecurrence.lean: 제출한 전체 원문(LF 줄끝)이다. 기존 원문 뒤에 보조 정의(choose, sumTo, lsum, cnt, words, runB, Rel, splitB)와 정리를 덧붙였고, 선언은 모두 111개다.
- 주 정리:
  - A_empty: A 0 ℓ = 1
  - A_rec: A (n+1) ℓ = sumTo (fun j => choose n j * min (j+1) (ℓ+1) * A j ℓ * A (n-j) ℓ) (n+1)
- 핵심 보조정리:
  - split_iff: 빈자리 j+1에서의 분할 동치
  - last_car
  - unique_missing: 비둘기집 원리
  - cnt_interleave: Σ C(k,i)·…
  - pascal_sum
  - cnt_splitB: C(n,j)·A_{j,ℓ}·A_{n−j,ℓ}
  - cnt_last: min(j+1,ℓ+1)
- 보존한 파일: 단계별 원문 work/S1.lean, work/S2a.lean, work/S2b.lean, 설계 work/PLAN.md, 선언 목록 work/declaration_names.json, 사전 검사 결과 work/preview-result.json.

## 사전 검사(preview) 실제 결과
python -B input/tools/check_lean.py --source work/ParkingRecurrence.lean을 111개 선언 전건(--declaration 반복)으로 실행했다.
- status=verified
- source_sha256=c43c7671e5a34cacd785684a6b893f54b6c7ff9a4edd8d8ae8601062cf1e476b
- toolchain: Lean (version 4.32.0, x86_64-w64-windows-gnu, commit 8c9756b28d64dab099da31a4c09229a9e6a2ef35, Release), 실행 파일 sha256 10c6a275…
- 공리: 모든 선언이 {propext, Classical.choice, Quot.sound} 안에 있다.
- 원문에 sorry, axiom, native_decide가 없다. lean.exe 직접 실행에서도 오류와 경고가 없었다.

검사 과정에서 두 번 다시 실행했다.
1. 첫 실행은 도구가 선언명 sumTo_succ'의 작은따옴표를 허용하지 않아 "invalid declaration"으로 거부됐다. 이름을 sumTo_shift로 바꾼 뒤 통과했다.
2. 이어 작업 파일이 CRLF 줄끝으로 저장된 것을 확인했다(당시 sha256 c939288b…). 제출 문자열과 같은 LF 바이트로 파일을 다시 쓰고 재검사해 위 결과를 얻었다.

이 preview는 비권위 검사이며, 권위 있는 판정은 중앙 형식 검사가 한다.

## 완료 기준 대조
1. 충족: 기존 정의를 그대로 포함한 완전한 원문과 declaration_names를 제출했다. A 0 ℓ = 1(A_empty)과 누적 점화식(A_rec)을 모든 n, ℓ에 대한 정리로 진술하고 증명했다.
2. 판정 대기: 중앙 형식 검사 통과 여부는 제출 뒤 실행기가 판정한다. preview 기준으로는 통과했다.
3. 충족: preview 결과를 위에 적었다.
4. 충족: 수학 해설 §2는 choose·sumTo 등 보조 개념을 설명한다. §3은 목표 문면의 Aₙ,ℓ와 S2 정리 3.7이 A_rec와 어떻게 대응하는지 대조한다. n↦n+1 이동, 합의 범위, n−j에 절삭이 없음, A₀,ℓ=1이 정리라는 점을 다룬다.
5. 해당 없음: 증명을 완결했다. 선택 항목인 b의 3항 분해는 수행하지 않았다.

## 한계
이 결과는 목표 P를 해결하지 않는다. 점화식을 직접 정의에 연결하는 기반 결과다. 동일성 검토와 K 편입은 별도 관문이다.