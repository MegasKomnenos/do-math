---
유형: 결산
행: 2.6.z
상태: DONE
단계: 종결
---

## 판정 (병합 앞)

### 검증런·렌즈 행 종료 확인

파견표 `C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md`에서 행 번호가 `2.6`으로 시작하는 행은 50건이다. 그중 49건의 상태 열이 `완`이고, `진행`은 이 행 `2.6.z` 하나뿐이다. 검산 명령 `python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md`는 `[dag_check] 무발견 (drive: 서식·어휘·칸 계약·폐쇄·수렴·순환·좌표 실재·게이트 결정·운전)`과 exit code 0을 냈다.

worktree 좌표는 전사받지 않고 메인 체크아웃에서 재도출했다. `git worktree list --porcelain`은 브랜치 `dag/pvsnp-탐사-1/2.6`에 경로 `C:/Users/wogud/AppData/Local/dag-wt/pvsnp-탐사-1+2.6`을 붙였고, 그 값이 파견문 「작업 디렉토리」 슬롯과 같다. 그 worktree에서 `git rev-parse --show-toplevel`은 같은 경로를 냈다.

### 재개 판정 — 행 `2.6.10` 수리의 실물 대조

이 결산의 앞선 판정은 `상태: 완료미충족`이었다. 그 판정은 저장소 도구 기준선 `research/pvsnp/environment/toolchain-baseline.md`의 SAT-MINI 광고가 라이브 로그 `experiments/pvsnp/smoke/evidence/sat-solvers.txt`의 실제 값과 어긋난 것을 근거로 삼았다. 그 뒤 행 `2.6.10`이 같은 worktree에서 수리했으므로, 앞선 판정을 병합 허가로 쓰지 않고 세 조건을 실물로 다시 열었다.

**조건 1 — 행 `2.6.10` 보고의 편집 귀속과 실제 diff가 일치한다.** `10-보고.md` 「편집 귀속」 표는 8행이다. 그중 worktree 안 파일이 6건, 런 디렉토리 파일이 2건(`C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md`와 `C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\6.d\10-보고.md`)이다. worktree 변경 집합과 대조한 결과는 아래 「귀속 대조」다. 런 디렉토리 두 파일은 저장소 추적 밖이고 worktree 밖이므로 worktree diff에 나타나지 않는다. 두 파일의 내용은 아래 조건 3이 직접 열어 확인했다.

**조건 2 — `sat-solvers.txt`의 SAT-MINI 상태와 두 exit code.** 파일을 직접 열어 읽은 값이다.

| 좌표 | 값 |
|---|---|
| `candidate_status` | `PASS` |
| `solvers.minisat.status` | `PASS` |
| `solvers.minisat.available` | `true` |
| `solvers.minisat.executable` | `%LOCALAPPDATA%\Microsoft\WinGet\Packages\PolarGoose.minisat_Microsoft.Winget.Source_8wekyb3d8bbwe\minisat.exe` |
| `solvers.minisat.package_queries[0].exit_code` · `stdout` | `0` · `minisat PolarGoose.minisat 2.2` |
| `solvers.minisat.sat.exit_code` | `10` |
| `solvers.minisat.unsat.exit_code` | `20` |
| `runtime.local_package_managers.winget.path_lookup.exit_code` | `1` |
| `runtime.local_package_managers.winget.probe.exit_code` · `stdout` | `0` · `v1.29.280` |
| `runtime.local_package_managers.winget.discovery` | `windowsapps_alias` |
| `candidate_discovery.packages` 건수 · `unresolved_candidates` 건수 | `80` · `79` |
| `installation_targets` | `["minisat"]` |
| `solvers` 전건의 상태 | `minisat` `PASS` · `cadical` `FAIL` · `kissat` `FAIL` · `cryptominisat` `PASS` |

