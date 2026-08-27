# 예외 기록: 행 2.6.z

## 접수

- 반환 첫 줄은 `예외`이고 공통 반환어휘 안이다.
- 반환 둘째 줄은 `코드: 싱크비완결`이다.
- 싱크의 상세 판정은 결산 frontmatter를 따른다.

## 실측

```증거 결산과 실행 상태
명령: Get-Content z-결산.md; git worktree list --porcelain; git status --porcelain -uall; git diff --cached --name-only; git ls-files --unmerged; python dag_marker.py lease --status
시각: 2026-08-25T04:48:29Z
결과: 결산은 상태 완료미충족·단계 판정완료다. 브랜치 dag/pvsnp-탐사-1/2.6의 worktree는 보존되어 있다. worktree HEAD와 main HEAD는 950170e0a383ce19f445270606a7d886951b8e4f로 같다. worktree의 미추적 파일은 귀속된 7건이다. 메인 인덱스와 unmerged 항목은 비어 있다. 병합 lease도 비어 있다.
문맥: 격리 커밋·squash 병합·메인 커밋·worktree 회수는 아직 실행되지 않았다.
```

```증거 SAT-MINI 정합
명령: ConvertFrom-Json sat-solvers.txt; rg SAT-MINI|candidate_status 두 기준선; python toolchain_smoke.py --json의 선택 필드 판독
시각: 2026-08-25T04:48:29Z~2026-08-25T04:50Z
결과: 저장된 로그는 winget path lookup 0, probe 127, MiniSat package query 0건, MiniSat FAIL, SAT·UNSAT exit code 127, candidate_status PASS다. 두 기준선은 MiniSat PASS·버전 2.2·SAT 10·UNSAT 20을 적는다. 런 기준선은 candidate_status FAIL을, 저장소 기준선과 저장된 로그는 PASS를 적는다. 현재 읽기 전용 재측정은 winget probe 0, package query 1건, MiniSat PASS, SAT 10, UNSAT 20, candidate_status PASS를 냈다.
문맥: 저장된 라이브 로그와 두 기준선의 광고가 어긋난다. 현재 재측정 성공만으로 실행 별칭 실패의 재발 조건은 닫히지 않는다.
```

## 판정

결산의 `상태: 완료미충족`은 실물과 맞는다. 행 `2.6.z`의 완료 기준 가운데 SAT-MINI 광고·라이브 로그·두 기준선의 일치가 충족되지 않았다. 결산은 첫 비가역 행위 전에 멈췄고, 같은 worktree에서 수리할 수 있다.

## 처분

**미착수** — 수리 행 `2.6.10`을 먼저 실행한 뒤 행 `2.6.z`를 다시 실행한다.

- 파견표에 행 `2.6.10`을 추가했다.
- 행 `2.6.z`의 선행에 `2.6.10`을 추가하고 상태를 `미착수`로 바꿨다.
- 행 `2.6.z` 파견문에 `2.6.10` 보고 좌표와 수리 후 대조 절차를 추가했다.
- worktree와 브랜치는 보존했다.

## 추가한 행

| 행 | 유형 | 임무 | 완료 신호 |
|---|---|---|---|
| `2.6.10` | 작업자 | Windows 앱 실행 별칭 실패 재발 방지, SAT-MINI 로그와 두 기준선 정합 수리 | `C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\10-보고.md` |

## 반증 의무

반환의 핵심 지적은 실물과 일치한다. 다만 현재 읽기 전용 재측정에서는 `winget`과 MiniSat이 통과했다. 따라서 수리 행은 로그 재생성만 하지 않고 실행 별칭 실패 조건을 회귀 테스트로 고정한다.
