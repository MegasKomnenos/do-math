## 수행 범위
과제 TK-01M2S813V92Q77YY3S08KSWHNV(revision 2)의 계약 전문(input/catalog/task.json)을 읽었다. 목표 정의는 context:goal과 source:문제와-선정-근거.md 9·18·31·35행에서, 기대 행 값은 source:published-counts.json에서 확인했다. 재사용할 K는 없다. 지식 목록의 기존 기록은 모두 candidate이며 이 과제의 정의에는 쓰지 않았다.

## 사전 검사(비권위)와 환경
- 도구: input/tools/check_lean.py(preview). 관찰한 toolchain은 `Lean (version 4.32.0, x86_64-w64-windows-gnu, commit 8c9756b28d64dab099da31a4c09229a9e6a2ef35, Release)`이다. 실행파일 sha256은 10c6a27583eb65ff6a7e92b9718ff01d851ad594e6d70bb283fa5a10092fd810이다. 구성 명령은 lean.exe 직접 호출이고 Lake 프로젝트는 없다.
- Mathlib은 사용할 수 없다. `import Mathlib.Data.Nat.Basic` 탐침이 "unknown module prefix 'Mathlib'"로 거부됐다. 따라서 Lean 코어만 사용했다.
- 최종 원문 work/ParkingDefs.lean(sha256 0efea0935f4ed744fdb2358cca7126525faea16b8e67146139a3bd984899bf19)의 43개 선언 전부에 사전 검사를 실행했다. 결과는 status=verified이고, 관찰한 공리 의존의 합집합은 {propext, Classical.choice, Quot.sound}다. 원 결과는 work/lean-preview-result.json에 있다. 이 사전 검사는 권위가 없다. 완료 기준 4는 중앙 형식 검사 기록으로만 판정된다.

## 결과
- 완료 기준 1: 정의 `lists, prefLists, firstFree, parkFrom, park, IsParkingFunction, PF, listMax, displacements, maxDisp, A, b, RowUnimodal, GoalP`를 제출했다. b는 M=ℓ인 개수로 직접 정의했다.
- 완료 기준 2: `A_zero`, `A_succ`(모든 n, ℓ, 덧셈 꼴)와 일반 보조정리 `count_le_zero`, `count_le_succ`를 목록 귀납으로 증명했다.
- 완료 기준 3: `bRow_one`–`bRow_four`와 `rowUnimodal_one`–`rowUnimodal_four`를 증명했다. **n=5도 성공했다.** `bRow_five`=[120,421,377,253,125]와 `rowUnimodal_five`(c=1)를 증명했고, `goalP_upto_five`가 n=1..5를 묶는다. 커널 decide(`decide +kernel`)만 사용했고 native_decide는 쓰지 않았다. 원문 전체의 로컬 컴파일은 약 10초 걸렸다.
- 완료 기준 5: 새 지식의 explanation §2에 대응을 적었다. 주차 규칙, 1..n 값을 그대로 쓴 점(Fin 표현 미사용), 변위의 비절삭(parkFrom_spec), max, b의 직접 정의를 다룬다. A_zero가 Aₙ,₋₁=0 규약을 나타낸다는 점, A₀,ℓ 미사용, c<n·k+1<n·n≥1 양화의 대응도 적었다. 계약 검토의 권고에 따라 열거의 완전성과 중복 없음을 정리로 증명했다(mem_prefLists, nodup_prefLists, nodup_PF). 다만 "filter 길이 = 집합 크기"는 Finset이 없어 형식 명제로 쓰지 않았고 해설의 표준 사실로 두었다.
- 완료 기준 6: 위 사전 검사 절을 보라.

## 추가 확인(재현 자료)
- work/lean-eval-rows.txt: 같은 정의로 `#eval`한 n=0..6의 b 행과 |PFₙ|이다. |PFₙ|은 1,1,3,16,125,1296,16807=(n+1)^{n−1}이다. n=6 행 [720,3963,4594,3688,2546,1296]도 공개 수치와 같다.
- work/independent_check.py와 work/independent-check-output.txt: 문면 정의(1-색인)를 그대로 구현한, Lean과 독립인 Python 전수 계산이다. n=1..6 행이 published-counts.json과 일치하며 종료 코드는 0이다.
- 이 계산들은 n≤6의 확인이며, 모든 n에 대한 P의 증거가 아니다.

## 남은 차이
P의 모든 n에 대한 증명은 이 과제 범위 밖이며 수행하지 않았다. 과제 완료 여부는 중앙 형식 검사 결과를 보고 연구 계획이 판정한다. 정의 대응의 동일성 검토는 그 뒤의 후속 절차다.