앞선 판정이 잡은 어긋남 9건은 모두 사라졌다. 라이브 로그가 SAT-MINI를 `PASS`로 적고, 버전 근거 `2.2`가 `package_queries[0].stdout`에 실재하며, SAT·UNSAT exit code가 10·20이다.

**조건 3 — 저장소 기준선과 런 기준선이 같은 로그 값과 `candidate_status` 정의를 쓴다.** 두 파일을 직접 열어 대조했다.

| 대조 항목 | 저장소 기준선 `research/pvsnp/environment/toolchain-baseline.md` | 런 기준선 `C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md` 8.3절 |
|---|---|---|
| SAT-MINI 상태 | `PASS` | `PASS` |
| SAT-MINI 버전과 그 근거 | `2.2`, 근거는 `solvers.minisat.package_queries[0].stdout` | `2.2`, 근거는 같은 좌표 |
| SAT-MINI 호출 표면 | `minisat.exe <DIMACS 파일>`. PATH에 없으면 `solvers.minisat.executable`이 적은 WinGet 패키지 절대 경로 | 같은 WinGet 패키지 절대 경로 |
| SAT-MINI 스모크 결과 | 단위 절 SAT exit code 10, 모순 단위 절 UNSAT exit code 20 | SAT exit code 10, UNSAT exit code 20 |
| `candidate_status` 값 | `PASS` | `PASS` |
| `candidate_status` 정의 | 필수 후보 넷(`minisat`·`cadical`·`kissat`·`cryptominisat`) 전건의 측정 행이 `measurement_status: MEASURED`일 때 `PASS`. `unresolved_candidates`는 입력이 아니다 | 같은 정의를 같은 낱말로 적는다 |
| `winget` 실행 경로 서술 | `where.exe`는 `winget`·`choco`·`scoop` 전건에 exit code 1을 반환했고, PATH 밖 WindowsApps 별칭 probe가 exit code 0과 `v1.29.280`을 반환했다 | 8.3절은 이 서술을 담지 않고 도구별 판정만 담는다. 두 문서가 어긋나는 진술은 없다 |
| 광범위 검색 계수 | 패키지 80건 중 1건 해소, 79건 미해소 | 같은 80건·79건 |

세 조건이 모두 통과하므로 병합으로 잇는다.

### 귀속 대조

```실측기 attrib
명령: python dag_measure.py attrib --worktree C:/Users/wogud/AppData/Local/dag-wt/pvsnp-탐사-1+2.6 --attributed research/pvsnp/environment/toolchain-baseline.md,experiments/pvsnp/smoke/toolchain_smoke.py,experiments/pvsnp/smoke/test_toolchain_smoke.py,experiments/pvsnp/smoke/evidence/python-packages.txt,experiments/pvsnp/smoke/evidence/smt-z3.txt,experiments/pvsnp/smoke/evidence/sat-solvers.txt,experiments/pvsnp/smoke/evidence/environment-changes.json --allow-untracked
시각: 2026-08-25T05:11:00Z
대상해시: sha1:------------
변경 0 / 귀속 7
미귀속 편집: 0
귀속됐으나 무변경: 7
  experiments/pvsnp/smoke/evidence/environment-changes.json
  experiments/pvsnp/smoke/evidence/python-packages.txt
  experiments/pvsnp/smoke/evidence/sat-solvers.txt
  experiments/pvsnp/smoke/evidence/smt-z3.txt
  experiments/pvsnp/smoke/test_toolchain_smoke.py
  experiments/pvsnp/smoke/toolchain_smoke.py
  research/pvsnp/environment/toolchain-baseline.md
판정: 전건 귀속
[/실측기]
```

실측기 `attrib`은 `git status --porcelain`을 `-uall` 없이 돌리므로, 추적 파일이 하나도 없는 새 디렉토리를 디렉토리 한 줄로 접는다. 접힘을 편 실측은 아래다.

