# 반례 실험 도구 기준선

## 1. 판정 범위와 기준

이 문서는 2026년 8월 25일 Windows x64와 CPython 3.11.9 환경을 판정한다. 이 절이 정의하는 `PASS`와 `FAIL`은 3절부터 5절까지 판정표의 「상태」 열 값만 가리킨다. `PASS`는 최소 SAT·UNSAT 풀이가 모두 성공했다는 뜻이다. `FAIL`은 실행 파일을 확보하지 못했거나 최소 풀이가 실패했다는 뜻이다. `sat-solvers.txt`의 `candidate_status`는 도구 하나의 상태가 아니라 필수 SAT 후보 집합의 측정 완전성 판정이고, 그 `PASS|FAIL`의 뜻은 5절이 따로 정의한다. 버전 조회 결과는 판정표의 버전 열에만 기록하고 「상태」 열의 `PASS|FAIL` 판정에는 넣지 않는다. 유한 스모크는 도구 호출 가능성만 보여 준다.

Python 실행 파일은 `%LOCALAPPDATA%\Programs\Python\Python311\python.exe`다. `pip 24.0`은 이 Python 3.11 환경에 연결되어 있다. `where.exe`는 `winget`, `choco`, `scoop` 전건에 exit code 1을 반환했다. PATH 밖 `%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe --version`은 exit code 0과 `v1.29.280`을 반환했다. 따라서 `winget`만 기존 로컬 패키지 관리자다. `choco`와 `scoop`은 실행 가능한 경로가 없다. 새 패키지 관리자는 설치하지 않았다. `winget` probe가 실패하면 로그는 발견 경로, probe exit code, stderr를 보존하고 조회 결과 없음으로 축약하지 않는다.

## 2. 과거 환경 변경 사건

이 절은 라이브 측정이 아닌 과거 사건 기록이다. `experiments/pvsnp/smoke/evidence/environment-changes.json`은 사건별로 `evidence_type: recorded_event`와 근거 좌표를 갖는다. Python 설치 명령은 소스 배포를 거부하도록 `--only-binary=:all:`을 사용했다.