```
명령: git -C C:/Users/wogud/AppData/Local/dag-wt/pvsnp-탐사-1+2.6 status --porcelain -uall
?? experiments/pvsnp/smoke/evidence/environment-changes.json
?? experiments/pvsnp/smoke/evidence/python-packages.txt
?? experiments/pvsnp/smoke/evidence/sat-solvers.txt
?? experiments/pvsnp/smoke/evidence/smt-z3.txt
?? experiments/pvsnp/smoke/test_toolchain_smoke.py
?? experiments/pvsnp/smoke/toolchain_smoke.py
?? research/pvsnp/environment/toolchain-baseline.md
```

편 결과의 파일 7건은 위 `--attributed` 목록 7건과 같다. 귀속 출처는 `2-보고.md` 「편집 귀속」, `6-보고.md` 「편집 귀속」, `9.d/2-보고.md`와 `9.d/5.d/2-보고.md`의 `environment-changes.json` 행, `10-보고.md` 「편집 귀속」의 6건, 검증런 `3.d/종료보고.md`·`7.d/종료보고.md`의 「앵커 대조 변경 자리」다. `experiments/pvsnp/smoke/__pycache__/`는 저장소 `.gitignore` 2행 `__pycache__/`가 막아 변경 집합에 들지 않는다.

**미귀속 편집 0건이다.** 귀속 대조는 통과한다.

### 노드 완료 기준의 전건 판정

| 기준 | 판정 | 증거 좌표 |
|---|---|---|
| 자식 완료 신호 전건이 실재한다 | 충족 | 파견표 「완료 신호」 열이 지명한 `2.6*` 행 49건의 좌표 41건 전건이 실재한다. 부재 0건 |
| P5′ 승인 목록 밖 설치 0건 | 충족 | `environment-changes.json`의 설치 사건 대상은 `python-sat`·`sympy`·`z3-solver`·`ortools`·`z3`·`cryptominisat`·`minisat`뿐이다. 저장소 기준선 2절 표가 같은 목록을 싣는다 |
| 형식 증명 도구 설치 0건 | 충족 | worktree의 `experiments/`·`research/` 전건에서 `lean 4`·`coq`·`rocq`·`isabelle` 검색 히트 0건 |
| WSL·컨테이너·새 패키지 관리자·소스 빌드 사용 0건 | 충족 | 같은 범위의 `wsl`·`docker`·`podman`·`chocolatey`·`apt-get`·`cmake` 검색 히트는 셋 다 타자 문자열이다. `toolchain_smoke.py` 183행의 출력 파싱 접두어 `Chocolatey`, 저장소 기준선 96행의 이 기준 자체를 적은 한 줄, `sat-solvers.txt`가 데이터로 실은 `winget` 광범위 검색 결과의 패키지 이름(`Docker` 7회·`CMAKE` 6회)이다. 설치·실행 명령은 0건이다 |
| 크리덴셜 값·개인 식별 정보 출현 0건 | 충족 | `kudos`·`knu.ac.kr`·`password` 검색 0건. 사용자 이름 `wogud` 히트는 `.gitignore`가 막는 `__pycache__` 바이너리 2건뿐이고 변경 집합 밖이다. 경로는 `%LOCALAPPDATA%`·`%TEMP%`로 정규화되어 있다 |
| 유한 스모크 결과의 복잡도 계급 주장 0건 | 충족 | 저장소 기준선 1절이 「유한 스모크는 도구 호출 가능성만 보여 준다」로 한정한다. 복잡도 계급 도출 문장 0건 |
| Markdown 연구 문서·보고의 한국어 산문·LaTeX 수식 형식 | 충족 | 저장소 기준선 전건이 한국어 산문이고 수식은 $x$와 $x \land \neg x$로 표기한다 |
| 귀속 대조 통과 | 충족 | 위 「귀속 대조」 |
| 최종 기준선과 S1 광고의 도구별 필드 일치 | 충족 | 위 「재개 판정」 조건 2·3 |
| 두 기준선 동치 | 충족 | 위 「재개 판정」 조건 3 |

저장된 증거 로그가 판정표를 뒷받침한다. `python-packages.txt`는 `python-sat 1.9.dev15`·`sympy 1.14.0`·`z3-solver 5.1.0.0`·`ortools 9.15.6755`을 모두 `PASS`로 적었고, `smt-z3.txt`는 `Z3 version 5.1.0 - 64 bit`와 `PASS`를 적었다. 구조 검증 명령 `python experiments/pvsnp/smoke/test_toolchain_smoke.py`는 `Ran 20 tests`·`OK`·exit code 0을 냈고, 실행 뒤에도 worktree 변경 집합은 위 7건 그대로다. 그 명령은 임시 디렉토리에만 쓰므로 증거 로그를 바꾸지 않는다.

## 병합·회수

| 행위 | 명령 | 결과 |
|---|---|---|
| worktree 커밋 | `git -C C:/Users/wogud/AppData/Local/dag-wt/pvsnp-탐사-1+2.6 add -A && git … commit -m "2.6 작업"` | 커밋 `cde1276ac0bd633aec7074b4caa710faa46410e5`. 커밋 뒤 `git status --porcelain -uall`은 비었다 |
| `병합lease` 획득 | `python C:\math\.claude\skills\do-dag\scripts\dag_marker.py lease --acquire --owner 2.6.z --minutes 30` | exit code 0. 만료 `2026-08-25T05:42:21Z` |
| 메인 인덱스 실측 | `git diff --cached --name-only` · `git ls-files --unmerged` | 둘 다 빈 출력. 병합 자리가 비어 있다 |
| 커밋 grant 취득 | `python …\dag_marker.py allow --minutes 30 --reason "2.6 병합"` | `grant-1` 발급, 만료 `2026-08-25T05:42:28Z` |
| squash 병합 | `git merge --squash dag/pvsnp-탐사-1/2.6` | exit code 0. Fast-forward squash로 파일 7건 3,681줄이 스테이징에 섰다. 충돌 0건 |
| 메인 커밋 | `git commit -m "반례 실험 도구 기준선과 스모크 측정기를 병합한다"` | 커밋 `9586710821f61e12eb0b5f2b1df09875d66b7c9a`. 파일 12건 4,088줄 |
| 트리 처분 | `git worktree remove C:/Users/wogud/AppData/Local/dag-wt/pvsnp-탐사-1+2.6 --force` | exit code 0. `--force`는 `.gitignore`가 막는 `__pycache__` 잔재 때문에 붙였다. 추적 내용은 이미 커밋됐다 |
| 브랜치 처분 | `git branch -D dag/pvsnp-탐사-1/2.6` | 삭제됨(`was cde1276`) |
| grant 해제 | `python …\dag_marker.py clear-token --grant grant-1` | 아래 실행 |
| `병합lease` 반납 | `python …\dag_marker.py lease --release --owner 2.6.z` | 아래 실행 |

grant와 lease는 만료되지 않았다. 만료로 다시 돌린 판정은 없다.

**메인 커밋의 스테이징 반경.** 병합 인덱스 7건, 이 커밋의 layer-1 메모리 노드 `기억/layer1/M-0004.md`, 색인 `기억/색인.md` 한 줄, 편입 집합 3건이다. 착수 시 `git ls-files .sdd/`가 낸 추적 집합은 0건이므로 편입 집합 3건을 `git add -f`로 편입했다.

편입 집합의 판별 술어는 「이 커밋만 놓고 볼 때 그 파일이 없으면 이 커밋의 변경이 왜 그렇게 됐는지 설명되지 않는 결정·규율 산출」이다. 셋이 그 술어를 만족한다.