| 변경 ID | 명령 또는 공식 자산 | 대상 | exit code | 결과 |
|---|---|---|---:|---|
| I-PY | `python -m pip install --disable-pip-version-check --only-binary=:all: python-sat sympy z3-solver ortools` | `python-sat`, `sympy`, `z3-solver`, `ortools` | 0 | 네 배포를 설치하거나 설치 상태를 확인했다 |
| I-Z3 | [Z3 5.1.0 공식 Windows x64 ZIP](https://github.com/Z3Prover/z3/releases/download/z3-5.1.0/z3-5.1.0-x64-win.zip)을 `%LOCALAPPDATA%\pvsnp-toolchain\z3-5.1.0`에 압축 해제 | `z3` | 0 | `z3.exe`를 확보했다 |
| I-CMS | [CryptoMiniSat 5.14.7 공식 Windows x64 ZIP](https://github.com/msoos/cryptominisat/releases/download/release/v5.14.7/cryptominisat5-v5.14.7-windows-x86_64.zip)을 `%LOCALAPPDATA%\pvsnp-toolchain\cryptominisat-5.14.7`에 압축 해제 | `cryptominisat` | 0 | `cryptominisat5.exe`를 확보했다 |
| I-SAT-MINISAT | `%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe install --id PolarGoose.minisat --exact --source winget --accept-package-agreements --accept-source-agreements --disable-interactivity` | `minisat` | 2316632107 | 기존 설치를 확인했으나 업그레이드가 없어 설치 사건은 FAIL이다. 설치 뒤 재측정은 PASS다 |

`python -m pip check`는 exit code 1을 반환했다. OR-Tools가 설치한 `protobuf 6.33.6`은 기존 `kfp`, `kfp-kubernetes`, `kfp-pipeline-spec`의 `protobuf<5` 제약과 충돌한다. 네 승인 패키지의 최소 스모크는 모두 통과했지만, 이 Python 환경에서 기존 KFP 계열을 함께 쓸 때는 별도 환경이 필요하다.

## 3. Python 패키지 판정표

PySAT의 공식 PyPI 배포 이름은 `python-sat`이고 import 이름은 `pysat`이다. PyPI의 `pysat` 배포는 위성 자료 분석 도구이므로 이 작업의 승인 대상이 아니다. 공식 경로는 [PySAT `python-sat`](https://pypi.org/project/python-sat/), [SymPy](https://pypi.org/project/sympy/), [Z3 Python 바인딩](https://pypi.org/project/z3-solver/), [Google OR-Tools 설치 안내](https://developers.google.com/optimization/install/)다.

| 판정 ID | 공식 배포명 | 로컬 패키지 관리 경로·확보 가능성 | 호출 표면 | 설치 시도 | 버전 | 최소 스모크 결과 | 상태 | 대체 수단 | 갱신 트리거 |
|---|---|---|---|---|---|---|---|---|---|
| PY-PYSAT | PyPI `python-sat` | 기존 `pip 24.0`, 가능 | `pysat.solvers.Minisat22` | I-PY | 1.9.dev15 | 명령은 `python-packages.txt`의 `python_packages.python-sat.smoke.command`이다. `[1]`은 SAT이고 `[1],[-1]`은 UNSAT이며 exit code는 0이다. | PASS | 없음. 직접 호출이 가능하다. | 배포 버전이나 Python 3.11 환경이 바뀔 때 |
| PY-SYMPY | PyPI `sympy` | 기존 `pip 24.0`, 가능 | `sympy.logic.inference.satisfiable` | I-PY | 1.14.0 | 명령은 `python-packages.txt`의 `python_packages.sympy.smoke.command`이다. $x$는 SAT이고 $x \land \neg x$는 UNSAT이며 exit code는 0이다. | PASS | PySAT | 배포 버전이나 Python 3.11 환경이 바뀔 때 |
| PY-Z3 | PyPI `z3-solver` | 기존 `pip 24.0`, 가능 | `z3.Solver` | I-PY | 5.1.0.0 | 명령은 `python-packages.txt`의 `python_packages.z3-solver.smoke.command`이다. 불 변수 $x$는 SAT이고 모순식은 UNSAT이며 exit code는 0이다. | PASS | Z3 실행 파일 | 배포 버전이나 Python 3.11 환경이 바뀔 때 |
| PY-ORTOOLS | Google 안내가 연결한 PyPI `ortools` | 기존 `pip 24.0`, 가능 | `ortools.sat.python.cp_model.CpSolver` | I-PY | 9.15.6755 | 명령은 `python-packages.txt`의 `python_packages.ortools.smoke.command`이다. 단위 제약은 SAT이고 모순 제약은 UNSAT이며 exit code는 0이다. | PASS | PySAT | 배포 버전, Python 3.11 환경, `protobuf` 제약이 바뀔 때 |

원시 명령과 stdout·stderr·exit code는 `experiments/pvsnp/smoke/evidence/python-packages.txt`에 있다.

## 4. SMT 실행 파일 판정표

Z3 실행 파일의 공식 배포 경로는 [Z3 공식 릴리스](https://github.com/Z3Prover/z3/releases)다. Python 바인딩과 실행 파일을 별도 행으로 판정했다.

| 판정 ID | 공식 경로 | 로컬 확보 경로·확보 가능성 | 호출 표면 | 설치 시도 | 버전 | SAT·UNSAT 스모크 결과 | 상태 | 대체 수단 | 갱신 트리거 |
|---|---|---|---|---|---|---|---|---|---|
| SMT-Z3 | Z3 공식 Windows x64 ZIP | `%LOCALAPPDATA%\pvsnp-toolchain\z3-5.1.0\z3-5.1.0-x64-win\bin\z3.exe`, 가능 | `z3.exe <SMT-LIB 파일>` | I-Z3 | 5.1.0 64-bit | 명령은 `smt-z3.txt`의 `solver.sat.command`와 `solver.unsat.command`다. $x$는 `sat`이고 $x \land \neg x$는 `unsat`이며 두 exit code는 0이다. | PASS | `z3-solver`의 `z3.Solver` | Z3 릴리스, 운영체제, 아키텍처가 바뀔 때 |

원시 명령과 stdout·stderr·exit code는 `experiments/pvsnp/smoke/evidence/smt-z3.txt`에 있다.

## 5. SAT 실행 파일 판정표

공식 경로는 [MiniSat 저장소](https://github.com/niklasso/minisat), [CaDiCaL 릴리스](https://github.com/arminbiere/cadical/releases), [Kissat 릴리스](https://github.com/arminbiere/kissat/releases), [CryptoMiniSat 릴리스](https://github.com/msoos/cryptominisat/releases)다. `sat-solvers.txt`의 `candidate_specs`는 후보 ID와 후보 이름을 구별한다. 각 명세는 발견 출처, 패키지 조회 이름, 실행 파일 이름과 탐색 방법, 버전 명령, DIMACS 호출 방식, 대체 수단, 갱신 트리거를 갖는다. MiniSat 명세의 `winget_package_glob`은 `winget` probe·조회 성공 여부와 무관하게 `%LOCALAPPDATA%\Microsoft\WinGet\Packages`에서 기존 `minisat.exe`를 찾는다. 실행 파일 이름은 후보 ID와 다를 수 있다. `cryptominisat` 후보의 실행 파일 이름은 `cryptominisat5`다.

`candidate_discovery.searches`는 실행 가능한 로컬 패키지 관리자 전건의 명령·exit code·stdout·stderr·발견 출처를 기록한다. `candidate_discovery.packages`는 그 광범위 검색이 찾은 패키지 ID마다 패키지 관리자, 해소한 후보 ID, `resolution_status`, 발견 출처를 적는다. 후보 명세로 해소하지 못한 패키지 ID는 `candidate_id`가 `null`이고 `resolution_status`가 `unresolved`이며, 같은 항목이 `unresolved_candidates`에도 실린다. 실행 메타데이터가 없는 발견 후보가 미결로 남는 자리가 `unresolved_candidates`다.

`candidate_discovery.candidates`는 명세별 조회와 패키지 ID를 같은 후보 ID에 연결한다. 각 행의 `broad_discoveries`는 그 후보로 해소한 광범위 발견을 싣는다. `solvers`는 후보 명세 전건에 측정 행을 하나씩 둔다. 각 측정 행은 `measurement_status: MEASURED|UNSUPPORTED`와 `measurement_error`를 갖는다. `MEASURED`는 현재 측정기가 후보의 DIMACS 호출 방식을 지원해 버전·SAT·UNSAT를 실행했다는 뜻이다. `UNSUPPORTED`는 후보가 없다는 뜻이 아니라 현재 측정기가 그 호출 방식을 지원하지 않는다는 뜻이다. 이때 측정 행의 `status`는 `FAIL`이다.

`installation_targets`는 로컬 패키지 관리자 조회로 설치할 후보 ID만 담는다. 공식 ZIP으로 확보한 `cryptominisat`은 「확보 가능성」 열이 `공식 ZIP으로 가능`이어도 이 목록에 들지 않는다.

`candidate_status`가 `PASS`가 되려면 필수 후보 — `candidate_specs`에서 `discovery_sources`에 `minimum_candidate_set`이 든 명세, 현재는 `minisat`·`cadical`·`kissat`·`cryptominisat` 넷 — 전건의 측정 행이 `measurement_status: MEASURED`여야 한다. 필수 후보가 하나도 없으면 공허한 `PASS`를 막기 위해 `candidate_status`는 `FAIL`이다. 이 판정은 `discovery_complete`와 `unresolved_candidates`를 입력으로 쓰지 않는다. 두 값은 광범위 검색의 완전성과 미해소 발견 패키지를 그대로 기록하는 데이터로 남지만, `winget search --query sat`가 이름에 `sat` 세 글자를 담은 무관 패키지까지 모두 돌려주는 한 `unresolved_candidates`는 구조적으로 비지 않으므로 판정에서 뺐다. 필수 후보 밖의 추가 발견 후보(`discovery_sources`에 `minimum_candidate_set`이 없는 명세)가 `UNSUPPORTED`이거나 미해소로 남아도, 그 사실만으로 `candidate_status`가 `FAIL`이 되지는 않는다 — 그 후보 자신의 판정표 행(있으면)이 자기 `상태`로 그 실패를 담당한다.

이 기준선을 뜬 실행에서 `candidate_status`는 `PASS`다. 필수 후보 넷의 측정 행이 모두 `measurement_status: MEASURED`이기 때문이다 — 네 명세의 DIMACS 호출 방식(`file_argument`)과 실행 파일 탐색 방식(`PATH`·`PATH_then_fallback_path`·`PATH_then_winget_package`)이 현재 측정기가 지원하는 종류다. 이 값은 필수 후보 각각의 실행 성공 여부(판정표 「상태」 열)와는 다른 판정이다 — 이번 실행에서 SAT-CADI·SAT-KISS는 실행 파일을 확보하지 못해 「상태」가 `FAIL`이지만, `measurement_status`는 셋 다 `MEASURED`다. `measurement_status`는 측정기가 그 호출 방식을 다룰 줄 아는지를 재고, 판정표 「상태」 열은 실제 실행 결과를 잰다. `winget`의 광범위 검색이 찾은 패키지 ID 80건 중 `PolarGoose.minisat` 1건만 후보 명세로 해소되었고, 나머지 79건은 `unresolved_candidates`에 데이터로 남아 있으나 이 판정에 들어가지 않는다.

그 광범위 검색은 `candidate_discovery.searches`의 `winget` 항목 하나이고 질의어는 `sat`다. 이 질의는 이름이나 장치 ID에 `sat`를 담은 패키지를 모두 반환하므로, 미해소 79건에는 `Docker.DockerDesktop`, `Mozilla.Firefox.ESR.sat`, `Schrodinger.PyMOL`처럼 SAT 풀이기가 아닌 패키지가 들어 있다. 이 기준선은 79건을 SAT 풀이기 여부로 분류하지 않았다. 따라서 79건 안에 판정표에 더할 후보가 있는지는 미결이다.

판정표의 기존 판정 ID `SAT-MINI`·`SAT-CADI`·`SAT-KISS`·`SAT-CMS`는 각각 현행 후보 ID `minisat`·`cadical`·`kissat`·`cryptominisat`에 일대일로 대응한다. 판정표의 「도구」 열은 같은 순서로 후보 이름 `MiniSat`·`CaDiCaL`·`Kissat`·`CryptoMiniSat`이고, `candidate_specs`의 `candidate_name` 값과 같다. `candidate_specs`가 이 네 후보 밖의 후보를 담으면, 그 후보마다 판정표에 행 하나를 더하고 그 행의 판정 ID를 이 문단의 대응 목록에 등재한다. 측정 행이 `UNSUPPORTED`인 후보의 행은 「버전」 열과 「SAT·UNSAT DIMACS 스모크」 열에 「미실행」과 그 행의 `measurement_error`를 적고, 「상태」 열에 `FAIL`을 적는다. 실행하지 않은 호출에는 exit code를 적지 않는다. 판정표에 행이 없는 후보 ID가 `candidate_specs`에 남아 있으면 이 절은 갱신 대상이다.

| 판정 ID | 도구 | 공식 배포 경로 | 사용 가능한 로컬 패키지 관리 경로 | 확보 가능성 | 호출 표면 | 설치 시도 | 버전 | SAT·UNSAT DIMACS 스모크 결과 | 상태 | 대체 수단 | 갱신 트리거 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SAT-MINI | MiniSat | 공식 저장소와 `winget` | `winget` 조회 exit 0, `PolarGoose.minisat` | 가능 | `minisat.exe <DIMACS 파일>`. PATH에 `minisat.exe`가 없으면 `sat-solvers.txt`의 `solvers.minisat.executable`이 적은 `%LOCALAPPDATA%\Microsoft\WinGet\Packages\PolarGoose.minisat_Microsoft.Winget.Source_8wekyb3d8bbwe\minisat.exe`를 부른다 | I-SAT-MINISAT | 2.2. 이 값은 `winget` 카탈로그가 적은 패키지 버전이고 `sat-solvers.txt`의 `solvers.minisat.package_queries[0].stdout`에 있다. 같은 파일의 `solvers.minisat.version`은 `minisat.exe --help` 출력이고 버전 문자열을 담지 않는다 | 명령은 `sat-solvers.txt`의 `solvers.minisat.sat.command`와 `unsat.command`다. 단위 절은 SAT와 exit code 10이고 모순 단위 절은 UNSAT와 exit code 20이다. | PASS | PySAT `Minisat22` | `winget` 패키지, MiniSat 버전, PATH가 바뀔 때 |
| SAT-CADI | CaDiCaL | 공식 릴리스는 소스 자산을 제공 | `winget` 조회 exit 2316632084, 패키지 ID 없음 | 불가 | 확보 뒤 `cadical.exe <DIMACS 파일>` | 해당 없음. 공식 Windows x64 자산과 로컬 패키지가 없어 확보 불가다. | 실행 파일 없음 | 실행 파일을 찾지 못해 버전·SAT·UNSAT 세 호출의 프로세스가 시작되지 않았다. 측정기는 그 실패에 상수 exit code 127과 stderr `실행 파일 없음: FileNotFoundError`를 기록했다. | FAIL | PySAT의 CaDiCaL 바인딩. 사용 전 독립 스모크가 필요하다. | `winget` 패키지나 공식 Windows x64 자산이 생길 때 |
| SAT-KISS | Kissat | 공식 릴리스는 macOS·Linux 실행 자산을 제공 | `winget` 조회 exit 2316632084, 패키지 ID 없음 | 불가 | 확보 뒤 `kissat.exe <DIMACS 파일>` | 해당 없음. 공식 Windows x64 자산과 로컬 패키지가 없어 확보 불가다. | 실행 파일 없음 | 실행 파일을 찾지 못해 버전·SAT·UNSAT 세 호출의 프로세스가 시작되지 않았다. 측정기는 그 실패에 상수 exit code 127과 stderr `실행 파일 없음: FileNotFoundError`를 기록했다. | FAIL | CryptoMiniSat 실행 파일 | `winget` 패키지나 공식 Windows x64 자산이 생길 때 |
| SAT-CMS | CryptoMiniSat | 공식 Windows x64 ZIP | `winget` 조회 exit 2316632084, 패키지 ID 없음 | 공식 ZIP으로 가능 | `cryptominisat5.exe <DIMACS 파일>` | I-CMS | 5.14.7 | 명령은 `sat-solvers.txt`의 `solvers.cryptominisat.sat.command`와 `unsat.command`다. 단위 절은 SAT와 exit code 10이고 모순 단위 절은 UNSAT와 exit code 20이다. | PASS | PySAT `Minisat22` | CryptoMiniSat 릴리스, 운영체제, `winget` 패키지가 바뀔 때 |

SAT-MINI 행의 버전 `2.2`는 버전 명령의 출력이 아니다. `sat-solvers.txt`의 `solvers.minisat.version`은 `minisat.exe --help`를 exit code 0으로 실행했고, stdout이 비었으며 stderr에 사용법만 담았다. `2.2`는 `candidate_discovery.candidates.minisat.package_queries`의 `winget` 조회 stdout `minisat PolarGoose.minisat 2.2`에서 왔다. 이 값을 갱신할 때는 같은 `winget` 조회를 다시 실행한다.

원시 명령과 stdout·stderr·exit code는 `experiments/pvsnp/smoke/evidence/sat-solvers.txt`에 있다. PySAT가 포함하는 solver 바인딩은 실행 파일 후보가 아니라 FAIL 도구의 대체 수단이다. 이 기준선의 PySAT 스모크는 `Minisat22`만 호출했으므로, PySAT 바인딩을 대체 수단으로 적은 행 중에서는 SAT-MINI 행과 SAT-CMS 행만 명령 출력으로 뒷받침된다. SAT-KISS 행의 대체 수단인 CryptoMiniSat 실행 파일은 `sat-solvers.txt`의 `solvers.cryptominisat`이 `PASS`로 뒷받침한다. SAT-CADI 행의 CaDiCaL 바인딩은 아직 호출하지 않았고, 그 바인딩을 실험에 쓰기 전에 같은 최소 SAT·UNSAT 스모크로 판정한다.

## 6. 명령·로그·판정 대응표

| 명령 표면 | 원시 로그 | 판정 행 |
|---|---|---|
| 저장소 루트에서 실행한 `python experiments/pvsnp/smoke/toolchain_smoke.py --evidence-dir experiments/pvsnp/smoke/evidence`의 Python 패키지 호출 | `experiments/pvsnp/smoke/evidence/python-packages.txt` | PY-PYSAT, PY-SYMPY, PY-Z3, PY-ORTOOLS |
| 같은 명령의 Z3 실행 파일 호출 | `experiments/pvsnp/smoke/evidence/smt-z3.txt` | SMT-Z3 |
| 같은 명령의 로컬 패키지 관리자 탐색·광범위 발견·후보별 조회·SAT 실행 파일 호출 | `experiments/pvsnp/smoke/evidence/sat-solvers.txt` | `candidate_specs`, `candidate_discovery`, `installation_targets`, `solvers`의 후보 ID 전건과 `candidate_status`의 전체 후보 판정 |
| 과거 환경 변경 사건 | `experiments/pvsnp/smoke/evidence/environment-changes.json` | I-PY, I-Z3, I-CMS, I-SAT-MINISAT |
| `python experiments/pvsnp/smoke/test_toolchain_smoke.py` | 테스트 stdout의 시험 건수와 `OK` | 새 구조의 생산자·소비자와 증거 종류 경계 |

`toolchain_smoke.py`는 매 실행에서 import, 패키지 관리자, 광범위 후보 발견, 후보별 조회, 지원하는 실행 파일을 다시 호출한다. `collect_report()`와 `--json`은 같은 후보 명세와 후보 발견 결과를 쓴다. `sat-solvers.txt`는 같은 후보 ID로 명세, 해소 상태, 조회, 설치 대상, 측정 결과를 쓴다. 두 출력 표면은 `measurement_status`와 `measurement_error`도 그대로 보존한다.

현재 측정기가 후보의 DIMACS 호출 방식을 지원하지 않으면 버전·SAT·UNSAT를 실행하지 않는다. 세 결과는 각각 `execution_status: NOT_RUN`, `command: 없음`, `exit_code: null`, 빈 stdout, 실패 사유 stderr를 갖는다. 실행하지 않은 결과에는 수치 exit code를 만들지 않는다. 같은 측정 행의 `executable`은 `없음`이고 `sat_input`과 `unsat_input`은 빈 문자열이다. 빈 `sat_input`은 빈 DIMACS 파일을 넘겼다는 뜻이 아니라 DIMACS 파일을 만들지 않았다는 뜻이다.

`environment-changes.json`의 SAT 설치 사건은 `package_manager`, `package_id`, `command`, `exit_code`, `stdout`, `stderr`를 갖는다. 설치가 실패하면 사건은 `error`, `fallback`, `refresh_trigger`, `status: FAIL`로 완결한다. 설치 시도 뒤의 `remeasurement`는 같은 후보 명세로 실행 파일, 버전, SAT DIMACS, UNSAT DIMACS를 다시 측정한다. 사건 자체는 `evidence_type: recorded_event`로, 사건이 담은 `remeasurement`는 `evidence_type: live_measurement`로 표시한다. 세 라이브 로그는 `recorded_event`를 담지 않는다.

## 7. 안전 경계 전수 검사

| 검사 대상 | 결과 | 근거 |
|---|---:|---|
| P5′ 목록 밖 환경 변경 명령 | 0건 | `environment-changes.json`의 I-PY, I-Z3, I-CMS, I-SAT-MINISAT 대상 전건 대조 |
| 형식 증명 도구 설치 시도 | 0건 | 환경 변경 명령 전건 대조 |
| WSL·컨테이너·새 패키지 관리자·소스 빌드 사용 | 0건 | 명령·원시 로그·문서 전건 대조 |
| 크리덴셜 값·개인 식별 정보 출현 | 0건 | 로컬 경로를 `%LOCALAPPDATA%`와 `%TEMP%`로 치환한 뒤 전건 검색 |
| 유한 스모크에서 복잡도 계급의 존재·부재를 도출한 주장 | 0건 | 명령·원시 로그·문서 전건 대조 |
| 이 문서의 한국어 산문·LaTeX 수식 형식 위반 | 0건 | 절 제목과 산문 전건 대조. 수식은 $x$와 $x \land \neg x$로 표기했다. 소스 코드·원시 로그·데이터 파일은 형식 검사에서 제외한다 |

형식 증명 도구 4종은 P5′에 따라 설치 범위 밖에 유지했다. FAIL 도구는 3절부터 5절까지의 판정표가 「대체 수단」 열에 적은 수단만 사용한다. 대체 수단이 기록되어 있지 않거나 대체 수단도 실패하면 해당 실험을 FAIL로 닫는다.