- `.sdd/dag/pvsnp-탐사-1/결정/1-프레임체급.md` — 「결정」 절 P5′가 설치할 도구 일습과 설치 금지 범위(Lean 4·Coq/Rocq·Isabelle/HOL)를 정한다. 이 커밋이 담은 기준선이 왜 그 9건만 판정하는지를 이 파일이 설명한다.
- `.sdd/dag/pvsnp-탐사-1/결정/2.6-도구기준선.md` — 이 기준선 문서를 승인한 내용 게이트 결정이다.
- `.sdd/dag/pvsnp-탐사-1/결정/상신-2.6.7-1.md` — `candidate_status`의 판정 계산을 「필수 SAT 후보 명세 전건의 측정 완료」 기준으로 재정의한 결정이다. 이 커밋의 `toolchain_smoke.py`와 기준선 5절이 그 재정의를 구현한다.

멈춤 조건에 걸린 `.sdd/` 경로는 없다. 커밋 직전 `git diff --cached --name-only`가 낸 12건은 위 반경과 정확히 같다.

**색인 파일의 부분 스테이징.** `기억/색인.md`의 작업 트리 사본에는 이 노드 밖 작업 단위가 남긴 `M-0003` 줄이 이미 들어 있었다. `M-0003.md`는 저장소 추적 밖이고 그 작업 단위(`.claude/skills/` 계열 변경)는 이 커밋의 반경이 아니다. 색인 전체를 그대로 스테이징하면 노드 파일 없는 색인 줄이 저장소에 선다. 그래서 스테이징에는 `M-0003` 줄을 뺀 사본을 올리고, 작업 트리 파일은 그 줄을 담은 원래 내용으로 되돌렸다. 커밋된 트리의 색인 줄 3건(`M-0001`·`M-0002`·`M-0004`)은 커밋된 노드 파일 3건과 일대일로 대응한다. `python 기억/scripts/validate_memory_index.py`는 `정합: 파일 13개 = 색인 13 + 아카이브 0줄`과 exit code 0을 냈다.

## 이음새 전기

| ID | 전이 | 증거 좌표 |
|---|---|---|
| S1 | `미착수` → `노출됨` | 저장소 도구 기준선 `research/pvsnp/environment/toolchain-baseline.md` 3~5절이 도구 9건(PY-PYSAT·PY-SYMPY·PY-Z3·PY-ORTOOLS·SMT-Z3·SAT-MINI·SAT-CADI·SAT-KISS·SAT-CMS)마다 이름·상태 `PASS｜FAIL`·버전·호출 표면·스모크 결과·대체 수단·갱신 트리거를 적는다. 런 기준선 `C:\math\.sdd\dag\pvsnp-탐사-1\기준선.md` 8.3절이 같은 9건을 같은 값으로 요약한다. 원시 로그는 `experiments/pvsnp/smoke/evidence/`의 `python-packages.txt`·`smt-z3.txt`·`sat-solvers.txt`·`environment-changes.json`이다. 재현 명령은 `python experiments/pvsnp/smoke/toolchain_smoke.py --evidence-dir experiments/pvsnp/smoke/evidence`다. 커밋은 `9586710821f61e12eb0b5f2b1df09875d66b7c9a`다 |

S1 명세의 실패 처분도 만족한다. `FAIL` 도구 둘에 대체 수단이 붙어 있다 — SAT-CADI는 PySAT의 CaDiCaL 바인딩, SAT-KISS는 CryptoMiniSat 실행 파일이다. 대체 수단이 없는 `FAIL` 도구는 0건이므로 실험을 `FAIL`로 닫아야 하는 항목도 0건이다.

계약 이동은 없다. 이 노드는 아직 파견되지 않은 노드의 계약을 움직이지 않았다.

## 경미 처분

산출물에서 유보 표지를 검색한 결과다. 명령은 `grep -rnE "\[미검증|\[미확인|미결|유보|열림" research/pvsnp/ experiments/pvsnp/`이고 히트는 2건이다. 둘 다 `research/pvsnp/environment/toolchain-baseline.md`의 49행과 59행이고, 같은 사안 하나를 가리킨다.

| 항목 | 처분 | 소유자 또는 근거 |
|---|---|---|
| `winget` 광범위 검색이 찾은 패키지 79건을 SAT 풀이기 여부로 분류하지 않았다. 그 안에 판정표에 더할 SAT 솔버 후보가 있는지 미결이다 (기준선 49·59행) | 이월 | 소유자는 행 `2.11`이다. 해소 행은 원자료 `experiments/pvsnp/smoke/evidence/sat-solvers.txt`의 `candidate_discovery.unresolved_candidates`를 열고 기준선 5절 판정표를 수정할 권한을 함께 받는다. 이월하는 이유는 결정 `상신-2.6.7-1.md`가 미해소 목록을 `candidate_status` 판정 입력에서 빼고 데이터로만 보존하기로 정했기 때문이다 — 그 79건의 분류는 이 노드의 완료 조건이 아니다 |
| OR-Tools가 설치한 `protobuf 6.33.6`이 기존 `kfp`·`kfp-kubernetes`·`kfp-pipeline-spec`의 `protobuf<5` 제약과 충돌해 `python -m pip check`가 exit code 1이다 | 이월 | 소유자는 행 `2.11`과 `2.12`다. 근거는 `2-보고.md` 「잔여·처분」, `10-보고.md` 「이월 사슬」, 기준선 2절 마지막 문단이다. 승인 패키지 4종의 최소 스모크는 모두 통과하므로 이 노드의 완료를 막지 않는다. 해소 행은 별도 Python 환경 분리를 검토한다 |
| SAT-CADI의 대체 수단인 PySAT CaDiCaL 바인딩을 아직 호출한 적이 없다 | 이월 | 소유자는 행 `2.11`이다. 근거는 기준선 5절 마지막 문단이 사용 전 독립 스모크를 요구하는 것이다. 해소 행은 최소 SAT·UNSAT 스모크로 그 바인딩을 판정한 뒤에 실험에 쓴다 |

검증런 종료보고의 무처분·기각 잔여는 0건이다. 기각한 잔여도 0건이다.

## 잔여·처분

미충족 항 없음. 노드 완료 기준 10항 전건이 충족이다.

계약 이동 없음. 되돌린 병합 없음. 병합 충돌 0건.

앞선 판정의 미충족 항 넷은 행 `2.6.10`이 닫았다. 넷 중 셋(`sat-solvers.txt`의 SAT 후보 탐색이 `winget` 실행 실패로 빈 값이 되는 문제, 저장소 기준선의 SAT-MINI 광고, 런 기준선 8.3절의 `candidate_status` 정의)은 위 「재개 판정」이 실물로 확인했다. 넷째(산문을 고친 뒤 로그를 다시 뜨는 순서의 금지)는 `10-보고.md` 증거 부록 4가 로그를 먼저 한 번 뜨고 그 뒤 증거 로그를 다시 쓰지 않았음을 적고, 파일 수정 시각이 그 순서와 맞는다.

## 반증 의무

파견문·입력과 어긋난 지점 하나를 발견해 기재한다.

행 `2.6.10`의 `10-보고.md` 「편집 귀속」 표는 8행이고, 그중 2행이 「무엇을 바꿨는가」 열에 「최종 라이브 로그를 쓰였다」·「최종 SAT 로그를 쓰였다」처럼 어법이 어긋난 문면을 담는다(`쓰였다`는 피동형이고 능동 서술이 와야 할 자리다). 이 어긋남은 그 표가 지명한 파일 목록과 실제 diff의 대조를 방해하지 않는다 — 파일 좌표와 귀속 대상은 명확하다. 귀속 대조 판정은 그대로 통과다.

앞선 판정에 담았던 반증 의무 기재는 그 내용이 해소되어 여기서 반복하지 않는다. 자식 보고의 「충족」 기재와 이 결산의 판정은 이제 어긋나지 않는다.
