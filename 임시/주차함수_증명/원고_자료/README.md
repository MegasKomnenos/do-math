# 원고 자료 묶음

## 처음 돌려 볼 것

아래 여섯 검산은 각각 1분 안에 끝나고, 출력에 오른쪽 열의 문자열이 나오면 부록 D의 해당 값과 같다. `<묶음>`은 이 폴더(`원고_자료`)의 경로이고, 현재 폴더에 작은 파일을 쓰는 것이 있으므로 빈 작업 폴더에서 돌린다. 시간은 이 기계(4코어, 다른 계산 셋과 공유)에서 잰 것이다.

| 명령 | 부록 D 항목 | 기대 출력 | 시간 |
|---|---|---|---|
| `python -I <묶음>/세션_재계산/logconcavity_n80/lc_n80.py` | `D.{{D:logconcavity-failure-n80}}` | `first failure: (n, l) = (80, 40)`, `three integers equal to appendix D (D.logconcavity-failure-n80): True` | 1초 |
| `python -I <묶음>/세션_재계산/fiber_exhaustive/fiber_exhaustive.py 7` | `D.{{D:fiber-enumeration}}` | `n=7: parking functions 262144`, `non-unimodal fibers 30` | 3초 |
| `python -I <묶음>/세션_재계산/zeta_constants/zeta_iv.py 4000 4000` | `D.{{D:zeta-constants}}` | `z_{3/2}  in [2.6123753485619…, 2.6123753487472…]  subset of [2.61237, 2.61238]: True` 외 둘(`z_{-1/2}`, `z_{1/2}`) | 4–5초 |
| `python -I <묶음>/세션_재계산/prop_W_thirteen/iv13.py` | `D.{{D:prop-W-thirteen}}` | `all 13 pass: True` | 1초 |
| `python -I <묶음>/세션_재계산/cumulative_logconcavity_n779/lca_exact.py quick 572 581 780` | `D.{{D:cumulative-logconcavity}}` | `violations at n = 780: [575, 576, 577, 578]` | 22초 |
| `python -I <묶음>/세션_재계산/band_check/band_cells.py 0.71216 0 4000 band_cells_CE0.tsv` | `D.{{D:band-check}}` | `minimum ratio lower bound = 1.35587396520276 at cell 0, [1/2, 12001/24000]` | 25–35초 |

첫 줄은 행의 로그오목성이 처음 깨지는 자리($n=80$, $\ell=40$)를 마지막 차 재귀의 정확 정수로 다시 만들고, 세 정수 $b_{80,39}$, $b_{80,40}$, $b_{80,41}$을 부록 D 결과 줄의 값과 비교한다. 다섯째 줄은 누적 로그오목성 계산(열 $1$–$798$, $n\le800$; 두 프로세스로 약 $25$분)의 축소판으로, 열 $572$–$581$과 $n\le780$만 계산해 $n=780$의 위반 넷을 보인다. 무거운 계산의 축소판까지 차례로 돌리려면 `python -I <묶음>/빠른_확인.py`(아래 「재실행표와 빠른 확인」)를 쓴다.

이 폴더는 `원고.md`(주차함수 최대 변위 개수열의 단봉성: 증명)의 부록 D가 가리키는 계산 자료의 사본이다. 부록 D의 각 항목은 어떤 진술을 어떤 식·알고리즘·범위·산술로 확인했는지를 적고, 그 계산을 수행한 코드와 입력·출력·표의 파일을 「자료」 줄에 기록 안의 경로(와 이 글의 재계산이면 `세션_재계산/` 아래의 경로)로 적으며, 기록의 파일이 이 폴더 안에 놓인 자리는 아래 「파일 목록」 표(기록 식별자 폴더 아래 원래 이름)로 찾는다. 기록의 파일은 연구 기록의 증거 폴더에서 그대로 복사한 것이며 내용을 고치지 않았다.

## 라이선스

이 묶음의 글과 자료는 이 묶음이 실리는 Zenodo 기록과 같이 CC-BY-4.0으로 배포한다. `세션_재계산/`의 코드와 `빠른_확인.py`도 따로 표시하지 않는 한 같은 라이선스를 따른다. 기록 식별자 폴더의 파일은 지식 베이스의 사본이며 그 라이선스를 그대로 따른다.

## 폴더 구조

`<기록 식별자>/<원 파일명>`. 기록 식별자는 `r` 뒤 일곱 자리 16진수이고, 원 파일은 그 기록의 `evidence/` 아래에 있던 것이다. 같은 기록의 다른 하위 폴더에서 온 파일이 이름이 겹치면 하위 폴더 이름을 접두로 붙인다(예: `peer__fixcheck.py`).

## 실행 환경

이 글의 재계산(`세션_재계산/`)과 `빠른_확인.py`는 아래 환경에서 돌렸다.

- **운영체제와 기계.** Windows 11 Pro 64비트(10.0.22631), Intel Core i5-4570(Haswell, 4코어; AVX2·FMA3 지원). 계산하는 동안 다른 계산과 코어를 나눠 썼으므로 적은 시간은 벽시계 시간의 대략값이다.
- **Python.** CPython 3.12.10(64비트). 표준 라이브러리 밖의 패키지는 numpy 2.5.2와 mpmath 1.3.0 둘이다(`requirements.txt`). 기록 코드 사본 가운데 몇은 sympy, gmpy2, python-flint를 더 쓴다(`requirements.txt`의 주석).
- **C 컴파일러.** MSVC 19.44(Visual Studio 2022, x64). 이 글의 C 프로그램은 `세션_재계산/c50_iv/c50iv.c` 하나이고 빌드 명령은 `build.bat`에 있다(아래 「컴파일 옵션」).
- **실행 방식.** 모든 스크립트는 `python -I <경로>`로 돌린다. `-I`(격리 모드)는 환경 변수와 사용자 site-packages를 읽지 않으며, Python 3.11부터는 스크립트의 폴더도 `sys.path`에 넣지 않는다. 그래서 이 글의 재계산 스크립트 가운데 같은 폴더의 모듈을 읽는 것은 스스로 `__file__`의 폴더를 `sys.path`에 넣는다. 기록 코드 사본(`r…/` 폴더)은 바이트 사본이라 그 처리가 없으므로, 같은 폴더의 모듈을 읽는 사본(예: `rce3dc75/vertical_exact_constant.py`, `rce3dc75/hermite_bounds_audit.py`, `r13b0b8f/indep_cert2.py`)은 `python -E -s <경로>`로 돌린다(`-I`에서 `-P`만 뺀 것이라 환경 변수와 사용자 site-packages는 여전히 읽지 않고, 스크립트의 폴더만 `sys.path`에 들어간다). `빠른_확인.py`는 각 명령을 새 임시 폴더에서 `python -I -B`로 돌려 묶음 안에 `__pycache__`나 출력 파일을 만들지 않는다.

**다른 환경에서 돌려 본 결과.** WSL의 Ubuntu 20.04에서 `빠른_확인.py`를 돌리려 했으나, 네 번의 시도가 모두 가상 머신을 띄우는 단계에서 시간 초과로 끝났다(오류 코드 `Wsl/Service/CreateInstance/CreateVm/ERROR_TIMEOUT`; WSL 3.0.5.0, 커널 6.18.58.1-1; `wsl --shutdown` 뒤에도 같음). 그래서 리눅스에서의 실행은 확인하지 못했다. 대신 같은 기계에서 다음을 확인했다.

| 환경 | 결과(`python -I -B 빠른_확인.py`, 기본 32개) |
|---|---|
| Python 3.12.10, numpy 2.5.2, mpmath 1.3.0(기준 환경) | 32개 모두 일치, 520초 |
| Python 3.11.9, numpy 2.3.5, mpmath 1.3.0(이 기계에 따로 설치된 판) | 32개 모두 일치, 419초 |
| Python 3.9.25, numpy 1.26.4, mpmath 1.3.0(`uv`로 만든 가상 환경; WSL에서 시도하려던 `numpy<2` 조합) | 30개 일치, 2개 불일치(456초) |
| Python 3.8.20, numpy 1.24.4, mpmath 1.3.0(같은 방식) | 21개 일치, 11개 불일치(431초) |

기준 환경의 줄은 지금의 항목 구성(자기일관 상수 (4)의 합 항목을 빼고 모멘트 판정 항목을 열 $k=840$으로 바꾼 뒤)으로 다른 계산과 코어를 나눠 쓰며 다시 잰 것이고, 나머지 세 줄은 그 전의 항목 구성에서 잰 것이다.

불일치는 모두 수치가 달라서가 아니라 스크립트가 중간에 멈춘 것이다. 원인은 둘이다.

- **`math.nextafter`.** Python 3.9에 들어온 함수라 3.8에서는 `bprime_boxes/ivbox_lib.py`(띠 상자도 이것을 쓴다), `Q_fin_1130/qfin_iv.py`, `Q_fin_1130/test_small.py`가 읽는 단계에서 멈춘다. 3.8의 불일치 11개 가운데 9개다.
- **`np.ldexp`의 지수 형.** `band_LP/bandlib.py`의 지수 함수 구간이 `np.ldexp(…, m.astype(np.int64))`를 쓰는데, Windows의 numpy 1.x는 이 지수로 32비트 정수만 받아 `TypeError`를 낸다. numpy 2부터는 Windows의 기본 정수가 64비트라 이 문제가 없다. 띠 LP의 (다)·(라) 축소판 둘이 여기에 걸리고, 3.9의 불일치 2개와 3.8의 나머지 2개가 이것이다. 리눅스의 numpy 1.x에서도 같은지는 확인하지 못했다.

따라서 이 묶음의 파이썬 스크립트에는 Python 3.9 이상이 필요하고, Windows에서는 numpy 2 이상도 필요하다. 기준 환경(`requirements.txt`)의 판을 쓰는 것이 가장 안전하다. 열 판독 항목(`--all`에서만 돈다)은 기준 환경에서 따로 돌려 일치했다(212초).

## 컴파일 옵션

부록 D가 가리키는 C 프로그램과 그 빌드 옵션이다. 「기록·이 글의 빌드」는 소스 머리 주석, 빌드 스크립트, 기록의 보고서에 적힌 그대로다. 「GCC·Clang」 열은 같은 산술을 얻기 위한 대응 옵션이다. 공통 원칙은 셋이다.

- 곱셈과 덧셈을 FMA 하나로 합치는 축약을 끈다: `-O2 -ffp-contract=off`. MSVC의 `/fp:precise`·`/fp:strict`와 `#pragma fp_contract(off)`에 해당한다.
- 반올림 모드를 바꾸는(`fesetround`) 구간 코드에는 `-frounding-math`를 더한다. Clang은 `-ffp-model=strict`가 두 설정을 함께 켠다.
- `-ffast-math`(와 그것을 켜는 `-Ofast`)는 쓰지 않는다. 결합 법칙 변형과 축약이 오차 해석과 반올림 방향을 깨뜨린다.

| 프로그램 | 부록 D 항목 | 기록·이 글의 빌드 | GCC·Clang |
|---|---|---|---|
| `세션_재계산/c50_iv/c50iv.c`(이 글) | `D.{{D:c50}}` | MSVC 19.44 `cl /O2 /fp:strict /arch:AVX /openmp`(`build.bat`; 생성된 어셈블리에 FMA 명령 없음) | `gcc -O2 -mavx -mno-fma -ffp-contract=off -frounding-math -fopenmp '-D__declspec(x)=__attribute__((x))' c50iv.c -lm`; Clang은 `-ffp-contract=off -frounding-math` 대신 `-ffp-model=strict`. `__declspec(noinline)` 다섯 곳 때문에 매크로 정의가 필요하고, `#pragma fenv_access(on)`은 GCC가 무시하므로 `-frounding-math`가 반드시 있어야 한다. `objdump -d`에서 `vfmadd`가 0개인지 확인한다. 아래 GCC 시험 참고 |
| `r59c82d7/qrcert.c`(기록) | `D.{{D:c50}}` | `cl /O2 /arch:AVX2 /openmp /fp:precise qrcert.c`(소스 머리 주석) | `-O2 -mavx2 -mfma -ffp-contract=off -fopenmp`. 내적은 명시적 FMA 내장함수(`_mm256_fmadd_pd`, `fma`)를 쓰고 오차 해석이 FMA를 반올림 한 번으로 센다. 반올림 모드는 바꾸지 않는다 |
| `rce3dc75/icert.c`(기록) | `D.{{D:central-gap-integer}}`, `D.{{D:exact-n20000}}` (ㄷ) | `cl /nologo /O2 /openmp icert.c`(기록 `build_icert.bat`) | 정수 고정소수점 프로그램이지만 MSVC 내장함수 `_umul128`(`<intrin.h>`)을 쓰므로 GCC·Clang에서는 `unsigned __int128` 곱으로 바꾸는 이식이 필요하다. 옵션 `-O2 -ffp-contract=off -fopenmp` |
| `r19de912/qr_cert2.c`(기록; 같은 기록의 `qr_cert3.c`도 같은 구조) | `D.{{D:exact-n20000}}` (ㄹ), `D.{{D:m1-column-reading}}` | `cl /nologo /O2 /openmp /W3 qr_cert2.c`(기록 `build.bat`) | `icert.c`와 같다(`_umul128` 이식 필요, `-O2 -ffp-contract=off -fopenmp`) |
| `r15df76b/leftcert.c`(기록; `leftcert_build1.c`·`leftcert_build2.c`는 빌드 이력판) | `D.{{D:exact-n20000}}` (ㄴ) | `clang -O3 -march=native -D_CRT_SECURE_NO_WARNINGS`(Visual Studio 2022 동봉 clang 19.1.5; `unsigned __int128` 때문에 MSVC `cl`은 불가) | `-O2 -ffp-contract=off`. 판정은 정수 비교이고 부동소수는 진단 출력에만 쓰인다 |
| `pcertv.c`(기록 [r15df76b], 이 묶음에 없음) | `D.{{D:exact-n20000}}` | `clang -O2 -mavx2 -ffp-model=strict` | `gcc -O2 -mavx2 -ffp-contract=off -frounding-math`(`fesetround`로 방향 반올림) |
| `icert_rows.c`(기록 [r6b37c7e]·[r475ada3], 이 묶음에 없음) | `D.{{D:band102-integer}}` (ㅁ) | `clang -O2 -D_CRT_SECURE_NO_WARNINGS`(MSVC 19 환경의 clang 19.1.5) | `-O2 -ffp-contract=off`. `unsigned __int128`을 쓰는 정수 전용 프로그램이고 MSVC `cl`로는 빌드되지 않는다 |
| `lmcert_sweep.c`(기록 [r10ff8c2], 이 묶음에 없음) | `D.{{D:moment-certification}}` | MSVC 19.44 `cl /O2 /fp:precise`, 소스 안 `#pragma fp_contract(off)` | `-O2 -ffp-contract=off`. 반올림-최근접 binary64와 사전 오차 해석이므로 반올림 모드는 바꾸지 않는다 |

**GCC 시험.** WSL이 뜨지 않아 리눅스에서는 빌드하지 못했다. 대신 같은 기계의 MSYS2 GCC 16.2.0(대상 `x86_64-pc-cygwin`)으로 `c50iv.c`를 소스 수정 없이 위 표의 GCC 줄 옵션에 `-fno-fast-math`를 더해 빌드했고, 역어셈블에 `vfmadd` 명령은 없었다. 이 빌드로 두 실행을 했다.

- **$n\le60$ 실행.** `run_commands.txt` 3단계의 `60 5 2 59 16 2 t60 <표 폴더> -dumpall`이다. `exact_small.py`의 대조 출력은 구간 927개가 모두 정확 정수를 담는다고 보고했고, MSVC 빌드의 `runs/t60_exact_check.txt`와 바이트 단위로 같았다. 행 파일은 줄 끝 문자만 다르다.
- **$n\le20000$ 재인증의 탐침 B.** `20000 5 19522 19585 64 1 c20_probeB <표 폴더> -probe 19522 19523 19524`이다. 구간 덤프(1,431개 값)가 MSVC 빌드의 `runs/c20_probeB_dump.bin`과 비트 단위로 같았다.

기록의 C 프로그램은 다시 빌드해 보지 않았다.

## 재실행표와 빠른 확인

- **`재실행표.md`.** 부록 D의 항목마다 스크립트, 실행 명령, 기대 출력, 출력 파일과 SHA-256, 실행 시간, 산술 등급, 재실행 여부를 한 줄로 적은 대응표다. `scripts/_gen_재실행표.py`가 부록 D와 이 README의 표에서 만들며, 다시 돌리면 갱신된다. 아직 끝나지 않은 계산이 걸린 항목이 있으면 그 칸을 「(진행 중)」으로 둔다(지금은 없다; 끝나야 아는 값은 `[Dn:이름]` 자리표시자).
- **`빠른_확인.py`.** 각 항목의 축소판을 차례로 돌려 기대 출력(핵심 수치)과 맞춰 보고 한 줄씩 일치/불일치를 적는다. 축소판은 원 계산의 한 부분이다. 예를 들어 앞쪽 $q$ 몇 개, 최솟값이 나온 상자 하나, 열 몇 개를 돌리며, 원래 짧은 계산은 전체를 돌린다. 기대 문자열은 축소판을 한 번 돌려 얻은 값이고, 원 출력 파일의 해당 줄과 같음을 확인했다. binary64 방향 반올림으로 하계를 계산하는 항목(열 $2001$·$3130$의 한 걸음 판정)은 합산 순서나 FMA 사용에 따라 하계의 마지막 표시 자리가 환경마다 다를 수 있으므로, 판정 `True`와 함께 두 하계를 기대값과 상대 $10^{-5}$ 안에서 견준다. `--list`는 항목 목록, `--fast`는 60초를 넘는 항목을 빼고, `--all`은 기본으로 빼 둔 긴 항목(열 판독 전체, 약 3–4분)까지 돌린다. C 프로그램 항목 둘은 빌드된 `세션_재계산/c50_iv/c50iv.exe`(Windows x64)를 부른다. 기본 실행(긴 항목을 뺀 32개)은 기준 환경에서 520초에 모두 일치했고(다른 계산과 코어를 나눠 쓴 상태), 긴 항목 하나(212초)를 더하면 약 12분이다.
- **축소 인자.** 무거운 스크립트는 대부분 범위 인자가 이미 있다. 출력 파일을 스크립트 폴더에 쓰던 다음 스크립트에는 `--quick` 옵션(출력을 현재 폴더에 쓴다)이나 모드를 더했고, 옵션을 주지 않은 기본 실행의 동작과 출력은 바뀌지 않았다.
  - `window_mass_env/cert_Cb_iv.py`, `window_mass_env/cert_interval_iv.py`: `--quick`.
  - `r030ffae_window/work/cert_Cb_range.py`: `--quick`. 입력을 파일 자신의 폴더에서 읽고 결과 JSON을 현재 폴더에 쓴다. 이 파일은 더 이상 바이트 사본이 아니다.
  - `band_LP/part_ga_na.py`, `part_da.py`, `part_ra.py`: `--quick`.
  - `cumulative_logconcavity_n779/lca_exact.py`: `quick LO HI N` 모드.
  - `r89eb039_polar/recert.py`: `-I`에서도 같은 폴더의 모듈을 읽도록 자기 폴더를 `sys.path`에 넣는 한 줄을 더했다.

## 세션이 만든 수정판(세션_재계산/)

부록 D의 항목 `D.{{D:window-mass-constant}}`(조립 뒤 번호)가 기대는 수정판 코드는 연구 기록에 서술로만 있고 파일로는 없다(기록 [r8a9b11e]의 검토 `review/feedback.md` §3.3). 글을 조립한 세션이 2026-11-13에 기록의 `evidence/peer/ul_iv.py`를 복사해 서술대로 한 줄 고친 판 `r8a9b11e/ul_iv_fixed.py`를 만들고 다시 실행했다. 고친 줄: 115행 `pref = SQ2PI_INV`(꼬리 인자 $e^{-(\theta-\mathfrak h_0)_+\theta/2}$를 자명한 상계 1로; 앞 상수 $1/\sqrt{2\pi}$는 유지). 실행: `python -I ul_iv_fixed.py 25000 1600 1200 0.1 6400 4`(약 3분; $\mathsf w_0\ge0.71216801$), `python -I ul_iv_fixed.py 25000 800 600 0.1 3200 4`($0.70623905$). 출력은 `outputs_fixed/`에 있다. 이 파일들은 기록의 원본이 아니라 세션이 만든 것이다.

| 경로 | SHA-256 |
|---|---|
| `세션_재계산/r8a9b11e/ul_iv_fixed.py` | `f43df11f6de018ec939662204c8e8eb42ce45a761a24190ca0c82dbd8cf7e76c` |
| `세션_재계산/r8a9b11e/outputs_fixed/ul_iv_fixed_1600x1200.txt` | `7f567e96585af3f24c78be6231c8b5988c3bafee9827f31bce069876e3bcba7f` |
| `세션_재계산/r8a9b11e/outputs_fixed/ul_iv_fixed_800x600.txt` | `d58310796e03821a5aa0a20bb02e82f5ffe8e4381109cb00c9ad9cf21e756c14` |
| `세션_재계산/zeta_constants/zeta_iv.py` | `541bd2dbf9868da06f39d0dfd0493c7280a6113046ddf85ae75d77fb2939def2` |
| `세션_재계산/zeta_constants/zeta_iv_out.txt` | `27d0aa9f2fd1a0969df579e18865152374e32eb8d8a14982738688a2d936b6ca` |
| `세션_재계산/r030ffae_window/work/xKrig.npy` | `a6177d01365d127a6a4a6716200fca9af1099f3043eef7a72077bea928c64330` |
| `세션_재계산/r030ffae_window/work/wKrig.npy` | `38664171e13017c864ebd9dca63cc4e46019a1d0b4b6b0eb8a8e3fda134be3dc` |
| `세션_재계산/r030ffae_window/work/xKrig_orig.npy` | `16f6fbc8fa801ba6e4e66e6336d943a0736096d00940406a300c599eda724287` |
| `세션_재계산/r030ffae_window/work/wKrig_orig.npy` | `8e047df2647393e22c7fbfb157fd1dcfa9de2bdd25aa06f6586ad603d52eb609` |
| `세션_재계산/r030ffae_window/work/FIXED_cert_interval_result_0_16.json` | `b039497680fb1f0ebac2d44701d1a14394b0f0ecb0b8ac4856fc18b56336363d` |
| `세션_재계산/r030ffae_window/work/FIXED_cert_Cb_result_1_31.json` | `802cfc4d4d57e01fb041ce5788b2ffd90be73f40d142cb21638666f4064d7d67` |
| `세션_재계산/r030ffae_window/work/FIXED_cert_Cb_result_31_1500.json` | `edfaafd681772978b437205b00ea62a73362dd14b822e691b9dc23466963672f` |
| `세션_재계산/r030ffae_window/work/FIXED_cert_Cb_result_1500_2250.json` | `8ecdafc3abdaacd3603f6bea272fea2e9b0418b5a68b7baf3465faf097800880` |
| `세션_재계산/r030ffae_window/work/FIXED_cert_Cb_result_2250_3000.json` | `15c0f733c74a35e8a6d83ed74d0cf7b59f297ec6e0a1b547693d62b093f4a35b` |
| `세션_재계산/r030ffae_window/NEW_cert_interval_0_16.out` | `6cab0cd0ba582e7781d376751b7a18a6e453787a243ae1e2713f13362eca6c27` |
| `세션_재계산/r030ffae_window/NEW_cert_Cb_1_31.out` | `4965b0fde084f4f4ba6323ae7524bb59f60b79d731a15fd8a9298b4c139ab60f` |
| `세션_재계산/r030ffae_window/NEW_cert_Cb_31_1500.out` | `c86c2ac4ecb5fd2758d5392a5bf08130a30248e00f4d4e605feea522e94be9fa` |
| `세션_재계산/r030ffae_window/NEW_cert_Cb_1500_2250.out` | `5ccd59f419542b03c2020ed67432638ce1d3a95ed358859a4ef53291d7acf8d4` |
| `세션_재계산/r030ffae_window/NEW_cert_Cb_2250_3000.out` | `55e08066959ce5a47d200e1b08038f2ce7fd68e05dce05b4844946e7ad42fde5` |
| `세션_재계산/prop_W_thirteen/iv13.py` | `bc6c4d7a8e3587d726bb6b4db03bdaf2ffc1fe57bdebf257697f5e9b8ef47d39` |
| `세션_재계산/prop_W_thirteen/iv13_out.txt` | `70f1db875f32769b8252e01868528437f68a83105bc9ed24920615f557c53458` |
| `세션_재계산/AR_integrals/ar_integrals_iv.py` | `51dd7fd64eec2321d269970db1af4cba6ca295dc56b459501c2cea0958bd7715` |
| `세션_재계산/AR_integrals/ar_integrals_iv_out.txt` | `68a4927eef59f99fc6232bdc666e2f525b8614acc15bb495a0a58f738776bf8f` |
| `세션_재계산/pair_one_variable/pair_iv.py` | `e5b9e938aaa4a2916379adc3c358260b72b752a976612f6259f752d33e248b38` |
| `세션_재계산/pair_one_variable/pair_iv_out.txt` | `a5ea4b85ccc14e12835ff5562ca7ba999ba9e7f34a590e2df504443dd6af93a3` |
| `세션_재계산/fiber_nonunimodal_bound/fiber_bound_iv.py` | `fa09ba2b03c24c4a04b4c9fab64fc557790eff95eb8c0ff300cd4c3115a862b7` |
| `세션_재계산/fiber_nonunimodal_bound/fiber_bound_iv_out.txt` | `9dc71ad4ff70d5eb6eef56329bd965d7b7d09fea5f3d9f4e509f075feec7f01a` |
| `세션_재계산/theorem_U_constant/theorem_U_iv.py` | `8feb686bb594d5090708c31970fb2ebc62ef99c24db61694c751cc00fa326dbe` |
| `세션_재계산/theorem_U_constant/theorem_U_iv_out.txt` | `0ec306b8695bb7f4accc1d18e68cf6249979fa8ec4c9681a77b22def942bab39` |
| `세션_재계산/theorem_U_constant/theorem_U_iv_out_32000.txt` | `52c0724b15f565291da1bd34bbf5c4d14478b1cd0ef16991dda76fc941c596e6` |
| `세션_재계산/theorem_D_base/thmD_base_iv.py` | `1934dfd0201edd58134b5d32a09c06d16bdcf63bbab08831effb947cc772e65e` |
| `세션_재계산/theorem_D_base/thmD_base_iv_out.txt` | `0768baa0474cbaa4b4aa1fc1674104810b511d906490ab79db46b50e465b1722` |
| `세션_재계산/M_natural/j_integrals_iv.py` | `76f0a54fd568eec1799e935e4ac9f1a064e1f57216890916875cf7dfb7b1d35c` |
| `세션_재계산/M_natural/j_integrals_iv_out.txt` | `94b66c90293152ed6e9c6df6d293d61bf66430510c14a1c5095ff9c7a5fd7023` |
| `세션_재계산/four_families/families_iv.py` | `429c15d9577922ede2892379bd1778d8e0e80c5bceb03039befd5604c71ee2f3` |
| `세션_재계산/four_families/families_iv_out.txt` | `014f46bf0bfaa50985021369246717998f30c0add8284af4fcdab1a3e4bc2b03` |
| `세션_재계산/r89eb039_polar/recert.py` | `dd26b61f29a84b20c29a1b84e675f6cf9fa806c76e7349161881ff309cea1ed1` |
| `세션_재계산/r89eb039_polar/sparts.py` | `1ba8de14883535a66dcc047bfaa160aa9969084c75ce1cb1f2e6d5648d9cac43` |
| `세션_재계산/r89eb039_polar/sparts_orig.py` | `a67fe867503baf74cdda2975f40232f17e2474b19cbc7af42fd7828b65589eeb` |
| `세션_재계산/r89eb039_polar/fixed/cert_ia2.py` | `a2471dbcaca6b1afe24dc177e08a4b7bd5dd6772c55650f197876bf85b352fd6` |
| `세션_재계산/r89eb039_polar/NEW_adaptive_2087_5000.jsonl` | `e0d187e94b29f7f6622bdc9f013bf7202a3a7332d5a443ca69bab3be14c071d7` |
| `세션_재계산/r89eb039_polar/NEW_recert_P1.jsonl` | `01d6eb56157f0b761002b7e7e366cde436a1c3c97b58c9894f336bb72ed8e274` |
| `세션_재계산/r89eb039_polar/NEW_recert_P2.jsonl` | `8454bfadd41e72b7fb93b0c6900147825bcc1d77fa482e392f7ea1466dd248b2` |
| `세션_재계산/r89eb039_polar/NEW_recert_P3.jsonl` | `4fd57cdd5ef02a8d4236ba8e71429dcee6016c4cd412f1576cf0257e25b55bc3` |
| `세션_재계산/r89eb039_polar/NEW_recert_P4a.jsonl` | `9ae0f9d27d1acab94c0b1c0a01b3f7165f1b034d5b1078b506e55ce56ecd20b7` |
| `세션_재계산/r89eb039_polar/NEW_recert_P4b.jsonl` | `bf46093e033438aa702525f458978429054fc3cb6663e2b2be98f2e877dceafc` |
| `세션_재계산/r89eb039_polar/NEW_recert_Q1.jsonl` | `bb44a80a0d6e3f4b15f1edbac857f9aa369d23a8a147424a353e7c547e303dd5` |
| `세션_재계산/r89eb039_polar/NEW_recert_Q2.jsonl` | `830b1aafb0a49f0726f0a80ab31f3c88d4cc9abbb0312d0e20dc9fade57272d3` |
| `세션_재계산/r89eb039_polar/NEW_adaptive_2087_5000.log` | `6dbbbf5fb32a464853e1cdf93d9db842f90be706622e18b1d8bde55963d73df4` |
| `세션_재계산/r89eb039_polar/NEW_recert_P1.log` | `79263df2d4135186f78d86cb501493f97b870f384e9aa74addc8aa4111fc920a` |
| `세션_재계산/r89eb039_polar/NEW_recert_P2.log` | `be7a9c656be6611f0e529508e7f2b648d41ffa0ca4d6aea90988e01a4edbf1b0` |
| `세션_재계산/r89eb039_polar/NEW_recert_P3.log` | `fd158cfe2147c0bec3eb222b620ec99054b58966f66a6f2cf834f152cdb4de55` |
| `세션_재계산/r89eb039_polar/NEW_recert_P4a.log` | `460ae3a5564342a6c57cc713929ef052cac40cfea55541caab505dfee9350752` |
| `세션_재계산/r89eb039_polar/NEW_recert_P4b.log` | `25b75c1996e4ea4885489ff6735d383fe35ea4433a3f5e73de552246601fd00a` |
| `세션_재계산/r89eb039_polar/NEW_recert_Q1.log` | `1f153287a80379f254a39ba0f8b9033759e6e0f21957a8de53bf3b21ce6bc326` |
| `세션_재계산/r89eb039_polar/NEW_recert_Q2.log` | `0a64cf3306cec6a7db35c0289c6e47a15ba12af8be1ce64bc743539cc00482e3` |
| `세션_재계산/band_LP/bandlib.py` | `f468a657172f75b9f2423c654cf923c1472c5f9ea9e329c6107e0b0e4a6f2284` |
| `세션_재계산/band_LP/part_ga_na.py` | `4392f544ff59582b068700c865f97b86a81897347e0deb8f4fc436f57cb3c6a8` |
| `세션_재계산/band_LP/part_da.py` | `8114b15ba2562c019854d75786f5355afba378acac190723f82b019cbb047a97` |
| `세션_재계산/band_LP/part_ra.py` | `a7421356744393c36a9efe7c019267b91f174e6a8489fb1508b3f04cbcf87d89` |
| `세션_재계산/band_LP/out_ga_na.txt` | `e70b0acc97b6ead2457a5577a4955594f398a1416e6d560ddd7e9d6cd27cfee7` |
| `세션_재계산/band_LP/out_da_9467_22000.txt` | `8d529452b8bdae154a3a58b10add31d961e5ffd70d5a81e2ba5d6829e05862e7` |
| `세션_재계산/band_LP/out_da_22001_38886.txt` | `2332121e20d308cc98efb7c8f78a1d9fd23f6eae22c80b160801b2ba4a142f35` |
| `세션_재계산/band_LP/out_ra_6668_8000.txt` | `ae86688361a73a6f943f20ad4ac566ed1402a32f600ef7cb35a20c29ab3cf856` |
| `세션_재계산/band_LP/out_ra_8001_9466.txt` | `7d1587e92717893ea8e0cb332d38e9dd275051f8165ff8619802780edb735723` |
| `세션_재계산/band_LP/xcheck_mp.py` | `d4df40447bca6fe1397ff41c7d0df0bd7942ecd88b704d1a113efaf4b2dfba69` |
| `세션_재계산/band_LP/xcheck_mp_out.txt` | `a0f4d6bda2958e00618ee3d90a6dcda2c896f9705bac91aace9d4e0a6df73d7c` |
| `세션_재계산/band_LP/ulp_check.py` | `73fecba6aa99cb37c54564343fa91a47e6a965ff49078decca5aa2bbe8ebf9f3` |
| `세션_재계산/band_LP/ulp_check_out.txt` | `7c06362f0ea318ff1fe3b24a5696f7c1e04acf01e88a4bfc8aef5fe0f98134eb` |
| `세션_재계산/band_boxes/band_iv.py` | `9e71706b1e719a376965909fa8f61ed0d16fb05db2a41aeb6bd49451972d9e7f` |
| `세션_재계산/band_boxes/band_result.txt` | `c0ebd4267bf232fa16c927fb6b843995cf39918f74752566e6e59253a6ceff48` |
| `세션_재계산/band_boxes/band_summary.py` | `3f957350810f8b22453cc2dc8eee014866bf75f2cac0a5619e419ef2859e0e83` |
| `세션_재계산/band_boxes/box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.json` | `c45ef79174f595c951aff327c32e4e41bbd0a0820f778081df21467cafe032e5` |
| `세션_재계산/band_boxes/box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.json` | `5847ceec24595dbcb5918368cb90df70028427565665bb4c510c912d3ad051c6` |
| `세션_재계산/band_boxes/box_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.json` | `9737654f03d1260c2201ac0d857adaa39e4843acf6e2833fb4d2f43993b2b5c4` |
| `세션_재계산/band_boxes/box_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.json` | `3323a35bed9faf4fdc112d0d5837642dafdfb1f38c907ad12ea0b763d29e7028` |
| `세션_재계산/band_boxes/compare_record.py` | `8f94619ba96abe12dd7be43fffdbbee17d89f3d76eff634d18146c3c8db0f029` |
| `세션_재계산/band_boxes/compare_record_out.txt` | `f9a45d11b8f11a16b3cfd9ed9ad1cf55b79e367c6a4982bad327719f3d553b51` |
| `세션_재계산/band_boxes/log_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.txt` | `a4437c7c058f9c1504899ec8860e09e40f4642784561b89650a67c48a300b271` |
| `세션_재계산/band_boxes/log_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.txt` | `677aa3c6c393588b38b360008ad6f3eeb1384298474be4b1ea1438f920b3620d` |
| `세션_재계산/band_boxes/log_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.txt` | `30762e597981c26528bb6df7bce1e666b0da7adfe740fdc97be688008d953f7c` |
| `세션_재계산/band_boxes/log_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.txt` | `7596c0f6701a19ce45423ae9b4ea6817609f0786fe1510897fdfb913b8a5730c` |
| `세션_재계산/band_boxes/run_all.sh` | `a748478f59a4bdb2a9bb8051e1061a83f26ac79513e05826299e7e13b8eb6f53` |
| `세션_재계산/band_boxes/tail_H_T12-25_k6668.txt` | `7b2f89bf1a5913fe487c789fb95ea0ef0c8b6cfd621b7108a8b5fa45d5414561` |
| `세션_재계산/bprime_boxes/box_RK1.04_RNU1.03_k6668_NY6000_p0.json` | `9d6873beedbdf169cfffa19a13bbca50863a082b9ad4c0b0ebe30383b7ebfc9b` |
| `세션_재계산/bprime_boxes/box_RK1.04_RNU1.03_k6668_NY6000_p1.json` | `67940a992a45e15bf99f37eb3ae1a16d3cea589d1a12896e2ab4844c4bafe187` |
| `세션_재계산/bprime_boxes/bprime_iv.py` | `237f30150a1929a5e3f7e9fe089f6fcd17bb50cd01047922baac15b10cbc8b40` |
| `세션_재계산/bprime_boxes/bprime_result.txt` | `0ee3eba4c5c5aeaf7f6385a23ac54d5fe62794246834e3c39c917b48c42487dd` |
| `세션_재계산/bprime_boxes/bprime_summary.py` | `1cd220a876a459ba61998a7ea4bcaa7309d9cd48e91290c69cb1c965bdf7f765` |
| `세션_재계산/bprime_boxes/checks_out.txt` | `ce8ca8ac06a9a317fd153dc1ac958b1dee9b92b4f760d800937c257dbe3155ac` |
| `세션_재계산/bprime_boxes/compare_record.py` | `63414855843f3af7d5394ee79239b4285ce7023b5bd0d18b1c4b3805fe81149c` |
| `세션_재계산/bprime_boxes/compare_record_out.txt` | `f1f06265dde986b1fb85d1410c45eea5d4c265552fd84d9e21cacb499f53164e` |
| `세션_재계산/bprime_boxes/ivbox_lib.py` | `be4fd555118b17a998788b6484b31252a705c6aba29b97716ba5604776674b0f` |
| `세션_재계산/bprime_boxes/log_box_RK1.04_RNU1.03_k6668_NY6000_p0.txt` | `47728e7e4b32ba8248d3ec32de5eeac73ef006f6d0d14fbd5094f1ea03b75a4d` |
| `세션_재계산/bprime_boxes/log_box_RK1.04_RNU1.03_k6668_NY6000_p1.txt` | `406ef8ca6f2b539cc8ba801ae061565b06dce6575117a4daabc64f19a2037d92` |
| `세션_재계산/bprime_boxes/run_p0.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `세션_재계산/bprime_boxes/run_p1.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `세션_재계산/bprime_boxes/tail_out.txt` | `b6ed31a30099cbc7ad655303a5e9438a627997931d21dd89ecd3c9c99044e11d` |
| `세션_재계산/bprime_boxes/test_lib.py` | `8876e988d63f5aa3a46f765fb26977dc4e77fd661aaa21e87506989644161b33` |
| `세션_재계산/window_mass_env/cert_Cb_iv.py` | `104db0e9f3656c06f93b8140fb74ff7a3cc30df03af39790da6326a380020c23` |
| `세션_재계산/window_mass_env/cert_Cb_iv_out_1_2280.txt` | `722ba85fe918fe3374644b046f29fa86ec41f21224d538876190d0f672a76862` |
| `세션_재계산/window_mass_env/cert_Cb_iv_out_2280_3000.txt` | `abbf5befcc90d2fa84e72716de0b15fe8b9acec421c2f69d74d8d9391e9f2267` |
| `세션_재계산/window_mass_env/cert_Cb_iv_result_1_2280.json` | `acfcbbf03dff637b3ef0465ccabef28135d7d4f8b75838f4d8611e66b82a74e4` |
| `세션_재계산/window_mass_env/cert_Cb_iv_result_2280_3000.json` | `116247dc865033f243d3688ec8f1de81e4c95098541f17e44d825b392a90dc6f` |
| `세션_재계산/window_mass_env/cert_interval_iv.py` | `a601cab38fde402bf2d9457f4dd9fdd3dd5a92ea499511477fd0e5e639ea75e3` |
| `세션_재계산/window_mass_env/cert_interval_iv_out.txt` | `873a8e1e388b509f763983268b35b1414c8d5b7f3da82b6e869807fbc0caa26b` |
| `세션_재계산/window_mass_env/cert_interval_iv_result.json` | `519b3951942ab1b8fda8d3d368857165d5e50ce9129100375ef29e64e90bc26e` |
| `세션_재계산/window_mass_env/check_table_iv.py` | `8a85b39263b8c2b24eee4450cf6d53d6649820cc024ce97dc4113d234610718f` |
| `세션_재계산/window_mass_env/check_table_iv_out.txt` | `88f1e13d97e36f98fa99d6f3166f13757148c895642da7a888b6cdf73039a690` |
| `세션_재계산/window_mass_env/ia.py` | `8106bd07c5706bf495c74d03b6a6df3a8b0459f10491679bfcc037d1ef90f17c` |
| `세션_재계산/window_mass_env/summarize.py` | `19b7a064b313e8ff3897b32531baa1ba7a44a962a76a134dbeef072e2c95dc49` |
| `세션_재계산/window_mass_env/summarize_out.txt` | `0cac74a6c6282c86a3b3f350d310ad219a143c626683e61297f338a5d9c62d72` |
| `세션_재계산/window_mass_env/test_ia.py` | `dc529b08b7502d3ef78e619d6663ec85ab89ec26c5228b3c79edc8fd500563ce` |
| `세션_재계산/H_star_plus/hplus_interval.py` | `4e78a27222ab9726e259f208ab159d93c75d55f913e334d4a2d8b127708e9fe7` |
| `세션_재계산/H_star_plus/hplus_interval_out.txt` | `496209aa3430dbe3719ba2260c598859dad1171f792905b2d9cf3f85a872a48c` |
| `세션_재계산/Q_fin_1130/extract_inputs.py` | `5ced9bc4e597d91082af655b40d2f2b1a5ff73e2d9f38a048ae6ad7a92a28de9` |
| `세션_재계산/Q_fin_1130/extract_inputs_out.txt` | `ef67481321fad83da17b4dcca5bdc84e0704224c9847e67b82db12dbef384ca7` |
| `세션_재계산/Q_fin_1130/qfin_iv.py` | `ca1aa8aa4b4ba76d99bd64a6acddc4c09165a9266351b8c50edd00096e26d5a0` |
| `세션_재계산/Q_fin_1130/qfin_iv_out_p0.txt` | `a8624f3a687c0e2e51cebc4322bd08646278f7e9866173949c5842833a147d79` |
| `세션_재계산/Q_fin_1130/qfin_iv_out_p1.txt` | `396314a2ce9f8201185d1889df79faf8e5c1f104d8b13c0cdd4199613a4a9fde` |
| `세션_재계산/Q_fin_1130/qfin_iv_result_p0.jsonl` | `1ffb268f82ecfad65d73810a7967d2af20e0f76e329e06e6d7cb89ea4c8da568` |
| `세션_재계산/Q_fin_1130/qfin_iv_result_p1.jsonl` | `e0f3232bd302a3ec071363679b366dfc9298a79e0fdbc9af8f08ee2bb81edb70` |
| `세션_재계산/Q_fin_1130/summarize.py` | `162882100520df99428cb9d351a17bc290941198d57c5f3d57e0ab9c3bcb1a8d` |
| `세션_재계산/Q_fin_1130/summarize_out.txt` | `ae10455f3c62c4eb8ccc16f3a4c8ccb7816a102b842ed93de66074039f5f7723` |
| `세션_재계산/Q_fin_1130/test_small.py` | `4c7b72cc5ce1a163c72d96075355bf119de09d107247b5af8ba10dcf877adf17` |
| `세션_재계산/Q_fin_1130/test_small_out.txt` | `f5f949a6941a792430bd747b650e016e54a74c0dbdac2b9064d20f8b37da5cea` |
| `세션_재계산/Q_fin_1130/xcert_rows_2001_3131.json` | `c79594d2b03b8daa1e47de49ae54992db85e377b31473406d63a34200d3de32e` |
| `세션_재계산/band_check/band_cells.py` | `0864f8d34eb2c00b60e1278dfc7f662340ba996173418bcf59fbb8a3fa380985` |
| `세션_재계산/band_check/band_iv.py` | `25b17b01d7f84d53f7f92d8f463e68e5113a2a0c08a1448bd6f34225d41ee208` |
| `세션_재계산/band_check/band_read.py` | `c4d63ac936dc6d75628769ae92ef4f04f947be180622b21042d11028675ef984` |
| `세션_재계산/m1_column_reading/m1_read.py` | `915bd7ef3e5910bb20fc0e2eb0bbd66dfa64d82e9fb5b9b746492fbf8f5d50db` |
| `세션_재계산/m1_column_reading/m1_read_out.txt` | `dbd586374bd49bb48b3fe16119746db7ad265762f6ff76439bc9056d0cb57085` |
| `세션_재계산/r89eb039_polar_block_audit/block_vs_truth_9843156.py` | `b02a52d8b79a178c0facd7b03d403f99de98621782a4066939647f295a1aa852` |
| `세션_재계산/r89eb039_polar_block_audit/bvt_block_9843156_10000000.json` | `e618da4713a3d1e8e8394493d27d4b04b7e76cfd8010cddab18fe95732b52930` |
| `세션_재계산/r89eb039_polar_block_audit/bvt_block_9843156_10000000.txt` | `cddc8eccf2d6bcf02390a28260fee98a6b313a2756a1660359e8ce3b115311a3` |
| `세션_재계산/r89eb039_polar_block_audit/make_table.py` | `af3ef2de4cba425e718f45e0f48fb3f205ad6e786d2be75d174bf26fbfadb806` |
| `세션_재계산/r89eb039_polar_block_audit/truth_accuracy_check.json` | `4e9237e30aa28ba0463a5209785a329bbe7b01f1f7b7b2adb82b6e59fa62bd20` |
| `세션_재계산/r89eb039_polar_block_audit/truth_accuracy_check.py` | `1835444c79b756dccf41ce1551bbf626f3d02b5a4a9eb679de8c0e6600ae7480` |
| `세션_재계산/cumulative_logconcavity_n779/lca_exact.py` | `13d00831881643e66c464c4197f7a2f9489f149be0cd7b37014207777b6ec0d9` |
| `세션_재계산/cumulative_logconcavity_n779/lca_exact_N800.txt` | `d12b698a93cee1345cd6c26c6292a761c14030fd12fb88f43a3b2241fda30ec4` |
| `세션_재계산/cumulative_logconcavity_n779/lca_violations_N800.json` | `72001e4e4ec380498c04347f2175685c072e19d31069c76d91a185d53dc5fa00` |
| `세션_재계산/cumulative_logconcavity_n779/part1.json` | `4002a5e0dd8a4fe4bb998216aa1ccaf73df354e3f8ab2ca3fafd5cc73c9284e6` |
| `세션_재계산/cumulative_logconcavity_n779/part2.json` | `188cd255342443338fadc006784bd1422d47c5d94513057a19681bbae83e5985` |
| `세션_재계산/fiber_exhaustive/fiber_exhaustive.py` | `b382c77047196f88112eaa90efd445fe4036ee98a02b77dfcc66e97097863512` |
| `세션_재계산/fiber_exhaustive/fiber_exhaustive.txt` | `b2122579d4b3682d1e8ce794d6ae929a16960397f8ebd91d50dedf2f7b9647f5` |
| `세션_재계산/newton_r61_169/newton_cert.py` | `7a2f19ffafc65a876dd6b96909a521613a23531ed2099fb04470c8a23c9ab36d` |
| `세션_재계산/newton_r61_169/newton_cert_out.txt` | `4405ae71a11d1c890fab995115fac369011ca08fad2d893ea889b6fb08084ee2` |
| `세션_재계산/c50_iv/build.bat` | `de492d8699aef9d2b90f941ae077f2c7489b95d49b39ac51ec8d4ced0e9a1cba` |
| `세션_재계산/c50_iv/build_out.txt` | `450ab1d7ed87832c68a92354df14c6e3e7bf7440f5232b8a2b503e68624ef6f4` |
| `세션_재계산/c50_iv/c50iv.c` | `e25aed64200cba23dc7661b65812ed4cd4c9a905d95c5ae3b09d69be117074b8` |
| `세션_재계산/c50_iv/exact_small.py` | `ed6d94dfd4a4c0507d5068f0d9f187dd983704cb7a8bdb6b1f57552cf74a2c16` |
| `세션_재계산/c50_iv/make_tables_iv.py` | `782b260ee88fb111daeab31083de09e677a41d35a1912497b33aa1aee5fb5cc7` |
| `세션_재계산/c50_iv/make_tables_iv_out.txt` | `88fecdb52f75f7da74d4bde3ee5fc8427d60405636abb2c3a734d0bbf0c9282e` |
| `세션_재계산/c50_iv/postprocess_iv.py` | `09f6c92c576c0db2792ef47a129f6f0efaf3f7f3724846f7d28b893e95942dc8` |
| `세션_재계산/c50_iv/probe_undercount.py` | `4e200de95a2d3ca18a4f687b311ef38735373ae24c1723bcff155982692683e5` |
| `세션_재계산/c50_iv/run_commands.txt` | `4351b54af9d3c028e02efefd042e4e97e0ee5ada18c1f07635dfb442e1933ef4` |
| `세션_재계산/c50_iv/runs/c20_post.json` | `1e3b24a8a5fa7496fca176420282d125151aef02a0ecbbc844d840d70aa66ca3` |
| `세션_재계산/c50_iv/runs/c20_probeA_summary.json` | `5ef6f13c86ca658ca60bb3858810da7969448d55deff8e286dbfc5d0ecdbf4c5` |
| `세션_재계산/c50_iv/runs/c20_probeA_undercount.txt` | `c532bb69b71cb0b3b925f125e2a91b8c0253eb63827233fa3cc4f28ad78d2b30` |
| `세션_재계산/c50_iv/runs/c20_probeB_summary.json` | `531395762518c60672400e122d566a2d2e3b9332ffa4569d206696c588fbb1bb` |
| `세션_재계산/c50_iv/runs/c20_probeB_undercount.txt` | `b7003470e0c38710327ee93858ae670f6a5906e4b12b83530509689bdd31255c` |
| `세션_재계산/c50_iv/runs/c20_probeC_summary.json` | `b319cca9ee5778457e8919bfd1de4ff8eb2ad8c386c56338929dc8efdba91856` |
| `세션_재계산/c50_iv/runs/c20_probeC_undercount.txt` | `00aa7cab5eca753af6155a9da8fd9fd5adb48c5ff61c41c908c937724cba8d2b` |
| `세션_재계산/c50_iv/runs/c20_stdout.txt` | `418a5c17f33c70e99b0cc0a07fce69191489cfedc94164bfa903785777c5bd4b` |
| `세션_재계산/c50_iv/runs/c20_summary.json` | `67593e8f6e63a4ff1fe2b2ff56d3f13ecfc937e0b5d94f571a567d6b29da887d` |
| `세션_재계산/c50_iv/runs/c50_post.json` | `b2d65ba1c71312c5a3a65c9a1c0e800294516b758f3c2cee7dfc59eb86bd371e` |
| `세션_재계산/c50_iv/runs/c50_probeA_summary.json` | `fd28f73049cf00c7889d8e1977e8de9b932f6e85621792c9287fa2bfef8d1d7c` |
| `세션_재계산/c50_iv/runs/c50_probeA_undercount.txt` | `387ef164201f0c7efc8bfe78f28b04a571085c50629124f1154a77c6019229cf` |
| `세션_재계산/c50_iv/runs/c50_probeB_summary.json` | `0f0bbf98b2594f9ebecb113f73af937c1ea3a057cb44d908750bf938889aa346` |
| `세션_재계산/c50_iv/runs/c50_probeB_undercount.txt` | `8663adc2fbcfa7343b747a4be6d559d47bb4b3e81499d3a8541cd6ff52c21228` |
| `세션_재계산/c50_iv/runs/c50_probeC_summary.json` | `ac73ec620de95a2b9d27589f8331ea46b8933472992ec6285a3eed15bf2ec318` |
| `세션_재계산/c50_iv/runs/c50_probeC_undercount.txt` | `30cced33aca465d0a67717beca7e6d1ecc5e74607a745ad26cd64fa869b67ef1` |
| `세션_재계산/c50_iv/runs/c50_probeD_summary.json` | `4226a06fde9795df9ec9fc36f68f6a9fdfdb656caa3c44853a279ac9a92dcf7d` |
| `세션_재계산/c50_iv/runs/c50_probeD_undercount.txt` | `502dc37947873a715d01a766a3a147a80d0ea8d395663136a0cfcd9f2bbf2bd4` |
| `세션_재계산/c50_iv/runs/c50_stdout.txt` | `418a5c17f33c70e99b0cc0a07fce69191489cfedc94164bfa903785777c5bd4b` |
| `세션_재계산/c50_iv/runs/c50_summary.json` | `80b57e6f3781e9426dec8e56a00cec1c39fbcf578c1da2f160e7b7d5098ec492` |
| `세션_재계산/c50_iv/runs/t300_exact_check.txt` | `8afc61e39ba297c83dcc22a6b0c29da54195510a31e2d4d39597361b51b2b410` |
| `세션_재계산/c50_iv/runs/t300_summary.json` | `12460e835f01ad0bf0289cf9fec2bc5c8b972fb8f032cb3b65c2dfe3cd867da1` |
| `세션_재계산/c50_iv/runs/t60_exact_check.txt` | `aaf22789257be43061fd2d4e67038aaec090742e6c54c21e8fd9c9dd06dc1152` |
| `세션_재계산/c50_iv/runs/t60_summary.json` | `0ebca30c47dd217e6d6d84be052b93e7244f1eaccbb8d4b4100020258fe05ba8` |
| `세션_재계산/c50_iv/runs/t60_undercount_check.txt` | `566adbf4346b4d4161da4e8714f2b8aa5a2c1157e2e82352c9d7539e4d716652` |
| `세션_재계산/c50_iv/tables_iv_manifest.json` | `d259d66dba53629306556fa605bee235be86bf59e617bcfbafcaa6f366d0a167` |
| `세션_재계산/band_LP/elem_check.py` | `2c506d24aa48b0c714380ff9d100c2b94a5a33ee7c9c3c318a839909b725f978` |
| `세션_재계산/band_LP/elem_check_out.txt` | `88d8302f3a4261678e39dc4e935d7fc453e23eb087c201f3e4f86098bd1a4ad9` |
| `세션_재계산/band_LP/out_ra_20001_29500.txt` | `db5515bb2bfdc8ce4d989d1c49c86320a5685b52111ada2e247c7d41ebf49e78` |
| `세션_재계산/band_LP/out_ra_29501_38886.txt` | `c352d21193481befc1f62ad71d5a43571baf9d8fac80c1f2a2f5eb3bb45b2ebb` |
| `세션_재계산/band_LP/out_ra_9467_20000.txt` | `a2f7d4b077cf21e6d2add54f0d76a318186ff518eab3953763436674854f630f` |
| `세션_재계산/r89eb039_polar_iv/achain_iv.py` | `af1c9c76d661403cc4d5587ddb20649a110b2472448ddc356661bcf7e192d7b9` |
| `세션_재계산/r89eb039_polar_iv/bounds_ia.py` | `e0c4faa5503031a06c0f038d55624cd4c0e723a967e1e6aec6aa5829f726ef56` |
| `세션_재계산/r89eb039_polar_iv/cert_fast.py` | `162abb87636abda055a3ce884fbf8817c208c2af5db9eedbb81ec6900d66820d` |
| `세션_재계산/r89eb039_polar_iv/cert_ia.py` | `b37721b74f2996f39363ee50195ac0346faa5ac15a685536c432f2fcd5e91de5` |
| `세션_재계산/r89eb039_polar_iv/cert_ia2.py` | `09c4d0ef3ddfd5f132eb7885c4984b54fff333621e6a50cef8473017ef047653` |
| `세션_재계산/r89eb039_polar_iv/check_L.py` | `bea0f9bd17917b2babac49c51588c44ce28418f9c6f3a821ace41b3212922722` |
| `세션_재계산/r89eb039_polar_iv/check_cover.py` | `b9be129b37a6ca36ed4a450de702fdf0c9c6df49531b60180d41b9c002098860` |
| `세션_재계산/r89eb039_polar_iv/compose_draft.py` | `cc612eebb02d07c151bd56f238030ce46045432e7e539819985be3eee2380006` |
| `세션_재계산/r89eb039_polar_iv/consts_check.py` | `ef4885c4ab2ee210fd9e728495c234bff71b5e5a48011c36319b752dcc759048` |
| `세션_재계산/r89eb039_polar_iv/ctx_fast.py` | `e39f26298ef0f27e7955b2a51462fe9181cac247e327f2b250b578a7138e9a8c` |
| `세션_재계산/r89eb039_polar_iv/ia.py` | `b3af342b149b2417c05773f615cbea3ea4cba0f5108ebb04a0fc2a1d4e892ce4` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_adaptive_2087_5000_w0.jsonl` | `fb443168bb7df0a856fd8b4a0c83caa79ecf19464578716e84b9c2558906eb25` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_adaptive_2087_5000_w1.jsonl` | `4fff6fd96f9cb3a87bc8ab13887c17685af4ec3ea0865346fd34fcb09d40a61d` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_adaptive_2087_5000_w2.jsonl` | `ac14cd5e6a08bb0ee8080ee04b8584e35b0c008a651b0913bbf1215d235e2e8e` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_blocks_merged.jsonl` | `0eca819dce5a688d9032ab475e59ba059a12a25c16e34529d516326bfd75c43d` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P1_w0.jsonl` | `1f428d53305ef4110d29125786d78cd58256de1d9e3ee0fb3cd9e12f2919352d` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P1_w1.jsonl` | `762e6b014eac5f4d321ce8131108a622d9cf9d83f11dbeaff18eb1c1e52036f6` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P1_w2.jsonl` | `800356ab20821165a4dcc591ea937e4b4984f75374512518bcd81bdeea1f28ec` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P2_w0.jsonl` | `8d1bd3a0445b90255db8ab92298f144df1cf629eeda2f83ddcb7689a88c859cf` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P2_w1.jsonl` | `7dd83ffa38506e6aec76315812346e9c7bb02de826ac8e646186fb56665dfc2b` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P2_w2.jsonl` | `b241a5e1f9ba1dc3aa4abd12554ba7873aac690b698d9f515ac477e8e91a44fd` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P3_w0.jsonl` | `b4d6e2ef704d7c1689bfe0d19b01f8b54693702a4c5c1c89c2e061f7557f74d2` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P3_w1.jsonl` | `e068a42801a4adafe9e0a580b786305526582337a7f65d54736c6df283c63b77` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P3_w2.jsonl` | `c685fef637728d8dc853a38b7d9edea23927237ad435b6baf94f015261f30c1f` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P4a_w0.jsonl` | `f48d2b730f0e30946d5988440f303f9a235d993794a0ed730899909ff431a619` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P4a_w1.jsonl` | `9b5e8c761c257b0c05ea5ec62c1b557374bea7644e385bde268fb11543f5689e` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P4a_w2.jsonl` | `043a9d79e716134af6bafe3bc19a4ea1f3ae1f9975d8216bb97648d3ffbb5582` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P4b_w0.jsonl` | `33ed263b2df1daf35d918e8785e84eeeaf3fe7704598fd42cd4c7daaf205cdf7` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P4b_w1.jsonl` | `3dfabeaa90d6f334aa6aeb0df77692abf972c879daff5601a242e000a5355ce8` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_P4b_w2.jsonl` | `546a581c0eaa443e052df766c71cf2564e9a3f26251e23c421fc28dd76609e7b` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_Q1_w0.jsonl` | `7ae1a82f578af68aa2135ab6d9b0ad2836ff714f2e2e51940a75fb5d7ecb778f` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_Q1_w1.jsonl` | `bbc1300acb63ee97c755bdeb81befa2dd048cb00f0ff3e83a42c6fc0881e46b8` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_Q1_w2.jsonl` | `d1cade721ebc7feeb4f77053830124c1d829e7569ea06958b08cf1946cfb3b45` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_Q2_w0.jsonl` | `fd4cc830662359d868d4394d0d07443c778fea4ff50a279167a72d9c14c00954` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_Q2_w1.jsonl` | `0fc6077756107f03119f61ae7e1cf27377ea7652909d71974cec4911afccfed6` |
| `세션_재계산/r89eb039_polar_iv/out/NEW_recert_Q2_w2.jsonl` | `1b53f9fc0781b82292bada5aa2f408b120254d40b1b9900f8daca90db0862ac2` |
| `세션_재계산/r89eb039_polar_iv/out/achain_iv.jsonl` | `e37ca752511456a2c67084b66b3335d203c7d79bcba64011febb20941a5e8a8f` |
| `세션_재계산/r89eb039_polar_iv/out/achain_iv.log` | `d8587d3deddd849864f3c449e372c570d0b235e61728a95a6f6f010a5f652736` |
| `세션_재계산/r89eb039_polar_iv/out/check_L_2061.txt` | `57420228cc5645fb90e4ce4c182d287e69d55861ae2ee6ba2a09169c28e64324` |
| `세션_재계산/r89eb039_polar_iv/out/check_L_7459875.txt` | `8003af7a27520c3f877c5998bd106dd14c95fee219ccf781551f3d43bfae3730` |
| `세션_재계산/r89eb039_polar_iv/out/consts_check.txt` | `8384356bba9d3779441af8da2e3f945d648ff547816e3c96d1e7e73d8cd3a7e7` |
| `세션_재계산/r89eb039_polar_iv/out/run_w0.log` | `e0104790a82de616b7edb51bfbbbca2b1eca533db26426d0f8a19fd4e9485483` |
| `세션_재계산/r89eb039_polar_iv/out/run_w1.log` | `debdf0bcabb72ada9bfedcaa012d1426bda2cc0c8b99671e904d6869ecec9bb3` |
| `세션_재계산/r89eb039_polar_iv/out/run_w2.log` | `7dc970b72c29cf1b94a691f2b76477ef69402e492d38586a625e46f36728a7f5` |
| `세션_재계산/r89eb039_polar_iv/out/summary.txt` | `6548046765ff1274eea93c35c99edced430dbf425122cdacb465ac866a3517ee` |
| `세션_재계산/r89eb039_polar_iv/out/test_ia.txt` | `fb4b46860aa9fba58bbfd94260cc03d1c990e7f05e58f42811b90fc0eb2f673a` |
| `세션_재계산/r89eb039_polar_iv/prof_orig.py` | `3903d30691de1a27e9809afdacaa93740ac5fc6e1d3f812933ad28d967bd5442` |
| `세션_재계산/r89eb039_polar_iv/recert.py` | `e0438538c8f21e8481ec78072c222ef04d7e73562a9339677035685af0574a60` |
| `세션_재계산/r89eb039_polar_iv/run_worker.sh` | `f1232cc50fb4a3ea940511bade185c03e0d9f3e867ed087187e0e243a770d9d6` |
| `세션_재계산/r89eb039_polar_iv/sparts.py` | `9dac0f9b723ead7f87d92265033377977d5c27e22351661b07f7a1d3df1951f7` |
| `세션_재계산/r89eb039_polar_iv/summarize.py` | `2bec4d0dad391f1e98c30840c7f73a7afb380740d934ea5d9b06c001a0583b70` |
| `세션_재계산/r89eb039_polar_iv/test_ia.py` | `97a81b0a5c54e60f626cfd026106127d862524d550a0371b1944eb4e6a6d6e98` |
| `세션_재계산/logconcavity_n80/lc_n80.py` | `0a195b472044a2468db2dfe897d070a079dcc9ef6c3167146e8442c5fa30b4a8` |
| `세션_재계산/logconcavity_n80/lc_n80_out.txt` | `61b9b0d36d942991838d9a261fe3fc2ba0be8f050a024e4a822dbe3b87726c14` |
| `세션_재계산/r030ffae_window/work/cert_Cb_range.py` | `68dce8b869b3ce49e16dced0002386be4900a6681eb72b4f1f97f56d46adbef3` |
| `세션_재계산/column_cert_iv/colcert_iv.py` | `5bc23e7bf941e60bb6c4eed62559473a42690aeb59bbbc63b8c52372ed543881` |
| `세션_재계산/column_cert_iv/ivlib.py` | `5c9f30bbc004eb9e56d07663894a5356204838ced166914bc45d2f6aa333a5f3` |
| `세션_재계산/column_cert_iv/tables.py` | `9e014f10d9ea4899ead55b5dd3cc50bb9e9e243a6d51a7344048bdcd69772dc7` |
| `세션_재계산/column_cert_iv/summary.py` | `5129283318f12484b9d7696ff4ddebf69fffd783c4d15a0109245988c1fdb8eb` |
| `세션_재계산/column_cert_iv/crosscheck_review.py` | `784fa08ff11e3eb258298449c1fb770095fae43276deb8f490066339a67ef6af` |
| `세션_재계산/column_cert_iv/make_draft.py` | `f6c77e83b9d545eea098672c90f1a592d05bc826bad4e3b1459b1923416b346f` |
| `세션_재계산/column_cert_iv/res_p0.jsonl` | `df0d5749ca95171f5db9f1a0010428d2cbb60482914776160279161c03e38a1b` |
| `세션_재계산/column_cert_iv/res_p1.jsonl` | `1a6ba31733bf2139725cc36ad8e367d26735d5ab1406de2f58645904bb5b3994` |
| `세션_재계산/column_cert_iv/res_ext_p0.jsonl` | `0d6d856230ef89adbdb378150c4d17d958466c195133f427514a55241ba499c7` |
| `세션_재계산/column_cert_iv/res_ext_p1.jsonl` | `f31f4569fafd83670af8dde60d7f10f0ebfff46761755e3a0248b9ba9feaeae0` |
| `세션_재계산/column_cert_iv/run_p0.log` | `5da97ac726ef84e9e66ebd9650b19e48f076127455c121912d62c192b5643542` |
| `세션_재계산/column_cert_iv/run_p1.log` | `13b159db96587a671e72b7152477c5efa2e338c1434c4b643a049688a1097a02` |
| `세션_재계산/column_cert_iv/run_ext_p0.log` | `9c85b4aae98ccd2a69019e840fc2181508fe68f27771b876f7e487c4cf34771f` |
| `세션_재계산/column_cert_iv/run_ext_p1.log` | `f8c7ef3cd8b9d1f7db4d156442259fdf9011e9486fb841b688e5d2580b4082c2` |
| `세션_재계산/column_cert_iv/summary_all_out.txt` | `c46e5455597daa6a76e7313ed90df550c43bb23591a0abb10733525639b5e7c1` |
| `세션_재계산/column_cert_iv/summary_out.txt` | `bb6dc91dcd01a4077de3e76cf51920671018b322a7d81497dd3b64ecb0c60863` |
| `세션_재계산/column_cert_iv/summary_ext_out.txt` | `5c09391b783ceea89fb6e2b8f1824de0b4df2fd9fc3a62facc4f888b9a97d3a0` |
| `세션_재계산/column_cert_iv/crosscheck_review_out.txt` | `44dcd354db92ffafb55ab97d67e2df4b00ab08053d17c84986f689bf447c2d69` |
| `세션_재계산/column_cert_iv/test_841.txt` | `bca53097a04768fce3ea515717f5e15fd314eafd37a77a4a8e828634b7b5f4a3` |
| `세션_재계산/column_cert_iv/test_1171.txt` | `76c6453d4a61251761ef54c0c0b0fd8d0dc31dea56b6c8d2d64ecfacda07c005` |
| `세션_재계산/column_cert_iv/test_2000.txt` | `fd74ac0d9a5c80ba079577bae41ea3dea7625cbed1f7bb236428f0249a1828dd` |
| `세션_재계산/column_cert_iv/tables_out.txt` | `a1222153291283b5b42e11d27d24bdef15d059df12f678c25361392c7c99f788` |
| `세션_재계산/moment_cert_iv/mcert_iv.py` | `4a8796d8a96c2cf557936e3a1788868a6a630bd8e10c7ce85117892d8fcbf64a` |
| `세션_재계산/moment_cert_iv/make_draft.py` | `940d63a303d516a8e9d5c9ca94c14233f60993daaa9ba3187d0f7698af131463` |
| `세션_재계산/moment_cert_iv/sweep_p0.jsonl` | `77143d1b5c102f43a4c8cb2ce207f17597779ba8b285fc652fe71b0fb6527009` |
| `세션_재계산/moment_cert_iv/sweep_p1.jsonl` | `6699672ff30a00402b2134e2931bf6cd0fd10c991205e97ce647347978c4c949` |
| `세션_재계산/moment_cert_iv/sweep_p0.log` | `31565069b7a4e3f938ce1b3d61e2abf29ba5fdabd312cb707d5e0609f99ef065` |
| `세션_재계산/moment_cert_iv/sweep_p1.log` | `aaf350cc69326d4e2590fcbe3bddc26ee80e35f0117dd3a254e51a8e7a581bb7` |
| `세션_재계산/moment_cert_iv/summarize.py` | `1a4b8d45a3536dbf9da3fd12dca831c4b3c91acd16e4e1a3e887a94827cd4f10` |
| `세션_재계산/moment_cert_iv/summary.txt` | `268e0670664859cb3ab376324c06b2fff4f02df3cc2b44d93a7513aa16031666` |
| `세션_재계산/moment_cert_iv/compare.py` | `0eae727bab12cdbabe881c87d313427d864771b93a566060294efb5668a2694f` |
| `세션_재계산/moment_cert_iv/compare_out.txt` | `9fe4f33b71d131184ee51ccc33c508443e2505247ae13cdff5d0d060ca41e1e0` |
| `세션_재계산/moment_cert_iv/compare_out.json` | `9b5f64ba6c3c05d783857abff1e15570139a1fabee62b2ac91e1ccb350485cd2` |
| `세션_재계산/moment_cert_iv/test_exact.py` | `a7a2f734df7fdd1bed517becae90b5abba7235fec162a8d4f9a5ad968d142b1d` |
| `세션_재계산/moment_cert_iv/test_exact_out.txt` | `4a947810edafd3f9342acf815ce10b5a9023af694e3277ad12f13d563af77cc3` |
| `세션_재계산/moment_cert_iv/nM.py` | `8bfadc59da7fad9439385949aec22a0eaa4f59232c426928b659de0fc70ac93b` |
| `세션_재계산/moment_cert_iv/nM.json` | `51b38b5eca6deb47f61dabd342c94617fce720c90ceb6efa99f260b3a0a9515a` |
| `세션_재계산/moment_cert_iv/nM_out.txt` | `464a26d0caa84b1849ce6ccb658cf8f695d6af2a5ec122a8839b073646638ad4` |
| `세션_재계산/band_check/band_iv_out_CE0.txt` | `3adfbb90df3050c60e6471cc2e81c7ed898fec78a9240c0715d6ea33bf648321` |
| `세션_재계산/band_check/band_cells_CE0.tsv` | `e1de404359992ea644ab9ae243fb9b44bf162680df6085eefa11c8258d83c167` |
| `세션_재계산/band_check/band_read_out_CE0.txt` | `523e47b33a29b31a56bef38389deb18f89e7b66b4c781b593c1442149e3354fa` |
| `세션_재계산/column_k500_iv/lastcar_iv.py` | `e2b558106af08139f4851420b827a800872ba2fbbad39d7992459088fdd3637a` |
| `세션_재계산/column_k500_iv/colk500.py` | `13f53c69fefd9857847948b3d786080dc07d7b57cfe0cd325a4ee37867421bd1` |
| `세션_재계산/column_k500_iv/summarize.py` | `ea41be63931caed1e6f164a4f223d16ade8b3b335b682dd99d595d6f97210ad9` |
| `세션_재계산/column_k500_iv/summary_out.txt` | `a40663abc0a1caff96a207bef42eeb3aa3d3432b26def0420fec01c204d61a20` |
| `세션_재계산/column_k500_iv/compare_indep.py` | `c28d78e7e6a61dd5c4c7a06a01a35026e8cfaad75c9aee09e5e4429c67aa0a7f` |
| `세션_재계산/column_k500_iv/compare_indep_out.txt` | `cc3f5176172249dc5dbbb78f0a327e76f5e34007b4820dd22319708ae021acf7` |
| `세션_재계산/column_k500_iv/test_small.py` | `a8c38e52c2468eb842af56623d47cd6e7308a5d725ee3d3bd7e5ce632d922383` |
| `세션_재계산/column_k500_iv/test_small_out.txt` | `f025390ee4a8c6092f9128ef42825accad43eb0b000f9c6fb05ed3dbc2521c08` |
| `세션_재계산/column_k500_iv/run_w0.log` | `2919a0c0d3044359fafba1387b1207e76e0697dd3c16409a03c12cbb6fb5c481` |
| `세션_재계산/column_k500_iv/run_w1.log` | `dd1d4c07898c915f4eb5d6f2a637a71b9320bc76185cf7d6f704a6bf3bc413c4` |
| `세션_재계산/column_k500_iv/make_draft.py` | `5e3d9b913316e256f43debc230d9f127a69e28ee04f56c4392ba10f50e95ef40` |
| `세션_재계산/column_k500_iv/res/SHA256SUMS.txt` | `e486caf213a5f5ad1004b32eee596866c614e17d343a2067ee0ab695bae4d9da` |
| `세션_재계산/xcert_iv/asym_iv.py` | `81f2b84b18e18c87cdf02a2fda34d90be47f640e4a92d8a562f5c82e33a68f7a` |
| `세션_재계산/xcert_iv/colcert_iv.py` | `6f8ca4674ffa20889c5a350a85099a01af0e3734aa344a76ff36651d4614dc27` |
| `세션_재계산/xcert_iv/common.py` | `d6ed4c6942e142827ba48663d60320f36cf615ed1c4134175a473bfb515ad6f7` |
| `세션_재계산/xcert_iv/crosscheck_fft.py` | `bdea44b893c71c2a49fb29f22dc0e489eb956812384b9d6476a63d624503d4b5` |
| `세션_재계산/xcert_iv/crosscheck_fft.txt` | `c53ef0c5f1bb302361c3283fc7e82cd4044c71ee3900a096ed49c4f33e60fbb6` |
| `세션_재계산/xcert_iv/ivlib.py` | `5c9f30bbc004eb9e56d07663894a5356204838ced166914bc45d2f6aa333a5f3` |
| `세션_재계산/xcert_iv/ivv.py` | `adb35a656236c2418914b5b3233693c0e5992dbb9b68b42ba2027703bd662a33` |
| `세션_재계산/xcert_iv/layerA1.py` | `ab4c95505150b52c7759a1dc54b0e2facff0d01a9b1d98644afa43c80b3952f8` |
| `세션_재계산/xcert_iv/layerA2.py` | `4b7d44af0eb02136f3d4609b0ee9a2a23b4b491c1e59c5938fc88a208148dfc0` |
| `세션_재계산/xcert_iv/layerA3.py` | `72644c000905edb56788be48e3bf226da5793bef2dcef6f100df1080712cfb4e` |
| `세션_재계산/xcert_iv/layerAint.py` | `dda4306e19a063feaa462148a52cc7e3862a5b859ce33da1f8f21c05b8d97cf8` |
| `세션_재계산/xcert_iv/layerB.py` | `aef49a162190bf5241d0f4ae7102cc19295d5a648fbf0e21fb38d4e54570cf6b` |
| `세션_재계산/xcert_iv/make_draft.py` | `ed3977d19e30e3ce43bbc2546daeddb733ed69fe547f39c7fc80d4fa7ee14318` |
| `세션_재계산/xcert_iv/midfft.py` | `5b1cab86b9a8edeb8a4ab5ee31e56c11e030cc702f9b9f7186d2ead9ffc1e138` |
| `세션_재계산/xcert_iv/resA1_p0.jsonl` | `c7507d7d739380f3f4ca6e87060d7a65b972a103c3152538e28948227c7f1ad5` |
| `세션_재계산/xcert_iv/resA1_p1.jsonl` | `c1448831f6c18b79065cb19d9f563b5d7711b8163d87ec80ddf1a476f3b1fbc3` |
| `세션_재계산/xcert_iv/resA1_p3.jsonl` | `7cf6853167975eecae151e679c457a03a314c542d00bc58acfabe28c2600215b` |
| `세션_재계산/xcert_iv/resA2.jsonl` | `6ec0e0ddfd97c765c5388acf465fd46d73cb67ddc856ebd17008091b3d0060eb` |
| `세션_재계산/xcert_iv/resA3.json` | `18b8335eca49c3d7b4d5861ded29efa4c2e6167d232bc81f01bb11785c38faef` |
| `세션_재계산/xcert_iv/resAint_p0.jsonl` | `c75616cb210fc2ddd1fccdc70c0799461b56cec9e69e5b89b94d804e07fb42b3` |
| `세션_재계산/xcert_iv/resAint_p1.jsonl` | `87111b32d0fa1a6f3eba76415c52fdab9d43fe424ffd83e8d2392a2eb4aaa113` |
| `세션_재계산/xcert_iv/resAint_p3.jsonl` | `13b9ddfcbc47d0a93634b0a5084edb77bb6cade533206eaba5d6e5a4d7fdef93` |
| `세션_재계산/xcert_iv/resB_p0.jsonl` | `1c6fa7c0780926d97d7de15061c1f7fad004862f60e781b468eccecfb40b2f67` |
| `세션_재계산/xcert_iv/resB_p1.jsonl` | `df856a595f173b3c050596592326ee98d260d98060c7ce381646be6c8e42775c` |
| `세션_재계산/xcert_iv/runA1_p0.log` | `f2d78330685ae7d75c7b8a096d0ac8f6ed717e8c28b1e71036bc587d11a45d6b` |
| `세션_재계산/xcert_iv/runA1_p1.log` | `eec0bafce28e0eb4011cfa043a390fddda7df52d5d8ec10ccdf130fd33f8d63d` |
| `세션_재계산/xcert_iv/runA1_p2.log` | `5f42d1d69fde27102d32a8f5c6274ad4d169f66079dbf6fa0e59b624d644b530` |
| `세션_재계산/xcert_iv/runA1_p3.log` | `3a7f1fce153530109651051b69d5a25a2a3793045fc07608a2e3f2f7a0a25ba8` |
| `세션_재계산/xcert_iv/runA2.log` | `249e6d4ca5ffdb68f9d85cd83f98e6aee9cb0bb98268efa2a35f6d289a75ec02` |
| `세션_재계산/xcert_iv/runAint_p0.log` | `8fa6edcecba6fb59dc2dda33c4e3b3d97619bbd53f0cfb4c4ba5476f59deaf9d` |
| `세션_재계산/xcert_iv/runAint_p1.log` | `9e7f8293df8c1831c59431988d24a9c6b15c05fdba5ca79187e1b952e600fccd` |
| `세션_재계산/xcert_iv/runAint_p2.log` | `0aa16f164f333bd88b0aafd585fdbd4fec2d008f314d22de6957cd0a37b8ee0d` |
| `세션_재계산/xcert_iv/runAint_p3.log` | `8d2c1e73d502c7da5ae060831c93df407e769273ed2a1c8c375150ff149eff59` |
| `세션_재계산/xcert_iv/runB_p0.log` | `9140c177669fadd467df35ecd41b58d87da952a2f8db23de2b37d7d07cf3778e` |
| `세션_재계산/xcert_iv/runB_p1.log` | `4f40764ad41204bb159d4f62b2a673cab0042841d4774acacc1b0573150ed7d7` |
| `세션_재계산/xcert_iv/run_slot1_after.sh` | `7430e7d2fda9bce2352d5aa642a9b42d7c1f972216c37a0d70ede5d69edd2d73` |
| `세션_재계산/xcert_iv/run_slot2.sh` | `607c65972bdb2d069b94c9ede39f9fba34f425cd49e5832f0465d3a1da16ddaa` |
| `세션_재계산/xcert_iv/summarize.py` | `1d654f24c1c6fd2a5e4a1f0322f5722c381bd4ebbde00461abb3f5f876d80b75` |
| `세션_재계산/xcert_iv/summary.json` | `840805aa83c8726afc0a8899722be65ef2f8ecad287ee93fd2404dbc87ac1e16` |
| `세션_재계산/xcert_iv/summary.txt` | `13f0527087d42babe387e31e3a002609ea8a2692fefd67d012baa70fa8ac1e91` |
| `세션_재계산/xcert_iv/tables.py` | `9e014f10d9ea4899ead55b5dd3cc50bb9e9e243a6d51a7344048bdcd69772dc7` |
| `세션_재계산/xcert_iv/tables_iv.py` | `6706900cb00857e094aa0176c1b75b1acc047520d20d31d8798574734782b676` |
| `세션_재계산/xcert_iv/testA1.txt` | `9693191074a5e56ef8e71681c38f705672821c605b505e0f9d310ff26a19de35` |
| `세션_재계산/xcert_iv/testA2.py` | `c1122e31bb769fd17cd0f02984b93820c66dc85ffb548cb2d59108896f96efbc` |
| `세션_재계산/xcert_iv/testA2.txt` | `103efe37bf0392f2c59f9a870cfc3148504f73f4d806125495468ddc685df296` |
| `세션_재계산/xcert_iv/testAint_97264.txt` | `a55842ce9f9f1b21dfc81f3970e9fade346a1413fc2cb5760d78a19f1e223013` |
| `세션_재계산/xcert_iv/test_ivv.py` | `0b7ae844825f7d135eadda28e2a86fb09b16dded55820b0e29853021f69e8245` |
| `세션_재계산/bprime_boxes/test_lib_out.txt` | `5ac7b2f276689af0f241c149080865c28d60b0ea52e41e04b96ea15d8cef4fbb` |
| `세션_재계산/c50_iv/runs/c50_rows.tsv` | `4e52cd3af555c580f39189381184ec04249ad04a9da78adb2005ef1b285db7ed` |
| `세션_재계산/c50_iv/runs/c20_rows.tsv` | `b34b10bba7a5be0f993e375f9cde6d360c43822723cdb580626b6f14cd2ada28` |
| `세션_재계산/r030ffae_window/work/qenv_fix_x.npy` | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
| `세션_재계산/r030ffae_window/work/qenv_fix_v.npy` | `64402ee14c829cdf9c8ffe4ce30796c03b4b56cd3329a7af5c7679150a097869` |
| `세션_재계산/r030ffae_window/work/design.json` | `5ca7ca94ea05873420053508c14ddec9562d60fb18c65d7ed2173afc0c12da7f` |
| `세션_재계산/left_columns_k2_120/code/left_columns.py` | `5618f2d91f246bb3affc37417485524207d73f95a4204ebff218d5466ac627dd` |
| `세션_재계산/left_columns_k2_120/code/positive_columns.py` | `2f1841a9bd301cfa541c3877e50ae0dfac10d84ed0b8434d3c3e35dff0c8065b` |
| `세션_재계산/left_columns_k2_120/code/summarize.py` | `7a8759777e143143a094d6a9f70ac3588ba16df979f0240f068877e39a447346` |
| `세션_재계산/left_columns_k2_120/code/exact_check.py` | `3533144585eb5e80b8b98c9edb848c60ad89e1dc7efd2f89a4975d15f04b7df3` |
| `세션_재계산/left_columns_k2_120/code/radii.json` | `7b2e5f9a73210c68c2c350ea4740399130df45380ff320298bb59d6fca266873` |
| `세션_재계산/left_columns_k2_120/summary.json` | `60b2229998f21b430f90b102c6d013012ef6be6dd840026ac9e8e4a2d5a5ea9a` |
| `세션_재계산/left_columns_k2_120/results_k2_70.jsonl` | `888c1463b05629a989d9b4b5b88772c5ebe848b17016399ff787e901a241cf92` |
| `세션_재계산/left_columns_k2_120/results_k71_120.jsonl` | `50857aa54bdc9501d8fa0bae8039006a2c03bea6fe7c7a598cf51b914125e8e4` |
| `세션_재계산/left_columns_k2_120/exact_check.json` | `a16718677be918061e041572e370df776125b7c3aa59ea70fe74632b2437be35` |
| `세션_재계산/left_columns_k2_120/indep/indep_lastcar.py` | `25b2af15b9ed44c7c115c6c7621fc62ac3db1da4274e233d636d494bb7a0bff5` |
| `세션_재계산/left_columns_k2_120/indep/indep_margin.py` | `3b3969af6bea00b8a07c344c8ca807b749efddd406f4aff584356b901aee9955` |
| `세션_재계산/left_columns_k2_120/indep/make_certs.py` | `fb90afc3efffe36b3057ad7618aef5c3a43d50acd2befe7847ff02467bbf5b4c` |
| `세션_재계산/left_columns_k2_120/indep/sample_certs.json` | `d0e1055c1d764cbbed933a924c5a24d752aa93db86e78ff045fa73a833a57b5f` |
| `세션_재계산/left_columns_k2_120/indep/indep_lastcar_out.json` | `1c39cc12ec5b6e4684f204cb307a0332f6659d619c8c05e559ec92161361d267` |
| `세션_재계산/left_columns_k2_120/indep/indep_margin.json` | `21d4d33340c1ad75cc7bc6d8aa7b182fa9c67b513a57e5089cc82f1a69c49af6` |
| `세션_재계산/left_columns_k2_120/indep/indep_margin_k2_3_n12.json` | `41e14f068739a6f3d49aaec4360c3b919c33473bf0bcc0c355dd5699577663b2` |
| `세션_재계산/left_columns_k2_120/logs/commands.txt` | `65f1ce99ea01d7c9d389ec99ab7a0026a57b3137e9c44a96fdedeff595ecd7e6` |
| `세션_재계산/witness_offset_iv/code/witness_offset_iv.py` | `3a224d306cedc21bc27b27e4863857d7ca5b8f90479fde1c2a675e7625fe7046` |
| `세션_재계산/witness_offset_iv/code/summarize.py` | `bce0eb80d1f4983ffafcf7f12870198e8457dd59a2ee75ba38ffa04007277d31` |
| `세션_재계산/witness_offset_iv/witness_offset_iv.json` | `0148bd7e576e5d19fb8d17971b96544d7453962050e937e619652028db5ccdf2` |
| `세션_재계산/witness_offset_iv/logs/commands.txt` | `f51aeec4dfdd678906f3b6c42d7e13b976df3e86967c563029fc68c68bc15b6e` |
| `세션_재계산/witness_offset_iv/README_run.md` | `5674cfb8f39a7660f0f6369c710202e99e825e42be8b6e3bbd6a06951509ac54` |
| `세션_재계산/critical_window_rerun/_test_exact_grid.py` | `6dc80ab5fde5dcd80987832fe9ad049e99925f71277c3dfa49ab2e4f07d06197` |
| `세션_재계산/critical_window_rerun/boxes.py` | `9f44b528f928a62f31390378140a02a58f1074a6a61ca16716195a6008ce2b7c` |
| `세션_재계산/critical_window_rerun/cert/A00.json` | `8028048ee9e42bdcb93dca0c6dc95ead07b98ff37da510791638d33dd8af54da` |
| `세션_재계산/critical_window_rerun/cert/A01.json` | `d5fcbaf28d1a4a09281f457a62ffffce063a8972d08e4298ab13f084282da8e3` |
| `세션_재계산/critical_window_rerun/cert/A02.json` | `0cb06bb0b8663a97fc79604b9277b254cb2b0541bd9901c428ef5fa3534c5463` |
| `세션_재계산/critical_window_rerun/cert/A03.json` | `b00f1011baa21e245de189f5402b47d5d82dce904732de549923e5107c1533e3` |
| `세션_재계산/critical_window_rerun/check_fixes.py` | `ddf036ca5553c68f911ee4eec2a887b464588c9593c635119ede01984a8bdeb5` |
| `세션_재계산/critical_window_rerun/check_fixes_out.txt` | `2f05ddac343e88e2d0dd9758ea2ef66393e0ed934b6fcfc6272c295e3504bd7e` |
| `세션_재계산/critical_window_rerun/common.py` | `25b9e23be2197be40a81b2be50bccd216cb1c8a7cf8a9fad962d006da313711b` |
| `세션_재계산/critical_window_rerun/ivio.py` | `0f5d2b6c96f3892d57e646e378457482914617c6f77d1a7ab7022f890008b716` |
| `세션_재계산/critical_window_rerun/launch_rerun.py` | `46f261df030ad53916f16bd9a9566914874a9ac8bf9ee34f6076a4f0869da79b` |
| `세션_재계산/critical_window_rerun/recert_first.py` | `d039c3aa0b163497ff36ad5b4316bb601bb4e904a0a004556b90d77554d3d61a` |
| `세션_재계산/critical_window_rerun/rerun_boxes.py` | `9ced573661d7e8850cb3e3a8f3292866583db97ab58205ac55f29376b9994f59` |
| `세션_재계산/critical_window_rerun/rerun_launches.txt` | `09b3ca7b13aab6e502fa3533024f1c54f8507bcbaffb0480015c071eff9cb41c` |
| `세션_재계산/critical_window_rerun/rerun_pids.txt` | `6d664826aed6fbee5fe18baa22cadf78fc819f9f54bd244ac9bc1a27147dd655` |
| `세션_재계산/critical_window_rerun/rerun_stdout_w0.txt` | `cb9b164e7f06d517e8c07e695ea9e19de2bc77b8966371ca199ae86937ce2d04` |
| `세션_재계산/critical_window_rerun/rig_H.py` | `48bd2cb2cb8cb4b8ac0c884fa528d84e910bee5e172163c575fd3f082fb88d8f` |
| `세션_재계산/critical_window_rerun/rig_W.py` | `e695b6e8a7b534798cf324769f3ef50ee3f0736ad53a9f3bbc079107e9e9434b` |
| `세션_재계산/critical_window_rerun/rig_cert.py` | `2742f05b61ed2bbe0d390c576bb3f349f98db7ee903106e8d27d2c2ef4af6fdd` |
| `세션_재계산/critical_window_rerun/rig_common.py` | `051e1eae119eb74d47cefaaa424444ee180e60c87b39bcec84d384748916ddd7` |
| `세션_재계산/critical_window_rerun/rig_pipeline.py` | `b42a611befe32745d7f8f08701e3fae094308185c5f14fdb3de59a90c2142eb7` |
| `세션_재계산/critical_window_rerun/rig_pipeline2.py` | `7f12815abae69b2e1c0521db72f753674dd7b05e7b8433f0b2982c33ff3d31d1` |
| `세션_재계산/critical_window_rerun/rig_ray2.py` | `30bd3d21313d27bfb2fe84c7c907aba68aab5211ff44fb5616add714f2a38a00` |
| `세션_재계산/critical_window_rerun/rig_ray4.py` | `235050c36bc5010efca2cc82f534e50ad9e9afd89bdce497014e08626d157245` |
| `세션_재계산/critical_window_rerun/summarize.py` | `b08b9d83771a7dcc984319bd1e1364896c56b60a0ddcc14acbabcde0aaa970ff` |
| `세션_재계산/critical_window_rerun/verify_exact_cover.py` | `f9e3cc3c94b5594f13bc607748ef29b7cba5b4942f67f55454ee25e35df6d321` |
| `세션_재계산/bprime_boxes/box_RK1.04_RNU1.03_k6668_NY6000_p0.npy` | `728dcaca633b235fb91776d8089ad4290e781bb203d8827fd85152ab2c977146` |
| `세션_재계산/bprime_boxes/box_RK1.04_RNU1.03_k6668_NY6000_p1.npy` | `122ac8beb936bda225c04da93442079d4aeec5c43f47b996d10dec751e6554bd` |
| `세션_재계산/band_boxes/box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.npy` | `b505f8bd932abd0ae67e23dc68f4d3e75799eb4805eb7d4d34f1cb1c970f65bc` |
| `세션_재계산/band_boxes/box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.npy` | `afded953badf2e763a140ad5b108dbb4ecd2ac8a29932391bbefc8eeb1f4c6f3` |
| `세션_재계산/band_boxes/box_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.npy` | `91858b8841172e801511d3236991373ce03c900814bd436706e58a158e99c4e8` |
| `세션_재계산/band_boxes/box_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.npy` | `c41d941372b25bced54e603baebff240b7b58be664f53524a69e744f4ef9f407` |
| `세션_재계산/band_LP/out_da_22001_38886.log` | `eea2a555e7919479c0bddaf189ef3a973298b11a01fb063549faf75f131854b0` |
| `세션_재계산/band_LP/out_da_9467_22000.log` | `bb5b79dae7e7d521d5fe74916b6c0f49908214412c70aabb7aa742802bde6f97` |
| `세션_재계산/band_LP/out_ra_20001_29500.log` | `83db3d425208b594d961959d906feb2ed71c1a09142a7c2e85f60b7e2bf45127` |
| `세션_재계산/band_LP/out_ra_29501_38886.log` | `e710790867804f0a6013210a4480177c195c3a865c5aca03ed3a88a4dfadaea4` |
| `세션_재계산/band_LP/out_ra_6668_8000.log` | `827990f8ec395645c65fbf8da01b67256ec10888a9cfd2a7783833f750c26d3b` |
| `세션_재계산/band_LP/out_ra_8001_9466.log` | `684e40fd1a724e191974a854a34a5b8cfda6496924a3ae1196995aadc708a997` |
| `세션_재계산/band_LP/out_ra_9467_20000.log` | `07af8d985a53861c0df016a8bcd0ba967021be16748fafa63cf720c9fe5a6a8c` |
| `세션_재계산/rerun_exactgrid_1116.sh` | `9838e37266ec787d832b5a1730aa5560295785f3a2db3dd8fd41ec7354e34637` |
| `세션_재계산/rerun_exactgrid_1116_log.txt` | `59909c8eef10dee35520257bd4d0348fbba93a037a335cc6783c6e66e882cab2` |
| `세션_재계산/critical_window_rerun/postrun.py` | `79980942572368bcf9b4c2cd6125c886fe63783629fec9f15e3addd24f7e1499` |
| `세션_재계산/critical_window_rerun/postrun_log.txt` | `2bd695fbb37078de9df80b1ce0a8b71e0029cba2590de72b3ea599e6de62e3d1` |
| `세션_재계산/critical_window_rerun/postrun_stdout.txt` | `2bd695fbb37078de9df80b1ce0a8b71e0029cba2590de72b3ea599e6de62e3d1` |
| `세션_재계산/critical_window_rerun/rerun_stdout_w1.txt` | `8f5853c09d6e5f6af99c51b7678533c206620597c5dd0b4513695ab1a50dcff6` |
| `세션_재계산/critical_window_rerun/summary_out.txt` | `4e045d66ea92bf2de5aed3bf0aeb302f1440de79beb05c1f8c27d28669b74763` |
| `세션_재계산/critical_window_rerun/verify_exact_cover_out.txt` | `cdda8f949233d287e79d41c991e7ab694bfb27720dc2f067319435a25f78d6db` |
| `세션_재계산/critical_window_rerun/cert/A04.json` | `a7ec19bce7dd11ecddf1b46fc10914782d07b77110594caea6ae4138fa54d105` |
| `세션_재계산/critical_window_rerun/cert/A05.json` | `bb01de3406fb34c9885559146bde511225e44372964816ff5dcf51badd4446b8` |
| `세션_재계산/critical_window_rerun/cert/A06.json` | `0667f47968e1958889382cc4e25f9f6c4888f7cb4e7368c9c7920a7797bf3635` |
| `세션_재계산/critical_window_rerun/cert/A07.json` | `be774b5ab6283274c65a471d693829a890c657f05e13ec27106ccccc0f419157` |
| `세션_재계산/critical_window_rerun/cert/A08.json` | `642df2a77f47a191b5a228b78d4dd1c31d74e8c69f382a60441eb7a15c3c3bb5` |
| `세션_재계산/critical_window_rerun/cert/A09.json` | `5d9b877a79a04245e86ce4022256d8a248f321e40eb15fa8389db375d7b749e7` |
| `세션_재계산/critical_window_rerun/cert/A10.json` | `9913084fa78ad01b21fe42fe14ff6fe83c4bc96d5f13cf2bcd5a0fbcbad40fd0` |
| `세션_재계산/critical_window_rerun/cert/A11.json` | `4fa62b741a02da96429997dfdc4fa0a0298ea22973c57d20f9d1b7e2162c95aa` |
| `세션_재계산/critical_window_rerun/cert/A12.json` | `86529bfdb338f1fc453a87b997da2d52ad44bf1201b088d50b5229e55eefcd66` |
| `세션_재계산/critical_window_rerun/cert/A13.json` | `19fd80fc2bc8c133e49d9297226b206e8e73db1fc4ef68ceb91894b443b00d38` |
| `세션_재계산/critical_window_rerun/cert/A14.json` | `7a463067a6db42a4dfccd3e45bc7f66e0693986143d4fabe104ec9750de7ef54` |
| `세션_재계산/critical_window_rerun/cert/A15.json` | `263fd2caa398395da4e6a145ba3091d3e3ebc1a40b74472eecd06b10ed239672` |
| `세션_재계산/critical_window_rerun/cert/A16.json` | `b633486735a289dc90b000690bc23435aab94b60377d6b9047c339427d8f1c76` |
| `세션_재계산/critical_window_rerun/cert/A17.json` | `b6a3416700c615ebe877900f047732eac4d34ebe627dd2d3dcf993202ae1bc2b` |
| `세션_재계산/critical_window_rerun/cert/A18.json` | `4615f9d0f99758f29785e5deda5bb9b1ed8a0c2b6f376a57104e02b2bc801d8a` |
| `세션_재계산/critical_window_rerun/cert/A19.json` | `2c2e77737197789972b8698502f734ddcd226bc796f958b603a21d6d2cbb3b1c` |
| `세션_재계산/critical_window_rerun/cert/A20.json` | `4f475d65158f6ec08b32c5f2fe04baa0cbc9158e01f0368c34ffdb944847ebbd` |
| `세션_재계산/critical_window_rerun/cert/A21.json` | `2525850acb942a5a2d53283c501eb239d8c44c7f22a145482123388cfe265e73` |
| `세션_재계산/critical_window_rerun/cert/A22.json` | `b994f36393178b468d3e27f9fa65a1dc6c503aed9f1b9a1ed2c79229aa057747` |
| `세션_재계산/critical_window_rerun/cert/A23.json` | `3f81654de15ed580c4864b43d44fa82697115e228e72c90d6062e65bdb8d902c` |
| `세션_재계산/critical_window_rerun/cert/A24.json` | `c60e6f4569eb46b51f079dada19ad68a8ceff091694b013d3cae2e9486b9100e` |
| `세션_재계산/critical_window_rerun/cert/A25.json` | `9e82d76409c8c7d17cee62bf8d2dd2859b6c74b2315c390a04d3fbe206cb60af` |
| `세션_재계산/critical_window_rerun/cert/A26.json` | `3a015e49bfb8bc125898855dc1a6c1c74345d83b1e3d3e41b796fa6eee7b3cb2` |
| `세션_재계산/critical_window_rerun/cert/A27.json` | `7388e836d4524b2fbae0a5add33df94a7c23f8491e77a171d706d196d2381d93` |
| `세션_재계산/critical_window_rerun/cert/A28.json` | `c26b74aa4652d0b1de7b59c84cc44f2a84c2d8ce8777d22d85fe0323a547ed5c` |
| `세션_재계산/critical_window_rerun/cert/A29.json` | `fc0620f905638a38aa099f9f23ca91a17a69a592a229ab601597c66a97c4ec6c` |
| `세션_재계산/critical_window_rerun/cert/A29_recert_first.json` | `d1c99990972a927fdc85c20ff9fbbf0d073508e5d46f3635f617b5a6d4e8e110` |
| `세션_재계산/critical_window_rerun/cert/G00.json` | `5c44d07f177554c812baa0dd709728a57c2cfa2a6b721454b5c47997ca7955b1` |
| `세션_재계산/critical_window_rerun/cert/G01.json` | `a7228821e8303aea06caa512e335bbc17ae10346886125e3e614c04c8c798058` |
| `세션_재계산/critical_window_rerun/cert/G02.json` | `ffec0a63acb8d2ecad063a72b9d34c35f204579364dc73b13c639be8d338c3dc` |
| `세션_재계산/critical_window_rerun/cert/G03.json` | `f25cf1fea98caff858c7417b8cb9594247ced24041c9f6b44da7affc2a5e6b61` |
| `세션_재계산/critical_window_rerun/cert/G04.json` | `76f810699d85915ed92007c3651e444476e204a9361fec5659fd019a76ab76f3` |
| `세션_재계산/critical_window_rerun/cert/G05.json` | `e3a379f2df9ac66d6785e95d592043bd3e1ec6e4c35807fe4dbf2f562ac501f2` |
| `세션_재계산/critical_window_rerun/cert/G06.json` | `1aa3e4f10aff9de3031d41ba6804587b370cbfdb146cd9a308f63aacea79da90` |
| `세션_재계산/critical_window_rerun/cert/G06_recert_first.json` | `66313974fe7488e8c1a79f08a2709b89d58d3d7e46df71e579a55e0e163fdfff` |
| `세션_재계산/critical_window_rerun/cert/G07.json` | `8dca77e45743712c634ea4d0b77f58ab845742fe297d9faae04ca602cb2a1242` |
| `세션_재계산/critical_window_rerun/cert/G07_recert_first.json` | `6569fc3c31f1e8450719d7f58c266daaa8fdaa0c02f7b40367fc9bf560be8edd` |
| `세션_재계산/critical_window_rerun/cert/G08.json` | `a69c5386b9a7c9668813be7adbfe5b787f97afc0ce1595dac99885f8f8e00c97` |
| `세션_재계산/critical_window_rerun/cert/G08_recert_first.json` | `6bb2153cc3ccbc396100c4d98de7231b264a945fb73fa84f48121b69d9a105bd` |
| `세션_재계산/critical_window_rerun/cert/G09.json` | `7903d2c7930412a7a90e53b80b79f0bd984ffd2d7fce1a75a0a0160bc89eaa6f` |
| `세션_재계산/critical_window_rerun/cert/G10.json` | `dba59ded363f9300374d254e15f93e5620b728e3cd8c926f219d234aeadc6686` |
| `세션_재계산/critical_window_rerun/cert/G11.json` | `509fb985500979ce08fb1fb06bb82911bf1d5a6cfa3c4bdb3aad5f577f977f4f` |
| `세션_재계산/critical_window_rerun/cert/G12.json` | `a1cf7b8f7362158d2116d0fdfd0e07713850c7471d407bf69fcd28af541f10e8` |
| `세션_재계산/critical_window_rerun/cert/G13.json` | `7a9323e57576256e3ec24c9bba761a2ff5eb4264a49c3fe37520b2ce95a51434` |
| `세션_재계산/critical_window_rerun/cert/G13_recert_first.json` | `273e4fcc15eeb1bfd723d86ee5a992aa63341d699de8684d572e300e74a6efd0` |
| `세션_재계산/moment_cert_iv/handoff_A3.py` | `370e128d714d449d54adae0b7306f34eb6ca5c4472760d22c41d51579b8b0414` |
| `세션_재계산/moment_cert_iv/launch_handoff.py` | `744903b47d85d20a1b63c98c5dc09a091b5a9fedb30ac41dcecf6be96de3d9db` |
| `세션_재계산/moment_cert_iv/make_draft_v2.py` | `f42e5ac17023dae2dcc06c7a71a3c61c8b1455bb58b947d127a4f36df936bba4` |
| `세션_재계산/moment_cert_iv/run_ct.sh` | `8ec6724b368bc69921e4ac3c6a7bd723f12064463b6bb38215a8fcbbfaddbf56` |
| `세션_재계산/moment_cert_iv/summarize_nb.py` | `1a76d34c2a7af482379e5db6e064bd0cd363b88d4a11089886df564c2a1a13c0` |
| `세션_재계산/moment_cert_iv/summary_noblas.txt` | `d8fa4d3e6ee1058488069bb059cbc36850e320fb68f16fc46fbe5627cbb2ddfd` |
| `세션_재계산/moment_cert_iv/sweep_ct_A3_s0.jsonl` | `012f27d4525db6cabf79f97c0df4fb8d973e87ccfa1d8652e2084dfe23fde700` |
| `세션_재계산/moment_cert_iv/sweep_ct_A3_s0.log` | `908cab704d387bc0fa8725c4a4ff371637385ed21cfce625667388375df12e4e` |
| `세션_재계산/moment_cert_iv/sweep_ct_A3_s1.jsonl` | `f3b50f71efad5e42e9a2d64c70cf28646db25132825f7e93f8dd05d74790375f` |
| `세션_재계산/moment_cert_iv/sweep_ct_A3_s1.log` | `8bbf3b7ab876fa70b50b9b07cc4dcc7bba1140407229471fc6adeebf88c126c0` |
| `세션_재계산/moment_cert_iv/sweep_ct_A3_s2.jsonl` | `2ccd4bb01a1a9f49a4cd5086455b74a6e3977576fa1525e90f9399e90c0274b9` |
| `세션_재계산/moment_cert_iv/sweep_ct_A3_s2.log` | `71cd0cf0fc08206eb79b0a52e6df8858a545421ba1b8f1db3237d33714eda5e4` |
| `세션_재계산/moment_cert_iv/sweep_ct_A3_s3.jsonl` | `6064f56aa83f69c27a48ec189bc8d6e6ad73fc704619f23665d029c72baf15c2` |
| `세션_재계산/moment_cert_iv/sweep_ct_A3_s3.log` | `030eab789d218a00192cac53f57458a53c736afc3715b2af2304f156aaa5d71f` |
| `세션_재계산/moment_cert_iv/sweep_ct_A5.jsonl` | `e2c89ca9de502d8e69fc60b41d6552d73a2a4f50002b6e4a18880558041348c4` |
| `세션_재계산/moment_cert_iv/sweep_ct_A5.log` | `8e69544849ae5e8a82a59e55bd891bddcb09c9d07136b25289544c4967c02ed4` |
| `세션_재계산/moment_cert_iv/sweep_ct_mp.py` | `eeeba4862293ca585f98ffd7bd7c9367ca13fd536f58c05fe349b5187fae9c85` |
| `세션_재계산/moment_cert_iv/test_count.py` | `f205146544f34fb5abcedd9661ad2f33a40ec75c3c869e5116469a2886ff0c5d` |
| `세션_재계산/moment_cert_iv/test_count_out.txt` | `3b2c27b4819c417510f5de8127504843d0cb7e53aa1f022550befb37102a880e` |
| `세션_재계산/moment_cert_iv/test_noblas.py` | `4420b02e780ebe3833a05cf00b7db7fd74bf04fad5418ece6e7cba2cd9102c61` |
| `세션_재계산/moment_cert_iv/test_noblas_out.txt` | `ed4ef0d6ed418295f4494abe61e67b4bd9b9c93729ae4628b352fc0a9d5e4600` |
| `세션_재계산/icert_py_full/rev_icert_unpaired_fast.py` | `e4bd4d675c7de685d0e3b969a2f8e8667604b8d04e7e7f0635a4f5e425c17b31` |
| `세션_재계산/icert_py_full/worker.py` | `590f398d5f2dcf738cae0ed06597c897f86d9d186bf516c1406813c837694302` |
| `세션_재계산/icert_py_full/launch.py` | `49b4dac59ac6b1714eb317838ef8f132b2e642c480d82d0ce4708093625d3f41` |
| `세션_재계산/icert_py_full/stop.py` | `73ce0c2b601980d707bf585bc45349a024c3fe202c621e17e3b98c3d9015ec95` |
| `세션_재계산/icert_py_full/summarize.py` | `58242c4ce130b2d0b63e02815e2159959832db65daf1f6759f11485003b9295f` |
| `세션_재계산/icert_py_full/make_draft.py` | `451a26b2c2f31447bc964e54423f53a37f088af0ca816f3f5fdc8ed62a9c4baa` |
| `세션_재계산/icert_py_full/README_run.md` | `93c7fedb1c8f691d0de25e5056afec032da1545def527b7acbdd25cc549f4901` |
| `세션_재계산/icert_py_full/summary.json` | `98da0e5b22c3f9bd558cf43316a2720f74a5d4f7efa6fa67ea05a17ee9750851` |
| `세션_재계산/icert_py_full/launches.txt` | `f0266ab2e4b79295b654305ec357efd8ac315455846ff620004403ef137e75dd` |
| `세션_재계산/icert_py_full/log_w0of1.txt` | `4dd574643139eec2d37a96f003656b65caa7a84fd67afe1493a80124b387322b` |
| `세션_재계산/icert_py_full/log_w0of2.txt` | `78b0d4ad141978dbbdefcd76e8fe7708334c3239ed5c79cc50bfb9f14682b2da` |
| `세션_재계산/icert_py_full/log_w0of3.txt` | `8f0bebe5ae517de93aeb70601240604b9affaf37ea7556e14c4c5a8f6de2e739` |
| `세션_재계산/icert_py_full/log_w0of4.txt` | `f29d8709ba0d663163dca792f0f53e0523ec43794f59d71ab897f33b5210dfdf` |
| `세션_재계산/icert_py_full/log_w1of2.txt` | `9477a4af01fbf849206422fba282c5206db31914661718b787853feab6b2b12c` |
| `세션_재계산/icert_py_full/log_w1of3.txt` | `4778c74357c49ec8aebf8683d630be728536aee043d1ca9960107c7d2da994b5` |
| `세션_재계산/icert_py_full/log_w1of4.txt` | `943cf974b153de02306b156133e59ccc16622c8724c70f302ef6aa84457e2015` |
| `세션_재계산/icert_py_full/log_w2of3.txt` | `97ad600e20a5d8e87fb69f87335accac79d35ba4c6b4c5dc185132dce5df5c2d` |
| `세션_재계산/icert_py_full/log_w2of4.txt` | `9435211fe74b0a881ed69fe7e3be0ae3d5250c7671e75f09fa5b468587c40a5b` |
| `세션_재계산/icert_py_full/log_w3of4.txt` | `3be5528be4b62056cda1f9f86246bce0df5df5267ad2690bc3b0ed8657b34924` |
| `세션_재계산/icert_py_full/out_1001_1100.txt` | `8dcaecb6511806aa1db9d6d4d4a3a6d7435c5b3bdaf3ca725f900f5b7e626463` |
| `세션_재계산/icert_py_full/out_1101_1200.txt` | `741054f964003b385bf693f5428f968545c5b6c51f56264a8250e38c6d4ea659` |
| `세션_재계산/icert_py_full/out_1201_1300.txt` | `b0711d38e65fdfbb171fb2be6d494af081c40f289065576db56ed6019da9b913` |
| `세션_재계산/icert_py_full/out_1301_1400.txt` | `2d84d6263b0816ea46ed5df189aff6d902bb92687b4ec1b1af65826f10526ccb` |
| `세션_재계산/icert_py_full/out_1401_1500.txt` | `950e880d61a2b9a4ff3f3119f0f7e884e6bde592f32dcbfd7df62b0cd9d9ff46` |
| `세션_재계산/icert_py_full/out_1501_1600.txt` | `492ec1d0ca659d0aa8c75408ab23249f775518cede90ec9229b4b6f3ae265a22` |
| `세션_재계산/icert_py_full/out_1601_1700.txt` | `330f58a574239a7ef8c03a3dabe3216b11cd65b1b2ce3bd43e438ac455fa6beb` |
| `세션_재계산/icert_py_full/out_1701_1800.txt` | `2c756f54d6f5bb739ecfe1fd6a384b8f049a1ec9bc4b0c8e1272530ea930deeb` |
| `세션_재계산/icert_py_full/out_1801_1900.txt` | `e7277aeb519237c03d9475d63041ce12b9eaedd830b670f6da3d190a7f1f06c1` |
| `세션_재계산/icert_py_full/out_1901_2000.txt` | `7177429f51986d3add58632a7c7d4bce886362a364ccfc9d5d8b8f5594a3e00d` |
| `세션_재계산/icert_py_full/out_2001_2100.txt` | `ed0092d6f5215d4eff7ca26e5a714c2076e2a4a679e6cec6181cf1c159197593` |
| `세션_재계산/icert_py_full/out_2101_2200.txt` | `6f1b2b47785975908b5e733472b108f2c30ff45b81d9fb05888a24946bb049e4` |
| `세션_재계산/icert_py_full/out_2201_2300.txt` | `49d86c7a6f0299d0153b76497dae52a3d5855c52a434669a366afe7b3953b7b1` |
| `세션_재계산/icert_py_full/out_2301_2400.txt` | `89da451173b6a1fa91af01f8ebaa06f8386eaedd7ec97c8f7cbbe001b66ccecb` |
| `세션_재계산/icert_py_full/out_2401_2500.txt` | `b580cff7d0a58a7bddf120c11397a18049ff99d9c0be4ed9f0c2fe22afcd6c5d` |
| `세션_재계산/icert_py_full/out_2501_2600.txt` | `01712f89ac0c00143bd9f4e39b760cc8e79f07a0233908a173d5bc0dfc7d3955` |
| `세션_재계산/icert_py_full/out_2601_2700.txt` | `5983248f45f98d591ab938c62ec7a3692d5ca843b9f9df51eaacced39e52a516` |
| `세션_재계산/icert_py_full/out_2701_2800.txt` | `1ca7bb4d4f96e6d41150d94959fee6d5f2b0472dc1efe3dbdc60eb0d03f6772c` |
| `세션_재계산/icert_py_full/out_2801_2900.txt` | `4f1592d84e5b8d0dce379a2d1f19560f9c8ace6d56d8f5c92d899420386d9330` |
| `세션_재계산/icert_py_full/out_2901_3000.txt` | `bbfd41b3bcfca2db84c1332835bc771fd418e65f468dce80cd72615f2c833dab` |
| `세션_재계산/icert_py_full/out_3001_3100.txt` | `e27afcf38eb2f842fea7fa20f4f090323ed7341ad26252f838a084ba5db284df` |
| `세션_재계산/icert_py_full/out_3101_3200.txt` | `c31994fdea1cad5d8da8f11f011734a2b130d6b5910d8fb82b9870fc8c8e2c28` |
| `세션_재계산/icert_py_full/out_3201_3300.txt` | `ecdb2fa95fbe3198fc0bab232b871cef0a8560db4f4f1857c2dec40f5b6e922f` |
| `세션_재계산/icert_py_full/out_3301_3400.txt` | `e7f0d4cb918f6fdd4cd72b718f8fe06ff791f57c0ec8c5c4dad43ba82af76ef3` |
| `세션_재계산/icert_py_full/out_3401_3500.txt` | `41681dbb46e704a5d9d881bd4a9217c4b9ed793d51992a8377e1ba6f1f3d64e1` |
| `세션_재계산/icert_py_full/out_3501_3545.txt` | `46390f399286da8ed1cd90eb094b7beb8944e647d5b384dc45465246a6ecb3f5` |
| `세션_재계산/icert_py_full/out_3546_3546.txt` | `72e369b007fe281933a0eca9e770a1bfe361650c7f4b1fa46c6c51d0c1c0d041` |
| `세션_재계산/icert_py_full/out_3547_3547.txt` | `c2cb776560c08d9a30603948d4c774e190aba3a33d0fccea8581f6e5c5eee2fc` |
| `세션_재계산/icert_py_full/out_3548_3548.txt` | `1834ad3cd940532e50b52d06c7e0adc07f4612b605af3a8742d314058f987f52` |
| `세션_재계산/icert_py_full/out_3549_3549.txt` | `00d8d999d4aeb4290a85182c346f03bc21b780a3d9d3c3972ec9fc279c5c5009` |
| `세션_재계산/icert_py_full/out_3550_3748.txt` | `284faa6695fbe16d75b87dad2573d082ec93cccf9fb0054146d06c6e9bfaafd4` |
| `세션_재계산/icert_py_full/out_3551_3749.txt` | `2d21e46f7a00da91adb2747b418100c4d33a92e878292399045b8b9cb223e468` |
| `세션_재계산/icert_py_full/out_3750_3896.txt` | `66b8c5ad99726e5a41ac5806b57162025232f721fade258dc04e5b415e45e114` |
| `세션_재계산/icert_py_full/out_3751_3897.txt` | `8feb3fbbdf1e3f192299afc53231da8f86776ff15bc2ddeac5e2f34ba99432f8` |
| `세션_재계산/icert_py_full/out_3898_4195.txt` | `1422ad8cfe9a92c0fe6b413cdbfd3b3422bb0c10e932113f52d7e9ca60091c45` |
| `세션_재계산/icert_py_full/out_3899_4196.txt` | `d8f707d97ac4aeb5e8691514a582865bff53e34c58f3e08e86f283e3e6d55ecd` |
| `세션_재계산/icert_py_full/out_3900_4197.txt` | `7ee39edb571c3a0c8bc9ed107c9faba93ef45813acf6b78174972ed3fdb7adfc` |
| `세션_재계산/icert_py_full/out_4198_4495.txt` | `36772dc3b006e8f9bfeacd549abed30d05db85e3175905e8737cb3b86f5bd46d` |
| `세션_재계산/icert_py_full/out_4199_4496.txt` | `b3ba79a621929d9f7695cc2a32635b10176b70a9a35a847c8695c59dd20f8108` |
| `세션_재계산/icert_py_full/out_4200_4497.txt` | `5fafe8b60fa9aee2319aa692768e7ca412c82d8c4ebed8b5939a10053a1df66f` |
| `세션_재계산/icert_py_full/out_4498_4795.txt` | `b741f8918aa3bcac235d41ff0717127939cd84b194e1e262bd27df49e43400d4` |
| `세션_재계산/icert_py_full/out_4499_4796.txt` | `840dd553e6459ac0bb6093bbeeedefdf2ab1a70798070356a5c0de92620d2dc7` |
| `세션_재계산/icert_py_full/out_4500_4797.txt` | `2c149bf81f55fed32f90768c6ec0c01c28d66a3a1c27eccf24bdb3c6b30c5686` |
| `세션_재계산/icert_py_full/out_4798_5095.txt` | `cb23e8cca638023e36a731ce5160903911e77facee28ac47cdb04e3cc9ba3ab3` |
| `세션_재계산/icert_py_full/out_4799_5096.txt` | `92b5f59ba0a387e46687041072104bb8f73e40716ad23cb7167e411ae142849b` |
| `세션_재계산/icert_py_full/out_4800_5097.txt` | `10fb3ed2f5903c956e4a89630adbcd7e23f12479fd5fa916e0043c1f6141b67e` |
| `세션_재계산/icert_py_full/out_5098_5395.txt` | `2c7fd952031fbc0bfa6b422c1380118ed9d464a0fc329cec4d6a008f058a8132` |
| `세션_재계산/icert_py_full/out_5099_5396.txt` | `92743e70e870dbcdbad53383612b6da3c0b47220bfec1ba0344ad5f156686051` |
| `세션_재계산/icert_py_full/out_5100_5397.txt` | `d89844193833337ea0790da2eff5784229a1d60c29c11da4bae0948dd2a47e43` |
| `세션_재계산/icert_py_full/out_5398_5695.txt` | `5e650aef4141d06c0f53a05359a54702fb388a88575379e1a8f8f7eb1364fc04` |
| `세션_재계산/icert_py_full/out_5399_5696.txt` | `5a310d7eba42d9da6e72aadfbb3c458f878d665bf5b819104ecd347df9706c91` |
| `세션_재계산/icert_py_full/out_5400_5697.txt` | `f7b9d31026cd2e50080f24d3c12448045ab21bbb0fe76c321eb30326dcd036b3` |
| `세션_재계산/icert_py_full/out_5698_5995.txt` | `684f506a6c5e81a65a88c4caf7ff9bda437a48c4d6e9adae25b5620e58a5e103` |
| `세션_재계산/icert_py_full/out_5699_5996.txt` | `c3496b57497ca7be1427ec73af6652f3155d3af1962aa8db2653b00bea744ebe` |
| `세션_재계산/icert_py_full/out_5700_5997.txt` | `18f25e7e5ad4011787b4f1bca00a008b8b471e4378640c0a638ee6af299f7c28` |
| `세션_재계산/icert_py_full/out_5998_6295.txt` | `aa1b1ee81e6fd67265b76f91b86168377e9f83d0cdbf9875bab17ce24d826e79` |
| `세션_재계산/icert_py_full/out_5999_6296.txt` | `3d865c7eeeaf1827b23583909748f346c52a273ea981c03b2aa026310735fc53` |
| `세션_재계산/icert_py_full/out_6000_6297.txt` | `52da1b374e319ee4923e5b99e312a0fd80a0d544ed098a783e8f1ff6df73dfc6` |
| `세션_재계산/icert_py_full/out_6298_6595.txt` | `2351a3f16548f47aac392a004dcf9ef4bb3655f15a9921fdd6d0b80828f88f48` |
| `세션_재계산/icert_py_full/out_6299_6596.txt` | `77b21a3d8e7c00c5434109809b3436c3b3ade658110e89f72eccf2019ee48c37` |
| `세션_재계산/icert_py_full/out_6300_6597.txt` | `a75ab45bdcab15068bc001b1e4138b2f653ce61c8a9636b36fb052da1c59c8a2` |
| `세션_재계산/icert_py_full/out_6598_6895.txt` | `33037f2ce612090bf8832be2d05803e56dfa2b09ee9b1d9c2b45c278922d8533` |
| `세션_재계산/icert_py_full/out_6599_6896.txt` | `fea427abc98b72db098f7c2713e35233170fb20ee7291081d8704f34c14bfb56` |
| `세션_재계산/icert_py_full/out_6600_6897.txt` | `209ab94a924c24138ae82d26c72f3489e4a69fd317c7c2f6653192f7a8196b49` |
| `세션_재계산/icert_py_full/out_6898_7195.txt` | `b202dc0f48d52b5977a245f64347db1806fae0079e5633f3bb499255f0737759` |
| `세션_재계산/icert_py_full/out_6899_7196.txt` | `eac820b7756cd0528169e72b9e5e8700fde78308c6d8d6bd7efc1f6397d24f33` |
| `세션_재계산/icert_py_full/out_6900_7197.txt` | `a32bfd5edc678ad0ea435121dac72966d4dc0682e1d85f488f7407d9ef2c044a` |
| `세션_재계산/icert_py_full/out_7198_7495.txt` | `ad98c32309700f7ffd62a885032cbc9bfb1bd058074bc7037f959382f4c522f8` |
| `세션_재계산/icert_py_full/out_7199_7496.txt` | `31a370e2ae708606b4cea3644fd5158d5d8d290f448b75691049a6f74f2de1f3` |
| `세션_재계산/icert_py_full/out_7200_7497.txt` | `f054f73eca44bde8c9a5a19b95ab7fa360faf151ac986273b7f426cc01c2f607` |
| `세션_재계산/icert_py_full/out_7498_7795.txt` | `3b7be3f462fe5b7ae537df72246eaba597c7503e0c92fc937c5dbd46c01445f4` |
| `세션_재계산/icert_py_full/out_7499_7796.txt` | `52df2da97f80696d2658e988e227bd411f7a2542155a45ca655ae1c4f0267945` |
| `세션_재계산/icert_py_full/out_7500_7797.txt` | `4fccf721cda0b06378ee1b4caf99cbd94b6b448be5839f540662e4b4c33ce856` |
| `세션_재계산/icert_py_full/out_7798_8095.txt` | `870090868772f4c7859b417ebec40ee4794abf63641add7d2ea7eb92e356ebb0` |
| `세션_재계산/icert_py_full/out_7799_8096.txt` | `415167d8858a2942c9a1a99b8a9a663fd1401e172482cab1e457906590243385` |
| `세션_재계산/icert_py_full/out_7800_8097.txt` | `739ea3e84e3cddae00b80e16136c7753a2ca43f896f547b21d49871171d0c165` |
| `세션_재계산/icert_py_full/out_8098_8395.txt` | `eb2f084df103cb15e520f226da97557103cf9433665418fa109dd1aa236ec5e0` |
| `세션_재계산/icert_py_full/out_8099_8396.txt` | `03a91c3ed21ca4bdff1b7cdfac3d9b900492ef5560c3fc84fc54737bc088c841` |
| `세션_재계산/icert_py_full/out_8100_8397.txt` | `b9d7b2684454ad497bbf142e20f5dd74078ada1faf3ab79373d1227b36797029` |
| `세션_재계산/icert_py_full/out_8398_8695.txt` | `2a25f9ac31b962c9cc0ebc13e35ff4f11e850a429b3fae0304c80ede8d07e1db` |
| `세션_재계산/icert_py_full/out_8399_8696.txt` | `75459c3ac3d158609331478bbf0436bdb8a79169f97d7417a11f1c7d486cc9a6` |
| `세션_재계산/icert_py_full/out_8400_8697.txt` | `f0c626cdbe89d6dd330cd0c431b66c5136f0b36d49807f6f8ce9892ce71eea0b` |
| `세션_재계산/icert_py_full/out_8698_8995.txt` | `68b01a5a55a77a77c9f9085ae9eb7602f38c201ceb42e8506a9b1bfbe8d62bfc` |
| `세션_재계산/icert_py_full/out_8699_8996.txt` | `74398be606d2b6af4a438750efbc401b012df21bb033096bbb36b6281ab1d36d` |
| `세션_재계산/icert_py_full/out_8700_8997.txt` | `1dc372888d49641904b5733bfe2e4b084558e4d0a8efb2135729f8288e08f527` |
| `세션_재계산/icert_py_full/out_8998_9220.txt` | `542bdca403c9a97a6df212712f0dbfc1fc31520d3a0c1f998ca40d27a61b9ee0` |
| `세션_재계산/icert_py_full/out_8999_9218.txt` | `119aa831b5efa278359f9afe64cf480e84a0428238495b5e4fff7d3d8a0f9f12` |
| `세션_재계산/icert_py_full/out_9000_9240.txt` | `e4514ffd3418f80e243e1b8f553ae0ee46c75881ceb39dcf5e63360bb757d394` |
| `세션_재계산/icert_py_full/out_9221_9625.txt` | `fece6ddc27b24c27cff88df6d875b93a5e3815543bfbe7e00ea2a47d77eea13b` |
| `세션_재계산/icert_py_full/out_9223_9623.txt` | `f716b90c7de69798e3c80220f4ce053e15739a65ee2543f2c89b9d818c265915` |
| `세션_재계산/icert_py_full/out_9224_9628.txt` | `0daea6c127957ccf299a45b25a491bedf0db398356cbdb2464ef24930ebbf6e7` |
| `세션_재계산/icert_py_full/out_9226_9626.txt` | `97a14a7839b8af78b778418ff7253d5496aea65b4f9b6aeda7689c3eb23351e0` |
| `세션_재계산/icert_py_full/out_9627_9999.txt` | `c42a1a0290d632937c309130cbbebcc748542f7c393c886b4aac7c0fa81e8a74` |
| `세션_재계산/icert_py_full/out_9629_9997.txt` | `b9b116e46f6056742586cfcd0a9577b18ffd3f6ab6497d2ebbe92a7d46c3b0e3` |
| `세션_재계산/icert_py_full/out_9630_9998.txt` | `6ec0902887cb8870566f5686107882869ef494494f259297bcedf2df0fb526d4` |
| `세션_재계산/icert_py_full/out_9632_10000.txt` | `68d52190f7e099486483c65b2456fd45ecce236bebd095b08796550bc2a60e13` |
| `세션_재계산/icert_py_full/pids.txt` | `cf90cad32e4bf6a8e6e8ec67d1f369a500de47bebb48cc00df24fd3d01118e82` |

`세션_재계산/zeta_constants/zeta_iv.py`는 부록 D의 Riemann 제타 상수 항목이 적은 방법을 mpmath 구간 산술(소수 30자리)로 다시 돌려 $\mathsf z_{3/2}$·$\mathsf z_{-1/2}$·$\mathsf z_{1/2}$의 구간을 확인한다(2026-11-13 세션; 인자는 부분합 항 수 $C$ 둘, 기본 4000). 함수 `z32`는 부분합 $S=\sum_{j<C}j^{-3/2}$에 항목 식 줄의 사다리꼴 하계 $2C^{-1/2}+\tfrac12C^{-3/2}$와 중점 상계 $2(C-\tfrac12)^{-1/2}$를 더하고, $\mathsf z_{-1/2}$·$\mathsf z_{1/2}$는 Euler–Maclaurin 공식과 첫 생략항의 나머지 상하계로 감싼다. `python -I zeta_iv.py 4000 4000`의 출력 `zeta_iv_out.txt`는 $\mathsf z_{3/2}\in[2.61237534856\ldots,2.61237534874\ldots]$, $\mathsf z_{-1/2}\in[-0.20788622497838\ldots,-0.20788622497735\ldots]$, $\mathsf z_{1/2}\in[-1.4603545088095868\ldots,-1.4603545088095855\ldots]$이고, 셋 다 확인하는 진술의 구간 안에 있다.

`세션_재계산/M_natural/j_integrals.py`는 부록 D의 대각선 손실 닫힌 꼴 항목의 두 적분 $\mathfrak j_1$, $\mathfrak j_2$를 위로 반올림한 상수 $0.70836$, $2.528571$로 tanh-sinh 구적(소수 30자리, 치환 꼴로 교차 확인)해 다시 계산하고 $\mathrm{DDL}^\natural(k)$를 평가한다(2026-11-13 세션). 출력은 `j_integrals_out.txt`.

`세션_재계산/prop_W_thirteen/iv13.py`는 부록 D의 핵심 근처 열세 항 항목의 열세 쌍 부등식 (6.50)을 mpmath 구간 산술(소수 40자리)로 확인한다(2026-11-13 세션). 출력은 `iv13_out.txt`.

`세션_재계산/r030ffae_window/`는 부록 D의 창의 수준 질량 하계 항목의 셀 검사를 시험 함수 격자를 한 점 늘려($0\le i\le12927$) 다시 돌린 것이다(2026-11-13 세션). `work/`는 기록 [r030ffae] `evidence/peer/rerun/work/`의 코드 사본에 늘린 표 `xKrig.npy`·`wKrig.npy`(기록의 표는 `xKrig_orig.npy`·`wKrig_orig.npy`; 처음 12,927개 값은 비트 단위로 같다)와 결과 JSON을 더한 것이고, `NEW_*.out`이 실행 출력이다.

`세션_재계산/M_natural/j_integrals_iv.py`는 부록 D의 대각선 손실 두 적분 항목의 두 적분, $\mathrm{DDL}^\natural$, 감소 조건, 부호 보조정리의 적분을 mpmath 구간 산술(소수 30자리, 칸별 구간 Taylor)로 확인한다(2026-11-13 세션). 출력은 `j_integrals_iv_out.txt`. 같은 폴더의 `j_integrals.py`는 그 전의 비인증 재계산이다.

`세션_재계산/four_families/families_iv.py`는 부록 D의 네 가족 검사 항목의 모든 값(여유, 하계, 가장자리, 보조정리 조건, 단조성 표본)을 mpmath 구간 산술(소수 30자리)로 다시 계산한다(2026-11-13 세션). 출력은 `families_iv_out.txt`.

`세션_재계산/r89eb039_polar/`는 부록 D의 극 영역 488개 $k$-구간 인증을 다시 돌린 것이다(2026-11-13 세션). 코드는 기록 [r89eb039] `evidence/producer/code/`의 사본이되 `sparts.py` 77행의 $\theta$ 지표를 항목 (ㄹ)의 식대로 $k-\ell$로 둔다(기록의 원문은 `sparts_orig.py`). `recert.py`가 `inputs/*.jsonl`의 기록 $k$-구간을 읽어 같은 분할로 다시 인증하고 결과를 `NEW_*.jsonl`과 `NEW_*.log`에 쓴다. 488개 $k$-구간 모두 통과했고, $k$-구간의 결정 여유 $\eta$와 $G\sqrt k$는 기록과 상대 $3\times10^{-4}$ 안에서 같다.

`세션_재계산/band_LP/`는 부록 D의 띠 정리들의 유한 확인과 선형 최소화 항목 네 부분을 구간 산술로 다시 계산한 것이다(2026-11-13 세션). `bandlib.py`가 공용 식, `part_ga_na.py`·`part_da.py`·`part_ra.py`가 (가)·(나), (다), (라)이고 출력은 `out_*.txt`다. 닫힌 꼴 스칼라는 mpmath `iv`(소수 30자리), $t$에 걸친 벡터는 binary64 numpy 위의 바깥 반올림 구간이다(사칙연산은 결과를 1 ulp 바깥으로 밀고, $e^x$·$e^x-1$·$\log(1+x)$는 numpy 초등함수를 부르지 않고 Taylor·artanh 급수에 나머지 항의 구간을 더해 만들며, 누적합은 Higham 한계로 넓힌다). `xcheck_mp.py`가 표본점을 `iv`만으로 대조하고, `elem_check.py`가 그 급수 포위가 표본점마다 mpmath 40자리 값을 담는지를 확인한다. `ulp_check.py`는 numpy 초등함수 자체의 오차를 잰 참고 자료이고 계산에는 들어가지 않는다. (라)의 선형 최소화는 LP 쌍대 가능해로 아래에서 막는다.

`세션_재계산/bprime_boxes/`는 부록 D의 첫 조립의 상자 검사 항목(140,729개 유한 상자와 꼬리 상자)을 구간 산술로 다시 계산한 것이다. 스칼라는 mpmath `iv`(소수 34자리), 리만 합 벡터는 binary64의 정확 반올림 사칙연산·제곱근만 써서 1 ulp 바깥 밀기와 합의 $1-10^{-11}$ 인자로 아래로 민다. `ivbox_lib.py`가 공용 구간 성분, `bprime_iv.py`가 계산, `bprime_summary.py`가 요약이며 `compare_record.py`가 기록의 상자 값과 대조한다. $\Omega$의 하계는 `window_mass_env/ia.py`의 정확 정의(격자 $i\mathsf K^{-2/3}$·절점값·Fritsch–Carlson 기울기의 구간)에서 조각별 3차 계수의 바깥 괄호를 만들어 쓰며 조각별 비증가를 구간으로 확인한다(`test_lib.py`→`test_lib_out.txt`가 기록의 binary64 함수와 대조). 저장된 봉투 표 $\hat{\mathcal T}$는 저장값을 정확한 점 $\xi^{\mathcal T}_i=0.0005\,i$에 둔 선형 보간으로 읽는다.

`세션_재계산/band_boxes/`는 부록 D의 띠 정리의 상자 검사 항목을 같은 구간 산술로 다시 계산한 것이다. 상자 안의 모든 경우 가름과 되먹임 폭의 점별 범위를 함께 고려해 식 (8.30) 자체를 아래에서 막는다. `band_iv.py`가 계산, `band_summary.py`가 요약, `run_all.sh`가 실행 순서이고, `compare_record.py`가 기록의 상자 값과 대조한다. $\Omega$는 `bprime_boxes/ivbox_lib.py`를 통해 같은 정확 정의를 쓴다. 두 폴더의 재실행 순서는 `세션_재계산/rerun_exactgrid_1116.sh`다.

`세션_재계산/window_mass_env/`는 부록 D의 창의 수준 질량 하계 항목의 셀 검사((가) $q\le2999$, (나) 구간 열일곱 개)를 구간 산술로 다시 계산한 것이다(2026-11-13 세션). `ia.py`가 바깥 반올림 구간(binary64의 정확 반올림 사칙연산·제곱근만 사용)과 $\Omega$의 Hermite 조각·봉투 표·정확 표(mpmath `iv` 25–40자리)를 만들고(세 제타 상수 $\zeta(\frac12)$, $\zeta(-\frac12)$, $\zeta(\frac32)$는 `zeta_constants/zeta_iv_out.txt`의 인증 구간을 바깥쪽으로 넓혀 넣는다), `cert_interval_iv.py`·`cert_Cb_iv.py`가 두 검사를 돌리며, `check_table_iv.py`가 저장된 봉투 표의 하계 조건을 다시 확인하고, `test_ia.py`가 기록의 값이 구간 안에 듦을 확인한다. 출력은 `*_out*.txt`와 `*_result*.json`, 요약은 `summarize_out.txt`.

`세션_재계산/H_star_plus/hplus_interval.py`는 부록 D의 머리 합 여유 정리 항목의 기록 코드([r33475a7] `evidence/peer2/scripts/hplus_interval.py`) 사본에 `mpmath.mp.dps = 30` 한 줄을 더해 두 끝값 $\upsilon_1$, $\upsilon_2$가 53비트로 다시 반올림되지 않게 한 것이다(2026-11-13 세션). 출력 `hplus_interval_out.txt`는 기록과 같은 세 상계를 준다.

`세션_재계산/critical_window_rerun/`은 부록 D의 임계 창 인증 항목의 44개 상자를 이 글의 코드로 다시 돌린 것이다. `rig_*.py`·`ivio.py`가 계산 코드, `orig/`가 기록의 원본, `boxes.py`·`common.py`·`rerun_boxes.py`·`launch_rerun.py`·`recert_first.py`·`postrun.py`가 상자 모임·실행기·기동기·첫 셀 재인증·뒤처리 기동기다. 이 글의 코드가 기록의 코드와 다른 넷(실수축 나머지의 지수 상수, $\hat x$ 셀의 격자, 둘러싸기 식 세 곳, $(e^w-1)/w$의 1·2계 도함수 급수의 계수)은 부록 D 항목의 「독립 재계산」에 적혀 있다. $\hat x$ 셀은 십진 격자 $[1.4+0.2i,1.6+0.2i]$를 품는 바깥 구간으로 두고 Taylor 중심·반지름이 셀을 품게 하며 끝점·중심·반지름·여유를 정확한 이진값으로 저장한다. `verify_exact_cover.py`는 저장된 인증서만 읽어 $\mathrm{ku}$ 타일링과 $\mathrm{ku}_{\mathrm{top}}^3\cdot10001\ge1$, 셀의 격자 포함, Taylor 영역의 셀 포함, 여유의 양수성을 허용 오차 없는 유리수로 검사한다(출력 `verify_exact_cover_out.txt`). 인증서는 `cert/`, 상자 자료는 `cache/`, 실행 기록은 `logs/`, 요약은 `summarize.py`→`summary_out.txt`, `_test_exact_grid.py`는 두 셀 시험, `check_fixes.py`→`check_fixes_out.txt`는 코드 자체 검사(둘러싸기의 포함, 급수 상수, 감마 상계, 상자 모임)다.

`세션_재계산/band_check/`는 부록 D의 띠 검사 항목을 이 글의 입력 인자($\mathsf w_0=0.71216$, 우변에 더하는 항의 계수 $0$, 소구간 $4000$개)로 다시 돌린 것이다(2026-11-13 세션). `band_cells.py`는 항목의 식에서 새로 쓴 구간 판정(소구간 끝점은 정확한 유리수, mpmath `iv` 30자리)으로 부록 D 항목의 「결과」가 기대는 코드이고, `python -I band_cells.py 0.71216 0 4000 band_cells_CE0.tsv`가 소구간별 비의 하계 표 `band_cells_CE0.tsv`를 내고 그 최솟값을 표준 출력에 적는다(`minimum ratio lower bound = 1.35587396520276 at cell 0`). `band_read.py`는 `python -I band_read.py band_cells_CE0.tsv band_iv_out_CE0.txt`로 그 표의 덮개·문턱·최솟값을 읽어 기록 코드의 출력과 대조한다(출력 `band_read_out_CE0.txt`: 최솟값 $1.3558739652$, 문턱 $1.3558$ 대비 여유 $7.4\times10^{-5}$). `band_iv.py`는 기록 [r8a9b11e] `evidence/peer/band_iv.py`의 바이트 사본이고, `python -I band_iv.py 0.71216 0 4000`의 출력은 `band_iv_out_CE0.txt`(최소 비 $1.355874$, 첫 소구간 $[1/2,12001/24000]$)로 표시 자리에서 위와 일치한다.

`세션_재계산/m1_column_reading/m1_read.py`는 부록 D의 열 판독 항목에서 기록 [r19de912]의 행 자료 `v2run20000-rows.tsv`를 새로 쓴 판독기로 읽어 증가 구간의 연속성, 두 문턱 판정식, $m_1'(k)$의 최댓값, 봉우리 위치의 일치를 다시 확인한 것이다(2026-11-13 세션). 출력은 `m1_read_out.txt`.

`세션_재계산/r89eb039_polar_block_audit/`는 부록 D의 극 영역 488개 $k$-구간 항목에서 마지막 $k$-구간 $[9843156,10^7]$의 상하계를 세 $k$($9843156$, $9921578$, $10^7$)의 참값과 $135$개 항목씩 대조한 것이다(2026-11-13 세션; 기록의 검토가 다른 다섯 $k$-구간에 쓴 `block_vs_truth.py`의 방법). `block_vs_truth_9843156.py`가 대조, `truth_accuracy_check.py`가 참값 계산의 오차 측정(항별 $1.5\times10^{-14}$ 이하)이고, 결과는 `bvt_block_9843156_10000000.txt`·`.json`이다. $135$개 모두 상하계 안이며 가장 얇은 상대 여유는 $6.3\times10^{-7}$이다.

`세션_재계산/fiber_exhaustive/fiber_exhaustive.py`는 부록 D의 섬유 전수 항목에서 $n\le7$의 선호 수열 $n^n$개를 곱 공식 없이 직접 주차시켜 주차함수의 수, 결과 순열의 섬유 행, 용량 다중집합의 수, 섬유 행의 단봉성($n\le6$ 전부 단봉, $n=7$에서 비단봉 섬유 30개)을 다시 센 것이다(2026-11-13 세션). 출력은 `fiber_exhaustive.txt`.

`세션_재계산/cumulative_logconcavity_n779/lca_exact.py`는 부록 D의 누적 로그오목성 항목에서 마지막 차 재귀를 파이썬 큰 정수로 새로 구현해 $n\le800$의 모든 $(n,\ell)$에서 $A_{n,\ell}^2-A_{n,\ell-1}A_{n,\ell+1}$의 부호를 정확히 판정한 것이다(2026-11-13 세션; 두 프로세스 `part1.json`·`part2.json`). 위반 390개의 집합이 기록과 같고 $n\le779$에 위반이 없으며 $n=780$의 위반은 $\ell=575$–$578$이다. 요약은 `lca_exact_N800.txt`, 위반 목록은 `lca_violations_N800.json`.

`세션_재계산/newton_r61_169/newton_cert.py`는 부록 D의 Newton 인증 항목에서 4.2절의 정의로 $\Gamma_d$, $\mathrm{hg}_d$, $\mathrm{sd}_d$, $\mathrm{Nw}_{r,d}$를 새로 구현해 $2\le r\le170$의 다항식 14,365개 전부에서 $\mathrm{nv}=0,\dots,2r+2$의 정확한 정수값과 전진 차분이 음이 아님을 확인한 것이다(2026-11-13 세션; 실패 0). 출력은 `newton_cert_out.txt`(r마다 한 줄).

`세션_재계산/c50_iv/`는 부록 D의 $20001\le n\le50000$의 오른쪽 절반 인증과 $n\le20000$의 재인증 항목을 본문의 마지막 차 재귀에서 새로 쓴 C 프로그램 `c50iv.c`로 다시 인증한 것이다(2026-11-13 세션). 아래 끝은 아래 반올림 패스, 위 끝은 위 반올림 패스로 따로 계산하는 binary64 방향 반올림 구간이고, 표 $\mathrm{Bor}$·$\mathrm{hB}$는 `make_tables_iv.py`가 mpmath `iv` 40자리로 포위해 바깥 반올림한 이진 표다. 빌드는 `build.bat`(MSVC `/O2 /fp:strict /arch:AVX /openmp`; 어셈블리에 FMA 명령이 없음을 확인). `runs/`에 C20·C50의 요약과 행 파일, $n\le300$의 정확 정수 대조(`exact_small.py`), 넘는 수 재귀 참조 대조(`probe_undercount.py`)의 출력이 있다. 명령은 `run_commands.txt`. 미결 위치 0, 최대 상대 폭 $2.25\times10^{-12}$.

`세션_재계산/r89eb039_polar_iv/`는 부록 D의 극 영역 488개 $k$-구간 항목을 라이브러리 함수 가정 없이 다시 인증한 것이다(2026-11-13 세션). `ia.py`가 binary64 정확 반올림 사칙연산·제곱근 뒤 한 ulp 바깥 밀기의 구간 산술과, 그 연산만으로 만든 초월함수(exp·log·log1p·expm1·cos·sin·반정수 거듭제곱; 상수는 유리수 포위)를 제공하고, 기록 코드의 모든 단계(Poisson 기댓값, $\mathcal L^{\mathrm T}(\theta)$, 묶음 가중, $\eta$의 뺄셈, 행렬곱, 합)를 구간으로 바꾼 사본(`sparts.py`, `cert_fast.py`, `cert_ia2.py`, `recert.py` 등)과 $k\ge10^7$ 연쇄의 구간판 `achain_iv.py`가 있다. 결과는 `out/NEW_blocks_merged.jsonl`(488개 $k$-구간 모두 통과), `out/achain_iv.jsonl`(2472구간), 요약 `out/summary.txt`, 상수 확인 `out/consts_check.txt`, 초월함수 포위 검사 `out/test_ia.txt`다.

`세션_재계산/logconcavity_n80/lc_n80.py`는 부록 D의 행 로그오목성 항목(`D.{{D:logconcavity-failure-n80}}`)을 짧게 다시 확인하는 정확 정수 검산이다(2026-11-13, 이 글). 마지막 차 재귀로 $0\le\ell\le79$의 모든 열을 $n\le80$까지 파이썬 정수로 계산하고(포화값으로 채우지 않는다), 행마다 $\sum_\ell b_{n,\ell}=(n+1)^{n-1}$과 $A_{n,0}=n!$을 확인한 뒤 모든 내부 첨자에서 $b_{n,\ell}^2\ge b_{n,\ell-1}b_{n,\ell+1}$을 정수 비교로 판정한다. 깨지는 자리는 $(n,\ell)=(80,40)$ 하나이고 $n\le79$에는 없다. 세 정수 $b_{80,39}$, $b_{80,40}$, $b_{80,41}$은 부록 D 결과 줄의 값과 같고, 유리수 분리자 $25928/25000$의 두 교차곱 부등식도 성립한다. 출력은 `lc_n80_out.txt`(약 1초).

`세션_재계산/column_cert_iv/`는 부록 D의 열 841–2000 열별 갱신 인증서 항목을 라이브러리 함수 가정 없이 방향 반올림 구간으로 다시 계산한 것이다(2026-11-13 세션). `colcert_iv.py`가 열 $501\le k\le2000$마다 정리 G′의 조건 (a′)(b′)(c′)를 확인한다: 소인 질량과 창 계수의 양의 재귀는 아래 끝·위 끝 두 줄의 binary64 구간(연산마다 바깥 밀기, 내적은 짝지은 합 나무와 끝의 $(1\mp2^{-53})^{-(d+1)}$ 인자), 원 위의 격자값은 `ivlib.py`의 자기 구현 구간 FFT(실부·허부 상자, 회전 인자는 mpmath `iv` 표), 주편각은 $\arctan$ 포위, 스칼라 조립은 mpmath `iv` 소수 40자리다. $k$에 무관한 표(Borel 수, $n\le2000$의 소인 질량, 회전 인자)는 `tables.py`가 `_cache/bor_pr0.npy`·`_cache/twiddle_2p21.npy`로 만든다(약 1.5분; 33 MB라 묶음에 넣지 않고 다시 만든다). 실행은 `python -I colcert_iv.py --ks 841-2000 --part 0 --nparts 2 --batch 16 --out res_p0.jsonl`과 `--part 1`(각 2.9시간), 열 501–840은 `--ks 501-840 … --out res_ext_p0.jsonl`과 `--part 1`(각 16분)이다. 열별 성분과 판정은 `res_*.jsonl`(binary64 값을 왕복 가능한 전체 자리로), 실행 기록은 `run_*.log`, 요약은 `summary.py`(`summary_all_out.txt`: 1500열 모두 성공, 최소 $\mathfrak b_0=0.03478$, 최소 여유 $0.02722$, $V$ 위 끝은 저장값 곱의 $1.000007$배 이하), 기록 검토의 40자리 값과의 대조는 `crosscheck_review.py` → `crosscheck_review_out.txt`, numpy FFT와의 대조는 `test_841.txt`·`test_1171.txt`·`test_2000.txt`다. `make_draft.py`는 결과에서 부록 D 항목 본문을 만든다.

`세션_재계산/moment_cert_iv/`는 부록 D의 모멘트 판정 항목 (ㄱ)(두 범위의 재귀 인증)을 구간 산술로 다시 계산한 것이다(2026-11-13~15 세션). `mcert_iv.py`는 재귀 (7.2)·(7.3)에 $\hat{\mathfrak a}_n$을 곱해 나눗셈 없는 네 양의 재귀로 바꾸고, 필요한 끝점만 binary64 구간으로 계산한다(아래 끝 $\hat{\mathfrak a}$, $\hat{\mathfrak a}\mathfrak Z^\flat$, $\hat{\mathfrak a}\mathfrak Z$; 위 끝 $\hat{\mathfrak a}$, $\hat{\mathfrak a}\mathfrak Z^{\mathrm H}$). 항목이 쓰는 본 실행은 BLAS 없는 연산 수 한계 판(`sweep_nb … --count`)이다. 각 합을 numpy 원소별 곱과 원소별 덧셈의 짝지은 나무로 계산하고 한 항이 겪는 반올림 횟수 $r$을 세어 끝에서 $(1\pm u)^r$로 넓히며, 저장값이 모두 $[2^{-400},2^{400}]$ 안임을 확인하고(벗어나면 척도 $\beta$를 고쳐 다시 돈다; (A3)는 짧은 선행 실행으로 미리 고친다), 스칼라 연산은 한 ulp 밖으로 민다. 초등함수와 기록의 binary64 판정식(부록 D 모멘트 판정 항목의 「식」 줄)은 쓰지 않고 $\mathbb E>0$을 직접 판정한다. 1500열 60,479,535개 위치 전부 통과(실패 0; (A5) 1160열은 프로세스 1개 `mcert_iv.py sweep_nb A5 sweep_ct_A5.jsonl --low --count`, (A3) 340열은 claim 파일로 열을 나눈 샤드 4개 `sweep_ct_mp.py A3 <i>`; 열별 소요 시간 합 219,744초(다른 계산과 코어를 나눠 써서 CPU 시간보다 길다); `sweep_ct_A5.jsonl`·`sweep_ct_A3_s0.jsonl`–`sweep_ct_A3_s3.jsonl`과 로그). `summarize_nb.py`→`summary_noblas.txt`(범위별 집계와 BLAS 판과의 판정 대조). 대조 실행으로, 같은 재귀의 합을 행렬곱으로 계산한 뒤 덧셈 순서·융합 여부와 무관한 한계 $(1\pm u)^{m+1}$($m=6n+3$)로 넓힌 판(`sweep 0 2`·`sweep 1 2`)이 기록의 다섯 실행 A1–A5(글이 쓰는 두 범위는 A3·A5이고, A1·A2는 어느 장도 쓰지 않는 추가 계산이다) 7619열 60,703,015개 위치에서 전부 통과했고(프로세스 2개로 약 2시간 10분, CPU 합 15,164초; `sweep_p0.jsonl`·`sweep_p1.jsonl`과 로그), 항목의 1500열에서 두 판의 열별 최솟값 하계는 상대 $1.1\times10^{-9}$ 안에서 같다. `summarize.py`→`summary.txt`(BLAS 판의 범위별 집계), `compare.py`→`compare_out.txt`(기록의 여덟 열 대조: 인쇄값이 모두 구간 안), `test_exact.py`→`test_exact_out.txt`(작은 열의 정확 유리수 포함), `test_count.py`→`test_count_out.txt`(연산 수 한계 판의 나무 깊이 검증, 작은 열의 포함 검사, BLAS 판과의 세 열 대조), `nM.py`→`nM.json`·`nM_out.txt`(열별 문턱 $n_{\mathrm M}(k)$의 정확 유리수 재계산; 1160열 모두 기록과 같음). `make_draft.py`·`make_draft_v2.py`는 결과에서 부록 D 항목 본문을 만든다. `handoff_A3.py`·`launch_handoff.py`는 (A3) 샤드의 기동 순서를 자동화한 운영 스크립트다.

`세션_재계산/column_k500_iv/`는 부록 D의 열 인증($121\le k\le500$) 항목을 이 글의 새 구현으로 380열 전부 다시 인증한 것이다(2026-11-13 세션). `lastcar_iv.py`는 세 재귀 G·H·E를 쓰지 않고 마지막 차 재귀 $n\mathfrak e_n=\mathfrak x\sum_j\min(j+1,y)\mathfrak e_j\mathfrak e_{n-1-j}$ 하나를 정확한 큰 정수 합성곱의 온라인 분할 정복(Kronecker 포장; 큰 크기는 `decimal`의 수론 변환, 부정확 반올림은 트랩)으로 160비트 고정소수점 정수 구간에서 계산하며, 반올림은 계수를 확정할 때 한 번(아래 끝은 내림, 위 끝은 올림)뿐이라 끝점이 직접 합과 비트 단위로 같다. 연속한 열 열 개가 하나의 정확한 이진 유리수 $\mathfrak x=e^{-1}(1+c/\bar k)$를 공유한다. `colk500.py`(`--worker i --nworkers 2`)가 열별 판정·최소 상대 여유·시간을 `res/k<k>.json`에 쓰고(380개; 해시 목록 `res/SHA256SUMS.txt`), `summarize.py`→`summary_out.txt`(380열 실패 0, 직접 차분 20,368,570개·띠 10,302,655개, 최소 상대 여유 $1.3778\times10^{-5}$($k=500$, $n=2k+1$)), `compare_indep.py`→`compare_indep_out.txt`(기록 검토의 다섯 열과 판정·최대 폭 일치, $k=121$은 모든 끝점 동일; 열별 최소 여유가 기록과 상대 $1.1\times10^{-35}$ 안), `test_small.py`→`test_small_out.txt`($n\le7$ 전수·$n\le120$ 정확 개수 포함, 분할 정복과 직접 합의 일치). 두 작업자 각 약 9500초(공유 기계, 벽시계 2.7시간; `run_w0.log`·`run_w1.log`). `make_draft.py`는 결과에서 부록 D 항목 본문을 만든다.

`세션_재계산/xcert_iv/`는 부록 D의 유한 크기 전달 정리의 다섯 범위 인증 항목을 binary64 사전 오차 해석 대신 방향 반올림 구간 산술로 다시 계산한 것이다(2026-11-14 세션). 사칙연산·제곱근은 결과를 1 ulp 바깥으로 밀고, 음이 아닌 합·내적(BLAS 포함)은 $4(n+2)2^{-53}$로 바깥으로 밀며, 초등함수는 numpy·libm을 쓰지 않고 나머지 항을 넣은 Taylor·atanh 급수로 감싼다(`ivv.py`; 상수는 mpmath `iv`). 원 위의 격자값은 `midfft.py`의 중점–반지름 FFT로 단마다 사후 오차 상계를 갱신한다(`column_cert_iv`의 상자형 구간 FFT와의 대조는 `crosscheck_fft.py` → `crosscheck_fft.txt`). 공용 식은 `common.py`, 점근 범위의 식은 `asym_iv.py`, $k$에 무관한 표는 `tables_iv.py`다(`ivlib.py`·`tables.py`·`colcert_iv.py`는 `column_cert_iv`의 사본). 범위별 코드는 `layerB.py`(범위 1 $[501,5000]$; `--ks 501-5000 --part 0/1 --nparts 2`), `layerAint.py`(범위 2 $[5000,10^5]$)·`layerA1.py`(범위 3; 두 프로세스가 `--idx`의 번호 범위를 받아 구간마다 요구 파일(`_claims/`)을 먼저 만든 쪽이 맡는 방식으로 나누어 돌렸고, 명령과 조각 파일의 대응은 부록 D 항목의 「자료」 줄에 있다), `layerA2.py`(범위 4), `layerA3.py`(범위 5)이고(파일 이름의 B·Aint·A1–A3은 기록의 실행 이름), 열·구간별 성분과 판정은 `res*.jsonl`·`resA3.json`, 실행 기록은 `run*.log`, 실제 실행 순서는 `run_slot2.sh`·`run_slot1_after.sh`다(프로세스 2개로 벽시계 약 9.6시간). `summarize.py`는 `summary.txt`·`summary.json`을 만들며 범위별 성공 구간의 합집합이 $[501,\infty)$를 빈틈없이 덮는지도 확인한다(다섯 범위 전부 통과, 최대 $R_U$ 1.938978, 최소 여유 0.0610). `test_ivv.py`·`testA2.py`와 `test*.txt`는 시험 실행이다. `make_draft.py`는 결과에서 부록 D 항목 본문을 만든다. `tables_iv.py`가 만드는 표 `_cache/tables_iv.npz`는 처음 실행 때 저장해 두고 그 뒤에는 읽는 캐시이며, `column_cert_iv/_cache/`와 같이 묶음에 넣지 않고 다시 만든다.

`세션_재계산/left_columns_k2_120/`는 부록 D의 모든 $n\le20000$의 단봉성 항목 (ㄱ) 가운데 열 $2\le k\le120$($\max(2k+1,12)\le n\le10000$)을 기록 [rc9aee43]의 열 인증 코드(`code/positive_columns.py`, 바이트 그대로의 사본)의 열 계산으로 다시 인증한 것이다(2026-11-15 세션). `code/left_columns.py`가 용량 $1\le c\le121$의 열을 열별 이진 유리 반지름(`code/radii.json`)으로 한 번씩 계산하고 이웃 세 열을 정확한 유리수 배율의 구간으로 한 반지름에 맞추어 비교하며, 출력은 `results_k2_70.jsonl`·`results_k71_120.jsonl`과 `summary.json`(비교 1,175,466개, 실패 0, 최소 상대 여유 $1.2608\times10^{-4}$, $k=6$, $n=13$)이다. `code/exact_check.py`→`exact_check.json`은 $n\le300$의 정확 정수(정리 2.6의 재귀)와 전수 대조, `indep/`는 기록의 독립 프로그램 `indep_lastcar.py`(사본)와 그 재귀로 최소 여유를 재는 `indep_margin.py`를 표본 열 $k\in\{2,3,7,30,60,120\}$에 돌린 것이다. 첫 실행(범위 $2k+1$부터; $n=5,7,9,11$의 네 예외가 드러남)의 결과는 `logs/firstpass/`에 있다.

`세션_재계산/witness_offset_iv/`는 부록 D의 모든 $n\le20000$의 단봉성 항목 (ㅂ), 곧 명제 witness-position-bound(5.1절)가 확인하는 증인 위치 차 $n+1-\ell^\ast_n-0.59963(n+1)^{2/3}-1.24847(n+1)^{1/3}$을 기록 [r19de912]의 행 자료(자료 묶음의 사본 `r19de912/evidence__peer__cert__v2run20000-rows.tsv`의 봉우리 열 `mode_ell_mid`)에서 방향 반올림 구간(mpmath `iv`, 소수 30자리)으로 다시 계산한 것이다(2026-11-15 세션). 기록의 계산 `mode_offset.py`는 binary64 최근접 반올림의 배정밀도 평가였다. `code/witness_offset_iv.py`는 두 상수를 십진 문자열의 구간으로, 두 지수 $2/3$·$1/3$을 정수 나눗셈의 구간으로 두고 두 범위 $50\le n\le900$·$901\le n\le20000$마다 구간 아래 끝의 최솟값과 위 끝의 최댓값을 이진 유리수 그대로의 분수와 소수 열다섯 자리(아래 끝 내림·위 끝 올림)로 `witness_offset_iv.json`에 적고, 진술의 구간 $[0.85,1.99]$ 안에 드는지를 정확한 유리수 비교로 판정한다(두 범위 $[0.889979773145161,1.986242781217464]$·$[0.850826875264814,1.875832792791377]$, 모두 안에 듦, 최소 여유 $8.27\times10^{-4}$, 구간 폭 $7.5\times10^{-28}$ 이하, 약 10초). `code/summarize.py`가 부록 D 항목과 재실행표에 적는 꼴(바깥쪽 세 자리 $[0.889,1.987]$·$[0.850,1.876]$)로 요약하고, 실행 명령·시각·환경은 `logs/commands.txt`, 설명은 `README_run.md`에 있다.

`세션_재계산/icert_py_full/`는 부록 D의 가운데 증가의 정수 인증 항목의 독립 재계산, 곧 기록 검토의 Python 큰 정수 구현 `rev_icert_unpaired_fast.py`(사본; `CERT` 경로 한 줄만 기록 사본으로 바꿈)를 $1001\le k\le10000$의 9000열 전부에 돌려 `icert.c`의 출력 `out_8_10000.txt`와 비트 단위로 대조한 것이다(2026-11-13~16 세션). `worker.py W i`가 작업자 $W$개 가운데 $i$번째 몫을 100열 묶음으로 자식 프로세스에 돌리고 묶음마다 `out_<k1>_<k2>.txt`에 열별 JSON 한 줄(`k`, `bit_identical_to_C`, `ok`, `sec`)을 남기며, `launch.py W`가 작업자를 띄우고(`launches.txt`에 이력, 끊긴 묶음의 `.part`는 완결된 줄만 거둠) `stop.py`가 멈춘다. 작업자 1→4→2→3개로 돌리다 2026-11-15 13:51 멈추고 21:00 4개로 다시 띄워 2026-11-16 08:01 끝났다(정지 기간에는 자료 묶음 밖의 세션 구현이 같은 열의 잠정 판정을 냈고, 원본의 결과와 열마다 같다). `summarize.py`→`summary.json`: 9000열 전부, 결측 0, 비트 불일치 0, `ok` 거짓 0, 중복 0, 열별 시간 합 573,393.5초(159.28시간; 다른 계산과 코어를 나눠 쓴 구간이 있다), 출력 파일 96개, 열당 최대 421초($k=9537$). `make_draft.py`는 `summary.json`이 완결일 때만 부록 D 항목의 자리표시자 셋을 채운 초안을 만든다. `README_run.md`에 실행·정지·재기동 기록이 있다.

## 파일 목록

| 경로 | 출처(기록·원 경로) | 부록 D 항목 | SHA-256 |
|---|---|---|---|
| `r030ffae/FIXED_cert_Cb_1_2080.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_1_2080.out` | window-mass-env | `fbdbc0d9c6e41cc3d06c5497842aaa645c98d471e2ef4574f17d68de54bac29d` |
| `r030ffae/FIXED_cert_Cb_2080_2621.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_2080_2621.out` | window-mass-env | `3e11d73a425ac6e47ceae21c610fc6c0aa1268b8b30370c60f4fed8a2e2d9ca4` |
| `r030ffae/FIXED_cert_Cb_2621_3000.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_2621_3000.out` | window-mass-env | `53443ba751bd73925874a66c24d7fbd7ec67301d60a958f1dc5443f67fcf5af9` |
| `r030ffae/FIXED_cert_Cb_result_1_2080.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_result_1_2080.json` | window-mass-env | `d53f5100782f83c3f43656a79c924aa2dd424ba4dd6632bb6fc7613dd04dc3cf` |
| `r030ffae/FIXED_cert_Cb_result_2080_2621.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_result_2080_2621.json` | window-mass-env | `a184fbaf9dae626c7021ab009fc0c699a2df1b351bb79a632b992641d1c7e7b2` |
| `r030ffae/FIXED_cert_Cb_result_2621_3000.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_result_2621_3000.json` | window-mass-env | `f9ebcaad8c969d4103fc63c1592136821bcc282956b5956a03a85fc2820829b0` |
| `r030ffae/FIXED_cert_assembly_U_3.6_run2.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_assembly_U_3.6_run2.out` | bprime-boxes | `95619f98dfc2afa1bf0bba867a0303c6b3b9eb3d144770bc7f7a0ed41ec6ce0c` |
| `r030ffae/FIXED_cert_assembly_result_U_X3.6_k6668.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_assembly_result_U_X3.6_k6668.json` | bprime-boxes | `929768aa7443f9600b8c7ef5628bb002133c925707c4a3bbed1e9eb0983e6229` |
| `r030ffae/FIXED_cert_interval.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_interval.out` | window-mass-env | `fd3fa7a870f7cef03f04059b336be837756859f3f751b2fc6dad130ad141378d` |
| `r030ffae/FIXED_cert_interval_result.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_interval_result.json` | window-mass-env | `b039497680fb1f0ebac2d44701d1a14394b0f0ecb0b8ac4856fc18b56336363d` |
| `r030ffae/LOWH_cert_assembly_T0.48_k6668.out` | [r030ffae] `evidence/peer/rerun/work/LOWH_cert_assembly_T0.48_k6668.out` | band-boxes | `c36cbe45437af3890dda5af0ed370314f7ecdc6136a0b63059f8fb8e89490c2e` |
| `r030ffae/REVIEW_Bprime_3.6.out` | [r030ffae] `review/evidence/REVIEW_Bprime_3.6.out` | bprime-boxes | `4f1c6e5841ec9d134fb0888e1e83c938eb26f4c5ade436dbcd4dd8c6a5d44504` |
| `r030ffae/REVIEW_LOWH_T0.48_k6668.out` | [r030ffae] `review/evidence/REVIEW_LOWH_T0.48_k6668.out` | band-boxes | `9084778d9d65294cd58343a763d5d6e7221eaf10b97f39e4c7eb27bbf051eccf` |
| `r030ffae/build_env_fixed.py` | [r030ffae] `evidence/peer/rerun/work/build_env_fixed.py` | window-mass-env | `c1396fd7d3d982ca0c4ce8d0758785e6015711faf3fcb9e2c5a35ac4a1cd2c68` |
| `r030ffae/cert_Cb_range.py` | [r030ffae] `evidence/peer/rerun/work/cert_Cb_range.py` | window-mass-env | `895e2fac0f7f86fae7a977f7306dc2ae6bc2936386f74446989e6fb14707f0e2` |
| `r030ffae/cert_assembly_fixed.py` | [r030ffae] `evidence/peer/rerun/work/cert_assembly_fixed.py` | bprime-boxes | `819928c1bc0309e247d74c57b8b7354a7d203e96cfd5ecb0166d09d0ebaf6f1f` |
| `r030ffae/cert_assembly_lowH.py` | [r030ffae] `evidence/peer/rerun/work/cert_assembly_lowH.py` | band-boxes | `26f2e8989cfa86fb6b83c71dc6885e20294d01dc1d834fcbd0f9b7d0a15c4f6c` |
| `r030ffae/cert_assembly_mono.py` | [r030ffae] `evidence/peer/rerun/work/cert_assembly_mono.py` | band-boxes | `d5e3c4ec4fbee044fafb11c507765317bb2be83a909fd7f8bfba023f721966bd` |
| `r030ffae/cert_lib.py` | [r030ffae] `evidence/peer/rerun/work/cert_lib.py` | window-mass-env | `0ff3452340fdcf81dde638f29a8d0c7b3bb7fd905a7d4eecc31d1065b26ccb87` |
| `r030ffae/cert_lib_fixed.py` | [r030ffae] `evidence/peer/rerun/work/cert_lib_fixed.py` | window-mass-env | `18bbfcfe0a370fce8cf50015011ffb35538b118addf7897fa43bfbeef97402e7` |
| `r030ffae/check_BV.out` | [r030ffae] `evidence/peer/check/check_BV.out` | bprime-boxes | `3d8bc7b1870a2cd786c34ed526573568f5c39a2c3abdb9c5a65911dd21c5bdcc` |
| `r030ffae/check_BV.py` | [r030ffae] `evidence/peer/check/check_BV.py` | bprime-boxes | `6fa99d2a18e851345dfd0c36bb9676ae563ccbf59a86122d806f6e319bd40c79` |
| `r030ffae/design.json` | [r030ffae] `evidence/peer/rerun/work/design.json` | window-mass-env | `5ca7ca94ea05873420053508c14ddec9562d60fb18c65d7ed2173afc0c12da7f` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_v.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_v.npy` | band-boxes | `64402ee14c829cdf9c8ffe4ce30796c03b4b56cd3329a7af5c7679150a097869` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_v.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_v.npy` | bprime-boxes | `64402ee14c829cdf9c8ffe4ce30796c03b4b56cd3329a7af5c7679150a097869` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_v.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_v.npy` | stored-table-check | `64402ee14c829cdf9c8ffe4ce30796c03b4b56cd3329a7af5c7679150a097869` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_x.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_x.npy` | band-boxes | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_x.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_x.npy` | bprime-boxes | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_x.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_x.npy` | stored-table-check | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
| `r030ffae/evidence__peer__rerun__work__wKrig.npy` | [r030ffae] `evidence/peer/rerun/work/wKrig.npy` | band-boxes | `8e047df2647393e22c7fbfb157fd1dcfa9de2bdd25aa06f6586ad603d52eb609` |
| `r030ffae/evidence__peer__rerun__work__wKrig.npy` | [r030ffae] `evidence/peer/rerun/work/wKrig.npy` | bprime-boxes | `8e047df2647393e22c7fbfb157fd1dcfa9de2bdd25aa06f6586ad603d52eb609` |
| `r030ffae/evidence__peer__rerun__work__xKrig.npy` | [r030ffae] `evidence/peer/rerun/work/xKrig.npy` | band-boxes | `16f6fbc8fa801ba6e4e66e6336d943a0736096d00940406a300c599eda724287` |
| `r030ffae/evidence__peer__rerun__work__xKrig.npy` | [r030ffae] `evidence/peer/rerun/work/xKrig.npy` | bprime-boxes | `16f6fbc8fa801ba6e4e66e6336d943a0736096d00940406a300c599eda724287` |
| `r030ffae/exact_lib.py` | [r030ffae] `evidence/peer/check/exact_lib.py` | bprime-boxes | `310ab79bc4d3da780634d354a05752597963541c93cb4ea84495f688068cddaf` |
| `r030ffae/fixes.py` | [r030ffae] `evidence/peer/rerun/work/fixes.py` | window-mass-env | `36c741e815fe403c9551c5accb4a08717b7895270f0a5467f9a0161be0b6ee9f` |
| `r030ffae/qenv_fix_v.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_v.npy` | window-mass-env | `64402ee14c829cdf9c8ffe4ce30796c03b4b56cd3329a7af5c7679150a097869` |
| `r030ffae/qenv_fix_x.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_x.npy` | window-mass-env | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
| `r030ffae/review/evidence/REVIEW_Bprime_3.6.out` | [r030ffae] `review/evidence/REVIEW_Bprime_3.6.out`(패턴 `review/evidence/REVIEW_*.out`) | window-mass-env | `4f1c6e5841ec9d134fb0888e1e83c938eb26f4c5ade436dbcd4dd8c6a5d44504` |
| `r030ffae/review/evidence/REVIEW_Cb_1_60.out` | [r030ffae] `review/evidence/REVIEW_Cb_1_60.out`(패턴 `review/evidence/REVIEW_*.out`) | window-mass-env | `08bcc0de62ce81be7fc2cb042e4b6413bd4ac21bef85b98429b607d0d2d7f1ea` |
| `r030ffae/review/evidence/REVIEW_Cb_2980_3000.out` | [r030ffae] `review/evidence/REVIEW_Cb_2980_3000.out`(패턴 `review/evidence/REVIEW_*.out`) | window-mass-env | `fea0d8a4fa9350d026207878a3fce3f92f0455bab478334fff959b384498e19a` |
| `r030ffae/review/evidence/REVIEW_LOWH_T0.48_k6668.out` | [r030ffae] `review/evidence/REVIEW_LOWH_T0.48_k6668.out`(패턴 `review/evidence/REVIEW_*.out`) | window-mass-env | `9084778d9d65294cd58343a763d5d6e7221eaf10b97f39e4c7eb27bbf051eccf` |
| `r030ffae/review/evidence/REVIEW_build_env.out` | [r030ffae] `review/evidence/REVIEW_build_env.out`(패턴 `review/evidence/REVIEW_*.out`) | window-mass-env | `6faf3b139e86e4fd820ff644149aa8c7f2b7c21581cc702754bdd80e381362de` |
| `r030ffae/review/evidence/REVIEW_interval_0_0.out` | [r030ffae] `review/evidence/REVIEW_interval_0_0.out`(패턴 `review/evidence/REVIEW_*.out`) | window-mass-env | `751e8b36f818b7803d7a424c5cbcdb6c256e3ca069c4e2f0988aeedb37c21d40` |
| `r030ffae/review/evidence/REVIEW_interval_11_16.out` | [r030ffae] `review/evidence/REVIEW_interval_11_16.out`(패턴 `review/evidence/REVIEW_*.out`) | window-mass-env | `066b3461d0da8a1b88c0d2e4e2482bb76e0ab8baed09f2dff20073115d1dc06a` |
| `r030ffae/review/evidence/REVIEW_interval_part1_killed.out` | [r030ffae] `review/evidence/REVIEW_interval_part1_killed.out`(패턴 `review/evidence/REVIEW_*.out`) | window-mass-env | `30fbe774ac21bfa2b67cda35e2c9fbab79cae733c82032988c430f4877618bab` |
| `r030ffae/rv_checks.out` | [r030ffae] `review/evidence/rv_checks.out` | window-mass-env | `fe1cbdeb26d7ef69651205bce35e064d865ebabfe287793759bc008f2382c209` |
| `r030ffae/rv_checks.py` | [r030ffae] `review/evidence/rv_checks.py` | window-mass-env | `1bd1a31ca12a7612306c1d53e6f271bd337b49c5837a61694f0478cb7cf2191e` |
| `r030ffae/rv_exact.py` | [r030ffae] `review/evidence/rv_exact.py` | window-mass-env | `b3b81a125aaeddb7cb26f4f3a604d70925543b1b51f22894ecd535ec9518234d` |
| `r030ffae/wKrig.npy` | [r030ffae] `evidence/peer/rerun/work/wKrig.npy` | window-mass-env | `8e047df2647393e22c7fbfb157fd1dcfa9de2bdd25aa06f6586ad603d52eb609` |
| `r030ffae/window_lib.py` | [r030ffae] `evidence/peer/rerun/work/window_lib.py` | window-mass-env | `7a85805800f8b2242e0aa9229f077edfddd978420ec29aaa7c6f00218ad2ad5d` |
| `r030ffae/xKrig.npy` | [r030ffae] `evidence/peer/rerun/work/xKrig.npy` | window-mass-env | `16f6fbc8fa801ba6e4e66e6336d943a0736096d00940406a300c599eda724287` |
| `r051bfe1/check3.log` | [r051bfe1] `evidence/producer/check3.log` | tilt-sum-small-k | `1fb59db95ab6edaa5630d44a91bf448a39585983ca705af341da1751115586d5` |
| `r051bfe1/check3.py` | [r051bfe1] `evidence/producer/check3.py` | tilt-sum-small-k | `38e44a70a378e715359c39edfb38b8a3df50d373a5df5fdd648742dd006c9735` |
| `r051bfe1/peer_lemmaS.log` | [r051bfe1] `evidence/peer/peer_lemmaS.log` | tilt-sum-small-k | `e0d469938f87931ab02de4e9244d7f3d45e83cc90b4d662e61ac9fcdba4b15b2` |
| `r051bfe1/peer_lemmaS.py` | [r051bfe1] `evidence/peer/peer_lemmaS.py` | tilt-sum-small-k | `48801436c3709ae33f51eb41311c9a56b583e9b9aa920ef8ec46ebba900fe73c` |
| `r059f11e/exact_stream.py` | [r059f11e] `evidence/producer/code/exact_stream.py` | cumulative-logconcavity | `53ca266668f12cef08be704525a02c0bbe1b6def5fbbf62aea592de01336b55d` |
| `r059f11e/exact_stream_N800.json` | [r059f11e] `evidence/producer/data/exact_stream_N800.json` | cumulative-logconcavity | `28123d18c44d7609548f565f87c4ffbcc0cec4655947f5ceac850f16f079418e` |
| `r059f11e/exact_witness.py` | [r059f11e] `evidence/producer/code/exact_witness.py` | cumulative-logconcavity | `a1a6b38a93382a50835bc40fefc7f41f04dcafc3059fb8237b929deb441e2bf5` |
| `r059f11e/exact_witness_n779.json` | [r059f11e] `evidence/producer/data/exact_witness_n779.json` | cumulative-logconcavity | `49407214e316b586743397f5880c893c5e7f56cd807b6916c573e44f29335423` |
| `r059f11e/exact_witness_n780.json` | [r059f11e] `evidence/producer/data/exact_witness_n780.json` | cumulative-logconcavity | `f58b2fd97dcc201442ba1deff48221026d4b3ece88a6354276364e2578c7c2a0` |
| `r059f11e/lca_float_scan.py` | [r059f11e] `evidence/peer/lca_float_scan.py` | cumulative-logconcavity | `764a64c5fbc3405a95d88e2f3b62f4f0d62434f7e23f5bd33b6b92ae3ea2acd8` |
| `r059f11e/lca_float_scan_N800.json` | [r059f11e] `evidence/peer/lca_float_scan_N800.json` | cumulative-logconcavity | `5cbdb15f334058f4f167cdc4517726134461c5a9760a8c4fdc746908ecb210ef` |
| `r059f11e/lca_float_scan_N800.out` | [r059f11e] `evidence/peer/lca_float_scan_N800.out` | cumulative-logconcavity | `0714f02f4d3c84671c4388a25805db38debbaca1b39d6477c4224b992d9d2553` |
| `r059f11e/pk_exact.py` | [r059f11e] `evidence/peer/pk_exact.py` | cumulative-logconcavity | `78f31399588dc85d7a251857d47122ab9b4f5aea30192c539cbd2412d799c0fd` |
| `r059f11e/witness780.py` | [r059f11e] `evidence/peer/witness780.py` | cumulative-logconcavity | `eb80b36f709b49d995c1e76419c793f000839d35714a8aa0aea0ea01f6dd9d1b` |
| `r059f11e/witness780_peer.json` | [r059f11e] `evidence/peer/witness780_peer.json` | cumulative-logconcavity | `0b38810df2719b829c41606e15e923cc5eb4cfad302a26b81bba6dfd68399760` |
| `r0dc57fa/S_float.py` | [r0dc57fa] `evidence/peer/code/S_float.py` | tail-T1-partAB | `b80feaff5b160997bd1c62247dde95905b124ceff91a17257d54263a920d9a40` |
| `r0dc57fa/cert_tail_alpha1.py` | [r0dc57fa] `evidence/peer/code/cert_tail_alpha1.py` | tail-T1-partAB | `c127c67383aaea32f024ba997ec5da6fc181b5ba744c2c957159c7d0085ca9c6` |
| `r0dc57fa/cert_tail_alpha1_171_9999.json` | [r0dc57fa] `evidence/peer/data/cert_tail_alpha1_171_9999.json` | tail-T1-partAB | `16e76ff20368d8fff847d6bed1dcd8a908f71078dbb8a7adde75720e69a4df47` |
| `r0dc57fa/core_exact.py` | [r0dc57fa] `evidence/peer/code/core_exact.py` | tail-T1-partAB | `5acc9d8e951dfe8eb43446041e0288785feb41e77cbb43d98717ea09824a2a0b` |
| `r0dc57fa/t1_check.py` | [r0dc57fa] `review/evidence/t1_check.py` | tail-T1-partAB | `5261a85ccae07ccfff4d8eae1fc7a5597338a425fdfa80b9f7ef8206d5de7920` |
| `r0dc57fa/t1_check_out.json` | [r0dc57fa] `review/evidence/t1_check_out.json` | tail-T1-partAB | `59dd2dba516a4fd682bb223709d7b1c5db252277f7b30db6466707199b5a4f6b` |
| `r0dc57fa/tail_alpha_scan.json` | [r0dc57fa] `evidence/peer/data/tail_alpha_scan.json` | tail-T1-partAB | `b0b3a4cbe232110c7e709e9583d477f0945b7447976320492e5d9021fd00271b` |
| `r0dc57fa/tail_alpha_scan.py` | [r0dc57fa] `evidence/peer/code/tail_alpha_scan.py` | tail-T1-partAB | `291adb2e1aaefd54f6d51350a48f81e17595839c90b6be6fa8441bb246dffe3e` |
| `r10ff8c2/block3_501_2000_all.json` | [r10ff8c2] `evidence/peer/block3_501_2000_all.json` | moment-certification | `0fcac5fef27b255718bf15fd0a91b909d4424a795e7e3444ea43f173a31c21a6` |
| `r10ff8c2/brute.py` | [r10ff8c2] `evidence/peer/brute.py` | moment-certification | `7a6b3733cdcc7c9773b96e79f3dee32156f2b4ff238ca7fb13559c7b5e5124d7` |
| `r10ff8c2/c_results.txt` | [r10ff8c2] `evidence/peer/c_results.txt` | moment-certification | `df9445998924c14c0b63df35d17f33ba8fee884e131069a64ff1d7a38d456af4` |
| `r10ff8c2/coverage.py` | [r10ff8c2] `evidence/peer/coverage.py` | moment-certification | `8c5e93eaaff4c91700706583afb09dc7cffac6d8862b0cdded1ed17f3808ac0b` |
| `r10ff8c2/coverage_out.txt` | [r10ff8c2] `evidence/peer/coverage_out.txt` | moment-certification | `b53b6a0e9f8f1cc25283d7fe8135d15f02a4a3ddfe1654ddcd940a71c79aa0ae` |
| `r10ff8c2/evidence/producer/cert/band_A.txt` | [r10ff8c2] `evidence/producer/cert/band_A.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `2765705b6fe5afd7b39f907d869adea5723a2a994e7cb7d2c5595fd6ed88216d` |
| `r10ff8c2/evidence/producer/cert/band_B.txt` | [r10ff8c2] `evidence/producer/cert/band_B.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `b10ebca5c3d681a7656509ee95af564d7fd44a6c00b0a7c8210bba625d342452` |
| `r10ff8c2/evidence/producer/cert/extra_cols.txt` | [r10ff8c2] `evidence/producer/cert/extra_cols.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `1b5395e313b8f141bca1ab325cc3a905f603cbd4ca370277218b59344ed722fe` |
| `r10ff8c2/evidence/producer/cert/extra_k1200.txt` | [r10ff8c2] `evidence/producer/cert/extra_k1200.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `794c476741552ac35e16443f8e888dccc9729e621870dc4329c8a48b88ba36ce` |
| `r10ff8c2/evidence/producer/cert/extra_k1500.txt` | [r10ff8c2] `evidence/producer/cert/extra_k1500.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `27d737de7efe0cf48610e7f46f6496b6849a0efedef89f62553177b07597882a` |
| `r10ff8c2/evidence/producer/cert/extra_k1500b.txt` | [r10ff8c2] `evidence/producer/cert/extra_k1500b.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `09ce6dc1ef25e5003f846e80d3e0047a361511efd2cf6ca3cd88b22b56aa5ed1` |
| `r10ff8c2/evidence/producer/cert/full_501_800.txt` | [r10ff8c2] `evidence/producer/cert/full_501_800.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `06f97d5471a91f3b81e2983305b0caf0a27740dec0c3030bdcecedb640aa8d14` |
| `r10ff8c2/evidence/producer/cert/full_B1.txt` | [r10ff8c2] `evidence/producer/cert/full_B1.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `a2e8681d26ddcff2597daea679fed52167872cd61a5fe37949a57551ae3a8af9` |
| `r10ff8c2/evidence/producer/cert/full_B2.txt` | [r10ff8c2] `evidence/producer/cert/full_B2.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `65ddf768922752e6b69636cf74d0d26db7bcb84bfa549a91fc994c3fa3fcd60f` |
| `r10ff8c2/evidence/producer/cert/full_C1.txt` | [r10ff8c2] `evidence/producer/cert/full_C1.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `d14bb1f7256c75c11e9f491c9fa4529c5cdaac15177cf9082f3b541b9ab52d34` |
| `r10ff8c2/evidence/producer/cert/full_C2.txt` | [r10ff8c2] `evidence/producer/cert/full_C2.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `78ae8728198d22f996c5a3ef718c0bc3ab221e7fb6654395315b37a111a393a4` |
| `r10ff8c2/evidence/producer/cert/full_D1.txt` | [r10ff8c2] `evidence/producer/cert/full_D1.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `849aaad8478c0ae84cf3c3fa1560f9d574213be2829fdbd3bfaf139c29fdfb95` |
| `r10ff8c2/evidence/producer/cert/full_D2.txt` | [r10ff8c2] `evidence/producer/cert/full_D2.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `e1d18294213c17adc0be494756a24fe2a311e0a745408adf0d4db996dad3ea4e` |
| `r10ff8c2/evidence/producer/cert/full_E1.txt` | [r10ff8c2] `evidence/producer/cert/full_E1.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `2fe056a1533f825f41bbfe7debbfb407d233f3b4d13b8d9972125a2e4d275068` |
| `r10ff8c2/evidence/producer/cert/full_E2.txt` | [r10ff8c2] `evidence/producer/cert/full_E2.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `bd3c6cd685b396a336247f54699e1e8d1b07a7a1a1a1ade7b75306ef511af49d` |
| `r10ff8c2/evidence/producer/cert/wband_A.txt` | [r10ff8c2] `evidence/producer/cert/wband_A.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `0760d76ed6bcb5a4414482fc239db5f393926edaf634d9cf60a94928ef174178` |
| `r10ff8c2/evidence/producer/cert/wband_B.txt` | [r10ff8c2] `evidence/producer/cert/wband_B.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `da94ad6c44854617bae31553bfcd26e9f07c824bfbb381f6dec765cc10a8cab5` |
| `r10ff8c2/evidence/producer/cert/win_0.txt` | [r10ff8c2] `evidence/producer/cert/win_0.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `825c7df6d3249eb61db747d3bd287cef87dc11b892ced1a3b8e661983a6cdad9` |
| `r10ff8c2/evidence/producer/cert/win_1.txt` | [r10ff8c2] `evidence/producer/cert/win_1.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `f3eeee0cbef73c9e63c973c64db6dd90ff21368ad43ed9fd7b817ba6a19eeac1` |
| `r10ff8c2/evidence/producer/cert/win_2.txt` | [r10ff8c2] `evidence/producer/cert/win_2.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `0f5d9011aaf58f71c8e8f7a7a641db94c9afe79bf2b16183d094fe16038c5c01` |
| `r10ff8c2/evidence/producer/cert/win_3.txt` | [r10ff8c2] `evidence/producer/cert/win_3.txt`(폴더 `evidence/producer/cert/`) | moment-certification | `7f14d9dbad354afcea75b99e20a5a85e797011b15da79a95ceab34f37ade0513` |
| `r10ff8c2/evidence__peer__block3_501_2000_all.json` | [r10ff8c2] `evidence/peer/block3_501_2000_all.json` | column-certificates-841-2000 | `0fcac5fef27b255718bf15fd0a91b909d4424a795e7e3444ea43f173a31c21a6` |
| `r10ff8c2/exact_cols.py` | [r10ff8c2] `evidence/peer/exact_cols.py` | moment-certification | `2d6febab3aebc4f5422cd3abaf3c93be1f296830353b152eb761087947f1d058` |
| `r10ff8c2/identities.py` | [r10ff8c2] `evidence/peer/identities.py` | moment-certification | `7fbb74baa785a2c0682411321a689bcfa972219950ac3f22d3eb7a875b01ea1e` |
| `r10ff8c2/lmcert_sweep.c` | [r10ff8c2] `evidence/producer/lmcert_sweep.c` | moment-certification | `4203421474b9e2c6b6c9fde59cb1639e780ad7754c222aea36c04715f25ee74d` |
| `r10ff8c2/nj_summaries.txt` | [r10ff8c2] `evidence/peer/nj_summaries.txt` | moment-certification | `d87781d016a0b0afb15880bb4b8367ef205fa2fa0f094cce916f32cdd09dff88` |
| `r10ff8c2/notes_errors.md` | [r10ff8c2] `evidence/producer/notes_errors.md` | moment-certification | `b1541cefd8ab26d5fb45cd6c9010fac81d72a49d8567192f1a497d38cad4d454` |
| `r10ff8c2/np_results.txt` | [r10ff8c2] `evidence/peer/np_results.txt` | moment-certification | `0f5044826e9f629fd3b0530dfb30ea3f7b3fbb0dafd008e23141b2952772ce56` |
| `r10ff8c2/npcheck.py` | [r10ff8c2] `evidence/peer/npcheck.py` | moment-certification | `ecd8d4e45c1c4eb34bb7932ff3130d18f9d5180e0299a5b874eaac71cf8ef3df` |
| `r10ff8c2/win_targets.py` | [r10ff8c2] `evidence/producer/win_targets.py` | moment-certification | `0d7340f86a43eb13eede5a9b1ed02b3328054e6bc880158881c92491ac83199b` |
| `r13b0b8f/J_identity_check.json` | [r13b0b8f] `evidence/peer/J_identity_check.json` | band-A-certification | `adae94350479f175581d7720595a6834bf11cbec55c9be9523d28b0ddbaf3f4c` |
| `r13b0b8f/cert2_12_15.json` | [r13b0b8f] `evidence/peer/cert2_12_15.json` | band-A-certification | `083dd09a9fb46385b6be9d26221f437f1143c2eb7bf1631b495130a3494bccf7` |
| `r13b0b8f/cert3_15_18.json` | [r13b0b8f] `evidence/peer/cert3_15_18.json` | band-A-certification | `11cbd37e00d8e1efa35222a850c1d18995da5658a32cc67fa93a4ddacb91d803` |
| `r13b0b8f/cert_critical_strip.py` | [r13b0b8f] `evidence/producer/output/code/cert_critical_strip.py` | band-A-certification | `743b2cc263e8716a0e388250a0af0842bfe791e20fec9d7f9c33e0da1e8717b8` |
| `r13b0b8f/certificate-run.log` | [r13b0b8f] `evidence/producer/output/certificate-run.log` | band-A-certification | `5022344f28e89bf52a8b234d2f5ee41e56cbddcfed46e626104a862a9c905a5a` |
| `r13b0b8f/critical-strip-certificate-rerun.json` | [r13b0b8f] `evidence/peer/reproduction/critical-strip-certificate-rerun.json` | band-A-certification | `12f796a9778f4a9c1c27402a2d2e8b30a671136bb9ee77b8bc1402cf99f4da0c` |
| `r13b0b8f/critical-strip-certificate.json` | [r13b0b8f] `evidence/producer/output/critical-strip-certificate.json` | band-A-certification | `fe778f0b93cac6b16dd875053b89e70d5505087eb7be1911080b1734610bb201` |
| `r13b0b8f/gf_identity_check.json` | [r13b0b8f] `evidence/peer/gf_identity_check.json` | band-A-certification | `1bf70d4df60f60d00991a3ce1f3cc625905c043441886e755cd32f909deefb29` |
| `r13b0b8f/indep_cert.py` | [r13b0b8f] `evidence/peer/code/indep_cert.py` | band-A-certification | `f71757cb8c8a50c26fde5a41f278d33af1e1363da67d828ef608b9b7ae254b0f` |
| `r13b0b8f/indep_cert2.py` | [r13b0b8f] `evidence/peer/code/indep_cert2.py` | band-A-certification | `198db720d347a476ed980252b4663a93680afabeb6edd580ed40181a2eb77def` |
| `r13b0b8f/indep_cert3.py` | [r13b0b8f] `evidence/peer/code/indep_cert3.py` | band-A-certification | `621aafdf7acb8eea264700bb66a78c2d27bbe7bdcd02a0cea81372310e0977a9` |
| `r13b0b8f/indep_cert_A.json` | [r13b0b8f] `evidence/peer/indep_cert_A.json` | band-A-certification | `9b9f592919338b7170b13df792b6e2f2606eed5996f183722d1f4e97835ffc89` |
| `r13b0b8f/indep_cert_ext15.json` | [r13b0b8f] `evidence/peer/indep_cert_ext15.json` | band-A-certification | `119f6b486dceee14d685769cef9d753c2b084d6418f4c5de83a5bbb673f953de` |
| `r13b0b8f/laurent_fast.py` | [r13b0b8f] `evidence/peer/code/laurent_fast.py` | band-A-certification | `30f4f1d421e6acdb87513096ee4f79053b3e7d7dab04f3904ba0e4b670796ecd` |
| `r13b0b8f/laurent_series_check.json` | [r13b0b8f] `evidence/peer/laurent_series_check.json` | band-A-certification | `41ab48a8f7d7fd5c1f3a9b11502555f2d7ae8c95c3bfca353ff49d66ef41792b` |
| `r13b0b8f/laurent_sympy.py` | [r13b0b8f] `evidence/peer/code/laurent_sympy.py` | band-A-certification | `ca6c81e2e27eee42f45c13ee1eab28a5b3360996a2b80ea35eb852e89befbbd0` |
| `r13b0b8f/rerun_summary.json` | [r13b0b8f] `review/reruns/rerun_summary.json` | band-A-certification | `9cc4bb9bc1bb17e4595143aa26f81ae61b26c0688cf93a6f8825df2873a44f6d` |
| `r13b0b8f/strip_sample.json` | [r13b0b8f] `evidence/peer/strip_sample.json` | band-A-certification | `f9b6ea73ee3244abaac3a79f5977c747995762140c582aed963671efaa660166` |
| `r13b0b8f/tsv_crosscheck.json` | [r13b0b8f] `evidence/peer/tsv_crosscheck.json` | band-A-certification | `223d66d2f18196e44cbd549f862893871a9a95212f093b112db1a32736d7fd39` |
| `r13b0b8f/verification.json` | [r13b0b8f] `evidence/producer/output/verification.json` | band-A-certification | `80a80d0793310830c5cd40c392f3d0f6e34ac7f6aa01745bd98b88ac26202379` |
| `r15524fd/counts.json` | [r15524fd] `evidence/counts.json` | logconcavity-failure-n80 | `a3f8a62dc3fe4b43c638898857a3c4624ca5c162cc63a3b778eba4aeebc5b74b` |
| `r15524fd/logconcavity-witness.json` | [r15524fd] `evidence/logconcavity-witness.json` | logconcavity-failure-n80 | `df8353362aef69656b7d53c3e52aea1d7e59726f21fcc5e65811c6e874924935` |
| `r15df76b/center20000_k5001-8000_center.tsv` | [r15df76b] `evidence/producer/run2/center20000_k5001-8000_center.tsv` | exact-n20000 | `bf4a384f5a302bca454401a0b7f23816fa37a86860b2cc8ee05e9f51f4b76328` |
| `r15df76b/center20000_k8001-10000_center.tsv` | [r15df76b] `evidence/producer/run2/center20000_k8001-10000_center.tsv` | exact-n20000 | `12074f6dea5fe5840eabf7b96938d3ca5a25c1ea2103650fa879a96f1bf533bb` |
| `r15df76b/compare_runs.json` | [r15df76b] `evidence/peer/checks/compare_runs.json` | exact-n20000 | `0632e92f43142f8397d8b59b4d56c1c08c7805d91289596ba842262ee3524834` |
| `r15df76b/coverage_producer.json` | [r15df76b] `evidence/peer/checks/coverage_producer.json` | exact-n20000 | `b2852590fbfcf542d41afe8be0921be4dbab8c9d459868b97286766f783822b8` |
| `r15df76b/left20000_k2876-5250.tsv` | [r15df76b] `evidence/producer/run/left20000_k2876-5250.tsv` | exact-n20000 | `673e2660aadf0490ae39400ac89d92bb314c86f4b4470b666ed28fde2bac7bc1` |
| `r15df76b/left20000_k501-2875.tsv` | [r15df76b] `evidence/producer/run/left20000_k501-2875.tsv` | exact-n20000 | `1af19329f3b764ade2fcad9e0e8d509807aec0c7b96b18ed3163056b5cd7ff7b` |
| `r15df76b/left20000_k5251-7625.tsv` | [r15df76b] `evidence/producer/run/left20000_k5251-7625.tsv` | exact-n20000 | `bcd133ec4f16017c31cccb4802a7b36f9a58c8d519eb83823af7cea12f149bff` |
| `r15df76b/left20000_k7626-9999.tsv` | [r15df76b] `evidence/producer/run/left20000_k7626-9999.tsv` | exact-n20000 | `f51cf6dbd0431d8eaa4a5bf6f6e514e2645ef1bce2dab1d2faca3153f66eeb4c` |
| `r15df76b/leftcert.c` | [r15df76b] `evidence/producer/code/leftcert.c` | exact-n20000 | `0ca5da95473a3d079ed61f11e3662323212886cc3cba534866878f6402184a33` |
| `r15df76b/leftcert_build1.c` | [r15df76b] `evidence/producer/code/leftcert_build1.c` | exact-n20000 | `0f10a4b9c337397ae252bb240e839e1ae5a08dcdbecb64ef4a594de89e2b71e6` |
| `r15df76b/leftcert_build2.c` | [r15df76b] `evidence/producer/code/leftcert_build2.c` | exact-n20000 | `b2b1d6534860edb756b7f5e10e540be6a975352bf364da2b65d907f468228c1b` |
| `r15df76b/pcertv.c` | [r15df76b] `evidence/peer/code/pcertv.c` | exact-n20000 | `a6625ac674c6911d46c0082a6376d313ee10f8a8091a01b337275d47afb52b1b` |
| `r15df76b/pv_k2-2501.tsv` | [r15df76b] `evidence/peer/run/pv_k2-2501.tsv` | exact-n20000 | `592b512365fa8a439021e823924dccf6fd9032fba3e59ffa329a09bfbd2130de` |
| `r15df76b/pv_k2502-5001.tsv` | [r15df76b] `evidence/peer/run/pv_k2502-5001.tsv` | exact-n20000 | `578283961124f731776f8d6f7d3a559e368092e088a19d2aa0a0c19fef8a016b` |
| `r15df76b/pv_k5002-7501.tsv` | [r15df76b] `evidence/peer/run/pv_k5002-7501.tsv` | exact-n20000 | `3e25e06296b3273cee5b80e4eb39838759b177fe8c4ac3ee5a086ec9e26a4576` |
| `r15df76b/pv_k7502-10000.tsv` | [r15df76b] `evidence/peer/run/pv_k7502-10000.tsv` | exact-n20000 | `ceadd1b8949c3e026019edfc012be8fd9d42851188c2c709a539f50f8c85bc92` |
| `r15df76b/small20000_k2-250.tsv` | [r15df76b] `evidence/producer/run2/small20000_k2-250.tsv` | exact-n20000 | `9d52e8d0bd97ba19d2a35aaed4269b889a34c407d3f05e60d88ce3f8100dc0bf` |
| `r15df76b/small20000_k251-500.tsv` | [r15df76b] `evidence/producer/run2/small20000_k251-500.tsv` | exact-n20000 | `beef52e25117b4be25ff70c421d7036bc1b2411adbced3989e7570b3be1130de` |
| `r19de912/certify_right_half.py` | [r19de912] `evidence/producer/certify_right_half.py` | exact-n20000 | `130d1fded0625c8ef7ad9834b87b796b1a01e365ccb951260b4d2ba016185492` |
| `r19de912/class-hashes.txt` | [r19de912] `evidence/peer/cert/class-hashes.txt` | exact-n20000 | `92b1fe42e59b542d813c0a5dad2cee5b7725f2fa5456f465e00f43d2f634b238` |
| `r19de912/evidence__peer__cert__qr_cert2.c` | [r19de912] `evidence/peer/cert/qr_cert2.c` | m1-column-reading | `7b611e838f8d20d5970cf8ca597b0263e9deae3b12e8d66b426b68a319cb1ab4` |
| `r19de912/evidence__peer__cert__v2run20000-rows.tsv` | [r19de912] `evidence/peer/cert/v2run20000-rows.tsv` | m1-column-reading | `d35451d1431a6167228c41a5fb688d097de76cc043470b10a95487c88b838f48` |
| `r19de912/gen_s.py` | [r19de912] `evidence/peer/cert/gen_s.py` | exact-n20000 | `1e435ad8eb6202b9aada4a4354ad40bcb63d4f7d3eedfd8c7641ba0d76f1149c` |
| `r19de912/mode_offset.json` | [r19de912] `evidence/peer/checks/mode_offset.json` | exact-n20000 | `69e8f0908be8f91e4a7b8d012593599505084afca22a2cd222cb3e0d21096b95` |
| `r19de912/mode_offset.py` | [r19de912] `evidence/peer/checks/mode_offset.py` | exact-n20000 | `73c23a56b3ee0bcfe9636d9de1a30fa0b435491268de05e696e5f7e29f70376e` |
| `r19de912/producer-rerun-summary.json` | [r19de912] `evidence/peer/checks/producer-rerun-summary.json` | exact-n20000 | `4ada1ef3687bd6660dc50888235a4bb3b6f753cd9ca03a06a9c3cdec02eee087` |
| `r19de912/qr_cert2.c` | [r19de912] `evidence/peer/cert/qr_cert2.c` | exact-n20000 | `7b611e838f8d20d5970cf8ca597b0263e9deae3b12e8d66b426b68a319cb1ab4` |
| `r19de912/qr_cert3.c` | [r19de912] `evidence/peer/cert/qr_cert3.c` | m1-column-reading | `2d18c9ba61afa4f74655ea7c86c50797c1cd94649cde66db5cf7117d7a2cc249` |
| `r19de912/review/evidence/peer-rerun/rr2000-class.sha256` | [r19de912] `review/evidence/peer-rerun/rr2000-class.sha256`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `c4865cd10180c3fe078c88f2b9af3b6d529e03d45c033e0d078b860a3b64e40f` |
| `r19de912/review/evidence/peer-rerun/rr2000-summary.json` | [r19de912] `review/evidence/peer-rerun/rr2000-summary.json`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `c81c69d041497bf76ec3d4412bd9382303c02dacd73e90d35835895f8cab11bc` |
| `r19de912/review/evidence/peer-rerun/rr20000-rows.sha256` | [r19de912] `review/evidence/peer-rerun/rr20000-rows.sha256`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `ce99d4996d95f77e50ba303a75f0252cb0fab905b798848a6f6562a27ac25af8` |
| `r19de912/review/evidence/peer-rerun/rr20000-summary.json` | [r19de912] `review/evidence/peer-rerun/rr20000-summary.json`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `aa7797b6d0cad17da78f4ebc10aa0c32955f910acd28ea21b6558c97fbc6dc19` |
| `r19de912/review/evidence/peer-rerun/rr20000.log` | [r19de912] `review/evidence/peer-rerun/rr20000.log`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `ef836d26ff49bcecefe19bed41f219de99ae66b20accd8342595571f7417fedc` |
| `r19de912/right-half-certificate-2000.json` | [r19de912] `evidence/producer/right-half-certificate-2000.json` | exact-n20000 | `165c71d0e7ee9a1b5c1dd8ba79d049ad2dbc5e36580d707e1b1ad475540d85d0` |
| `r19de912/v2run20000-rows.tsv` | [r19de912] `evidence/peer/cert/v2run20000-rows.tsv` | exact-n20000 | `d35451d1431a6167228c41a5fb688d097de76cc043470b10a95487c88b838f48` |
| `r19de912/v2run20000-summary.json` | [r19de912] `evidence/peer/cert/v2run20000-summary.json` | exact-n20000 | `c47472c68f463654a09ab5d6071c9681f43b3743eb6b9fb28dc150a74ac10e31` |
| `r19de912/v2run20000.log` | [r19de912] `evidence/peer/cert/v2run20000.log` | exact-n20000 | `aa0fcd6a0e130d597ba4ac5d7282e24e816b6e5830dfd79f4a604b839bd0fdae` |
| `r207f124/colsb.py` | [r207f124] `evidence/peer/code/colsb.py` | Q-fin-1130 | `940cfd709a6c4be6809ae78262b6c60da274f037e65d46ac956eea597a7fefb3` |
| `r207f124/feedback.md` | [r207f124] `review/feedback.md` | Q-fin-1130 | `a3f6b2d36ed4cae9d945ee234b9917ebaea3d335bef10f1d80a229fd0af69191` |
| `r207f124/polar_check.out` | [r207f124] `evidence/peer/out/polar_check.out` | Q-fin-1130 | `b494e5f8607dd2391d47d36fe28f380afeae60a4c08410855b508ccc272d28d0` |
| `r207f124/polar_q.py` | [r207f124] `evidence/peer/code/polar_q.py` | Q-fin-1130 | `3cc5dc45f9d01a0fa8eb3ceae6fa5256ad94ae81d13fcf35d9c138f4488c4a1a` |
| `r207f124/polar_q_2001_4999_all.log` | [r207f124] `evidence/peer/out/polar_q_2001_4999_all.log` | Q-fin-1130 | `0fcca11afd12ccc02e40f8bc6196585d0ecd0f5a76b606c84675516c04fe6653` |
| `r207f124/polar_table.out` | [r207f124] `evidence/peer/out/polar_table.out` | Q-fin-1130 | `6dd5cb03ebb0d47d3bb0c98fe935ccf58eadbea03a0ada7bd9a55ac39d73c840` |
| `r207f124/polar_uniform.out` | [r207f124] `evidence/peer/out/polar_uniform.out` | Q-fin-1130 | `29e612709bac6051bca3c362379dbfc9896049d870b7665b7b5754a5f56675fa` |
| `r29c10cd/near_window_thresholds.out` | [r29c10cd] `evidence/peer/data/near_window_thresholds.out` | prop-W-thirteen | `c27b7d574db047505d513a785e346973016f06ea30beaaaaf3a19a506872e274` |
| `r29c10cd/near_window_thresholds.py` | [r29c10cd] `evidence/peer/code/near_window_thresholds.py` | prop-W-thirteen | `f077370174df564a67029203604f3656d3d9b5786b656e5ea48dfa2ca9de5799` |
| `r2ec875c/cert_readout.out` | [r2ec875c] `evidence/peer/out/cert_readout.out` | m1-column-reading | `0403ad927837dc7dcd2fce0c4863c083f3d8a5637ec766fbfbc7fea192edb8ce` |
| `r2ec875c/cert_readout.py` | [r2ec875c] `evidence/peer/scripts/cert_readout.py` | m1-column-reading | `d9a1ff23bc814902aa23223162f56d0bc8fe714a99115bab7f5aa3c4a8b114bc` |
| `r33475a7/float_tools.py` | [r33475a7] `evidence/peer2/scripts/float_tools.py` | H-star-plus-interval | `57bae08f41f54252667b06cbf6805ef814498edd221df2a84fef440ec11a4dc8` |
| `r33475a7/hplus_float.py` | [r33475a7] `evidence/peer2/scripts/hplus_float.py` | H-star-plus-interval | `27e5511a86fba0d4841e654dac0659f40b9ea109edf86483129d05a798eabe37` |
| `r33475a7/hplus_interval.py` | [r33475a7] `evidence/peer2/scripts/hplus_interval.py` | H-star-plus-interval | `135ce70b965f827f6a52548fd110352977110a55c36ca29e252048163e210623` |
| `r33475a7/hplus_interval_0.2.out` | [r33475a7] `evidence/peer2/out/hplus_interval_0.2.out` | H-star-plus-interval | `dca4eb4b614b612743a50a18c87e9934d10ed4591675e405174b90a90dddb12d` |
| `r33475a7/hplus_sanity.out` | [r33475a7] `evidence/peer2/out/hplus_sanity.out` | H-star-plus-interval | `3f0a8b88fecf6b5fe9d2ac87d590dbf1267770aa410b4a1e6c3d710dde7f04ab` |
| `r33475a7/hplus_sanity.py` | [r33475a7] `evidence/peer2/scripts/hplus_sanity.py` | H-star-plus-interval | `c5a2bbd5a2291e4512f9f2d35937873013da8489c6118f0a441e426ab9864ff6` |
| `r475ada3/audit_band.py` | [r475ada3] `evidence/producer/band/audit_band.py` | band102-integer | `3a1b12169f4b3b6de6dc9dba2709e2518720736ff9b2936fd657eac0092a69ab` |
| `r475ada3/audit_band_run.txt` | [r475ada3] `evidence/peer/repro/audit_band_run.txt` | band102-integer | `f64345812da75a5c6eb2c5264b70b665bcff50ebafe2bd7a29e0091d2506f3bd` |
| `r475ada3/audit_diag_run.txt` | [r475ada3] `evidence/peer/repro/audit_diag_run.txt` | band102-integer | `2d45ffbbcb379ed570e52cd1029321a0e0e8b2250c8b104f5d0479c50d874858` |
| `r475ada3/audit_f1_f2.json` | [r475ada3] `evidence/peer/icert/audit_f1_f2.json` | band102-integer | `087463e6a621e14d155b27c79b3c4d89f9f2d75700560bd45f3ae629484aa621` |
| `r475ada3/audit_f2.py` | [r475ada3] `evidence/peer/icert/audit_f2.py` | band102-integer | `0696899204964006d788f25442a482780674e48b0062b7523deb0a7711d60348` |
| `r475ada3/audit_param.py` | [r475ada3] `evidence/peer/repro/audit_param.py` | band102-integer | `9befd93d9f33aed3ef16f8e86b59e34d7dcb967b9c9564a6afe329ef346e96d4` |
| `r475ada3/audit_param_K11100_nu20_40.txt` | [r475ada3] `evidence/peer/repro/audit_param_K11100_nu20_40.txt` | band102-integer | `cec3eb46f3338eb1c5ee68351684f4cdce8491058050399682fe42557aae69ca` |
| `r475ada3/hermite_exact.py` | [r475ada3] `evidence/producer/code/hermite_exact.py` | band102-integer | `63be858f55d1912e1aedada0a7d86a92dbb91c527a220679c28c577aadaba484` |
| `r475ada3/icert_rows.c` | [r475ada3] `evidence/peer/icert/icert_rows.c` | band102-integer | `97856048e2c6f24e66e4959a331a27e34a6fe45a996e7258e82e5fcbf2196b38` |
| `r475ada3/nk_strip2.txt` | [r475ada3] `evidence/peer/icert/nk_strip2.txt` | band102-integer | `fea04f1964690820d029e37128e3d4feb80f7a9a41534b3a912d4ae4027ba73b` |
| `r475ada3/out_band_check.txt` | [r475ada3] `evidence/peer/icert/out_band_check.txt` | band102-integer | `ffd8896215c200e01098106b7f6a1c70eedff646e52a1e43ffc211398b15acf1` |
| `r475ada3/out_s2_a.txt` | [r475ada3] `evidence/peer/icert/out_s2_a.txt` | band102-integer | `c17db983e9a1bd24a57d75a605afa7386ba6862ab481f9cf06f1463b6e9b212e` |
| `r475ada3/out_s2_b.txt` | [r475ada3] `evidence/peer/icert/out_s2_b.txt` | band102-integer | `f0304375b5e558389a517b4184037551611dc8c8abae340f8d0f7c0f7f0cae02` |
| `r475ada3/out_s2_c.txt` | [r475ada3] `evidence/peer/icert/out_s2_c.txt` | band102-integer | `01f218f38c8bbd9acb60ce2220beceb1369ac9e9155b87239a59c8026df159ed` |
| `r475ada3/out_selftest.txt` | [r475ada3] `evidence/peer/icert/out_selftest.txt` | band102-integer | `e90c40a5b5c8e1d4c9fff172a5cb6d6544f16705a89265c0886c2520c4da9750` |
| `r475ada3/out_strip.txt` | [r475ada3] `evidence/peer/icert/out_strip.txt` | band102-integer | `ef039bb83e3064d9d2fd02e281f8c00145475d55b4e0f398a6fafc944e2b366a` |
| `r475ada3/peer_jets.py` | [r475ada3] `evidence/peer/exact/peer_jets.py` | band102-integer | `b59eedd8540b29531ebcf682c5d9c3646eec1ef83f04308d963853e9358f5b77` |
| `r475ada3/peer_pair_check_bound.py` | [r475ada3] `evidence/peer/exact/peer_pair_check_bound.py` | band102-integer | `6df9eb054582d598ad52f90663143f47d7a0dbd9b7e9689f088cf392e27f5e26` |
| `r475ada3/peer_pair_improved.py` | [r475ada3] `evidence/peer/exact/peer_pair_improved.py` | band102-integer | `d7fe79055e9d530c3b5a48ab8a1e7ee59482ab3fd646549c393e8860d1b99a0f` |
| `r475ada3/peer_pair_improved_out.json` | [r475ada3] `evidence/peer/exact/peer_pair_improved_out.json` | band102-integer | `472e7eadfe7760b7c3af73bab6f5a9103449fd51f7d9f0f1f9ce28228028bfc3` |
| `r475ada3/uv_general.py` | [r475ada3] `evidence/peer/repro/uv_general.py` | band102-integer | `43cf662deb14267e75cff8213b086cfe36fb1c80eecafb57852b3c20ce4b7351` |
| `r5909c9e/README.md` | [r5909c9e] `evidence/peer/w_data/README.md` | pair-one-variable | `8b5cbcd656d64de1be9a374b3eb6f1aa886c38c6133e2c91cdf536b33e7060bd` |
| `r5909c9e/W_exact.py` | [r5909c9e] `evidence/producer/code/W_exact.py` | pair-one-variable | `fa50b901bb8a6b1a510f5c8ca37b329be3da6795c04fbacd1841f1a1d2a7aa79` |
| `r5909c9e/design.json` | [r5909c9e] `evidence/peer/w_data/design.json` | pair-one-variable | `5ca7ca94ea05873420053508c14ddec9562d60fb18c65d7ed2173afc0c12da7f` |
| `r5909c9e/evidence/peer/w_data/README.md` | [r5909c9e] `evidence/peer/w_data/README.md`(폴더 `evidence/peer/w_data/`) | pair-one-variable | `8b5cbcd656d64de1be9a374b3eb6f1aa886c38c6133e2c91cdf536b33e7060bd` |
| `r5909c9e/evidence/peer/w_data/design.json` | [r5909c9e] `evidence/peer/w_data/design.json`(폴더 `evidence/peer/w_data/`) | pair-one-variable | `5ca7ca94ea05873420053508c14ddec9562d60fb18c65d7ed2173afc0c12da7f` |
| `r5909c9e/evidence/peer/w_data/wKrig.npy` | [r5909c9e] `evidence/peer/w_data/wKrig.npy`(폴더 `evidence/peer/w_data/`) | pair-one-variable | `8e047df2647393e22c7fbfb157fd1dcfa9de2bdd25aa06f6586ad603d52eb609` |
| `r5909c9e/evidence/peer/w_data/xKrig.npy` | [r5909c9e] `evidence/peer/w_data/xKrig.npy`(폴더 `evidence/peer/w_data/`) | pair-one-variable | `16f6fbc8fa801ba6e4e66e6336d943a0736096d00940406a300c599eda724287` |
| `r5909c9e/flow_check.out` | [r5909c9e] `evidence/peer/flow_check.out` | pair-one-variable | `45ef142965fa5e466c72afd2bd90bb41e60e534aaf359f027cb2f9a91b1e62e5` |
| `r5909c9e/flow_check.py` | [r5909c9e] `evidence/peer/flow_check.py` | pair-one-variable | `9a41e90f6c2b19e9447b2e40ab884ed6c5fbc24272832fe453153ceed6dde287` |
| `r5909c9e/flow_check_rerun.out` | [r5909c9e] `evidence/peer/flow_check_rerun.out` | pair-one-variable | `45ef142965fa5e466c72afd2bd90bb41e60e534aaf359f027cb2f9a91b1e62e5` |
| `r5909c9e/flow_mp.out` | [r5909c9e] `evidence/peer/flow_mp.out` | pair-one-variable | `0b9be76bac271a88926c30ee8a179f1af4cdff1ee527b9a03f25c3d2e9f39282` |
| `r5909c9e/flow_mp.py` | [r5909c9e] `evidence/peer/flow_mp.py` | pair-one-variable | `d1fc11335445a56c0ff87c56323c2d9c7433e574a4f3d173d27c074ca1739571` |
| `r5909c9e/levelmass_upper.py` | [r5909c9e] `evidence/producer/code/levelmass_upper.py` | pair-one-variable | `ff814d1aa94a6152380a9d8cdc45642ab5647ad875e97fe46b5bb703c65e6b0d` |
| `r5909c9e/my_flow.out` | [r5909c9e] `review/evidence/my_flow.out` | pair-one-variable | `b97e5823e32eb672db6519d62156d80793c4d4155cc64d0336bc92f9a1214974` |
| `r5909c9e/my_flow.py` | [r5909c9e] `review/evidence/my_flow.py` | pair-one-variable | `566a9603f0a0412e02562a631d68e1a14f1b1f51714eae92a3ef56bb06f794b1` |
| `r5909c9e/pdiamond_final.out` | [r5909c9e] `evidence/producer/out/pdiamond_final.out` | pair-one-variable | `c0965b1ba5bd6561ee54ec409b732d6833434ab57b1d6239f3120d47a4ca91e5` |
| `r5909c9e/pdiamond_final.py` | [r5909c9e] `evidence/producer/code/pdiamond_final.py` | pair-one-variable | `81c2435a4530f87240cdd0972823c110b411d2cd4572a26e37e27ada5e402668` |
| `r5909c9e/pdiamond_proof.out` | [r5909c9e] `evidence/producer/out/pdiamond_proof.out` | pair-one-variable | `0c7b1e0555d2bc9785cba79d40cf3f4aaf2b2efcfcd28f2fe1ed5da4a879dd08` |
| `r5909c9e/pdiamond_proof.py` | [r5909c9e] `evidence/producer/code/pdiamond_proof.py` | pair-one-variable | `7330a2efabc0626bd20ab9b6e4165247990607efe2377133727c56fb15b42115` |
| `r5909c9e/sandwich.out` | [r5909c9e] `evidence/peer/sandwich.out` | pair-one-variable | `4916c5d66d7f69bbd651c773b147b4a647723c15171206d3132f5203d8c8c922` |
| `r5909c9e/sandwich.py` | [r5909c9e] `evidence/peer/sandwich.py` | pair-one-variable | `fcfb40c18c57a83be73632ce786004c42da61cc7540cae5cecef155fd1219aa2` |
| `r5909c9e/wKrig.npy` | [r5909c9e] `evidence/peer/w_data/wKrig.npy` | pair-one-variable | `8e047df2647393e22c7fbfb157fd1dcfa9de2bdd25aa06f6586ad603d52eb609` |
| `r5909c9e/xKrig.npy` | [r5909c9e] `evidence/peer/w_data/xKrig.npy` | pair-one-variable | `16f6fbc8fa801ba6e4e66e6336d943a0736096d00940406a300c599eda724287` |
| `r59c82d7/bor.bin` | [r59c82d7] `evidence/code/bor.bin` | c50 | `f931a43ca031dbefe0e4399b41903f2416418ff5a9c791bc9872ed4d63c8e31c` |
| `r59c82d7/e50_1_summary.json` | [r59c82d7] `evidence/runs/e50_1_summary.json` | c50 | `7e60a287fdae262b0cbd279970d348315790b64a6cd6874025bfa6445e4a29f1` |
| `r59c82d7/e50_2_summary.json` | [r59c82d7] `evidence/runs/e50_2_summary.json` | c50 | `1387a04520f8798b1b653cd35dac2db9c642cbe42b4fe634c86459828ffdd541` |
| `r59c82d7/e50_3_summary.json` | [r59c82d7] `evidence/runs/e50_3_summary.json` | c50 | `b305ddd4fa481d4d546114cf3a6de1caaf109b80696684827da337b947c4738c` |
| `r59c82d7/e50_4_summary.json` | [r59c82d7] `evidence/runs/e50_4_summary.json` | c50 | `05cbddac6d83d7711684692c2b87495ed1121f8d212cc1fc3c5edbd65fbf9aa8` |
| `r59c82d7/e50_5_summary.json` | [r59c82d7] `evidence/runs/e50_5_summary.json` | c50 | `0de57651a0cb0dd2b645c43ddd154169927dd0560685cbedbb85504469ffe23a` |
| `r59c82d7/e50_6_summary.json` | [r59c82d7] `evidence/runs/e50_6_summary.json` | c50 | `36625f744d6d8eb5ea37f38b4ba8889c747b4cc9c516cfd4dbbec8071d7b05c6` |
| `r59c82d7/exact_check.json` | [r59c82d7] `evidence/exact_check.json` | c50 | `32697b2be91d4d35e12ed8237d93cb1e1e15f6872babac52a7e3dee647356015` |
| `r59c82d7/ext50000_post.json` | [r59c82d7] `evidence/runs/ext50000_post.json` | c50 | `7dd0762caf4986e844ed846c3ce5335aaf7efc3c2a89ed23a6e90e9772dc7c8c` |
| `r59c82d7/ext50000_rows.tsv` | [r59c82d7] `evidence/runs/ext50000_rows.tsv` | c50 | `93df99636f8d0d85bbdb0afd90efd98964bbde6416108c678de6ad58f6b1ea24` |
| `r59c82d7/ext50000_summary.json` | [r59c82d7] `evidence/runs/ext50000_summary.json` | c50 | `1f8dcc4ffb368661eb2055cae3ca18cc36ddef915cf5e4b5566b4f2fbf0e05c8` |
| `r59c82d7/full20000_compare_published.txt` | [r59c82d7] `evidence/runs/full20000_compare_published.txt` | c50 | `6a7e1e2aa0d9877ff5d78f83c43df7142e751a9594db49a2e3c2e349000e5902` |
| `r59c82d7/full20000_rows.tsv` | [r59c82d7] `evidence/runs/full20000_rows.tsv` | c50 | `7ea5c118ea5d8b8578b4b657347135e70da8248e9c508e4370930bba235708a7` |
| `r59c82d7/full20000_summary.json` | [r59c82d7] `evidence/runs/full20000_summary.json` | c50 | `c19d89470d98a54d71db0e5543b8c3f698ef87860868a7703727f7d3edc28115` |
| `r59c82d7/h.bin` | [r59c82d7] `evidence/code/h.bin` | c50 | `8b0b50f5b0c698621573eb26c16a68142f25251b918959a63e4e497be114e739` |
| `r59c82d7/make_tables.py` | [r59c82d7] `evidence/code/make_tables.py` | c50 | `79feaa76e11a80891f2079e305d718e571f124703be0e8cb40a1cb8f4e6e31ed` |
| `r59c82d7/merge_chunks.py` | [r59c82d7] `evidence/code/merge_chunks.py` | c50 | `dce4ffb6c21a32a94075ec43488bbdc7a75c0556f69afd09cb248825aa80d8c7` |
| `r59c82d7/postprocess_rows.py` | [r59c82d7] `evidence/code/postprocess_rows.py` | c50 | `41bdf9ec5957f6e89334629f5eed022e2f9824bc0bb9eeb28e9ec942f8622ad9` |
| `r59c82d7/qrcert.c` | [r59c82d7] `evidence/code/qrcert.c` | c50 | `d0e2ebcebe0c93085b37288c776f2ff2916eadee6af7baaaef04f9e5d0b4057c` |
| `r59c82d7/t60_validate.json` | [r59c82d7] `evidence/runs/t60_validate.json` | c50 | `7aecd85302eb43c871b722fc3797adafc183e7f45aa5bc22a326648c0e84d63c` |
| `r59c82d7/tables_manifest.json` | [r59c82d7] `evidence/code/tables_manifest.json` | c50 | `c929b6f10ba4b6cd8f3ff154c19a7ca5392658abbd55abcf2d3172174874e73c` |
| `r5bbc534/thmD_base.py` | [r5bbc534] `evidence/producer/code/thmD_base.py` | theorem-D-base | `2515c0ab921abbb6b10de659bf89e0a6d264db7d25655c2e405450ec3483aef1` |
| `r5bbc534/thmD_base_L700.out` | [r5bbc534] `evidence/producer/out/thmD_base_L700.out` | theorem-D-base | `9e53086d23eb8ee833d2f012b7117b29d962a913b1a16ecfdef38c75363c0745` |
| `r5bbc534/verify_DR_thmD.out` | [r5bbc534] `evidence/peer/verify_DR_thmD.out` | theorem-D-base | `2b45c065de5d47e1b220e9232ff7dee4d5b9b125f40cc7902febe0f4a71dd217` |
| `r5bbc534/verify_DR_thmD.py` | [r5bbc534] `evidence/peer/verify_DR_thmD.py` | theorem-D-base | `0def3e0a505b9a9eff7c9d979159754fade2b42bae4237844febb0fd499b5034` |
| `r6373c70/exact-rows-300.json` | [r6373c70] `evidence/peer/output/exact-rows-300.json` | exact-n20000 | `deb310f9cdba17f8ba203df70d234865c22857fce1e1191a5c2b5bee83c6d7eb` |
| `r6373c70/exact_rows.py` | [r6373c70] `evidence/peer/code/exact_rows.py` | exact-n20000 | `ab2b6fe8ad97850d22402c8e5821c24b9ba430738acef2622bf631b455db19fb` |
| `r6373c70/my_exact_rows.py` | [r6373c70] `review/evidence/code/my_exact_rows.py` | exact-n20000 | `1f54ed8f982674391bd82de823334cb5f470a9029ddbe57a4208b93548851408` |
| `r656206c/pv_check_Y.json` | [r656206c] `evidence/peer/data/pv_check_Y.json` | crossing-small-n | `5210c60541016d1d08f26f57427a1c196f6f7bd69295a35c490034a584dbfcbe` |
| `r656206c/pv_check_Y.py` | [r656206c] `evidence/peer/code/pv_check_Y.py` | crossing-small-n | `ce6c27da261e2e1de90f255bc92bb578a126ae469b3740452ad2a53e59cd1d49` |
| `r656206c/pv_check_rows.json` | [r656206c] `evidence/peer/data/pv_check_rows.json` | crossing-small-n | `3171e8b07f8fefff9a8539459dc8af04e30b6c87f72726637b72c1ab2ab22ee9` |
| `r656206c/pv_check_rows.py` | [r656206c] `evidence/peer/code/pv_check_rows.py` | crossing-small-n | `7dec49880d8059da2194aa96e099b38a6b2049b69a4d71b7bae3d694848d0e23` |
| `r656206c/pv_core.py` | [r656206c] `evidence/peer/code/pv_core.py` | crossing-small-n | `bafa8033433ece0fb04381588ebe911f10468617c8dabee941c40cdfdcea06d7` |
| `r690be93/certificate-check.json` | [r690be93] `evidence/producer/certificate-check.json` | bernstein-signs | `a76afbbd18f0662e6b7607adb7c0daf3b51f84d7f5c2fe0678bc042e35497628` |
| `r690be93/certify_concavity.py` | [r690be93] `evidence/producer/certify_concavity.py` | bernstein-signs | `45e65c3d014d647aa050ba88b8663b1de3b5650785f26ec77323645931cb0495` |
| `r690be93/certify_entry.py` | [r690be93] `evidence/producer/certify_entry.py` | bernstein-signs | `41312e5e04ace5c2a88981cd385e3e3c3fcfd86f633efc630bc2744e8dc00b1d` |
| `r690be93/check_certificates.py` | [r690be93] `evidence/producer/check_certificates.py` | bernstein-signs | `b251414977d01e6cb5d54909851005cf38507661a190e473b2bb4edb07edee4f` |
| `r690be93/direct-checks.json` | [r690be93] `evidence/producer/direct-checks.json` | bernstein-signs | `0da9c1a952886a2d31439ce115ad1f6ab8bd196eabb7ce98f3a75e27203e87b2` |
| `r690be93/direct_checks.py` | [r690be93] `evidence/producer/direct_checks.py` | bernstein-signs | `0a6c349976cd7af1ea6aa57e99fddb83e94e046d4b73b265341f7b3dcd2f1bfd` |
| `r690be93/entry-slope-certificate.json` | [r690be93] `evidence/producer/entry-slope-certificate.json` | bernstein-signs | `4df23ee34be0324bd79e074dfadb64bee39c8d46500298471408194a12b4a6f4` |
| `r690be93/evidence/peer/kernel_sample/kernel_sample_N1050000.json` | [r690be93] `evidence/peer/kernel_sample/kernel_sample_N1050000.json`(폴더 `evidence/peer/kernel_sample/`) | bernstein-signs | `8927ce9f4591be06398b6c0ae094797bc0d48035404c10c656f8330980c08f40` |
| `r690be93/evidence/peer/kernel_sample/kernel_sample_N160000.json` | [r690be93] `evidence/peer/kernel_sample/kernel_sample_N160000.json`(폴더 `evidence/peer/kernel_sample/`) | bernstein-signs | `2f92b75305ab76ea361bf54501241008aa43c0ffc6b5a208daef44f37d963858` |
| `r690be93/evidence/peer/kernel_sample/kernel_sample_N20010.json` | [r690be93] `evidence/peer/kernel_sample/kernel_sample_N20010.json`(폴더 `evidence/peer/kernel_sample/`) | bernstein-signs | `17b19d752d55ca65fc3590142c5fa562b907839d45c2572500bc883c247fe7e0` |
| `r690be93/evidence/peer/kernel_sample/kernel_sample_N320000.json` | [r690be93] `evidence/peer/kernel_sample/kernel_sample_N320000.json`(폴더 `evidence/peer/kernel_sample/`) | bernstein-signs | `baf8e5528c681b72aeb987d41f416b84c817daa8c3df44644e0e8af5c8dc5a78` |
| `r690be93/evidence/peer/kernel_sample/kernel_sample_N40000.json` | [r690be93] `evidence/peer/kernel_sample/kernel_sample_N40000.json`(폴더 `evidence/peer/kernel_sample/`) | bernstein-signs | `c3dc5af6626aed6b5c9a0c56ab932459e5af74eeac9f16c893f393ada7fe77f0` |
| `r690be93/evidence/peer/kernel_sample/kernel_sample_N640000.json` | [r690be93] `evidence/peer/kernel_sample/kernel_sample_N640000.json`(폴더 `evidence/peer/kernel_sample/`) | bernstein-signs | `a25a1dc2f12386c7977437d55635a44d45f3b0c60e740aeb48733b11efdc7602` |
| `r690be93/evidence/peer/kernel_sample/kernel_sample_N80000.json` | [r690be93] `evidence/peer/kernel_sample/kernel_sample_N80000.json`(폴더 `evidence/peer/kernel_sample/`) | bernstein-signs | `8400aedc1cd1877f5540a6c961cfb9e7511313b288340425aeeb301d88df60de` |
| `r690be93/evidence/peer/reproduction/byte_compare.txt` | [r690be93] `evidence/peer/reproduction/byte_compare.txt`(폴더 `evidence/peer/reproduction/`) | bernstein-signs | `e26a1e4857c33590b11a48ad9623256623ba3352167c9d1323874ede292ed1ad` |
| `r690be93/evidence/peer/reproduction/log_check_certs.txt` | [r690be93] `evidence/peer/reproduction/log_check_certs.txt`(폴더 `evidence/peer/reproduction/`) | bernstein-signs | `02d51ac6190d50283426d4608173ae023387ab5a583c8dfd6a25bda6fd3b932f` |
| `r690be93/evidence/peer/reproduction/log_direct.txt` | [r690be93] `evidence/peer/reproduction/log_direct.txt`(폴더 `evidence/peer/reproduction/`) | bernstein-signs | `f3c824ce36d774c6ec2659a7f3fa738540b3633787c6d4b713720f2c96819ca5` |
| `r690be93/evidence/peer/reproduction/log_kernel_audit.txt` | [r690be93] `evidence/peer/reproduction/log_kernel_audit.txt`(폴더 `evidence/peer/reproduction/`) | bernstein-signs | `559200922c5de8fdd0562dccf5cc756be709b18b348c4656efb7d0db8da6d9d5` |
| `r690be93/evidence/peer/reproduction/log_times.txt` | [r690be93] `evidence/peer/reproduction/log_times.txt`(폴더 `evidence/peer/reproduction/`) | bernstein-signs | `b4d5ce45719d22558cbd301f30375b15af5f0f2af249a7e8457d11c56361ce1c` |
| `r690be93/kernel_sample.py` | [r690be93] `evidence/peer/kernel_sample.py` | bernstein-signs | `e5ee3e0334d206a3039836c7f550b7f0fc10575c63b87d9ef8048d45e4dc28fd` |
| `r690be93/published_algebra.py` | [r690be93] `evidence/producer/published_algebra.py` | bernstein-signs | `b523da49cbb009f090b1962fcb039f9d0aed39a7dc379810c4c09a2d604dde57` |
| `r690be93/tsv_crosscheck_output.txt` | [r690be93] `evidence/peer/tsv_crosscheck_output.txt` | bernstein-signs | `d21d64ddb72f2e9b06c146ceb64f50099cabc20331124bd0f93c26315278daee` |
| `r690be93/window_check.json` | [r690be93] `evidence/peer/window_check.json` | bernstein-signs | `cfda8d4c837b252a82613417cd8f76ba5b31c75ae233f74467fcd4e7ea597fcb` |
| `r6b37c7e/audit_monotone_check.py` | [r6b37c7e] `evidence/peer/audit_monotone_check.py` | band102-integer | `56b3f94445a1befb4669d13d65cb53e926a599b0b571728e3061efcfaf3cc9de` |
| `r6b37c7e/audit_monotone_check.txt` | [r6b37c7e] `evidence/peer/out/audit_monotone_check.txt` | band102-integer | `a57ba2379aa78ff0a0c0ae54662cd42709f96bb16d1468b4bd8c9f62882dd320` |
| `r6b37c7e/audit_strip.py` | [r6b37c7e] `evidence/producer/icert/audit_strip.py` | band102-integer | `e9139d9cb0426fbb5c9c1e94d50858d6f8701a7951c7185f50735105ae95c82f` |
| `r6b37c7e/audit_strip102_A.json` | [r6b37c7e] `evidence/producer/icert/audit_strip102_A.json` | band102-integer | `f6700cedcadf2267b04895faa734008ef653ce153cd78e31143462f9853b506e` |
| `r6b37c7e/audit_strip102_B.json` | [r6b37c7e] `evidence/producer/icert/audit_strip102_B.json` | band102-integer | `23716c1981dac68045feaf82f6aeaf0a7650669be0701b8e300c8f5e54e4c580` |
| `r6b37c7e/audit_strip102_C.json` | [r6b37c7e] `evidence/producer/icert/audit_strip102_C.json` | band102-integer | `e986c026a261177cdd76b8b31f3ef8598a38935b43f6b9d8a02a4f13204b2229` |
| `r6b37c7e/audit_strip102_D.json` | [r6b37c7e] `evidence/producer/icert/audit_strip102_D.json` | band102-integer | `62f9b75ceb3399aaa92203d49b468c4c2938a17760030a4748714b63bc355de8` |
| `r6b37c7e/audit_strip58.json` | [r6b37c7e] `evidence/producer/icert/audit_strip58.json` | band102-integer | `a8a54a80ba775673f6fd8e9b1b4874fc1911c198816d7fc0afe66dcb8dfd84ee` |
| `r6b37c7e/coverage_4B.py` | [r6b37c7e] `evidence/peer/coverage_4B.py` | band102-integer | `3f959cf1e65d2154c350137356025647a328f99677063e86869aa9b0d7a93efc` |
| `r6b37c7e/coverage_4B.txt` | [r6b37c7e] `evidence/peer/out/coverage_4B.txt` | band102-integer | `65d51abecbd0914c0236d802d521011120e6bf8d8b8c92aaa871828fae53a879` |
| `r6b37c7e/coverage_out.txt` | [r6b37c7e] `review/checks/coverage_out.txt` | band102-integer | `256fa3786a4096541816db59a389d04fe7dbbfce6d69eb09777ff7f5b99b0865` |
| `r6b37c7e/coverage_review.py` | [r6b37c7e] `review/checks/coverage_review.py` | band102-integer | `a2f4f0f60d4537d1ecc5c5d89fac9061a36faee530570e829a54c353eedeba4d` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K100000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K100000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `f0474e6f62358ca3c500d8d9f2de619437e910b14514bce4b821cbba4c3ce372` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K1000000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K1000000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `347749af3b0ea30e6e956163b356e23948ce7dec3c1e5d94afb36139ae62cbb4` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K12000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K12000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `408ef28acec441d26ad24edd5dfb19ba4db2ab45d883850305fc389a3f4fea79` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K13000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K13000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `2706f484e822e655a06fcdf527843a04a80bf6bce3b07e304346ddb3e6f28850` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K14000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K14000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `664704009764410004a14aad0ec15d201f4e1585e9f75c6e74395424345d252f` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K14000_nu97_100.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K14000_nu97_100.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `e089b980e16d0e9e07c8fac409b5e11cb27012ae212d6f52dcdf550131a883c1` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K15000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K15000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `a3d34d37cc6acc4c1dc14ab29b0eeba3e289aa46444a18d84dbd8f669d29f186` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K20000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K20000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `da2f126908d618ff74f86c2d50dbef37f38232a733a09ce1c4b3f7e83627c043` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K200000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K200000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `6adf53d6f539f43d1d922531a3b0d3fce61c1de6ebc0206339d788f504742ec0` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K30000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K30000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `973acf7f036c8fa1817ddd42ac8fb9ba60feb1bb41890378befce208a3bf53de` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K50000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K50000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `89ab9e0758d6869b26be0864e16f4e046a91ca1e0dfffa33ddf6ead5955bb433` |
| `r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K500000.txt` | [r6b37c7e] `evidence/peer/audit_rerun/rerun_audit_K500000.txt`(폴더 `evidence/peer/audit_rerun/`) | band102-integer | `6f117e5e0d625617084875b6a892533f86326f7b31e8cf47ddc9035b5d2a6b85` |
| `r6b37c7e/evidence/producer/audit/audit_band_run.txt` | [r6b37c7e] `evidence/producer/audit/audit_band_run.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `f64345812da75a5c6eb2c5264b70b665bcff50ebafe2bd7a29e0091d2506f3bd` |
| `r6b37c7e/evidence/producer/audit/audit_diag_run.txt` | [r6b37c7e] `evidence/producer/audit/audit_diag_run.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `2d45ffbbcb379ed570e52cd1029321a0e0e8b2250c8b104f5d0479c50d874858` |
| `r6b37c7e/evidence/producer/audit/audit_lm_K10000_nu1_19.txt` | [r6b37c7e] `evidence/producer/audit/audit_lm_K10000_nu1_19.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `66eb6db13805873c58fa2061fe91e6ac0be3897e7cc3545acd68986a065d5cba` |
| `r6b37c7e/evidence/producer/audit/audit_lm_K11100_nu20_40.txt` | [r6b37c7e] `evidence/producer/audit/audit_lm_K11100_nu20_40.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `cec3eb46f3338eb1c5ee68351684f4cdce8491058050399682fe42557aae69ca` |
| `r6b37c7e/evidence/producer/audit/audit_param.py` | [r6b37c7e] `evidence/producer/audit/audit_param.py`(폴더 `evidence/producer/audit/`) | band102-integer | `9befd93d9f33aed3ef16f8e86b59e34d7dcb967b9c9564a6afe329ef346e96d4` |
| `r6b37c7e/evidence/producer/audit/audit_param_K1000000_nu41_237.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K1000000_nu41_237.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `d4da9db1a2ae318b930183fe50b421752edcdaa94141c216f421dc6ad36a574c` |
| `r6b37c7e/evidence/producer/audit/audit_param_K1000000_nu41_590_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K1000000_nu41_590_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `8db5bfe9b02c88663a1dedaec7170fded243bed88c39037711286585bf634936` |
| `r6b37c7e/evidence/producer/audit/audit_param_K100000_nu194_228_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K100000_nu194_228_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `3bc41faa5f989c9ab9f0dd015ef45ce28a998505f64243d168d91d17cc330686` |
| `r6b37c7e/evidence/producer/audit/audit_param_K100000_nu41_110.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K100000_nu41_110.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `238e28be4b0e3852e2064bc886b49cea129c7e1849cf0f2718fbfb4f37ba3d5f` |
| `r6b37c7e/evidence/producer/audit/audit_param_K100000_nu41_228_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K100000_nu41_228_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `587e695a88f435d273c756a959739c87f5bdc8820bef8f09124fd630d831c4f1` |
| `r6b37c7e/evidence/producer/audit/audit_param_K10000_nu41_86_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K10000_nu41_86_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `b75afbfd841e96c8b3a5c3a8f4e691949564d92bd1021afd94b86108ff5e1714` |
| `r6b37c7e/evidence/producer/audit/audit_param_K10000_nu41_86_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K10000_nu41_86_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `342b81ecf7c50f0960de7413b40e11b9e3744969eeb13065e3eb9bb5e303d88c` |
| `r6b37c7e/evidence/producer/audit/audit_param_K11100_nu20_40.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K11100_nu20_40.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `cec3eb46f3338eb1c5ee68351684f4cdce8491058050399682fe42557aae69ca` |
| `r6b37c7e/evidence/producer/audit/audit_param_K11100_nu41_60_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K11100_nu41_60_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `d50ae42e5afe6881cfc245bac33bb4375bc1d73d0600e4761284cd5d7b53e007` |
| `r6b37c7e/evidence/producer/audit/audit_param_K12000_nu41_92_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K12000_nu41_92_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `03e04fbfa017f75b897cf548b3b01f6f3eb1add811ac3257c50846147ccc2f92` |
| `r6b37c7e/evidence/producer/audit/audit_param_K13000_nu41_93_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K13000_nu41_93_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `89ec782d16e282c9b8fed5a883a8118fc2e2c155b90eb33257757624aa4811e0` |
| `r6b37c7e/evidence/producer/audit/audit_param_K14000_nu41_95_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K14000_nu41_95_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `2884dedd45cec1ba83cdbba4b6dba1799b702a15a4c1feb85bc79f37fc06f41f` |
| `r6b37c7e/evidence/producer/audit/audit_param_K15000_nu41_58.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K15000_nu41_58.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `a14407f92218c51f5617ba0ae0bfe77eab94b1b2c88b7e295978709fbd2250ce` |
| `r6b37c7e/evidence/producer/audit/audit_param_K15000_nu41_96_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K15000_nu41_96_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `d7f28642cc56b9386367f4c44311fac3d60d62a359811401d7ddba27ba383e1d` |
| `r6b37c7e/evidence/producer/audit/audit_param_K15000_nu55_96_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K15000_nu55_96_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `a75bcdbf574daca25bb5920ca4c1499a4eef7cd8754a83b67954d3cc72505411` |
| `r6b37c7e/evidence/producer/audit/audit_param_K15000_nu97_102_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K15000_nu97_102_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `54f247403fece1377ba7ed8970b9407faa677240c15bb55c7fe963b901a362c6` |
| `r6b37c7e/evidence/producer/audit/audit_param_K200000_nu284_298_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K200000_nu284_298_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `8c23a3d61927d17cd7b2d4f4b5115b60d960f4ed873560e45eac1a8d6dfcff49` |
| `r6b37c7e/evidence/producer/audit/audit_param_K200000_nu41_138.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K200000_nu41_138.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `f353cbf14331bd206b73182ca4cc68541af28f0fc1859075e773b61ad3c1bbd6` |
| `r6b37c7e/evidence/producer/audit/audit_param_K200000_nu41_298_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K200000_nu41_298_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `8dcbe4983062df1ca4844cf40f30aaf0d2e1ed493a5da5ea5932b21acf566c04` |
| `r6b37c7e/evidence/producer/audit/audit_param_K20000_nu113_115_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K20000_nu113_115_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `8fba4091294fcd3805c6f9d93cf2db16acfe80b08b1c3d33acdb9cfb26ee9292` |
| `r6b37c7e/evidence/producer/audit/audit_param_K20000_nu41_112_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K20000_nu41_112_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `2bece7286ff03d7beae18b38789e0dc761a2a3179961c5bf8778082a4dff4f1f` |
| `r6b37c7e/evidence/producer/audit/audit_param_K20000_nu41_64.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K20000_nu41_64.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `72499260baf1cf05fb22b8f5d6991fd94a5a8892e204a2ff7db2f1665ca9ac41` |
| `r6b37c7e/evidence/producer/audit/audit_param_K20000_nu70_112_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K20000_nu70_112_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `2c172811850f11f83c2a83785b0ab4338f4eae4bf4c6bd6ce3fb88540bad5c92` |
| `r6b37c7e/evidence/producer/audit/audit_param_K30000_nu41_132_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K30000_nu41_132_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `54a31e2ebb74b4065e538c0a087d44ca4bb1b407adcd7c36825530c384075657` |
| `r6b37c7e/evidence/producer/audit/audit_param_K30000_nu41_73.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K30000_nu41_73.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `2c2f006c2128d8c603677ea2278fecdbcf67b5609ec0be51463aa56951352cf5` |
| `r6b37c7e/evidence/producer/audit/audit_param_K30000_nu93_132_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K30000_nu93_132_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `acf75c6ff0661f6f9e2d6bc5ac6180539502b1969c9ed8d3ab0c25a9bbdeac3d` |
| `r6b37c7e/evidence/producer/audit/audit_param_K500000_nu400_435_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K500000_nu400_435_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `563053f11ca2f5baddf9ecf244cd979a978340dcadfa0e35eaf6b7f1e2a54fcc` |
| `r6b37c7e/evidence/producer/audit/audit_param_K500000_nu41_188.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K500000_nu41_188.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `f92e9aaca1a4ce743e2bd557afaf8a3ff598a81b76d53c5b7b41376faa4adb0b` |
| `r6b37c7e/evidence/producer/audit/audit_param_K500000_nu41_435_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K500000_nu41_435_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `0570d96b5d993f1d0951eb098f5e7f616eb3039e81483f287adc40a2ea4fe994` |
| `r6b37c7e/evidence/producer/audit/audit_param_K50000_nu129_164_ext2.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K50000_nu129_164_ext2.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `ba090ae4334ff786f31ef75a491f69c0cf39d5c2b6013090e083d49274724acc` |
| `r6b37c7e/evidence/producer/audit/audit_param_K50000_nu41_164_ext.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K50000_nu41_164_ext.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `4d63ede78d38efd9e684866394513786e4c035b075ad686936a272bd507f0e67` |
| `r6b37c7e/evidence/producer/audit/audit_param_K50000_nu41_87.txt` | [r6b37c7e] `evidence/producer/audit/audit_param_K50000_nu41_87.txt`(폴더 `evidence/producer/audit/`) | band102-integer | `a9c2eb6fd32a0d5d69f01628304eb94b9f7b13771a2adf24425bc1cdfdd8ef94` |
| `r6b37c7e/evidence/producer/audit/audit_param_ext.py` | [r6b37c7e] `evidence/producer/audit/audit_param_ext.py`(폴더 `evidence/producer/audit/`) | band102-integer | `b138d15c815f514f25bb40f5391e55881201c2beab3213b3af85bb79c3137692` |
| `r6b37c7e/evidence/producer/audit/audit_param_ext2.py` | [r6b37c7e] `evidence/producer/audit/audit_param_ext2.py`(폴더 `evidence/producer/audit/`) | band102-integer | `75063d44015c4fe6e7974f645cf9a17fb9b492160bf7eefc92b5dfc8b09ad3a6` |
| `r6b37c7e/evidence/producer/audit/hermite_probe.py` | [r6b37c7e] `evidence/producer/audit/hermite_probe.py`(폴더 `evidence/producer/audit/`) | band102-integer | `2396c794b60ed003c4ff3a9d7a642f0b0553dbcef4410be88875774f850ae5da` |
| `r6b37c7e/evidence/producer/audit/uv_general.py` | [r6b37c7e] `evidence/producer/audit/uv_general.py`(폴더 `evidence/producer/audit/`) | band102-integer | `43cf662deb14267e75cff8213b086cfe36fb1c80eecafb57852b3c20ce4b7351` |
| `r6b37c7e/evidence/producer/audit/uv_general_ext.py` | [r6b37c7e] `evidence/producer/audit/uv_general_ext.py`(폴더 `evidence/producer/audit/`) | band102-integer | `c0c6dc7f4dcc816a8110e63a1e81a87c918a7381a33f868ae716da223913298f` |
| `r6b37c7e/evidence/producer/audit/work/hermite/hermite_exact.py` | [r6b37c7e] `evidence/producer/audit/work/hermite/hermite_exact.py`(폴더 `evidence/producer/audit/`) | band102-integer | `63be858f55d1912e1aedada0a7d86a92dbb91c527a220679c28c577aadaba484` |
| `r6b37c7e/evidence/producer/audit/work/hermite/uv_20_23.json` | [r6b37c7e] `evidence/producer/audit/work/hermite/uv_20_23.json`(폴더 `evidence/producer/audit/`) | band102-integer | `8a98aef4c952ed4c0e1c8dbdbc1f81e184603f27b44183feaa3b9b951e1b0486` |
| `r6b37c7e/evidence/producer/audit/work/hermite/uv_5_19.json` | [r6b37c7e] `evidence/producer/audit/work/hermite/uv_5_19.json`(폴더 `evidence/producer/audit/`) | band102-integer | `f72e575f254f43418b5943ae78e295125156e6b3ea4fffe47096338127de8c1a` |
| `r6b37c7e/evidence/producer/audit/work/hermite/uv_general_m1_120.json` | [r6b37c7e] `evidence/producer/audit/work/hermite/uv_general_m1_120.json`(폴더 `evidence/producer/audit/`) | band102-integer | `c696b3644f9439188238d9d5d45dc676a9a25b20f2cd8a44d28c81f41702dbba` |
| `r6b37c7e/evidence/producer/audit/work/hermite/uv_general_m1_600.json` | [r6b37c7e] `evidence/producer/audit/work/hermite/uv_general_m1_600.json`(폴더 `evidence/producer/audit/`) | band102-integer | `f6e3e0e08bf3b839a74d033a1f4d5bb7c5964d9b42daaf4ced355ae9467b35ea` |
| `r6b37c7e/evidence/producer/icert/audit_strip.py` | [r6b37c7e] `evidence/producer/icert/audit_strip.py`(폴더 `evidence/producer/icert/`) | band102-integer | `e9139d9cb0426fbb5c9c1e94d50858d6f8701a7951c7185f50735105ae95c82f` |
| `r6b37c7e/evidence/producer/icert/audit_strip102_A.json` | [r6b37c7e] `evidence/producer/icert/audit_strip102_A.json`(폴더 `evidence/producer/icert/`) | band102-integer | `f6700cedcadf2267b04895faa734008ef653ce153cd78e31143462f9853b506e` |
| `r6b37c7e/evidence/producer/icert/audit_strip102_B.json` | [r6b37c7e] `evidence/producer/icert/audit_strip102_B.json`(폴더 `evidence/producer/icert/`) | band102-integer | `23716c1981dac68045feaf82f6aeaf0a7650669be0701b8e300c8f5e54e4c580` |
| `r6b37c7e/evidence/producer/icert/audit_strip102_C.json` | [r6b37c7e] `evidence/producer/icert/audit_strip102_C.json`(폴더 `evidence/producer/icert/`) | band102-integer | `e986c026a261177cdd76b8b31f3ef8598a38935b43f6b9d8a02a4f13204b2229` |
| `r6b37c7e/evidence/producer/icert/audit_strip102_D.json` | [r6b37c7e] `evidence/producer/icert/audit_strip102_D.json`(폴더 `evidence/producer/icert/`) | band102-integer | `62f9b75ceb3399aaa92203d49b468c4c2938a17760030a4748714b63bc355de8` |
| `r6b37c7e/evidence/producer/icert/audit_strip58.json` | [r6b37c7e] `evidence/producer/icert/audit_strip58.json`(폴더 `evidence/producer/icert/`) | band102-integer | `a8a54a80ba775673f6fd8e9b1b4874fc1911c198816d7fc0afe66dcb8dfd84ee` |
| `r6b37c7e/evidence/producer/icert/icert_rows.c` | [r6b37c7e] `evidence/producer/icert/icert_rows.c`(폴더 `evidence/producer/icert/`) | band102-integer | `97856048e2c6f24e66e4959a331a27e34a6fe45a996e7258e82e5fcbf2196b38` |
| `r6b37c7e/evidence/producer/icert/launch_A.ps1` | [r6b37c7e] `evidence/producer/icert/launch_A.ps1`(폴더 `evidence/producer/icert/`) | band102-integer | `ca2e054a94c1748d24e44e24b5e3abb3bfde85ad57493dc48a643d45ddae0b1e` |
| `r6b37c7e/evidence/producer/icert/nk_selftest.txt` | [r6b37c7e] `evidence/producer/icert/nk_selftest.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `6e5e6afac1e5e957e6330a5e7b311f542d00f8916d8bd2c1c1ac3b96a0189f39` |
| `r6b37c7e/evidence/producer/icert/nk_strip102_A1.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_A1.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `831a28d8a89ba033a29118abfc5e88f95c41bc60e77c55077fc94fd6f8064bf7` |
| `r6b37c7e/evidence/producer/icert/nk_strip102_A2.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_A2.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `2a5faa3595043571af51d7a34cf8f0fc004b93b2693f9e122d44c2e910f69ffa` |
| `r6b37c7e/evidence/producer/icert/nk_strip102_B.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_B.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `0a859f7c9aef06c52d2a2d5e15a2ee7ce76c7398db26e5f46987fd9414eb1711` |
| `r6b37c7e/evidence/producer/icert/nk_strip102_C.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_C.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `ef66453a2ce7a7871fde39a13695f6007ee6a86f9e4d9e7a730968a104c555a9` |
| `r6b37c7e/evidence/producer/icert/nk_strip102_D.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_D.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `446dd246dd7dc89f5f2babb3257bc3f023c9868a2a3a961ff3d098bfd08de3b1` |
| `r6b37c7e/evidence/producer/icert/nk_strip58_0.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip58_0.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `7421779b5fb2d50e4d05f47782c55514d0cab1a2814358ecfe73ef6133490e4b` |
| `r6b37c7e/evidence/producer/icert/nk_strip58_1.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip58_1.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `db4121af07ac6c3ef22dc3a5197deca45a5b73cfed46d51fb30b19020a0178ef` |
| `r6b37c7e/evidence/producer/icert/nk_strip58_2.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip58_2.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `8852280b841c2b1b6c9b03e7e700e45c23ae307b8611f64281cb6e2eb3242874` |
| `r6b37c7e/evidence/producer/icert/nk_strip58_3.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip58_3.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `de42b723b4fd89167db9d8fa5d60744d3e852535cc6ddf68f1bcf394fb0e48c9` |
| `r6b37c7e/evidence/producer/icert/out_selftest.txt` | [r6b37c7e] `evidence/producer/icert/out_selftest.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `e90c40a5b5c8e1d4c9fff172a5cb6d6544f16705a89265c0886c2520c4da9750` |
| `r6b37c7e/evidence/producer/icert/out_selftest.txt` | [r6b37c7e] `evidence/producer/icert/out_selftest.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `e90c40a5b5c8e1d4c9fff172a5cb6d6544f16705a89265c0886c2520c4da9750` |
| `r6b37c7e/evidence/producer/icert/out_selftest_mine.txt` | [r6b37c7e] `evidence/producer/icert/out_selftest_mine.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `778cc25cba8b8c7622f4757548cbbcb159dc2daac4a112e0f3de2fef0c3bbb69` |
| `r6b37c7e/evidence/producer/icert/out_selftest_mine.txt` | [r6b37c7e] `evidence/producer/icert/out_selftest_mine.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `778cc25cba8b8c7622f4757548cbbcb159dc2daac4a112e0f3de2fef0c3bbb69` |
| `r6b37c7e/evidence/producer/icert/out_strip102_A1.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_A1.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `e31a16ae42675011edda99294a7097b09b8b77e5c520ec516084acd56257827f` |
| `r6b37c7e/evidence/producer/icert/out_strip102_A1.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_A1.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `e31a16ae42675011edda99294a7097b09b8b77e5c520ec516084acd56257827f` |
| `r6b37c7e/evidence/producer/icert/out_strip102_A2.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_A2.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `955244459cf251aeedfa2339932206c13a44cc7c8e3c0ba076396cac42099702` |
| `r6b37c7e/evidence/producer/icert/out_strip102_A2.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_A2.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `955244459cf251aeedfa2339932206c13a44cc7c8e3c0ba076396cac42099702` |
| `r6b37c7e/evidence/producer/icert/out_strip102_B.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_B.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `d513b2f353eac2e63e5063e0200a0520a1fc108f91ad510eaa5657ac5f5a82d8` |
| `r6b37c7e/evidence/producer/icert/out_strip102_B.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_B.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `d513b2f353eac2e63e5063e0200a0520a1fc108f91ad510eaa5657ac5f5a82d8` |
| `r6b37c7e/evidence/producer/icert/out_strip102_C.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_C.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `942bc49637a3fd83b3c45abbc4325e82fe0e001b993084d727e3e18397cb737b` |
| `r6b37c7e/evidence/producer/icert/out_strip102_C.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_C.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `942bc49637a3fd83b3c45abbc4325e82fe0e001b993084d727e3e18397cb737b` |
| `r6b37c7e/evidence/producer/icert/out_strip102_D.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_D.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `bad83b9c0bccff42ad9e5e2ecd953c879ace1dba5632e1b992e92c168d940eec` |
| `r6b37c7e/evidence/producer/icert/out_strip102_D.txt` | [r6b37c7e] `evidence/producer/icert/out_strip102_D.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `bad83b9c0bccff42ad9e5e2ecd953c879ace1dba5632e1b992e92c168d940eec` |
| `r6b37c7e/evidence/producer/icert/out_strip58_0.txt` | [r6b37c7e] `evidence/producer/icert/out_strip58_0.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `3be419503a43b21d6f203a5eb198867c0a5c51ecfcc6e8971fcc3faa93810a60` |
| `r6b37c7e/evidence/producer/icert/out_strip58_0.txt` | [r6b37c7e] `evidence/producer/icert/out_strip58_0.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `3be419503a43b21d6f203a5eb198867c0a5c51ecfcc6e8971fcc3faa93810a60` |
| `r6b37c7e/evidence/producer/icert/out_strip58_1.txt` | [r6b37c7e] `evidence/producer/icert/out_strip58_1.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `123f7a3c6062846b3d8a215027d1ced77ec48057f49d27fc4626aecb6fb043b8` |
| `r6b37c7e/evidence/producer/icert/out_strip58_1.txt` | [r6b37c7e] `evidence/producer/icert/out_strip58_1.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `123f7a3c6062846b3d8a215027d1ced77ec48057f49d27fc4626aecb6fb043b8` |
| `r6b37c7e/evidence/producer/icert/out_strip58_2.txt` | [r6b37c7e] `evidence/producer/icert/out_strip58_2.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `12428a2bc88f2af00ea92d82272d34372b057a56e7e93ff1a5f7824de2eb9c4f` |
| `r6b37c7e/evidence/producer/icert/out_strip58_2.txt` | [r6b37c7e] `evidence/producer/icert/out_strip58_2.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `12428a2bc88f2af00ea92d82272d34372b057a56e7e93ff1a5f7824de2eb9c4f` |
| `r6b37c7e/evidence/producer/icert/out_strip58_3.txt` | [r6b37c7e] `evidence/producer/icert/out_strip58_3.txt`(패턴 `evidence/producer/icert/out_*.txt`) | band102-integer | `de28cedc20edad8ae6c5408449eb5859d630bfa7a50643b04aa2fccf997de504` |
| `r6b37c7e/evidence/producer/icert/out_strip58_3.txt` | [r6b37c7e] `evidence/producer/icert/out_strip58_3.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `de28cedc20edad8ae6c5408449eb5859d630bfa7a50643b04aa2fccf997de504` |
| `r6b37c7e/evidence/producer/icert/run102_A_start.txt` | [r6b37c7e] `evidence/producer/icert/run102_A_start.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `569022ff16e9807cf4b48be7ffe1590d42ca44a5a86f44c68fa2cddc5b29e4f3` |
| `r6b37c7e/evidence/producer/icert/run102_BCD_start.txt` | [r6b37c7e] `evidence/producer/icert/run102_BCD_start.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `12c6d1444961d2a6a0e37c3b095a77388631f09b7beb1c6f02f70adcbde6999e` |
| `r6b37c7e/evidence/producer/icert/run58_start.txt` | [r6b37c7e] `evidence/producer/icert/run58_start.txt`(폴더 `evidence/producer/icert/`) | band102-integer | `876a2c68f7369228791692d1ddadf998f5ad42f0d7543560beca5119354a2e5c` |
| `r6b37c7e/icert_rows.c` | [r6b37c7e] `evidence/producer/icert/icert_rows.c` | band102-integer | `97856048e2c6f24e66e4959a331a27e34a6fe45a996e7258e82e5fcbf2196b38` |
| `r6b37c7e/icert_sample_rerun.txt` | [r6b37c7e] `evidence/peer/icert/icert_sample_rerun.txt` | band102-integer | `1ac3ec7746718a0b423edd048eb5eae714b695d22720083c55bfbe68f88431af` |
| `r6b37c7e/nk_strip102_A1.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_A1.txt` | band102-integer | `831a28d8a89ba033a29118abfc5e88f95c41bc60e77c55077fc94fd6f8064bf7` |
| `r6b37c7e/nk_strip102_A2.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_A2.txt` | band102-integer | `2a5faa3595043571af51d7a34cf8f0fc004b93b2693f9e122d44c2e910f69ffa` |
| `r6b37c7e/nk_strip102_B.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_B.txt` | band102-integer | `0a859f7c9aef06c52d2a2d5e15a2ee7ce76c7398db26e5f46987fd9414eb1711` |
| `r6b37c7e/nk_strip102_C.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_C.txt` | band102-integer | `ef66453a2ce7a7871fde39a13695f6007ee6a86f9e4d9e7a730968a104c555a9` |
| `r6b37c7e/nk_strip102_D.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip102_D.txt` | band102-integer | `446dd246dd7dc89f5f2babb3257bc3f023c9868a2a3a961ff3d098bfd08de3b1` |
| `r6b37c7e/nk_strip58_0.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip58_0.txt` | band102-integer | `7421779b5fb2d50e4d05f47782c55514d0cab1a2814358ecfe73ef6133490e4b` |
| `r6b37c7e/nk_strip58_1.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip58_1.txt` | band102-integer | `db4121af07ac6c3ef22dc3a5197deca45a5b73cfed46d51fb30b19020a0178ef` |
| `r6b37c7e/nk_strip58_2.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip58_2.txt` | band102-integer | `8852280b841c2b1b6c9b03e7e700e45c23ae307b8611f64281cb6e2eb3242874` |
| `r6b37c7e/nk_strip58_3.txt` | [r6b37c7e] `evidence/producer/icert/nk_strip58_3.txt` | band102-integer | `de42b723b4fd89167db9d8fa5d60744d3e852535cc6ddf68f1bcf394fb0e48c9` |
| `r6b37c7e/pair_reach_T.py` | [r6b37c7e] `evidence/producer/code/pair_reach_T.py` | band102-integer | `b0f97a0c02ee6dbf14478c97c4500fd51c3da0586b61c8c9ebb7ec766f7085de` |
| `r6b37c7e/rerun_audit_K14000_nu97_100.txt` | [r6b37c7e] `evidence/peer/out/rerun_audit_K14000_nu97_100.txt` | band102-integer | `e089b980e16d0e9e07c8fac409b5e11cb27012ae212d6f52dcdf550131a883c1` |
| `r6b37c7e/rerun_audit_summary.txt` | [r6b37c7e] `evidence/peer/out/rerun_audit_summary.txt` | band102-integer | `36ee4563d930302e264d047f9972cf6255d321d4dd046a7f3a082512ddefa790` |
| `r6b37c7e/rerun_tail_pair.txt` | [r6b37c7e] `evidence/peer/out/rerun_tail_pair.txt` | band102-integer | `26e36f444b181b541950a32aa1ec01c28943731cdf1af816a9cfeeb7024b4753` |
| `r6b37c7e/review/checks/audit_rerun/log_K100000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K100000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `f0474e6f62358ca3c500d8d9f2de619437e910b14514bce4b821cbba4c3ce372` |
| `r6b37c7e/review/checks/audit_rerun/log_K1000000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K1000000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `347749af3b0ea30e6e956163b356e23948ce7dec3c1e5d94afb36139ae62cbb4` |
| `r6b37c7e/review/checks/audit_rerun/log_K12000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K12000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `408ef28acec441d26ad24edd5dfb19ba4db2ab45d883850305fc389a3f4fea79` |
| `r6b37c7e/review/checks/audit_rerun/log_K13000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K13000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `2706f484e822e655a06fcdf527843a04a80bf6bce3b07e304346ddb3e6f28850` |
| `r6b37c7e/review/checks/audit_rerun/log_K14000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K14000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `2c5827a548d1887a4e83b9e04e21f5cd2833155f54cf3c21191d9e6efe2c5d88` |
| `r6b37c7e/review/checks/audit_rerun/log_K15000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K15000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `a3d34d37cc6acc4c1dc14ab29b0eeba3e289aa46444a18d84dbd8f669d29f186` |
| `r6b37c7e/review/checks/audit_rerun/log_K20000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K20000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `da2f126908d618ff74f86c2d50dbef37f38232a733a09ce1c4b3f7e83627c043` |
| `r6b37c7e/review/checks/audit_rerun/log_K200000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K200000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `6adf53d6f539f43d1d922531a3b0d3fce61c1de6ebc0206339d788f504742ec0` |
| `r6b37c7e/review/checks/audit_rerun/log_K30000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K30000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `973acf7f036c8fa1817ddd42ac8fb9ba60feb1bb41890378befce208a3bf53de` |
| `r6b37c7e/review/checks/audit_rerun/log_K50000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K50000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `89ab9e0758d6869b26be0864e16f4e046a91ca1e0dfffa33ddf6ead5955bb433` |
| `r6b37c7e/review/checks/audit_rerun/log_K500000.txt` | [r6b37c7e] `review/checks/audit_rerun/log_K500000.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `6f117e5e0d625617084875b6a892533f86326f7b31e8cf47ddc9035b5d2a6b85` |
| `r6b37c7e/review/checks/audit_rerun/runrows.sh` | [r6b37c7e] `review/checks/audit_rerun/runrows.sh`(폴더 `review/checks/audit_rerun/`) | band102-integer | `88611212dfca6dcba7e7fc76fc1d04881be9d05f77f6b4f96372294d6e859396` |
| `r6b37c7e/review/checks/audit_rerun/summarize.py` | [r6b37c7e] `review/checks/audit_rerun/summarize.py`(폴더 `review/checks/audit_rerun/`) | band102-integer | `e5d498bae602bafe689a1d46233985332b3c48770a964691c6d7145a2f824f64` |
| `r6b37c7e/review/checks/audit_rerun/summary.txt` | [r6b37c7e] `review/checks/audit_rerun/summary.txt`(폴더 `review/checks/audit_rerun/`) | band102-integer | `c69cc1493cfa65ca3b0d3c07603b7170a8a5ba4fd0436f9e260dd1be93a27490` |
| `r6b37c7e/review/checks/icert/nk_review.txt` | [r6b37c7e] `review/checks/icert/nk_review.txt`(폴더 `review/checks/icert/`) | band102-integer | `ca23130e95a61f36ab339afd7568a4ce50a06b9c71d268415658870f1126edef` |
| `r6b37c7e/review/checks/icert/out_10500.txt` | [r6b37c7e] `review/checks/icert/out_10500.txt`(폴더 `review/checks/icert/`) | band102-integer | `61df802124851c2611708b301be51b234476667c56856065328756de7bbeb7dc` |
| `r6b37c7e/review/checks/icert/out_12500.txt` | [r6b37c7e] `review/checks/icert/out_12500.txt`(폴더 `review/checks/icert/`) | band102-integer | `24a766b0191a5c17ba8c124cbe5280b265707d1c4025938086bbf4c32c60f2cc` |
| `r6b37c7e/review/checks/icert/out_13500.txt` | [r6b37c7e] `review/checks/icert/out_13500.txt`(폴더 `review/checks/icert/`) | band102-integer | `897922f5fa4384f8234e31a14e96a913e3218639eaaf2905302a1ec531e16a1c` |
| `r6b37c7e/tail_lemma_check.py` | [r6b37c7e] `evidence/producer/code/tail_lemma_check.py` | band102-integer | `c652117479d49e0346cbfca9ce3002cf52f03aaf2f73f86d887ada3665df6cb7` |
| `r6b37c7e/verify_identities.py` | [r6b37c7e] `evidence/peer/verify_identities.py` | band102-integer | `1fb5077fbaf615e97520bcc0ddfdbe4691f479df3fb1d116378ef7ca1f52e816` |
| `r6b37c7e/verify_identities_n7.txt` | [r6b37c7e] `evidence/peer/out/verify_identities_n7.txt` | band102-integer | `c2b461a3d6ee7780fa9b31e0179913ecfccc0d2eb31c9c92d8c06d0de9bc64a2` |
| `r708d99c/cert_newton.py` | [r708d99c] `evidence/peer/cert_newton.py` | newton-m170 | `fc84b4e44b34f707e05d19e83ef4ffbbb39a07f4f7c34588a16a68f11c456b78` |
| `r708d99c/cert_newton_summary.json` | [r708d99c] `evidence/peer/cert_newton_summary.json` | newton-m170 | `7ae165cfd5687dcb88084b5cc4bcee995e6af495b25711759b0b36c272e989cf` |
| `r708d99c/peer_core.py` | [r708d99c] `evidence/peer/peer_core.py` | newton-m170 | `b71d30e78d52efb23956ff350dc76e7054cc26805df5df834b5ab1d1559ed6e3` |
| `r708d99c/recheck_certificate.py` | [r708d99c] `evidence/peer/recheck_certificate.py` | newton-m170 | `6abbb7b243616387607bd348bba10e5ee566939a3aed7e8637953a22830bb16a` |
| `r708d99c/recheck_certificate_out.json` | [r708d99c] `evidence/peer/recheck_certificate_out.json` | newton-m170 | `627a95f941718f1e1ebd5f364b96a84e5e65f1ba20b4cf35f7aa08c7de9b8962` |
| `r708d99c/renewal_poly_results.json` | [r708d99c] `evidence/producer/work/renewal_poly_results.json` | newton-m170 | `cf4d72c8f60d533d9b283b93794521a0ee245dccc5306a439d86899d8c03402d` |
| `r708d99c/rv_cert.py` | [r708d99c] `review/checks/rv_cert.py` | newton-m170 | `6470e7b164237777af963b16bcfa4f5208bef7cc49e7002cb8da15de3f191d9b` |
| `r708d99c/rv_cert_newton_A.json` | [r708d99c] `review/checks/rv_cert_newton_A.json` | newton-m170 | `d74b67a5f2073dd8028d1be2b8357677ca6262325d6b15e0f982eecbbb052895` |
| `r708d99c/rv_cert_newton_B.json` | [r708d99c] `review/checks/rv_cert_newton_B.json` | newton-m170 | `8e085e2ed8a3b0df0cb0d29e8a87d72a440ae69b32f16cf2a7af839c2e38254e` |
| `r708d99c/rv_core.py` | [r708d99c] `review/checks/rv_core.py` | newton-m170 | `d416e337f1b5923acc21ab97f911df372fda564827f2e98cb376edb5adc0f1e4` |
| `r708d99c/verify_P_poly.py` | [r708d99c] `evidence/peer/verify_P_poly.py` | newton-m170 | `2227542a2530eb8269b1ff1e53763cd1788fe21f84c87954dc6baa7043f34923` |
| `r708d99c/verify_reduction.py` | [r708d99c] `evidence/peer/verify_reduction.py` | newton-m170 | `d8cf90d391bba981b6d911ce5de7cdc39f8386d992f213f1b7c2f5a05ca578ab` |
| `r81e7051/computation-summary.json` | [r81e7051] `evidence/producer/output/computation-summary.json` | fiber-enumeration | `cc488c04238c1d0a054898050cd1324836e3d0f1bee90b85864a5c6d8cb4eaa4` |
| `r81e7051/counts.json` | [r81e7051] `evidence/producer/output/counts.json` | logconcavity-failure-n80 | `d6f43779914a31973dbc969590e5088e671c6339db7e2c1930b946d2f0a6dca8` |
| `r81e7051/evidence__peer-checks.json` | [r81e7051] `evidence/peer-checks.json` | logconcavity-failure-n80 | `303bcacd5630727b4fbeb5813d4e4c98bb63f8c6d9c3f0e2c7025ee6b761e28c` |
| `r81e7051/evidence__peer_verify.py` | [r81e7051] `evidence/peer_verify.py` | logconcavity-failure-n80 | `78ad8795c72c105b5b4db8d0c4cc16f05677668092953473bef4c0042e7b444c` |
| `r81e7051/evidence__producer__output__computation-summary.json` | [r81e7051] `evidence/producer/output/computation-summary.json` | logconcavity-failure-n80 | `cc488c04238c1d0a054898050cd1324836e3d0f1bee90b85864a5c6d8cb4eaa4` |
| `r81e7051/evidence__producer__work__explore.py` | [r81e7051] `evidence/producer/work/explore.py` | logconcavity-failure-n80 | `746a0aa105ee49e3abf5cd79d455081093407b0792ff48bbf1525645160d68c2` |
| `r81e7051/explore-run.log` | [r81e7051] `evidence/producer/work/explore-run.log` | fiber-enumeration | `800a351195917b56988e8477c51d77a7cf339b2ef8307c21f994ae853e4245ce` |
| `r81e7051/explore.py` | [r81e7051] `evidence/producer/work/explore.py` | fiber-enumeration | `746a0aa105ee49e3abf5cd79d455081093407b0792ff48bbf1525645160d68c2` |
| `r81e7051/peer-checks.json` | [r81e7051] `evidence/peer-checks.json` | fiber-enumeration | `303bcacd5630727b4fbeb5813d4e4c98bb63f8c6d9c3f0e2c7025ee6b761e28c` |
| `r81e7051/peer_verify.py` | [r81e7051] `evidence/peer_verify.py` | fiber-enumeration | `78ad8795c72c105b5b4db8d0c4cc16f05677668092953473bef4c0042e7b444c` |
| `r81e7051/structure-checks.json` | [r81e7051] `evidence/producer/output/structure-checks.json` | logconcavity-failure-n80 | `4f55114c67a2e90168ee075cba72b0f3d00f7967f9e1b7cae0fd0c20f47c021e` |
| `r845b205/rv_constU.py` | [r845b205] `review/evidence/rv_constU.py` | theorem-U-constant | `d8b25b2879396f6fd3f6192dc4a43150ada33bedcec6285570339eadce8a22ed` |
| `r845b205/rv_constU_out.txt` | [r845b205] `review/evidence/rv_constU_out.txt` | theorem-U-constant | `056cf0fc8707ff9bd5eebf4eacfd731ba86254242c0ae2d28998ed8ec3e1973e` |
| `r845b205/tv_certify.py` | [r845b205] `evidence/peer/tv_certify.py` | theorem-U-constant | `a386c75ed949e7cd6f018ed5c1e25106b8e31a94662bfbfd7891af58d5db85a3` |
| `r845b205/tv_certify_out.txt` | [r845b205] `evidence/peer/tv_certify_out.txt` | theorem-U-constant | `a9103e2875f58e1f4321e1f59d371c109746599f08525f406dd41b459b50f55c` |
| `r845b205/tv_stages.py` | [r845b205] `evidence/peer/tv_stages.py` | theorem-U-constant | `42c7c4b08ddb6028dab305fefd6a6c3677659e7af432b501c254eb1ad20a3ba7` |
| `r845b205/tv_stages_out.txt` | [r845b205] `evidence/peer/tv_stages_out.txt` | theorem-U-constant | `63c1a07bed40acf453129afbf54f84c57a7fec438d92321a4e0e5989f6c14ba8` |
| `r88bed8a/fibre_bound.txt` | [r88bed8a] `evidence/peer/data/fibre_bound.txt` | fiber-nonunimodal-bound | `9395d093d5e9441b3e9733c5dc38b00743f42bff00fe522dc43dc05f848790e3` |
| `r88bed8a/peer_fibre_bound.py` | [r88bed8a] `evidence/peer/code/peer_fibre_bound.py` | fiber-nonunimodal-bound | `881e58a8098bba48cadbef630d660f3b3e1023b86f8be2def62490e9a6f6dafd` |
| `r88bed8a/rv_check2.py` | [r88bed8a] `review/evidence/rv_check2.py` | fiber-nonunimodal-bound | `7f8d22c8a81ef3d6b8190db5eaed90099789c5ed7ad789700cdc235fb5f16d02` |
| `r88bed8a/rv_check2.txt` | [r88bed8a] `review/evidence/rv_check2.txt` | fiber-nonunimodal-bound | `c461499f460ce0164326ba2415d9e7f804ec033a6142dc35fa1342cbd8dd35d5` |
| `r89eb039/Gprime_samples.json` | [r89eb039] `evidence/peer/data/Gprime_samples.json` | polar-blocks-488 | `e17e5c71a41f8ccd7ce37b58efd3d551da2eb1280143faeeff3dea5b9bb4880d` |
| `r89eb039/achain3.py` | [r89eb039] `evidence/producer/code/asym/achain3.py` | polar-blocks-488 | `583661e25404dd8f49402ac99038b638a3736dac12998989a154a20a4271d17a` |
| `r89eb039/achain3_fix.diff` | [r89eb039] `review/evidence/L15_fix/achain3_fix.diff` | polar-blocks-488 | `2dfd94aa147144a68aaf81a3e34941b536b840233da171b050067e9b9a74d9ac` |
| `r89eb039/achain3_fixed.py` | [r89eb039] `review/evidence/L15_fix/achain3_fixed.py` | polar-blocks-488 | `5ad3ff891b794fc74febb927c82a69d21be49b8f680a6b25dfe58886307c2fac` |
| `r89eb039/achain_ia.py` | [r89eb039] `evidence/producer/code/asym/achain_ia.py` | polar-blocks-488 | `f13b5bf3886b9f19a525315da601115392d83b23398a2afef2bde633a1f73a13` |
| `r89eb039/adaptive_2087_5000.jsonl` | [r89eb039] `evidence/peer/data/adaptive_2087_5000.jsonl` | polar-blocks-488 | `16b50841bd5de587fedb6f20962d7adcd2cf364bc20c7a9703b81861a5e8fad3` |
| `r89eb039/asymptotic3.md` | [r89eb039] `evidence/producer/notes/asymptotic3.md` | polar-blocks-488 | `5048d8055e8e25f9c6913cdb827550b28dfe76d23865a344dc036dd1d10fe930` |
| `r89eb039/asymptotic3_tail.md` | [r89eb039] `evidence/producer/notes/asymptotic3_tail.md` | polar-blocks-488 | `ae0c14210918ccbedaf6156735ae2b1a1d5a50148052de2393898d00a34263e3` |
| `r89eb039/audit_report.md` | [r89eb039] `review/evidence/L15_fix/audit_report.md` | polar-blocks-488 | `335af6efd20d38f56d9780e640c0843d56efe00a1fe42571a52dbf056bc3c363` |
| `r89eb039/base.py` | [r89eb039] `evidence/peer/code/base.py` | polar-blocks-488 | `07414e6cfa08c8cdbad050282a811a06b7c17d7ba98f64d823410d3e560b293d` |
| `r89eb039/block_vs_truth.py` | [r89eb039] `evidence/peer/code/block_vs_truth.py` | polar-blocks-488 | `de39be51f64eae237d1b0a0394b33ebda1bb0e9fb1b87a02b311fc607bff14bc` |
| `r89eb039/bound_vs_truth.py` | [r89eb039] `evidence/peer/code/bound_vs_truth.py` | polar-blocks-488 | `b57e3d964187c0d39de7ebfd8c80cadfb4f8099cc7acb26ed24a85b0245d266f` |
| `r89eb039/bounds_ia.py` | [r89eb039] `evidence/producer/code/bounds_ia.py` | polar-blocks-488 | `c77ad31eb98cb6f4c71a32cb833b34a324820eeab0bc1696577551f36d92c25c` |
| `r89eb039/cert_fast.py` | [r89eb039] `evidence/producer/code/cert_fast.py` | polar-blocks-488 | `55d500bb9bb96ec134629bffeeab0e78eea4fa9270215de168f9cbec08fa532b` |
| `r89eb039/cert_ia.py` | [r89eb039] `evidence/producer/code/cert_ia.py` | polar-blocks-488 | `90f82f3a940f8ae86fe63e9db46a600f001cca5672474531bf2e445245de7471` |
| `r89eb039/cert_ia2.fix.diff` | [r89eb039] `evidence/peer/code/cert_ia2.fix.diff` | polar-blocks-488 | `4e52d528af4273c979e65fae9e23620cff5610dd7376449b290e04f0a4ced0b5` |
| `r89eb039/cert_ia2.py` | [r89eb039] `evidence/producer/code/cert_ia2.py` | polar-blocks-488 | `374e9a73f91182eb81d2f5611aece5854f663d887f5f411e7dda4b95669d41a0` |
| `r89eb039/check_cover.py` | [r89eb039] `evidence/producer/code/check_cover.py` | polar-blocks-488 | `b9be129b37a6ca36ed4a450de702fdf0c9c6df49531b60180d41b9c002098860` |
| `r89eb039/check_cover_sorted.py` | [r89eb039] `evidence/peer/code/check_cover_sorted.py` | polar-blocks-488 | `77ba0c4c90da3dc6c4cb47321bf4bd678c8d1a48978c8823e857a571cc5d6557` |
| `r89eb039/check_thmAB.py` | [r89eb039] `evidence/peer/code/check_thmAB.py` | polar-blocks-488 | `30915ac6048ec0f0ba152ecfd576fea82f96c73e29d057d837a484942e67f35f` |
| `r89eb039/coverage.txt` | [r89eb039] `evidence/peer/data/coverage.txt` | polar-blocks-488 | `33899ad067bf5a60f057b808b080a40e0af6c29aa94ffb95a78aa4d4bea6e8ea` |
| `r89eb039/ctx_fast.py` | [r89eb039] `evidence/producer/code/ctx_fast.py` | polar-blocks-488 | `aaff674c721fad4c6ddec29bfadacc96f056948bac3a4e99fb194852301a97da` |
| `r89eb039/evidence/peer/data/Gprime_samples.json` | [r89eb039] `evidence/peer/data/Gprime_samples.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `e17e5c71a41f8ccd7ce37b58efd3d551da2eb1280143faeeff3dea5b9bb4880d` |
| `r89eb039/evidence/peer/data/adaptive_2087_2400.log` | [r89eb039] `evidence/peer/data/adaptive_2087_2400.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `6403567563f7ae9318fa366f9309171856ee017df382e836aa16004534fb806c` |
| `r89eb039/evidence/peer/data/adaptive_2087_5000.jsonl` | [r89eb039] `evidence/peer/data/adaptive_2087_5000.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `16b50841bd5de587fedb6f20962d7adcd2cf364bc20c7a9703b81861a5e8fad3` |
| `r89eb039/evidence/peer/data/adaptive_2087_5000.log` | [r89eb039] `evidence/peer/data/adaptive_2087_5000.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `356c7516cad2d5a54378e25a87e261b6c4214eac1498132ca93373e63def8c45` |
| `r89eb039/evidence/peer/data/block_vs_truth.log` | [r89eb039] `evidence/peer/data/block_vs_truth.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `bf5d910cc885514b5687f4653af84c3dfe76911d01b75939ac5996c00ce2c474` |
| `r89eb039/evidence/peer/data/bvt_20000.json` | [r89eb039] `evidence/peer/data/bvt_20000.json`(패턴 `evidence/peer/data/bvt_*.json`) | polar-blocks-488 | `a51f93a21b135005175187aaa8b8e8a3bc4164349f37f4cd02c8ff4dfc13c91e` |
| `r89eb039/evidence/peer/data/bvt_20000.json` | [r89eb039] `evidence/peer/data/bvt_20000.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `a51f93a21b135005175187aaa8b8e8a3bc4164349f37f4cd02c8ff4dfc13c91e` |
| `r89eb039/evidence/peer/data/bvt_2001.json` | [r89eb039] `evidence/peer/data/bvt_2001.json`(패턴 `evidence/peer/data/bvt_*.json`) | polar-blocks-488 | `f72cc333dfb3f2a09c311577abd691e9696ce47c1096417ecb57db97a15c4b4c` |
| `r89eb039/evidence/peer/data/bvt_2001.json` | [r89eb039] `evidence/peer/data/bvt_2001.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `f72cc333dfb3f2a09c311577abd691e9696ce47c1096417ecb57db97a15c4b4c` |
| `r89eb039/evidence/peer/data/bvt_2001_fixed.json` | [r89eb039] `evidence/peer/data/bvt_2001_fixed.json`(패턴 `evidence/peer/data/bvt_*.json`) | polar-blocks-488 | `10bdc3d77b5dcfa00d702ea06917b07d6a7d5ff8078fc09671f8010c6a341d72` |
| `r89eb039/evidence/peer/data/bvt_2001_fixed.json` | [r89eb039] `evidence/peer/data/bvt_2001_fixed.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `10bdc3d77b5dcfa00d702ea06917b07d6a7d5ff8078fc09671f8010c6a341d72` |
| `r89eb039/evidence/peer/data/bvt_block_144741_147635.json` | [r89eb039] `evidence/peer/data/bvt_block_144741_147635.json`(패턴 `evidence/peer/data/bvt_*.json`) | polar-blocks-488 | `dd0a262e02db94084dc6ac392e2c93cce3c48b978cad440969a4c4af030aaa7b` |
| `r89eb039/evidence/peer/data/bvt_block_144741_147635.json` | [r89eb039] `evidence/peer/data/bvt_block_144741_147635.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `dd0a262e02db94084dc6ac392e2c93cce3c48b978cad440969a4c4af030aaa7b` |
| `r89eb039/evidence/peer/data/bvt_block_2001_2011.json` | [r89eb039] `evidence/peer/data/bvt_block_2001_2011.json`(패턴 `evidence/peer/data/bvt_*.json`) | polar-blocks-488 | `8739b4d428e3c7b5e99915ed5368cd2ae7688fcfe8bd1ea3310e883a852af354` |
| `r89eb039/evidence/peer/data/bvt_block_2001_2011.json` | [r89eb039] `evidence/peer/data/bvt_block_2001_2011.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `8739b4d428e3c7b5e99915ed5368cd2ae7688fcfe8bd1ea3310e883a852af354` |
| `r89eb039/evidence/peer/data/bvt_block_2895680_2953593.json` | [r89eb039] `evidence/peer/data/bvt_block_2895680_2953593.json`(패턴 `evidence/peer/data/bvt_*.json`) | polar-blocks-488 | `b270ba19a55b192a9c842c0c0ea9d58b56caf70656431e9a8e15e8be0406a333` |
| `r89eb039/evidence/peer/data/bvt_block_2895680_2953593.json` | [r89eb039] `evidence/peer/data/bvt_block_2895680_2953593.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `b270ba19a55b192a9c842c0c0ea9d58b56caf70656431e9a8e15e8be0406a333` |
| `r89eb039/evidence/peer/data/bvt_block_4670_4716.json` | [r89eb039] `evidence/peer/data/bvt_block_4670_4716.json`(패턴 `evidence/peer/data/bvt_*.json`) | polar-blocks-488 | `5fbd1c1d68981e5c2a91bc77cae0515ca0ecc760e371a12494c2bf48efceaba3` |
| `r89eb039/evidence/peer/data/bvt_block_4670_4716.json` | [r89eb039] `evidence/peer/data/bvt_block_4670_4716.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `5fbd1c1d68981e5c2a91bc77cae0515ca0ecc760e371a12494c2bf48efceaba3` |
| `r89eb039/evidence/peer/data/bvt_block_935263_953968.json` | [r89eb039] `evidence/peer/data/bvt_block_935263_953968.json`(패턴 `evidence/peer/data/bvt_*.json`) | polar-blocks-488 | `d4cfc839a14430091aef2e77900d9a36083590828e3f086b7ea7172e89966feb` |
| `r89eb039/evidence/peer/data/bvt_block_935263_953968.json` | [r89eb039] `evidence/peer/data/bvt_block_935263_953968.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `d4cfc839a14430091aef2e77900d9a36083590828e3f086b7ea7172e89966feb` |
| `r89eb039/evidence/peer/data/check_thmAB.out` | [r89eb039] `evidence/peer/data/check_thmAB.out`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `b5df9118851603884565d04621410381f8fbb830ec72e52061dc40ed23abe53c` |
| `r89eb039/evidence/peer/data/coverage.txt` | [r89eb039] `evidence/peer/data/coverage.txt`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `33899ad067bf5a60f057b808b080a40e0af6c29aa94ffb95a78aa4d4bea6e8ea` |
| `r89eb039/evidence/peer/data/l15_1e7_fast2.log` | [r89eb039] `evidence/peer/data/l15_1e7_fast2.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `d84bda7e82c81e6e40a3078b90da369876e55e3cb817468735548f934f6ea3c5` |
| `r89eb039/evidence/peer/data/l15_check_10000000.json` | [r89eb039] `evidence/peer/data/l15_check_10000000.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `eed2508d9eba19d3d8eaafd94aebdda5018f8bfd6487b77b9766565ff48b592a` |
| `r89eb039/evidence/peer/data/l15_sweep_100000.json` | [r89eb039] `evidence/peer/data/l15_sweep_100000.json`(패턴 `evidence/peer/data/l15_sweep_*.json`) | polar-blocks-488 | `ed23eedbe4a7cf7d9cc0b9377407b096709118ddd5a873b41b2eb3c345f1f384` |
| `r89eb039/evidence/peer/data/l15_sweep_100000.json` | [r89eb039] `evidence/peer/data/l15_sweep_100000.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `ed23eedbe4a7cf7d9cc0b9377407b096709118ddd5a873b41b2eb3c345f1f384` |
| `r89eb039/evidence/peer/data/l15_sweep_1000000.json` | [r89eb039] `evidence/peer/data/l15_sweep_1000000.json`(패턴 `evidence/peer/data/l15_sweep_*.json`) | polar-blocks-488 | `53058698a64b4d6c795e38f888be552571cbc83b964114efbc25eabe8d3ba79b` |
| `r89eb039/evidence/peer/data/l15_sweep_1000000.json` | [r89eb039] `evidence/peer/data/l15_sweep_1000000.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `53058698a64b4d6c795e38f888be552571cbc83b964114efbc25eabe8d3ba79b` |
| `r89eb039/evidence/peer/data/l15_sweep_10000000.json` | [r89eb039] `evidence/peer/data/l15_sweep_10000000.json`(패턴 `evidence/peer/data/l15_sweep_*.json`) | polar-blocks-488 | `5ad7aa6b7becfdd46b28f671ac11ee653e61cfe43914b93f426757d829616937` |
| `r89eb039/evidence/peer/data/l15_sweep_10000000.json` | [r89eb039] `evidence/peer/data/l15_sweep_10000000.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `5ad7aa6b7becfdd46b28f671ac11ee653e61cfe43914b93f426757d829616937` |
| `r89eb039/evidence/peer/data/l15_sweep_1e6.log` | [r89eb039] `evidence/peer/data/l15_sweep_1e6.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `296832592e9d35309d33a7b9be27ff6a0c1d51da0236840f8c693ef1d3f6796a` |
| `r89eb039/evidence/peer/data/l15_sweep_1e7.log` | [r89eb039] `evidence/peer/data/l15_sweep_1e7.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `a2cf9a6077ec84ace87652f38abf2024259cddda59fca79036ce23fbed8d2f91` |
| `r89eb039/evidence/peer/data/l15_sweep_300000.json` | [r89eb039] `evidence/peer/data/l15_sweep_300000.json`(패턴 `evidence/peer/data/l15_sweep_*.json`) | polar-blocks-488 | `e866dbe12f9c425c84eec900be9f89d9a155caa1d823ed50deefa25506ab2563` |
| `r89eb039/evidence/peer/data/l15_sweep_300000.json` | [r89eb039] `evidence/peer/data/l15_sweep_300000.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `e866dbe12f9c425c84eec900be9f89d9a155caa1d823ed50deefa25506ab2563` |
| `r89eb039/evidence/peer/data/l15_sweep_3000000.json` | [r89eb039] `evidence/peer/data/l15_sweep_3000000.json`(패턴 `evidence/peer/data/l15_sweep_*.json`) | polar-blocks-488 | `92a915eb1819eeda8c66560af4b5e31924715ff53b8a6da9d06367649c3308cc` |
| `r89eb039/evidence/peer/data/l15_sweep_3000000.json` | [r89eb039] `evidence/peer/data/l15_sweep_3000000.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `92a915eb1819eeda8c66560af4b5e31924715ff53b8a6da9d06367649c3308cc` |
| `r89eb039/evidence/peer/data/l15_sweep_3e5.log` | [r89eb039] `evidence/peer/data/l15_sweep_3e5.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `5a15ce4a1e85dd54e86d64e41c0158f0f5d5b5b19a7ce4af15ef7294511629a8` |
| `r89eb039/evidence/peer/data/l15_sweep_3e6.log` | [r89eb039] `evidence/peer/data/l15_sweep_3e6.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `b504d2b0a7d91d6334bf38fa17b6cb362b24eb4c0a28f6294f0f8a4d1150300e` |
| `r89eb039/evidence/peer/data/l15_sweep_repro.out` | [r89eb039] `evidence/peer/data/l15_sweep_repro.out`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `235e6cf7c059dd5aeb255da0fd438a79e8a2e95221cf0853d1df451a34fc4cae` |
| `r89eb039/evidence/peer/data/moments_check.out` | [r89eb039] `evidence/peer/data/moments_check.out`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `2404882912a63339c72900483b7de34059bc2124ed40f7347e890c5c2018ba59` |
| `r89eb039/evidence/peer/data/psi_exact_check.out` | [r89eb039] `evidence/peer/data/psi_exact_check.out`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `3aad5607003af880581588f7d1e9386d300ad415d4b6d65f4ccd0025ea6722dc` |
| `r89eb039/evidence/peer/data/recert_P1.jsonl` | [r89eb039] `evidence/peer/data/recert_P1.jsonl`(패턴 `evidence/peer/data/recert_*.jsonl`) | polar-blocks-488 | `671ad3f40e56734a7ec54e82bdcdcee25159dc5dd4101f09844794fec49f7bd0` |
| `r89eb039/evidence/peer/data/recert_P1.jsonl` | [r89eb039] `evidence/peer/data/recert_P1.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `671ad3f40e56734a7ec54e82bdcdcee25159dc5dd4101f09844794fec49f7bd0` |
| `r89eb039/evidence/peer/data/recert_P2.jsonl` | [r89eb039] `evidence/peer/data/recert_P2.jsonl`(패턴 `evidence/peer/data/recert_*.jsonl`) | polar-blocks-488 | `9f63b3787340fec9244bc70d7bc32bbb14d01cc7e2575c9d6b9eb4461af264ca` |
| `r89eb039/evidence/peer/data/recert_P2.jsonl` | [r89eb039] `evidence/peer/data/recert_P2.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `9f63b3787340fec9244bc70d7bc32bbb14d01cc7e2575c9d6b9eb4461af264ca` |
| `r89eb039/evidence/peer/data/recert_P3.jsonl` | [r89eb039] `evidence/peer/data/recert_P3.jsonl`(패턴 `evidence/peer/data/recert_*.jsonl`) | polar-blocks-488 | `112407a1c30e33b58693ec94c5a68e2b461a1f3072fe3c1d3f249136ec202379` |
| `r89eb039/evidence/peer/data/recert_P3.jsonl` | [r89eb039] `evidence/peer/data/recert_P3.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `112407a1c30e33b58693ec94c5a68e2b461a1f3072fe3c1d3f249136ec202379` |
| `r89eb039/evidence/peer/data/recert_P4a.jsonl` | [r89eb039] `evidence/peer/data/recert_P4a.jsonl`(패턴 `evidence/peer/data/recert_*.jsonl`) | polar-blocks-488 | `9075c54c504cfacac03adfc6d541ad0bb26c3d62fe6b3b411b51cd33ea37ecbe` |
| `r89eb039/evidence/peer/data/recert_P4a.jsonl` | [r89eb039] `evidence/peer/data/recert_P4a.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `9075c54c504cfacac03adfc6d541ad0bb26c3d62fe6b3b411b51cd33ea37ecbe` |
| `r89eb039/evidence/peer/data/recert_P4b.jsonl` | [r89eb039] `evidence/peer/data/recert_P4b.jsonl`(패턴 `evidence/peer/data/recert_*.jsonl`) | polar-blocks-488 | `b62972b70994dbc14e5868fe4c8fa7ad4c9f5160f31aec5a58a5e1a3560db93d` |
| `r89eb039/evidence/peer/data/recert_P4b.jsonl` | [r89eb039] `evidence/peer/data/recert_P4b.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `b62972b70994dbc14e5868fe4c8fa7ad4c9f5160f31aec5a58a5e1a3560db93d` |
| `r89eb039/evidence/peer/data/recert_Q1.jsonl` | [r89eb039] `evidence/peer/data/recert_Q1.jsonl`(패턴 `evidence/peer/data/recert_*.jsonl`) | polar-blocks-488 | `285c1db857c7d1d10e51f9fa330461a950f8fb86a6f1632fbf691fb622e28604` |
| `r89eb039/evidence/peer/data/recert_Q1.jsonl` | [r89eb039] `evidence/peer/data/recert_Q1.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `285c1db857c7d1d10e51f9fa330461a950f8fb86a6f1632fbf691fb622e28604` |
| `r89eb039/evidence/peer/data/recert_Q2.jsonl` | [r89eb039] `evidence/peer/data/recert_Q2.jsonl`(패턴 `evidence/peer/data/recert_*.jsonl`) | polar-blocks-488 | `66e7f70bb91af407832cbdd77036df91f103bde50760787ecc02268c46608790` |
| `r89eb039/evidence/peer/data/recert_Q2.jsonl` | [r89eb039] `evidence/peer/data/recert_Q2.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `66e7f70bb91af407832cbdd77036df91f103bde50760787ecc02268c46608790` |
| `r89eb039/evidence/peer/data/recert_summary.json` | [r89eb039] `evidence/peer/data/recert_summary.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `0bb285e9aca0064095d23ae3e4767aeb2287e82e8042393814a050b4e32cb336` |
| `r89eb039/evidence/peer/data/recert_summary.md` | [r89eb039] `evidence/peer/data/recert_summary.md`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `ad8b73ce08f39ce474367f842af7aedfa92cdf8ffc6a8c5d310a03e4df425d6f` |
| `r89eb039/evidence/peer/data/recert_tight.jsonl` | [r89eb039] `evidence/peer/data/recert_tight.jsonl`(패턴 `evidence/peer/data/recert_*.jsonl`) | polar-blocks-488 | `5b6cb53b42e3f45df6ff411799184827d36698321f126259b5470ab5fa4cf8a5` |
| `r89eb039/evidence/peer/data/recert_tight.jsonl` | [r89eb039] `evidence/peer/data/recert_tight.jsonl`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `5b6cb53b42e3f45df6ff411799184827d36698321f126259b5470ab5fa4cf8a5` |
| `r89eb039/evidence/peer/data/recert_tight.log` | [r89eb039] `evidence/peer/data/recert_tight.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `0545bbfe062764099065b2dbf5ae84ed7050ddaa16d0b0063c87369f8e67de9a` |
| `r89eb039/evidence/peer/data/tail_split.log` | [r89eb039] `evidence/peer/data/tail_split.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `8de47e52cbc7fb4c47dcfecd0cef0473e9696076aad4348145e1e132774dfb0d` |
| `r89eb039/evidence/peer/data/tail_split_1e4_1e5_1e6.json` | [r89eb039] `evidence/peer/data/tail_split_1e4_1e5_1e6.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `1125b099ce50b65e65b0000b2bc4e557bf3c30016941eef39a4b33da5446072e` |
| `r89eb039/evidence/peer/data/tail_split_1e7.json` | [r89eb039] `evidence/peer/data/tail_split_1e7.json`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `7a4c324775f5f8ed43700c67dbb45a569e96d44607909febfb9b7c41e8b8e4dd` |
| `r89eb039/evidence/peer/data/tail_split_1e7.log` | [r89eb039] `evidence/peer/data/tail_split_1e7.log`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `72e591bf9f6d83a9693b7a8a027d0acaa5d8c0c2e6cff785e86ad2489c4e7679` |
| `r89eb039/evidence/peer/data/tv_allotment_check.out` | [r89eb039] `evidence/peer/data/tv_allotment_check.out`(폴더 `evidence/peer/data/`) | polar-blocks-488 | `7ddfb2c8b61ed3e6ac85cf7387821a260ad1876c30944df32c2029d5cdc8109a` |
| `r89eb039/evidence__peer__code__fixed__cert_ia2.py` | [r89eb039] `evidence/peer/code/fixed/cert_ia2.py` | polar-blocks-488 | `a2471dbcaca6b1afe24dc177e08a4b7bd5dd6772c55650f197876bf85b352fd6` |
| `r89eb039/ia.py` | [r89eb039] `evidence/producer/code/ia.py` | polar-blocks-488 | `99759f0eccd13d9611191da9c9d46dfed623dfad03686167ca6e11a6a1e8557e` |
| `r89eb039/l15_check.py` | [r89eb039] `evidence/peer/code/l15_check.py` | polar-blocks-488 | `ad094ba6bc0fe6bef6a00621ea8e789944300a22d56dfd6848db11b6d91c2732` |
| `r89eb039/l15_check_10000000.json` | [r89eb039] `evidence/peer/data/l15_check_10000000.json` | polar-blocks-488 | `eed2508d9eba19d3d8eaafd94aebdda5018f8bfd6487b77b9766565ff48b592a` |
| `r89eb039/l15_sweep_check.py` | [r89eb039] `evidence/peer/code/l15_sweep_check.py` | polar-blocks-488 | `33754926562e9c3a2436ba0cf2b984c8847f4b3db6b1d2bbc5a14a6e0d20743d` |
| `r89eb039/lemmas_L14.md` | [r89eb039] `evidence/producer/notes/lemmas_L14.md` | polar-blocks-488 | `23ce7979d9aecce4d1e50464f33e1256f0af84595f9213f3d1ca558d4e4af9b4` |
| `r89eb039/polecore.py` | [r89eb039] `evidence/producer/code/polecore.py` | polar-blocks-488 | `3f8797622960e0afeda641aaa45e50959be69e8083a1010a9dafe9744936f712` |
| `r89eb039/psi_exact_check.py` | [r89eb039] `evidence/peer/code/psi_exact_check.py` | polar-blocks-488 | `7dba09f004f48a594474e72606666f8536b097c58a46aada5e19ff738d889b96` |
| `r89eb039/recert.py` | [r89eb039] `evidence/peer/code/recert.py` | polar-blocks-488 | `9c71de65b076d0d23ccd92192df6861fe5ff8effe89b5d942e74887e757e3813` |
| `r89eb039/recert_summary.md` | [r89eb039] `evidence/peer/data/recert_summary.md` | polar-blocks-488 | `ad8b73ce08f39ce474367f842af7aedfa92cdf8ffc6a8c5d310a03e4df425d6f` |
| `r89eb039/review__evidence__block_audit__audit_report.md` | [r89eb039] `review/evidence/block_audit/audit_report.md` | polar-blocks-488 | `8307bb7fd7b4c1f1615dc6331d1603932135412a827f832055e49bcfe25fef37` |
| `r89eb039/run_blocks3.py` | [r89eb039] `evidence/producer/code/run_blocks3.py` | polar-blocks-488 | `08360e7446bedcb6d4e7c1af0982ceb6a2531c102f3b1176fab3e72967123195` |
| `r89eb039/run_fixed_driver.py` | [r89eb039] `evidence/peer/code/run_fixed_driver.py` | polar-blocks-488 | `346c8f8fdff1f3a40d848e7a532b724c589dfcd7c2d1ee8c068d950a1dada330` |
| `r89eb039/sparts.py` | [r89eb039] `evidence/producer/code/sparts.py` | polar-blocks-488 | `a67fe867503baf74cdda2975f40232f17e2474b19cbc7af42fd7828b65589eeb` |
| `r89eb039/sweep3_K10000000.jsonl` | [r89eb039] `evidence/producer/data/asym/sweep3_K10000000.jsonl` | polar-blocks-488 | `faeaceaf8f278239f86d702d75c0d8e38474192289ada7592cbdf36844febe72` |
| `r89eb039/sweep3fixed_K10000000.jsonl` | [r89eb039] `review/evidence/L15_fix/sweep3fixed_K10000000.jsonl` | polar-blocks-488 | `98d25162a8ed00849c9f660c87f8a73e99952645b406ac0dfa3bc146bd353432` |
| `r89eb039/truth_big.py` | [r89eb039] `evidence/peer/code/truth_big.py` | polar-blocks-488 | `2c3aae7afad03d0094e93108013b6bb90ff32c3eca4a4349987ae6d0b5044989` |
| `r89eb039/tv_allotment_check.out` | [r89eb039] `evidence/peer/data/tv_allotment_check.out` | polar-blocks-488 | `7ddfb2c8b61ed3e6ac85cf7387821a260ad1876c30944df32c2029d5cdc8109a` |
| `r8a9b11e/band_iv.py` | [r8a9b11e] `evidence/peer/band_iv.py` | band-check | `25b17b01d7f84d53f7f92d8f463e68e5113a2a0c08a1448bd6f34225d41ee208` |
| `r8a9b11e/cemaj_iv.py` | [r8a9b11e] `evidence/peer/cemaj_iv.py` | zeta-constants | `1e2efc48b3ca11526501d382fb43885da47a4985bacfffa6c8fccafa02ff4893` |
| `r8a9b11e/ul_iv.py` | [r8a9b11e] `evidence/peer/ul_iv.py` | window-mass-constant | `ef7169f09ac2e046f08c7e55484d453d0a8f9b42c191ab02dcc4bace6d451294` |
| `r9e782f5/audit.json` | [r9e782f5] `peer/audit.json` | seed-certificates-k120 | `318aa5f1d771343ce8c4be2f0b49c626a4ea424250aba97a79ed94fca3bf11f9` |
| `r9e782f5/peer_verify.py` | [r9e782f5] `peer_verify.py` | seed-certificates-k120 | `ab1f381b7f16d4414bc0b0ed8ce89ebd6b0934a1b1d0e23b9d4a671c75d6a5d7` |
| `r9e782f5/producer-files.json` | [r9e782f5] `producer-files.json` | seed-certificates-k120 | `a42fe23c4c437ea84d4a875a5aed6f117bd65bb1e55fa859314ddaf529f044c9` |
| `r9e782f5/producer/certificate-k10.json` | [r9e782f5] `producer/certificate-k10.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `fbd8bd71f1dd495becb873f37b05d5c20862cdd774bc6dc630c199cb811c29e2` |
| `r9e782f5/producer/certificate-k100.json` | [r9e782f5] `producer/certificate-k100.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `a2616787dfa84e4aac246d3a1f2a1e8fef5b66945d8f647fa0b0f23eb85232f1` |
| `r9e782f5/producer/certificate-k101.json` | [r9e782f5] `producer/certificate-k101.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `b09b6ce05e704427267405b1bb8970383c3813a9304e5c3d93e0723dc04c8378` |
| `r9e782f5/producer/certificate-k102.json` | [r9e782f5] `producer/certificate-k102.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `89a4b87e116def6e617bcd34593be620fcfc6292712b87cfaa7acc0a4f027f75` |
| `r9e782f5/producer/certificate-k103.json` | [r9e782f5] `producer/certificate-k103.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `387a60e504371d7a77aae923d7fd2d0546cecedc63b818c093cc1131ca2afa98` |
| `r9e782f5/producer/certificate-k104.json` | [r9e782f5] `producer/certificate-k104.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `f1f54766012efd7eb2072a7adf1f23874790fd3d1c802c632513c467a7619ce7` |
| `r9e782f5/producer/certificate-k105.json` | [r9e782f5] `producer/certificate-k105.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `96a38e8f42d8fe3f85ec56305a4326a5622e695e4e986556383ff589e97d53ed` |
| `r9e782f5/producer/certificate-k106.json` | [r9e782f5] `producer/certificate-k106.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `bfc1f7d3177bf529ba2b6f0cd0a2cf27f4a1acdf2dbc6dfa38ca5c96da15f19d` |
| `r9e782f5/producer/certificate-k107.json` | [r9e782f5] `producer/certificate-k107.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `19abc69c3bb145e0e194e7591e8672dae037397f8ddf995a01366ceced0c8d10` |
| `r9e782f5/producer/certificate-k108.json` | [r9e782f5] `producer/certificate-k108.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `5ec5affe502c6455890c327a10423683743e0185e752c5d94e92803ed1baad79` |
| `r9e782f5/producer/certificate-k109.json` | [r9e782f5] `producer/certificate-k109.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `db3fa5f7d5d66c034c3fc107c10aa2f4b953afb4db3af9a6a7c138c49f4d3de1` |
| `r9e782f5/producer/certificate-k11.json` | [r9e782f5] `producer/certificate-k11.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `3e1a587b48df03d5376c09536c966869b5584a5a092ff173398d83e1152f121e` |
| `r9e782f5/producer/certificate-k110.json` | [r9e782f5] `producer/certificate-k110.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `8ea18fecb352496cde516f2b8f6d6becb3ef32ea2e3f2d6a9f3e85b804f69c64` |
| `r9e782f5/producer/certificate-k111.json` | [r9e782f5] `producer/certificate-k111.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `90ab7e0970f9813a1823de9be1e7c583486b917f9dac33eeeaf70d80ea90470d` |
| `r9e782f5/producer/certificate-k112.json` | [r9e782f5] `producer/certificate-k112.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `3e861cf8f1092ea3695913c5e761d51f61ba3c5b8a9cab6480099685432ef262` |
| `r9e782f5/producer/certificate-k113.json` | [r9e782f5] `producer/certificate-k113.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `b5736ba4beea2ee941fb4899619c0fd51b351347e13dbba88255d8097505fa1c` |
| `r9e782f5/producer/certificate-k114.json` | [r9e782f5] `producer/certificate-k114.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `e59feb172c715d8d4ac8aaa3ffaad57649922e5d421c8dd1fd9b21a2ab3609e1` |
| `r9e782f5/producer/certificate-k115.json` | [r9e782f5] `producer/certificate-k115.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `b2b89e92ad8e5aa82081d93e5fb49c8eb988e2b9e25372755e30e30bad117329` |
| `r9e782f5/producer/certificate-k116.json` | [r9e782f5] `producer/certificate-k116.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `5621202f9e412bdf8ef59cac9145cd12e7f1a01ea1024405f2ab868a0f2d0a2e` |
| `r9e782f5/producer/certificate-k117.json` | [r9e782f5] `producer/certificate-k117.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `e9807f0212b4e47075f96ae727b396eda663e1d291a5a50488b9f6dd66fdac95` |
| `r9e782f5/producer/certificate-k118.json` | [r9e782f5] `producer/certificate-k118.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `df3d84e8b7009eb44cb74a1e7b3e50a45842f20f65c668cf080aef562fd5b25a` |
| `r9e782f5/producer/certificate-k119.json` | [r9e782f5] `producer/certificate-k119.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `256e53aa92b915903a2b5fc6af75de20a82042db3013bb1bf68ada01bf644aa4` |
| `r9e782f5/producer/certificate-k12.json` | [r9e782f5] `producer/certificate-k12.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `924dd01c13b34448b3bb7d770e12753111fcc206adcbb56c0de1867ba805e8bc` |
| `r9e782f5/producer/certificate-k120.json` | [r9e782f5] `producer/certificate-k120.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `54065520f2192d1b031a31b28113a180f6508e2ba82c14670e61eeea2b5bd3c5` |
| `r9e782f5/producer/certificate-k13.json` | [r9e782f5] `producer/certificate-k13.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `173115a9be8f46929df6c28ebc244e4aa3d228341d778ae48555bbed3f622616` |
| `r9e782f5/producer/certificate-k14.json` | [r9e782f5] `producer/certificate-k14.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `25d4189922ba78e9d6d6ac2ad6c1c8d53cfeabe595bf0e00bb6cfd10e5f23d26` |
| `r9e782f5/producer/certificate-k15.json` | [r9e782f5] `producer/certificate-k15.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `cf6d01c4267c68aab631a411041948ea3fc223857beae7130a3a680002c411e5` |
| `r9e782f5/producer/certificate-k16.json` | [r9e782f5] `producer/certificate-k16.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `31a682dd572eda05a522b47bb6d16440c1e1ea3606537650e97eb133578a0007` |
| `r9e782f5/producer/certificate-k17.json` | [r9e782f5] `producer/certificate-k17.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `52a8fb5aaf45dfbc2e0689b5befaf30cec549e70a690af7b572e732cd796e6f7` |
| `r9e782f5/producer/certificate-k18.json` | [r9e782f5] `producer/certificate-k18.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `c232334088d8343173a45159513ff3eb781f60a599e11b5d826094491e5d4164` |
| `r9e782f5/producer/certificate-k19.json` | [r9e782f5] `producer/certificate-k19.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `66297e9a422359f0623853dcc272700e0c7b49f08546d401fddc9da0c9c13159` |
| `r9e782f5/producer/certificate-k2.json` | [r9e782f5] `producer/certificate-k2.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `bc2221f247cc4bfa1b0a256e527bf549d93218179e95586be1460e00ac1315d7` |
| `r9e782f5/producer/certificate-k20.json` | [r9e782f5] `producer/certificate-k20.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `d9332132aa71699b830074899c557f155e865bdd391316881590ed0e3d8713e3` |
| `r9e782f5/producer/certificate-k21.json` | [r9e782f5] `producer/certificate-k21.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `c3ee81d67d17e3ea9201283fdf3c4ce4ba54426d404f08e0890dd4f217e336ae` |
| `r9e782f5/producer/certificate-k22.json` | [r9e782f5] `producer/certificate-k22.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `5154864c0d8b6e841f99eee34d135f781d46c389b46a751aba9c9423b029e553` |
| `r9e782f5/producer/certificate-k23.json` | [r9e782f5] `producer/certificate-k23.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `5c3ceeca9823016216fc72accec68b9623a5752e039ec79937fb30d110d589ed` |
| `r9e782f5/producer/certificate-k24.json` | [r9e782f5] `producer/certificate-k24.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `b3c3a163187ad1fec85661c4303776e4ccb2d425f7369cb648ede8c663a1a3f5` |
| `r9e782f5/producer/certificate-k25.json` | [r9e782f5] `producer/certificate-k25.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `d8dfc5a570a812540369acb369df093bc34f9de6df4b38baef870ca802b3c9ce` |
| `r9e782f5/producer/certificate-k26.json` | [r9e782f5] `producer/certificate-k26.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `7facae50df39045121321bbb1ab203aec05ca125aa58e8163c16b4ce9ac10644` |
| `r9e782f5/producer/certificate-k27.json` | [r9e782f5] `producer/certificate-k27.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `dbeacf71dc6624f0353c07f2c74e831649f80d76deac7d430647e7d93e483b5d` |
| `r9e782f5/producer/certificate-k28.json` | [r9e782f5] `producer/certificate-k28.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `92e11474bfa5d867347afda755981f4c196e7923648d0bd17b5be760ca0fc233` |
| `r9e782f5/producer/certificate-k29.json` | [r9e782f5] `producer/certificate-k29.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `5a24da30982e99f4c10ee3fa262b749f57fe949d141cbf542cf0ed4cfa3e76aa` |
| `r9e782f5/producer/certificate-k3.json` | [r9e782f5] `producer/certificate-k3.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `2d3af8c1c52e3deacebc2347ad0fd23bd4974f2350bb9ec63e87ef000587f58a` |
| `r9e782f5/producer/certificate-k30.json` | [r9e782f5] `producer/certificate-k30.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `91c078a8b1da9fed20a8844d28b2dd9c6f9c0ac78f48b1cdfad8fa2f38aa2bfe` |
| `r9e782f5/producer/certificate-k31.json` | [r9e782f5] `producer/certificate-k31.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `2b27b620e730e770b0af30eff16eb390174be0d507d6079aa3022518a7b04e33` |
| `r9e782f5/producer/certificate-k32.json` | [r9e782f5] `producer/certificate-k32.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `4135c6e560485dd1a86e9843b3abcb2aa3a25d606b68430997aa38906397341a` |
| `r9e782f5/producer/certificate-k33.json` | [r9e782f5] `producer/certificate-k33.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `c558088c0f9de1cb4161e782d7ff10bbcd1219c3eb541e98bdfad1a5276a284f` |
| `r9e782f5/producer/certificate-k34.json` | [r9e782f5] `producer/certificate-k34.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `9a4dc014c7ae37a4a4e6ef74f047a6462599d3b5adbf6e36704b4e7c1e639278` |
| `r9e782f5/producer/certificate-k35.json` | [r9e782f5] `producer/certificate-k35.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `b36176eedd413705ed8a66d06306263a62fa64a330aeab291e22c8e7820d3187` |
| `r9e782f5/producer/certificate-k36.json` | [r9e782f5] `producer/certificate-k36.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `13442b1ee09d5b2e59352d9bf58f77111cfb22eb540414ae1496dd03e1b2f8b3` |
| `r9e782f5/producer/certificate-k37.json` | [r9e782f5] `producer/certificate-k37.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `df56316a3364b25653f2d7f6555da3859e95127067ba7142af4ee527e131fdb7` |
| `r9e782f5/producer/certificate-k38.json` | [r9e782f5] `producer/certificate-k38.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `f15b6c85386e305ddc6b718ff3c37debf593410bab8d4271ac47c5c3ab23bc85` |
| `r9e782f5/producer/certificate-k39.json` | [r9e782f5] `producer/certificate-k39.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `215cd4147306de7faf43b392df426c8237317fe21ede96826de25b22453bdd13` |
| `r9e782f5/producer/certificate-k4.json` | [r9e782f5] `producer/certificate-k4.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `10dcb927d618fcaab271ce41063bd66501b848f1cb74966e4d6638f42925c2b2` |
| `r9e782f5/producer/certificate-k40.json` | [r9e782f5] `producer/certificate-k40.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `b29708fa6cb4d85dc412cb1a28f98df5bc91f36c0f410f740f667ec8ea3e379e` |
| `r9e782f5/producer/certificate-k41.json` | [r9e782f5] `producer/certificate-k41.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `767618c111a6d54e147cc14e68c3756e68a5f01969b4bba46643e90366fed6f1` |
| `r9e782f5/producer/certificate-k42.json` | [r9e782f5] `producer/certificate-k42.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `78fb1f9380d7cd7222f526f516e4d42c4e659c5199bbe9d1c0f23266f7022d1c` |
| `r9e782f5/producer/certificate-k43.json` | [r9e782f5] `producer/certificate-k43.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `d4673b050f203c5bda268d8e81bde6e233b4fb671f27a5b1b850d0aa708a68fb` |
| `r9e782f5/producer/certificate-k44.json` | [r9e782f5] `producer/certificate-k44.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `c98eda1e96e582dd1fc54e37efc80dd61ac4680ccae154d8fe5899cf8968ce3c` |
| `r9e782f5/producer/certificate-k45.json` | [r9e782f5] `producer/certificate-k45.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `6380f480d40cfc779da4728f0789a62274b34d88a60dd1e5e22ca4972347d46b` |
| `r9e782f5/producer/certificate-k46.json` | [r9e782f5] `producer/certificate-k46.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `261057bffdf7a3a1c0153a46c01853415154ffe6dc58e7ea66145939a0cbcdc6` |
| `r9e782f5/producer/certificate-k47.json` | [r9e782f5] `producer/certificate-k47.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `38239537f84cb0d68d67cc6431673874c71d1f939933e24286ccd73cd7adc3e0` |
| `r9e782f5/producer/certificate-k48.json` | [r9e782f5] `producer/certificate-k48.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `464a1ccab03d187994e189e40382aa3a852c3fb5963fe4f6a659e873ec40e8ef` |
| `r9e782f5/producer/certificate-k49.json` | [r9e782f5] `producer/certificate-k49.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `f23fbc616f143d889fec4f0b5a0fe71025c5ed5030c07c4e6f6161054aa79c99` |
| `r9e782f5/producer/certificate-k5.json` | [r9e782f5] `producer/certificate-k5.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `e95f60e4343718606acbbdc4d41c3090bd2c8c67b16a41f5c928cdaccd7eff5c` |
| `r9e782f5/producer/certificate-k50.json` | [r9e782f5] `producer/certificate-k50.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `baca70799a5a183be368969df5300457d259b10900e73d41be9f850febc16fde` |
| `r9e782f5/producer/certificate-k51.json` | [r9e782f5] `producer/certificate-k51.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `dccb5168e77a2a4755de9b8b3a3c3243492c871475d70e607420d0a0b8465816` |
| `r9e782f5/producer/certificate-k52.json` | [r9e782f5] `producer/certificate-k52.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `42417373baf45612aec55e7ae3b0c4b07d93adc77494501a13ff4a7410d12837` |
| `r9e782f5/producer/certificate-k53.json` | [r9e782f5] `producer/certificate-k53.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `49b20d6d5d11ac5c68d9a34f807a33366851c2762a257f4bb9c88f89338b3f54` |
| `r9e782f5/producer/certificate-k54.json` | [r9e782f5] `producer/certificate-k54.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `31ea32c01bf8eb31ddac9bc9f8705556d9791b7150eb6ab91136d8f6a8159ea3` |
| `r9e782f5/producer/certificate-k55.json` | [r9e782f5] `producer/certificate-k55.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `d3ac4d8cc9eefee332a7c5b2fa8efddb841fac7e5cfe8110afd235eb3355c44f` |
| `r9e782f5/producer/certificate-k56.json` | [r9e782f5] `producer/certificate-k56.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `c70bf4bf7543fecba2c2f58ec32f651359294f004922122d3d4d5433f30d58d6` |
| `r9e782f5/producer/certificate-k57.json` | [r9e782f5] `producer/certificate-k57.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `9d760c504e12ddf88706648d6f75a9767a4f9feebf9e32b9872e5da3a348d3ec` |
| `r9e782f5/producer/certificate-k58.json` | [r9e782f5] `producer/certificate-k58.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `77b0638e8270e87884a4a70fdd5c711f33ad0fb672ca49fcc79126de8eab0aef` |
| `r9e782f5/producer/certificate-k59.json` | [r9e782f5] `producer/certificate-k59.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `ca75cd64835e27083ef69b52289390e7d0da0bbba4f07ad34bead2fa871ed658` |
| `r9e782f5/producer/certificate-k6.json` | [r9e782f5] `producer/certificate-k6.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `6ffb04a8c61e574a46989656abbbb970d8b0a124cf60e9e138b451e499741f9d` |
| `r9e782f5/producer/certificate-k60.json` | [r9e782f5] `producer/certificate-k60.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `c15a4edbd6f4216196024e8d74b54d32bda47efda99ebb46d1d83664c832a83c` |
| `r9e782f5/producer/certificate-k61.json` | [r9e782f5] `producer/certificate-k61.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `bef76dab5ece597052846c5e0a6be02aa6334d28db022c2eda78fd98ae90af7f` |
| `r9e782f5/producer/certificate-k62.json` | [r9e782f5] `producer/certificate-k62.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `dfbcd39bbd79944050d2ddd6dedd4829665a6d4612aa29041f854297c279e05f` |
| `r9e782f5/producer/certificate-k63.json` | [r9e782f5] `producer/certificate-k63.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `6b2900efa60d13bd68ba71495de222ca3b75899ca4c44717a700ca97e4b9b835` |
| `r9e782f5/producer/certificate-k64.json` | [r9e782f5] `producer/certificate-k64.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `4c1ef83f206467dae94002267e8959d9398c3144c3d497d87f95afb76019ff6a` |
| `r9e782f5/producer/certificate-k65.json` | [r9e782f5] `producer/certificate-k65.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `1c74fdfa14eef43805a787ff693a56c4c5831bb0666219d681d926b29fb2ad56` |
| `r9e782f5/producer/certificate-k66.json` | [r9e782f5] `producer/certificate-k66.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `bbf8b4308e4b8ac0d0427f7b1c1a3348eda5e31a0a510f220141649180cc19c6` |
| `r9e782f5/producer/certificate-k67.json` | [r9e782f5] `producer/certificate-k67.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `0ed185ce70a9e117df2114c29e7a97625c7d061bdf4c9411ca5c50e3c1509af4` |
| `r9e782f5/producer/certificate-k68.json` | [r9e782f5] `producer/certificate-k68.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `f447a0965d0cef6c34ae276e0f042fe0c1b80e09c654511f844f22cbf12688f0` |
| `r9e782f5/producer/certificate-k69.json` | [r9e782f5] `producer/certificate-k69.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `6d00e12ff3f4d78b08935afb80455cb8f1df9d28e2e990ea9cdfd0d787937408` |
| `r9e782f5/producer/certificate-k7.json` | [r9e782f5] `producer/certificate-k7.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `24bcb487d93e96d48b083960277f9340dda9a77cad5246db0d3fc46e1abd4e90` |
| `r9e782f5/producer/certificate-k70.json` | [r9e782f5] `producer/certificate-k70.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `7f078822cbd2579a573fb760a0a8bc95475d333a598f739d6c47a56b9c6237a0` |
| `r9e782f5/producer/certificate-k71.json` | [r9e782f5] `producer/certificate-k71.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `d34f6e8bb845f708752d815226e1489f430dc42c27aa4ea9e5256aa85483e3d9` |
| `r9e782f5/producer/certificate-k72.json` | [r9e782f5] `producer/certificate-k72.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `b33f2dbbbcdd5ed1e7dfb7d15264248d9c88378216c960750fb4be74f70b26be` |
| `r9e782f5/producer/certificate-k73.json` | [r9e782f5] `producer/certificate-k73.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `eaa521c52559de21e5ef713c64e21c5ba1dad9312c5c655cc5d41adeb46a4341` |
| `r9e782f5/producer/certificate-k74.json` | [r9e782f5] `producer/certificate-k74.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `084d85e1efd9e64880c1fea511e00b5f5452583e82643b55ea2c8d04d4ec667c` |
| `r9e782f5/producer/certificate-k75.json` | [r9e782f5] `producer/certificate-k75.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `25023944f6efc54c47bdffbc38b88a5a001ba273eecb494288193792db403bcf` |
| `r9e782f5/producer/certificate-k76.json` | [r9e782f5] `producer/certificate-k76.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `526c40221ff120bf631c5587213d31faf580f2f0fcf84c70e843c029631d7c12` |
| `r9e782f5/producer/certificate-k77.json` | [r9e782f5] `producer/certificate-k77.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `e2645f10ffa53c1da4c2a6f3db4e3aabde1ca469b06e9f596159c3722a929b04` |
| `r9e782f5/producer/certificate-k78.json` | [r9e782f5] `producer/certificate-k78.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `a6614ebef46afcb05248f579b8ec574bab49c850f5fcf62deaabcbd2169b92ae` |
| `r9e782f5/producer/certificate-k79.json` | [r9e782f5] `producer/certificate-k79.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `58e9f88d18d7ece55d20f7fa97470455d0df9927b04ec9cbdc1f616652c44026` |
| `r9e782f5/producer/certificate-k8.json` | [r9e782f5] `producer/certificate-k8.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `34a8920a9763a436975e4df161c4e7b5549c46e8a85de9f4dbb9b0973a35fb20` |
| `r9e782f5/producer/certificate-k80.json` | [r9e782f5] `producer/certificate-k80.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `f16d0030d46114d7a268dbed3c93c07e682d364ffdc9049ec9767a3efeb3a6ed` |
| `r9e782f5/producer/certificate-k81.json` | [r9e782f5] `producer/certificate-k81.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `8c832d5022787d513bd26c82e436e97a43144622eb8010446bf4a31e7c644a75` |
| `r9e782f5/producer/certificate-k82.json` | [r9e782f5] `producer/certificate-k82.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `57a645df89dc170310250636bf98cd6226a2999c71b3b47a1723c15efdd4e90d` |
| `r9e782f5/producer/certificate-k83.json` | [r9e782f5] `producer/certificate-k83.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `d356cd6c489e085fccd7f593467b5fb197aef10119b44d5b1ad4a2f6d90dcbda` |
| `r9e782f5/producer/certificate-k84.json` | [r9e782f5] `producer/certificate-k84.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `7cc85458c6559f70400a925691b94e11e1f074a4288c7477c81abf0717c72956` |
| `r9e782f5/producer/certificate-k85.json` | [r9e782f5] `producer/certificate-k85.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `a987ddccbc1358e292d86715e687155ca4f01ce35abc73549c8a657d84ea1d42` |
| `r9e782f5/producer/certificate-k86.json` | [r9e782f5] `producer/certificate-k86.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `5513aea962f4066a143a55d666e5d140b0907d967b393f0d0b07a77ed4ff40ec` |
| `r9e782f5/producer/certificate-k87.json` | [r9e782f5] `producer/certificate-k87.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `ce2d83e7b197bb9f15d41051876040637790625261f33c38a70624e0dba45d92` |
| `r9e782f5/producer/certificate-k88.json` | [r9e782f5] `producer/certificate-k88.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `10d804ab320083545a73781f45c5f5092ba8b1d47cc46293a464be72587cbbbf` |
| `r9e782f5/producer/certificate-k89.json` | [r9e782f5] `producer/certificate-k89.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `431327fdf74533adc75a6cd674216dd9b6ea1eaf7a91389d47cc8774ed662fb5` |
| `r9e782f5/producer/certificate-k9.json` | [r9e782f5] `producer/certificate-k9.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `c8f722e19c3eb97971c3aa800424608894c7fb195ef2dfb9fd89100e97c6a313` |
| `r9e782f5/producer/certificate-k90.json` | [r9e782f5] `producer/certificate-k90.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `fca74dd58b09611c46ca0e80395263d439f4af4506ad42b45090c420f3fec89c` |
| `r9e782f5/producer/certificate-k91.json` | [r9e782f5] `producer/certificate-k91.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `bd65abc5652d1f33084c33c8cbd7a6ef104c9d9c5d37deca27d8b7626341dd2d` |
| `r9e782f5/producer/certificate-k92.json` | [r9e782f5] `producer/certificate-k92.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `b6056e913d9196f5d317724c72ae584d2fad6eefdf44c8c74e2ee58e14fff835` |
| `r9e782f5/producer/certificate-k93.json` | [r9e782f5] `producer/certificate-k93.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `d4435d675b9dd098597df6c9d5140d5de6693f7d02b3f1ad6f633db19aa55c6a` |
| `r9e782f5/producer/certificate-k94.json` | [r9e782f5] `producer/certificate-k94.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `acf563fb679d48108cfe8c8274c9b2ad947b65b145e212aa1aeb2f472fa42056` |
| `r9e782f5/producer/certificate-k95.json` | [r9e782f5] `producer/certificate-k95.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `19f112e3d4bc8ffa174af01d5b3d498a5bae52e676db7cc5d2bc9cca5992925f` |
| `r9e782f5/producer/certificate-k96.json` | [r9e782f5] `producer/certificate-k96.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `4e90a0d5e58a1f8b4b0474e91dc326b7496bd3e95d287bc426b49ab758bbce2f` |
| `r9e782f5/producer/certificate-k97.json` | [r9e782f5] `producer/certificate-k97.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `c1cd2fc867f5123898e4b3d15e0430af60b3cc8b8fbd0b925d816421f7688336` |
| `r9e782f5/producer/certificate-k98.json` | [r9e782f5] `producer/certificate-k98.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `50a9a5d6b1595c25fbb652731465e6fa2dfdd678fa8583c408b0e3a3ff366942` |
| `r9e782f5/producer/certificate-k99.json` | [r9e782f5] `producer/certificate-k99.json`(패턴 `producer/certificate-k*.json`) | seed-certificates-k120 | `885263f43a442ef64f3ca70fb5c02b7e5176f436d20501a84514abc3cb124cff` |
| `r9e782f5/producer/lower-cone-k10-cut30.json.gz` | [r9e782f5] `producer/lower-cone-k10-cut30.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `64829ad92e229e12fc24132e277011bdc8aaa26423816cf9f9f1897eb717f4cd` |
| `r9e782f5/producer/lower-cone-k100-cut200.json.gz` | [r9e782f5] `producer/lower-cone-k100-cut200.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `8fcf45790ed2a827bde308d19e470b2b26233a9f4ed819a0f46e66dbd76df997` |
| `r9e782f5/producer/lower-cone-k101-cut202.json.gz` | [r9e782f5] `producer/lower-cone-k101-cut202.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `2a3faea1f87806e465af22b2f31f6e63daa1b394f5cf0182826e25c00d3bb066` |
| `r9e782f5/producer/lower-cone-k102-cut204.json.gz` | [r9e782f5] `producer/lower-cone-k102-cut204.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `daeff67fcd811e52ae32fa302fc9a5358e6d53a80e3bfc6621458f9fb0237995` |
| `r9e782f5/producer/lower-cone-k103-cut206.json.gz` | [r9e782f5] `producer/lower-cone-k103-cut206.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `9fed68fc5fe9f8ea802647dc6935c85e71c01507e15f2803b810eafbdb4e9784` |
| `r9e782f5/producer/lower-cone-k104-cut208.json.gz` | [r9e782f5] `producer/lower-cone-k104-cut208.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `5b1cb836e9750e7cda52fe163b365badaa8f7ed36d55a58289f7042d2dfbb9d6` |
| `r9e782f5/producer/lower-cone-k105-cut210.json.gz` | [r9e782f5] `producer/lower-cone-k105-cut210.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `cb02d9e5e3a467716b04026710c866186e101c545763f1a93a5327dd7539492d` |
| `r9e782f5/producer/lower-cone-k106-cut212.json.gz` | [r9e782f5] `producer/lower-cone-k106-cut212.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `f46bb0d7451b7d3914e50da5659359adcf5997153c1494ee3156ea9aef65243a` |
| `r9e782f5/producer/lower-cone-k107-cut214.json.gz` | [r9e782f5] `producer/lower-cone-k107-cut214.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `df7e87f24730c4a0dd419d631da01ef0626318da601a8b01b94b42091eab315e` |
| `r9e782f5/producer/lower-cone-k108-cut216.json.gz` | [r9e782f5] `producer/lower-cone-k108-cut216.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `984239f13751c9e72e768afdf78591e62a3e48d1be0f7d74b21cda1b7ef47452` |
| `r9e782f5/producer/lower-cone-k109-cut218.json.gz` | [r9e782f5] `producer/lower-cone-k109-cut218.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ce8b975e4bc039df293bb41c0cd2e31e848699a8eb633fa18db2c3ee23afd7cd` |
| `r9e782f5/producer/lower-cone-k11-cut33.json.gz` | [r9e782f5] `producer/lower-cone-k11-cut33.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `23a4081baa8f53bdccc5d5fb36356ee37500764d290b51670599cf8f5fe71767` |
| `r9e782f5/producer/lower-cone-k110-cut220.json.gz` | [r9e782f5] `producer/lower-cone-k110-cut220.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `2060c94b1c4ddcdf146a342aebeb5d21103cf59109bbe9d8f3f44918784c4175` |
| `r9e782f5/producer/lower-cone-k111-cut222.json.gz` | [r9e782f5] `producer/lower-cone-k111-cut222.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `3d67358d54dafd67c69e3149d37088eb7f1818d2d9700651731123b5105c7fdb` |
| `r9e782f5/producer/lower-cone-k112-cut224.json.gz` | [r9e782f5] `producer/lower-cone-k112-cut224.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `9d32d54425a881afbf14766acd59cacd88a584b18c403cf77f5e81b684746260` |
| `r9e782f5/producer/lower-cone-k113-cut226.json.gz` | [r9e782f5] `producer/lower-cone-k113-cut226.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `9cda9b435b97138113fb5614fd72aebc0ac8e954f6ca1df6ee84cb72864c8b25` |
| `r9e782f5/producer/lower-cone-k114-cut228.json.gz` | [r9e782f5] `producer/lower-cone-k114-cut228.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `fa39fe43fd2772bb7cf5327e81732a67569a7d05b018170db7451b41fb8ba461` |
| `r9e782f5/producer/lower-cone-k115-cut230.json.gz` | [r9e782f5] `producer/lower-cone-k115-cut230.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `8cc22a5efb7effeb1100b31afea5a5a46c3e5c698a3960cfec09b9b50defc66a` |
| `r9e782f5/producer/lower-cone-k116-cut232.json.gz` | [r9e782f5] `producer/lower-cone-k116-cut232.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `2e18bd7df1e2020d9bb7c018e8f5a7af104fa9ec39af9086ecc2d0aa47369657` |
| `r9e782f5/producer/lower-cone-k117-cut234.json.gz` | [r9e782f5] `producer/lower-cone-k117-cut234.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `36e201a318c5972d1515464fbffbfa19b3ab5228b769e6be086853f29276bfcd` |
| `r9e782f5/producer/lower-cone-k118-cut236.json.gz` | [r9e782f5] `producer/lower-cone-k118-cut236.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `95556907a2177021c6e9e953dfcca7c80797ea602fa5b01e23fd9201ed62007e` |
| `r9e782f5/producer/lower-cone-k119-cut238.json.gz` | [r9e782f5] `producer/lower-cone-k119-cut238.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `946defe784c47e140f21b2afc804cb6798b938ed1113783224ee13fd976999e1` |
| `r9e782f5/producer/lower-cone-k12-cut36.json.gz` | [r9e782f5] `producer/lower-cone-k12-cut36.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `9d2f23cb48415111fe3711f280d106c409ae8a4b09754ee7804e86a97405804c` |
| `r9e782f5/producer/lower-cone-k120-cut240.json.gz` | [r9e782f5] `producer/lower-cone-k120-cut240.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `3845a8976a78dcbcdad89172b04aabf216970408da02a07fc29e736151096c46` |
| `r9e782f5/producer/lower-cone-k13-cut39.json.gz` | [r9e782f5] `producer/lower-cone-k13-cut39.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ee8cc692e750db279e824ceb4fd130dd335e2f816ce0f6dbad1e5bd9d7af49c3` |
| `r9e782f5/producer/lower-cone-k14-cut42.json.gz` | [r9e782f5] `producer/lower-cone-k14-cut42.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `8dc3a0328872fa20eba194a29e8a2cbf523813635ea006ef7eb7f3cb4289d1af` |
| `r9e782f5/producer/lower-cone-k15-cut45.json.gz` | [r9e782f5] `producer/lower-cone-k15-cut45.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `a4f6b68ab64458e1f05b8d8600eb43c7874b2b7dca40a001c21d497572b8fa9f` |
| `r9e782f5/producer/lower-cone-k16-cut48.json.gz` | [r9e782f5] `producer/lower-cone-k16-cut48.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `9d9353debca400c554032ca4f0d328a867c61f58230cf234456bcfc56dbec703` |
| `r9e782f5/producer/lower-cone-k17-cut51.json.gz` | [r9e782f5] `producer/lower-cone-k17-cut51.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `c5279d0e5abe5d1fb11a6179ce69f6b35745ebdd198460d9b748ee2a20132b63` |
| `r9e782f5/producer/lower-cone-k18-cut36.json.gz` | [r9e782f5] `producer/lower-cone-k18-cut36.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `e56716bb1a1b60f5be0fd49e3cc8788821a6743e3f770e1593a76b5fd86a1527` |
| `r9e782f5/producer/lower-cone-k18-cut54.json.gz` | [r9e782f5] `producer/lower-cone-k18-cut54.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `968d90fe9ca2ee62f85316908b07e492302aa3a800e86b802b1f7fc8852e4b34` |
| `r9e782f5/producer/lower-cone-k19-cut38.json.gz` | [r9e782f5] `producer/lower-cone-k19-cut38.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `accfed5157a3204bb3c76ccdfde0de5a6de9fbd9c4bb7a130251b75427476f9b` |
| `r9e782f5/producer/lower-cone-k19-cut57.json.gz` | [r9e782f5] `producer/lower-cone-k19-cut57.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `e05cc7a1e2f40c81eb51fd33fb3c2294c48acc3f499f4785e00f37db301b216e` |
| `r9e782f5/producer/lower-cone-k2-cut8.json.gz` | [r9e782f5] `producer/lower-cone-k2-cut8.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `4ac459c2e278ea2faa4d8d4353eba2b5d0097071f3989c46402e544066fa53dd` |
| `r9e782f5/producer/lower-cone-k20-cut40.json.gz` | [r9e782f5] `producer/lower-cone-k20-cut40.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ba457455570c97be9c4b775e38fa19dd9623499d9543bf2f1f66774409413ccb` |
| `r9e782f5/producer/lower-cone-k21-cut42.json.gz` | [r9e782f5] `producer/lower-cone-k21-cut42.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `28f0b3fa98fb2917b8062c0610a5f5f0eac2ef998c881b60f6e0eaaa5db99c9d` |
| `r9e782f5/producer/lower-cone-k22-cut44.json.gz` | [r9e782f5] `producer/lower-cone-k22-cut44.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ab146f735b5adb4b175625190908dd5f1498b88a5e57a305afdd85c24c4d9eb1` |
| `r9e782f5/producer/lower-cone-k23-cut46.json.gz` | [r9e782f5] `producer/lower-cone-k23-cut46.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `626dda75896293848406a8c37201d9518b589aa4982d7326dc1002b7925d63cf` |
| `r9e782f5/producer/lower-cone-k24-cut48.json.gz` | [r9e782f5] `producer/lower-cone-k24-cut48.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `3db65ca1006ac2280c7bbb0b1adc6504204a9c4aca3ba806fa1bfed08242a06b` |
| `r9e782f5/producer/lower-cone-k25-cut50.json.gz` | [r9e782f5] `producer/lower-cone-k25-cut50.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `cca25191b12a51b44054fdb244a750efc50f87e42ad109163692c17455bcdd3b` |
| `r9e782f5/producer/lower-cone-k26-cut52.json.gz` | [r9e782f5] `producer/lower-cone-k26-cut52.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `1b1337b6b5e17672a547f4a54853197980902034e21cb3ed9b3d306ff8114c61` |
| `r9e782f5/producer/lower-cone-k27-cut54.json.gz` | [r9e782f5] `producer/lower-cone-k27-cut54.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `6147ecb7615e372c62668425b48fe2635cf81d2717a5955e0ee95e89d4e11af6` |
| `r9e782f5/producer/lower-cone-k28-cut56.json.gz` | [r9e782f5] `producer/lower-cone-k28-cut56.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `cef2e674e99bbe7d0f946172bcfb6d2f8ee8e034dffc4720278ecde57d0c1b85` |
| `r9e782f5/producer/lower-cone-k29-cut58.json.gz` | [r9e782f5] `producer/lower-cone-k29-cut58.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `52595a2b4f2e48cabe6427939fa9aecf1c2abdbc76dfe6a8e7d21589e0a17f3b` |
| `r9e782f5/producer/lower-cone-k3-cut11.json.gz` | [r9e782f5] `producer/lower-cone-k3-cut11.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `91e0831d88fae6eea1a07d971f2e990a395bae6ade45290f19db45859d778ee2` |
| `r9e782f5/producer/lower-cone-k30-cut60.json.gz` | [r9e782f5] `producer/lower-cone-k30-cut60.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `50313e3df447f0586092ec1fc255b6bcccf319818e5a83f1d591b82991544180` |
| `r9e782f5/producer/lower-cone-k31-cut62.json.gz` | [r9e782f5] `producer/lower-cone-k31-cut62.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b047a1515b49a1299dc05ed2896dc1fcea73f5bb280dce465468556a476a8e93` |
| `r9e782f5/producer/lower-cone-k32-cut64.json.gz` | [r9e782f5] `producer/lower-cone-k32-cut64.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `aa7721999bfd75c1da069de723443c8fbea8308b3d5d28af69fd3c3807e7f5e1` |
| `r9e782f5/producer/lower-cone-k33-cut66.json.gz` | [r9e782f5] `producer/lower-cone-k33-cut66.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `df49158dcf55bf065f3622815e1582e6ce885278c1cb93f27a154e30e1b3618b` |
| `r9e782f5/producer/lower-cone-k34-cut68.json.gz` | [r9e782f5] `producer/lower-cone-k34-cut68.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `11af9c25d9efbae226e1ef0eb8e34f099d69aae7fdad04404ad4d7548e069c3a` |
| `r9e782f5/producer/lower-cone-k35-cut70.json.gz` | [r9e782f5] `producer/lower-cone-k35-cut70.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `c86fcd53115245965b4ae5510c94555efe62fbac76eacd494e40aed20326a5a6` |
| `r9e782f5/producer/lower-cone-k36-cut72.json.gz` | [r9e782f5] `producer/lower-cone-k36-cut72.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `4d8d37d17446e0474993f8b8846601cb481c2f9851b61a23b3d09c7ed3ac688e` |
| `r9e782f5/producer/lower-cone-k37-cut74.json.gz` | [r9e782f5] `producer/lower-cone-k37-cut74.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `3ddbb0b079f03dd48dc2a8a91cd626388909d981c241c67ba5ebed143923e47f` |
| `r9e782f5/producer/lower-cone-k38-cut76.json.gz` | [r9e782f5] `producer/lower-cone-k38-cut76.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ccfab7f793ffe2b5b491d623948006d24a4894070393413257ae7621ed3ff4c1` |
| `r9e782f5/producer/lower-cone-k39-cut78.json.gz` | [r9e782f5] `producer/lower-cone-k39-cut78.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ed8f7e4cf575b6817ea5421c112631576c3dc2076799e16153574b4ce9ced161` |
| `r9e782f5/producer/lower-cone-k4-cut14.json.gz` | [r9e782f5] `producer/lower-cone-k4-cut14.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ec1e2dd67550c0427fde6ee20cb8ade545f4047f619271e4b0fdbb52a59dff0f` |
| `r9e782f5/producer/lower-cone-k40-cut80.json.gz` | [r9e782f5] `producer/lower-cone-k40-cut80.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b513e5ca6203e4917e7c8559bb957cc6d225cc3a45cf4d60fa4cc5b7f56db339` |
| `r9e782f5/producer/lower-cone-k41-cut82.json.gz` | [r9e782f5] `producer/lower-cone-k41-cut82.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b6cb9d68c648290ab852850bd09ddde090a4983ad7557df759e85af766fde970` |
| `r9e782f5/producer/lower-cone-k42-cut84.json.gz` | [r9e782f5] `producer/lower-cone-k42-cut84.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ca19fe46076817ecbcd76a83b1e19046ad97d6eed4fb09915264359d56b1727b` |
| `r9e782f5/producer/lower-cone-k43-cut86.json.gz` | [r9e782f5] `producer/lower-cone-k43-cut86.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `3d81cb04862639a85a1929a1c4f7f05f904fc14e7923767daad8f8241adda603` |
| `r9e782f5/producer/lower-cone-k44-cut88.json.gz` | [r9e782f5] `producer/lower-cone-k44-cut88.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `64372d85e3ba20fdb8f45766c556ca9c3eea5fc612ddfc3f01be1ea9b6d1185a` |
| `r9e782f5/producer/lower-cone-k45-cut90.json.gz` | [r9e782f5] `producer/lower-cone-k45-cut90.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `5eccca0ebdfebbfc49ed606bc2d6d1a8724cbe42d8530eb758bd7a7e1c49dcda` |
| `r9e782f5/producer/lower-cone-k46-cut92.json.gz` | [r9e782f5] `producer/lower-cone-k46-cut92.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `87969bd88fc45f7b6a822f7e08013e93edac8985f203e064a15c715a5a646c8b` |
| `r9e782f5/producer/lower-cone-k47-cut94.json.gz` | [r9e782f5] `producer/lower-cone-k47-cut94.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `f43fbf5b2cf79f91f1bbaf87f35839ef99d487addabdc1577b4d9068b444a991` |
| `r9e782f5/producer/lower-cone-k48-cut96.json.gz` | [r9e782f5] `producer/lower-cone-k48-cut96.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `bc9d11103ecbcb428422e96d4e22faad87525ad3224fc8c42a11a17d1d9f6775` |
| `r9e782f5/producer/lower-cone-k49-cut98.json.gz` | [r9e782f5] `producer/lower-cone-k49-cut98.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `d672b0391e8ee121437539ee2a33d966c2d960c16922d26571b9aa5c69ed6e58` |
| `r9e782f5/producer/lower-cone-k5-cut17.json.gz` | [r9e782f5] `producer/lower-cone-k5-cut17.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `2bb38b9f2946e5f52e817f472b039322a1e1686b0846f1f176122be2674901bb` |
| `r9e782f5/producer/lower-cone-k50-cut100.json.gz` | [r9e782f5] `producer/lower-cone-k50-cut100.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `c8e55fab058f0d4070b7148d42e261bcf63e05802947bc30b8cc63d72c5c9863` |
| `r9e782f5/producer/lower-cone-k51-cut102.json.gz` | [r9e782f5] `producer/lower-cone-k51-cut102.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `847a5027eaa73d151fd11b258f9be11f2e328ffc1ef9e1b378f803bf1be36f64` |
| `r9e782f5/producer/lower-cone-k52-cut104.json.gz` | [r9e782f5] `producer/lower-cone-k52-cut104.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `dc4f7e1e1fd7bbc5962695e0f52361cf8c6d72ed19d5ddefafc341c7904daf13` |
| `r9e782f5/producer/lower-cone-k53-cut106.json.gz` | [r9e782f5] `producer/lower-cone-k53-cut106.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `96d93ed25d7180f49d7f7e193218081f17c83438820f77f7186e2e9731857a4c` |
| `r9e782f5/producer/lower-cone-k54-cut108.json.gz` | [r9e782f5] `producer/lower-cone-k54-cut108.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `a0c94f7590152567546ecc3ca35c76e6510380f2caab728d75d9fc1a5d70be07` |
| `r9e782f5/producer/lower-cone-k55-cut110.json.gz` | [r9e782f5] `producer/lower-cone-k55-cut110.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `c1346b32b97adfb69c7ec23e2e57d27879ac001b51aa4630ad32cc620bd6ae56` |
| `r9e782f5/producer/lower-cone-k56-cut112.json.gz` | [r9e782f5] `producer/lower-cone-k56-cut112.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `d677f8381181a98d880821ddb118e6c442cdf88e3969642f0dc5074a8434dbc9` |
| `r9e782f5/producer/lower-cone-k57-cut114.json.gz` | [r9e782f5] `producer/lower-cone-k57-cut114.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `e094bd109541e832fc040dcc2ce0c8accfc30d681c80b7833811bfe8c8a8e7a3` |
| `r9e782f5/producer/lower-cone-k58-cut116.json.gz` | [r9e782f5] `producer/lower-cone-k58-cut116.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `cd48ae9f754a7cf841fdbf41bdbe7b911799af42566a40b49574696c11517279` |
| `r9e782f5/producer/lower-cone-k59-cut118.json.gz` | [r9e782f5] `producer/lower-cone-k59-cut118.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `e8a36e9b9c07ca97722b0c96ffded11ce74c5d93348599b259d34170bdb259d1` |
| `r9e782f5/producer/lower-cone-k6-cut20.json.gz` | [r9e782f5] `producer/lower-cone-k6-cut20.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ba226c28e0bb40e0d1189c8b9e30ed02219716b8caff5b4bd744db129a8a8124` |
| `r9e782f5/producer/lower-cone-k60-cut120.json.gz` | [r9e782f5] `producer/lower-cone-k60-cut120.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `3186b19b3278064781f981f91a67f2324cc294cd0b7f26e51fcda0607b4c5903` |
| `r9e782f5/producer/lower-cone-k61-cut122.json.gz` | [r9e782f5] `producer/lower-cone-k61-cut122.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `6227df3fda498c4fe8bfd18bc9d198134ab05f60d4e753acb6ded5e115d37c0e` |
| `r9e782f5/producer/lower-cone-k62-cut124.json.gz` | [r9e782f5] `producer/lower-cone-k62-cut124.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `74c368cf3a0145aa4bb830b05c1e1f7e09f3a0f9332b6eabc5393ba438b2646e` |
| `r9e782f5/producer/lower-cone-k63-cut126.json.gz` | [r9e782f5] `producer/lower-cone-k63-cut126.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `f382ac05c0437c0786cbf7cc3cd29c161fb3d8636d06d17419debfd8209a4237` |
| `r9e782f5/producer/lower-cone-k64-cut128.json.gz` | [r9e782f5] `producer/lower-cone-k64-cut128.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `7e2574224c4d9451a861d4dce072c3b93beda3436b198f9cb6fad4ba0a1befcc` |
| `r9e782f5/producer/lower-cone-k65-cut130.json.gz` | [r9e782f5] `producer/lower-cone-k65-cut130.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `50dd402e9abd815f288ca4552ed208f96b66ce4a492f5d61597f9fb193f504ac` |
| `r9e782f5/producer/lower-cone-k66-cut132.json.gz` | [r9e782f5] `producer/lower-cone-k66-cut132.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `d967f548f3d8869edf6a5f3d0bf14b118132791a27a4c98f2b8c5fa07bcde175` |
| `r9e782f5/producer/lower-cone-k67-cut134.json.gz` | [r9e782f5] `producer/lower-cone-k67-cut134.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `c74ee19125b28a2146de08442ea09e535b05d1514f948d488f38ea69a117117f` |
| `r9e782f5/producer/lower-cone-k68-cut136.json.gz` | [r9e782f5] `producer/lower-cone-k68-cut136.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `954d591ca796d910d43a07d0be7845d7c1ae23c729a5ab351bcc60e496b927eb` |
| `r9e782f5/producer/lower-cone-k69-cut138.json.gz` | [r9e782f5] `producer/lower-cone-k69-cut138.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `eb99325c7c7a46d74004ce25b2833e46b684819fef2d597e74f1708481e9c759` |
| `r9e782f5/producer/lower-cone-k7-cut23.json.gz` | [r9e782f5] `producer/lower-cone-k7-cut23.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `119b6c2eb4763453b72d49582acba9f4ad82d9f75190e6092ade491b92f06c92` |
| `r9e782f5/producer/lower-cone-k70-cut140.json.gz` | [r9e782f5] `producer/lower-cone-k70-cut140.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `c808c25219f13bb2fd23e3571721f4109c4460c9bc5cfffd2d9320dfd8809cc1` |
| `r9e782f5/producer/lower-cone-k71-cut142.json.gz` | [r9e782f5] `producer/lower-cone-k71-cut142.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `acd26614d61bc92756a5fb1b6a8835e4d1daa0bab72af5867274ab6c8e7d6726` |
| `r9e782f5/producer/lower-cone-k72-cut144.json.gz` | [r9e782f5] `producer/lower-cone-k72-cut144.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `725afed5d19ac5d01093047cc5f339ca9c2eb6676ecac1db9cfed491ecb75108` |
| `r9e782f5/producer/lower-cone-k73-cut146.json.gz` | [r9e782f5] `producer/lower-cone-k73-cut146.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `722d703f63ce4e9f463c2baa7e89866627b2cae8f8ffd94b740bc0eb40494593` |
| `r9e782f5/producer/lower-cone-k74-cut148.json.gz` | [r9e782f5] `producer/lower-cone-k74-cut148.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `03c2e1786aa77c16d1caafbfe61b21ff5beeaef8c8ef9ff3045715e2bf9f3094` |
| `r9e782f5/producer/lower-cone-k75-cut150.json.gz` | [r9e782f5] `producer/lower-cone-k75-cut150.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `77d0095c4fd6d30958af2498b86e86a26f794187ee5c6bb6c3c662bf84ee2a4c` |
| `r9e782f5/producer/lower-cone-k76-cut152.json.gz` | [r9e782f5] `producer/lower-cone-k76-cut152.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `e2140090ea73378334f52608e40e147bdcbd6ae159d046acc47ede5b59574336` |
| `r9e782f5/producer/lower-cone-k77-cut154.json.gz` | [r9e782f5] `producer/lower-cone-k77-cut154.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `413dbf2e9422c4f3dc23dfa6b06feba8919bc0bdf7feb3a6e2fa9d4292f815d6` |
| `r9e782f5/producer/lower-cone-k78-cut156.json.gz` | [r9e782f5] `producer/lower-cone-k78-cut156.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b216d16513f8a4653991414487f7c39c9067547aaac93a5659e5f7a04dc70ff8` |
| `r9e782f5/producer/lower-cone-k79-cut158.json.gz` | [r9e782f5] `producer/lower-cone-k79-cut158.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `8f37edd4b341615c187388032d5d447c6ed1bca49ab64050b9ec735fce824d19` |
| `r9e782f5/producer/lower-cone-k8-cut24.json.gz` | [r9e782f5] `producer/lower-cone-k8-cut24.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b31767e1aeed88e987026e24e38caa4405b49ab706c5746e2ba132a055144b5a` |
| `r9e782f5/producer/lower-cone-k80-cut160.json.gz` | [r9e782f5] `producer/lower-cone-k80-cut160.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `762112d5e11a6da5230f6efebe39858299412f3aba4898624aee5bef5e3473f3` |
| `r9e782f5/producer/lower-cone-k81-cut162.json.gz` | [r9e782f5] `producer/lower-cone-k81-cut162.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `449fb73adec98fb72354c050657e664e8b3f0742fbb936a82270756e07e3a182` |
| `r9e782f5/producer/lower-cone-k82-cut164.json.gz` | [r9e782f5] `producer/lower-cone-k82-cut164.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b72c2d79d76b3dfe2eb1c4a5c902fd3ee49e4216845c639c844317e931dac9ab` |
| `r9e782f5/producer/lower-cone-k83-cut166.json.gz` | [r9e782f5] `producer/lower-cone-k83-cut166.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b4ca02fc2609b6d72a8518d320934770c38452c14fb1de45455e307008f87d90` |
| `r9e782f5/producer/lower-cone-k84-cut168.json.gz` | [r9e782f5] `producer/lower-cone-k84-cut168.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `6e1e0d950a8db837497e8982a8ca0852ad6d4203cfbc505c568f2844a1bc200a` |
| `r9e782f5/producer/lower-cone-k85-cut170.json.gz` | [r9e782f5] `producer/lower-cone-k85-cut170.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `c3eeb0627c2612f4d990715ee05a05b63486dc1409bfeff59a8914b89b6e9edd` |
| `r9e782f5/producer/lower-cone-k86-cut172.json.gz` | [r9e782f5] `producer/lower-cone-k86-cut172.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `7ce2dfe56de5ca6e50d4f37e51939ff27e561d7138a251a7067736cdb70b4a6d` |
| `r9e782f5/producer/lower-cone-k87-cut174.json.gz` | [r9e782f5] `producer/lower-cone-k87-cut174.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `ed1ca7c306970f500b6644e4f59d9c0874d1eb456693329266fbec6f73c00553` |
| `r9e782f5/producer/lower-cone-k88-cut176.json.gz` | [r9e782f5] `producer/lower-cone-k88-cut176.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `fa3abca9b41cf695e06e5ff2e96616e00d68288b9c708dfb0f5d1bb8b1d342e5` |
| `r9e782f5/producer/lower-cone-k89-cut178.json.gz` | [r9e782f5] `producer/lower-cone-k89-cut178.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `5d365949344963b401a681e68db1b295240aedddb1ce28bed980a27c641a2275` |
| `r9e782f5/producer/lower-cone-k9-cut27.json.gz` | [r9e782f5] `producer/lower-cone-k9-cut27.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b7a77447f75e98987bdb8da8752dd3261c3912fcde5060722101b6ee124988ad` |
| `r9e782f5/producer/lower-cone-k90-cut180.json.gz` | [r9e782f5] `producer/lower-cone-k90-cut180.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `077d0ab6b8f25994b02437f3c3a7cdfb84cc26ed734784056886a23cefce1884` |
| `r9e782f5/producer/lower-cone-k91-cut182.json.gz` | [r9e782f5] `producer/lower-cone-k91-cut182.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `f24083cce552223c13d5c0b3d28d5488097de947430e44cbb15375aa3b4f0261` |
| `r9e782f5/producer/lower-cone-k92-cut184.json.gz` | [r9e782f5] `producer/lower-cone-k92-cut184.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `b6d1bd8f9189d33d9026c2d1c2796bdf863353887f5867c7ad1c14b2e923b5ce` |
| `r9e782f5/producer/lower-cone-k93-cut186.json.gz` | [r9e782f5] `producer/lower-cone-k93-cut186.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `8069a4541505bde696522bf3c077f8e7821f934e393f36b1d51046e0caae7ec0` |
| `r9e782f5/producer/lower-cone-k94-cut188.json.gz` | [r9e782f5] `producer/lower-cone-k94-cut188.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `f551109622517b245b24e9110525002410b0cd4ffbc821e2674ab81f66ecf940` |
| `r9e782f5/producer/lower-cone-k95-cut190.json.gz` | [r9e782f5] `producer/lower-cone-k95-cut190.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `57386f9599203c85e345d934ac667679ed057f21799eff8e9e88831677e11379` |
| `r9e782f5/producer/lower-cone-k96-cut192.json.gz` | [r9e782f5] `producer/lower-cone-k96-cut192.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `858fc8e268e7ee47d8796137d337348047746651e88c04653d7912f788d1d8ea` |
| `r9e782f5/producer/lower-cone-k97-cut194.json.gz` | [r9e782f5] `producer/lower-cone-k97-cut194.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `9459d6ddee19245aed02c7415d850eaab5df1309ad506eedabe7868331aecac7` |
| `r9e782f5/producer/lower-cone-k98-cut196.json.gz` | [r9e782f5] `producer/lower-cone-k98-cut196.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `14e2a36605bba3ff59ddc07055f8217db2f88e5ce797d80553c244e088641bee` |
| `r9e782f5/producer/lower-cone-k99-cut198.json.gz` | [r9e782f5] `producer/lower-cone-k99-cut198.json.gz`(패턴 `producer/lower-cone-k*-cut*.json.gz`) | seed-certificates-k120 | `108f1d74772ed94d68f05049166304d75523155432d6086f61109cb41cfa83b9` |
| `r9e782f5/review/reproduction/audit.json` | [r9e782f5] `review/reproduction/audit.json`(폴더 `review/reproduction/`) | seed-certificates-k120 | `4fa882a02fba5bfb1f283429dff5c36cc72d7e22f7ea35a41b452c73d25c8b3b` |
| `r9e782f5/review/reproduction/barriers.json` | [r9e782f5] `review/reproduction/barriers.json`(폴더 `review/reproduction/`) | seed-certificates-k120 | `41fdfbe23e7272d00af45ae6ce08388426588ed027bc00d41b2a9cd12abbf08f` |
| `r9e782f5/review/reproduction/original-dp.json` | [r9e782f5] `review/reproduction/original-dp.json`(폴더 `review/reproduction/`) | seed-certificates-k120 | `9725e84b5d03cde58873a76f43b9d59db1979dca5920ef12aab7948c75458729` |
| `r9e782f5/review/reproduction/replays.json` | [r9e782f5] `review/reproduction/replays.json`(폴더 `review/reproduction/`) | seed-certificates-k120 | `3048d56e09d4cff8843276d1897bd176742b916aeb7c7b5df6845c867c581cdb` |
| `r9e782f5/review/reproduction/residuals.json` | [r9e782f5] `review/reproduction/residuals.json`(폴더 `review/reproduction/`) | seed-certificates-k120 | `e5acd303c6e8755dfc6e5cd89104445a14989d996f58bb14c8d12074690d49cc` |
| `r9e782f5/review/reproduction/results.json` | [r9e782f5] `review/reproduction/results.json`(폴더 `review/reproduction/`) | seed-certificates-k120 | `8ef0568542778407f87d4300f4a0198e9b5db2de3401fb542327de53fd6114b7` |
| `ra4c01fc/check_constants.py` | [ra4c01fc] `evidence/peer/check_constants.py` | critical-window-rig | `b21e4a63f60497184cb8579d1899e119c34e87097885992eaf423f676fd574c3` |
| `ra4c01fc/check_h_contain.py` | [ra4c01fc] `evidence/peer/check_h_contain.py` | critical-window-rig | `cfd93eee69bb90347057b5cbd4f7d09693fba49194d262669ec88d69b078170d` |
| `ra4c01fc/check_xi.py` | [ra4c01fc] `evidence/peer/check_xi.py` | critical-window-rig | `6a9faf95e520a60be411b625c08916b8faf25d5e853c970990a9e5f1f64f5b01` |
| `ra4c01fc/contain_check.py` | [ra4c01fc] `evidence/peer/contain_check.py` | critical-window-rig | `4e1cd70f6f3ff8fdda79fc869ad66fc3be77af915746c95728a9ccb34db8216b` |
| `ra4c01fc/coverage_check.out` | [ra4c01fc] `evidence/peer/coverage_check.out` | critical-window-rig | `ee338186b3cd118e9d2d64d672c6d280c76394a1bf858902e052aae4d348f867` |
| `ra4c01fc/coverage_check.py` | [ra4c01fc] `evidence/peer/coverage_check.py` | critical-window-rig | `86b52927864ae26b00507448da1b659281e60bd332feb9fc5362420bd1b29234` |
| `ra4c01fc/evidence/certificates/cert2/ubox_00.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_00.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `67ee1830ffe75505df813a15819bde95586f3b638d167ed64baa6bb45413d6b8` |
| `ra4c01fc/evidence/certificates/cert2/ubox_01.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_01.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `e95d847a75cf4e269db9b91ed0a8315a768f4f27fa6d58f3e1d78452ec9ad09e` |
| `ra4c01fc/evidence/certificates/cert2/ubox_02.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_02.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `6e05d54c35d4a94daa9a64a24a783b595c82a827d0758761b039dc97b77fc2c1` |
| `ra4c01fc/evidence/certificates/cert2/ubox_03.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_03.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `04ddf63a8248c04978cb04c5d39c3ff54ff0133cb3633ace00b7f9aff9374d5b` |
| `ra4c01fc/evidence/certificates/cert2/ubox_04.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_04.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `fb099a0da4333a2ba0b61ba4d45b49a75a9db4d6b231fc8bdfce50b7068cfeab` |
| `ra4c01fc/evidence/certificates/cert2/ubox_05.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_05.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `827e085978284ca7dab469e14effccfa7671ea415e7a3d6a9e6dbe69622e0e4e` |
| `ra4c01fc/evidence/certificates/cert2/ubox_06.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_06.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `4bbbb45ee5ff1045752e796c2e58b3948e21679cf80a1df785a52f6c0dae6c47` |
| `ra4c01fc/evidence/certificates/cert2/ubox_07.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_07.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `a480896176bab5c56e69101ea8c62040fae0d77574bfdf746d292586ad2e438c` |
| `ra4c01fc/evidence/certificates/cert2/ubox_08.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_08.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `111adeb95d6b03b1c9bed95834adc9ce1dd7d9c2d97cf4c6e87420c84c11a4be` |
| `ra4c01fc/evidence/certificates/cert2/ubox_09.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_09.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `fc6fea5228d0210851e93c620d249862a4dad0ab71764ae2e75f2cfc42ae743f` |
| `ra4c01fc/evidence/certificates/cert2/ubox_10.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_10.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `cd57b926a9604921cb7df45a55c75432b209112658544a8e2c7d874f793a87cb` |
| `ra4c01fc/evidence/certificates/cert2/ubox_11.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_11.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `cfda56d43e2db28b5e61849ea5d555cec93813fce4eec3b083fcc7bb9976adf0` |
| `ra4c01fc/evidence/certificates/cert2/ubox_12.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_12.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `29162bb9dbc1caf024e2d1892c3191fd233a19103b28cfdf9805d4b4a3c75cd9` |
| `ra4c01fc/evidence/certificates/cert2/ubox_13.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_13.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `182c9196a5a392118fdfb333eb842bda49cdffa51178448bbc2bd98833ff36bd` |
| `ra4c01fc/evidence/certificates/cert2/ubox_14.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_14.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `19feb2034fa692396dccfc48149ede1a274777882df1d41439f26306f752cbaa` |
| `ra4c01fc/evidence/certificates/cert2/ubox_15.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_15.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `99e12b5b60df213e756029e27e7e3bea1582e1e604d3b91293876bbaa4b3a90b` |
| `ra4c01fc/evidence/certificates/cert2/ubox_16.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_16.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `1c8e1fcc6ab0e7381e328fb353342205717b02d4e2de394d079bd1911c5f8b13` |
| `ra4c01fc/evidence/certificates/cert2/ubox_17.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_17.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `a4ace037ae08f3e5859410df9d5daa19ecee3b2aa297024578d6a714bf92f43f` |
| `ra4c01fc/evidence/certificates/cert2/ubox_18.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_18.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `1f997956f9aeee0370cd527cbaae55d9463e4c5250aaa0cd069a300340d5daea` |
| `ra4c01fc/evidence/certificates/cert2/ubox_19.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_19.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `1d1382a9975008fa449f21e37cdbbc1161ec77b6f7f4ba80626ec7c30afa7eba` |
| `ra4c01fc/evidence/certificates/cert2/ubox_20.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_20.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `3ba95fa1c00faa033b547124019e32cb3d1e33923444a62445d7c389197ebe6b` |
| `ra4c01fc/evidence/certificates/cert2/ubox_21.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_21.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `022a5be96fa71fa7ad1b742d3714ea3ece482cf351fc888b6604a9322de6aee5` |
| `ra4c01fc/evidence/certificates/cert2/ubox_22.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_22.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `8c655d9520da9b90b5b01b1b6f0f57664bd55c9cff1a4e023c9461d20fbbfe64` |
| `ra4c01fc/evidence/certificates/cert2/ubox_23.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_23.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `639098c070594ce1b727d28675a9559a0c102368b0d546ac3f515959a8397ae8` |
| `ra4c01fc/evidence/certificates/cert2/ubox_24.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_24.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `cad1e9cbc52a356960d713f39e523e6ea968d8574ebf297ee625c65db5be1e90` |
| `ra4c01fc/evidence/certificates/cert2/ubox_25.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_25.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `003992f6e622d1a0e51071403da1123dac99c0cafe3d2b38b1784b2609e6bb7b` |
| `ra4c01fc/evidence/certificates/cert2/ubox_26.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_26.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `1b766ea6aa9ed5bd33a7f017f83bdf989ff7be8c64af1bb8ab298e6f769038a8` |
| `ra4c01fc/evidence/certificates/cert2/ubox_27.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_27.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `c339c233f46b99b238db05afeadbd1a1a95d95ed046567914923188dcaaa4381` |
| `ra4c01fc/evidence/certificates/cert2/ubox_28.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_28.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `e2bebd9794ee0b76402757d41ca58d35d5537380c82b48a12f6a7b944792ee36` |
| `ra4c01fc/evidence/certificates/cert2/ubox_29.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_29.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `a92d0fc35897d8895ac57afb06af5b17277ad00c7f0094bbad48b6d376a15f7e` |
| `ra4c01fc/evidence/certificates/cert2/ubox_29_recert_first.json` | [ra4c01fc] `evidence/certificates/cert2/ubox_29_recert_first.json`(폴더 `evidence/certificates/cert2/`) | critical-window-rig | `a28c5e0ccb83bcd3f4551ef42700016050302885136336c499ca2f18d414fab8` |
| `ra4c01fc/evidence/certificates/cert3/ubox_00.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_00.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `aa67bbdf13eec9b2348b75111327a6856b6d7368698b18732d3144415152da39` |
| `ra4c01fc/evidence/certificates/cert3/ubox_01.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_01.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `98aef585ed265324283640c5daaec9ed944b087f80c0a39441cfeea72043bccd` |
| `ra4c01fc/evidence/certificates/cert3/ubox_02.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_02.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `1fd1cc880610053a3bb2bd89c614a4168b77b1070609d68de28afa05c03f7d6e` |
| `ra4c01fc/evidence/certificates/cert3/ubox_03.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_03.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `aa56638c6700546ed766515a05cef3cd842fae1a6694cafabd11a89a93c2d235` |
| `ra4c01fc/evidence/certificates/cert3/ubox_04.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_04.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `9e8117452d593c537714a5f39dae811958485f261c14f5c2122185c94d438aeb` |
| `ra4c01fc/evidence/certificates/cert3/ubox_05.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_05.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `8a7cdd59c940f378f423edb28966ca7a1fa5ff04c93960081958612f1892bd4d` |
| `ra4c01fc/evidence/certificates/cert3/ubox_06.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_06.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `81287b322796acd9ce8600fb57e67ac181eeefc5a1d660328c6b05e622203b7e` |
| `ra4c01fc/evidence/certificates/cert3/ubox_06_recert_first.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_06_recert_first.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `541282d89c29ba6c17dc33a6bad1945e4d851ce1ba396828599a9c3b3832c020` |
| `ra4c01fc/evidence/certificates/cert3/ubox_07.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_07.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `506fad12ff85ce56b34554bcc5b0d81c6fb817606c72083df9d5a64136d88ff7` |
| `ra4c01fc/evidence/certificates/cert3/ubox_07_recert_first.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_07_recert_first.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `d2e3ce9a682ed784d10677505d0e4b776c73379abf5574527783ee67b9abc011` |
| `ra4c01fc/evidence/certificates/cert3/ubox_08.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_08.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `7064bad4e59eb0967b3844a93bb715611c3bb40077e6df92913f4f5cd74513f3` |
| `ra4c01fc/evidence/certificates/cert3/ubox_08_recert_first.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_08_recert_first.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `8d40e3b9dd488f9f36a6d5afcbcf7562df2bba920cac66c949bc31dcb720029c` |
| `ra4c01fc/evidence/certificates/cert3/ubox_09.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_09.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `730fc6dd826e3a2831475f34f6c774be8006932ee66f9adb9de8a016aacb3dc6` |
| `ra4c01fc/evidence/certificates/cert3/ubox_10.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_10.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `076dac91459f5bb1abfed063b5113c2365eb4550eeb954fee7c784573847ddb8` |
| `ra4c01fc/evidence/certificates/cert3/ubox_11.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_11.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `9cabd38c38620541c97a857226091e42d39ebec5e86e1f973de7a114cda5c93a` |
| `ra4c01fc/evidence/certificates/cert3/ubox_12.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_12.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `ae93042be8c2838ee5153357451ca617fadd113b9be4c80fce034935c07effb3` |
| `ra4c01fc/evidence/certificates/cert3/ubox_13.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_13.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `69718da6c8f281846472bf60a38ae503089a8aca243b21def886b926cc373247` |
| `ra4c01fc/evidence/certificates/cert3/ubox_13_recert_first.json` | [ra4c01fc] `evidence/certificates/cert3/ubox_13_recert_first.json`(폴더 `evidence/certificates/cert3/`) | critical-window-rig | `1a1e457bf402226d16ac95d07506c010321d8d3449a3a907f0d9cdf9b7f58a57` |
| `ra4c01fc/evidence/peer/contain_A00.log` | [ra4c01fc] `evidence/peer/contain_A00.log`(패턴 `evidence/peer/contain_*.log`) | critical-window-rig | `a65ea7b6354d2d64894d270525e776a9cbae11ae80332df18be61177d2ca0ac0` |
| `ra4c01fc/evidence/peer/contain_more.log` | [ra4c01fc] `evidence/peer/contain_more.log`(패턴 `evidence/peer/contain_*.log`) | critical-window-rig | `986984314f2181ac3932eaa502e391536766a82deb28530bc734d1d4cc7b553c` |
| `ra4c01fc/evidence/producer-code/SHA256SUMS.txt` | [ra4c01fc] `evidence/producer-code/SHA256SUMS.txt`(폴더 `evidence/producer-code/`) | critical-window-rig | `011f302b00edef126d3bee2c4a92eef5859f0ce85e8b5b8635756dd0ec7de918` |
| `ra4c01fc/evidence/producer-code/check_egf_N.py` | [ra4c01fc] `evidence/producer-code/check_egf_N.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `0dc1a467d048e0d68b513eb797e3ea412bc0e49d8f7646d1f788033ab00d841c` |
| `ra4c01fc/evidence/producer-code/check_lagrange.py` | [ra4c01fc] `evidence/producer-code/check_lagrange.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `4fad64bf31f58362ee394d32dffc0d0ba3504c3a9f77ed05550c6f27a7109378` |
| `ra4c01fc/evidence/producer-code/check_series_e.py` | [ra4c01fc] `evidence/producer-code/check_series_e.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `828973366e85a96ed484dc832a5e07d24dd13e4de5592b004a84a9814d2788e4` |
| `ra4c01fc/evidence/producer-code/check_stieltjes.py` | [ra4c01fc] `evidence/producer-code/check_stieltjes.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `abbba6a8fd46e66be9f4dad6634c3e70b37e43da946da4c06dfe737e8f93478b` |
| `ra4c01fc/evidence/producer-code/check_vertical.py` | [ra4c01fc] `evidence/producer-code/check_vertical.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `c22d0d30b2aa3cc445c9c644d1a34b5398d4e9254c7ce4a356b4f9bc593811c0` |
| `ra4c01fc/evidence/producer-code/check_vertical_fast.py` | [ra4c01fc] `evidence/producer-code/check_vertical_fast.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `46efe37a173e3af1bda3c74161093a1bc37ce0945d63c381af7ce584146fd0cb` |
| `ra4c01fc/evidence/producer-code/check_vertical_fast2.py` | [ra4c01fc] `evidence/producer-code/check_vertical_fast2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `389c26693fa01d83c052e4e15d848105777ef8209f2787f12047ac35937ccfaa` |
| `ra4c01fc/evidence/producer-code/circle.py` | [ra4c01fc] `evidence/producer-code/circle.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `a1c57d73aee119cbd0271063a8cb4c2fd9958a2a431ee48ad76af34305665599` |
| `ra4c01fc/evidence/producer-code/dbg2.py` | [ra4c01fc] `evidence/producer-code/dbg2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `0792ab4fe74de8b2fd27116b287155005f126707efe330886bdabea4a3b89cb0` |
| `ra4c01fc/evidence/producer-code/dbg_T.py` | [ra4c01fc] `evidence/producer-code/dbg_T.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `ad58ef6fdc84c101bf61e75d8e97dea391b78960cd00e6e3c34dc10484fceefd` |
| `ra4c01fc/evidence/producer-code/dbg_TD.py` | [ra4c01fc] `evidence/producer-code/dbg_TD.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `c7c4f85c490cf1e49f8e511c008d128e21e2e13294e9f9ad452bb4b27e3808c9` |
| `ra4c01fc/evidence/producer-code/dbg_attr.py` | [ra4c01fc] `evidence/producer-code/dbg_attr.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `b1c427c505badccb5f8da74036f0e817ebe50d2fe869fa25690a8a7132ba8fb2` |
| `ra4c01fc/evidence/producer-code/dbg_pipeline.py` | [ra4c01fc] `evidence/producer-code/dbg_pipeline.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `89f7f21e089dca840d343cbfcfc9fe26b1588e08fb0f5ad537e339b8328ef64a` |
| `ra4c01fc/evidence/producer-code/dbg_u2.py` | [ra4c01fc] `evidence/producer-code/dbg_u2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `78f345587fc3578d2096613545b0edea4ef4cd72c9986c3a20772a35c00fdda8` |
| `ra4c01fc/evidence/producer-code/dbg_width.py` | [ra4c01fc] `evidence/producer-code/dbg_width.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `abbcf81e132d540a1f2f368dcf708d7a12765e47a5097e38a583d71c6c96822c` |
| `ra4c01fc/evidence/producer-code/dbg_width2.py` | [ra4c01fc] `evidence/producer-code/dbg_width2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `3fe87a78b75386c4a0d4cb5730f87987cebb6299806b9a6a73ecfd2685fef0c3` |
| `ra4c01fc/evidence/producer-code/diag_Harc.py` | [ra4c01fc] `evidence/producer-code/diag_Harc.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `8f435799554ee8ffa00823df5a927c0cb9662470f76045f1f61d1e94c2a41681` |
| `ra4c01fc/evidence/producer-code/diag_abel.py` | [ra4c01fc] `evidence/producer-code/diag_abel.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `e3c6cc2de225bab63f0550620461197b1496be1877f69dfc0ed0b02d0191147f` |
| `ra4c01fc/evidence/producer-code/diag_cross.py` | [ra4c01fc] `evidence/producer-code/diag_cross.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `c48e9420ee71c28862783b832465f567f04a608c6d7588e88a275191345c2330` |
| `ra4c01fc/evidence/producer-code/diag_discount.py` | [ra4c01fc] `evidence/producer-code/diag_discount.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `d2135c3534cb4755220990281fb46d824544e1316f333f60d4d4795a275e9d5a` |
| `ra4c01fc/evidence/producer-code/diag_green.py` | [ra4c01fc] `evidence/producer-code/diag_green.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `1fdff0badfa3759c2e0047285b762ac9f85437a9be7fd7f55c0c73abffdeb641` |
| `ra4c01fc/evidence/producer-code/fpipe.py` | [ra4c01fc] `evidence/producer-code/fpipe.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `ef3c258c4d1301dec5b3ce4b04b9afa3343f5489241f6d918c6bbf607048255a` |
| `ra4c01fc/evidence/producer-code/ivio.py` | [ra4c01fc] `evidence/producer-code/ivio.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `c598f874aeb8b793edc52b264484bc5126a7741ddd3d4eba54229249bef65219` |
| `ra4c01fc/evidence/producer-code/lab.py` | [ra4c01fc] `evidence/producer-code/lab.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `3b0083899c2f6a2f2e5d4cb3ea1d11164cc7f07f8a6179da37e326e7e667e44f` |
| `ra4c01fc/evidence/producer-code/make_table.py` | [ra4c01fc] `evidence/producer-code/make_table.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `222370ad0acdbc67f77841b68ea313a2cacdb34759d1a30e220374f310d6d634` |
| `ra4c01fc/evidence/producer-code/patch1.py` | [ra4c01fc] `evidence/producer-code/patch1.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `2d21fb45130569ec4361ae5cb6c4557a25cc6027d94dac15af0d628e9f09112b` |
| `ra4c01fc/evidence/producer-code/patch2.py` | [ra4c01fc] `evidence/producer-code/patch2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `bb4faaccfca7cbc5cd85148c3d809ff847a0164fb2355b6790b6d153097104af` |
| `ra4c01fc/evidence/producer-code/patch3.py` | [ra4c01fc] `evidence/producer-code/patch3.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `4f809f47055aa32186c9aa335e9ee21c04c59e921fe69f86abc065a365025c74` |
| `ra4c01fc/evidence/producer-code/patch4.py` | [ra4c01fc] `evidence/producer-code/patch4.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `73ca192db3d0bdbc0a3b9e1aabdf13cff8bdd81dd35b136628ac43d92e4a87d6` |
| `ra4c01fc/evidence/producer-code/patch5.py` | [ra4c01fc] `evidence/producer-code/patch5.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `6e8debd9ef1ee09b93513b96c929356fa7e238fe7605c22ebd7dd96c86ca56ce` |
| `ra4c01fc/evidence/producer-code/patch6.py` | [ra4c01fc] `evidence/producer-code/patch6.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `a94657d4af31f4bb5c7592cf0278737dad8323d864db32201cf1a9ed80a898b3` |
| `ra4c01fc/evidence/producer-code/patch8.py` | [ra4c01fc] `evidence/producer-code/patch8.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `30ef3bbc7e858f37ede8ca6c5b6713db3a825b6137057f528e370281551d57cf` |
| `ra4c01fc/evidence/producer-code/patch9.py` | [ra4c01fc] `evidence/producer-code/patch9.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `7c491ead44c22cd20dc0e6b2fc78ae7929f3c6a10024f3a85eb784d71ece2a3a` |
| `ra4c01fc/evidence/producer-code/recert.py` | [ra4c01fc] `evidence/producer-code/recert.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `2707a45dd4a76908cb16713241d9aff046680c5a680aa5e9df588a35186f3512` |
| `ra4c01fc/evidence/producer-code/rig_H.py` | [ra4c01fc] `evidence/producer-code/rig_H.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `48bd2cb2cb8cb4b8ac0c884fa528d84e910bee5e172163c575fd3f082fb88d8f` |
| `ra4c01fc/evidence/producer-code/rig_W.py` | [ra4c01fc] `evidence/producer-code/rig_W.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `28d8bf90caa59f3ed05ebe716b70495c995ef2127cdcefa8fc00ee2873f0b128` |
| `ra4c01fc/evidence/producer-code/rig_cert.py` | [ra4c01fc] `evidence/producer-code/rig_cert.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `4e1794ca10e02f9d1c5e89654cc2e410d53c4659eb94509f375e847444a70532` |
| `ra4c01fc/evidence/producer-code/rig_common.py` | [ra4c01fc] `evidence/producer-code/rig_common.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `051e1eae119eb74d47cefaaa424444ee180e60c87b39bcec84d384748916ddd7` |
| `ra4c01fc/evidence/producer-code/rig_pipeline.py` | [ra4c01fc] `evidence/producer-code/rig_pipeline.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `14a391a1f5476639d440f8053b44e8df3f3f232e86bbf3c66746b8a557ed5b55` |
| `ra4c01fc/evidence/producer-code/rig_pipeline2.py` | [ra4c01fc] `evidence/producer-code/rig_pipeline2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `f6dd421f479cfb465bccc9baee47b38965d1c63f87975e8fbafe29254328be7e` |
| `ra4c01fc/evidence/producer-code/rig_ray2.py` | [ra4c01fc] `evidence/producer-code/rig_ray2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `30bd3d21313d27bfb2fe84c7c907aba68aab5211ff44fb5616add714f2a38a00` |
| `ra4c01fc/evidence/producer-code/rig_ray3.py` | [ra4c01fc] `evidence/producer-code/rig_ray3.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `0746cf10c51ee1a4ba7fc844efc396a013aff24e1d5bc677c2bc457890d94840` |
| `ra4c01fc/evidence/producer-code/rig_ray4.py` | [ra4c01fc] `evidence/producer-code/rig_ray4.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `27c7de305c6aa82b4098f2eeacdcf2932233c456089fac9fa9b07b470d291c21` |
| `ra4c01fc/evidence/producer-code/scan_c1e4.py` | [ra4c01fc] `evidence/producer-code/scan_c1e4.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `46d180e03ccbdc50be62b457e5174aac60c9fcad912c732b07469193997ed552` |
| `ra4c01fc/evidence/producer-code/sweep.py` | [ra4c01fc] `evidence/producer-code/sweep.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `9f2e4703de78646d3df940df5df10d2f04aca5b03fb74426c1df9e3a17515625` |
| `ra4c01fc/evidence/producer-code/sweep_ext.py` | [ra4c01fc] `evidence/producer-code/sweep_ext.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `205c32e8606e9c422cc56ff7951403d6c278ffd522ee1ec542d1344f4cbf1992` |
| `ra4c01fc/evidence/producer-code/sweep_u.py` | [ra4c01fc] `evidence/producer-code/sweep_u.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `c78ad76ed2e8330fdecaf7f1a2e2851b8ac1f66f2b71d9e3f93f8afc606b5dcc` |
| `ra4c01fc/evidence/producer-code/sweep_u2.py` | [ra4c01fc] `evidence/producer-code/sweep_u2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `edfaccc90d7aafd9b3a3b1acb42e5fbe815776efe6c248d567f3fa1bcf1072a5` |
| `ra4c01fc/evidence/producer-code/sweep_u3.py` | [ra4c01fc] `evidence/producer-code/sweep_u3.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `8bf84cba6574ef70d3fdaab39feb10b3a452e1207d89c4a2dd31e9e7715b7b9f` |
| `ra4c01fc/evidence/producer-code/test_cD_sign.py` | [ra4c01fc] `evidence/producer-code/test_cD_sign.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `95d89228b8b484706d8b7b5edeb8b2216799f9d50fe67885e61009955159b327` |
| `ra4c01fc/evidence/producer-code/test_hybrid.py` | [ra4c01fc] `evidence/producer-code/test_hybrid.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `6ff1538b4ac15d3728c6af91984245b581b53d499ee39da17f05d81c21a378de` |
| `ra4c01fc/evidence/producer-code/test_lab.py` | [ra4c01fc] `evidence/producer-code/test_lab.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `9f826fa05bcef04ccbf1824d60d8f6cedda16f4c45becd84a18600496b49f6cc` |
| `ra4c01fc/evidence/producer-code/test_u0.py` | [ra4c01fc] `evidence/producer-code/test_u0.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `4997de35af8b70e101a60460f352413f48ca9b22057b0c4d5da4e6a2f8134d3a` |
| `ra4c01fc/evidence/producer-code/time_W.py` | [ra4c01fc] `evidence/producer-code/time_W.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `51aac517011f7aa9c100be46ec7151a094a1d882fe6a46be931c9e606988e118` |
| `ra4c01fc/evidence/producer-code/time_W2.py` | [ra4c01fc] `evidence/producer-code/time_W2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `d64d7aa7e512ad26f288998f65250a1b237c85be9b21e4df6c1144fc2ab08876` |
| `ra4c01fc/evidence/producer-code/universal.py` | [ra4c01fc] `evidence/producer-code/universal.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `37d377893e95b3d0d14cf52618d08514a4250f78b60f636e0af919507da06d4a` |
| `ra4c01fc/evidence/producer-code/universal2.py` | [ra4c01fc] `evidence/producer-code/universal2.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `2296c9f1ccda04ae31330ec1d7d7b7843411e6cd5b15ee761ef40ff2eea3c82e` |
| `ra4c01fc/evidence/producer-code/universal3.py` | [ra4c01fc] `evidence/producer-code/universal3.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `2827cb997273004e3c413baa199b9544b79d5f009669137186fbebe70e3c4fdc` |
| `ra4c01fc/evidence/producer-code/universal_fast.py` | [ra4c01fc] `evidence/producer-code/universal_fast.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `3d2c750a21c41d106ad8e1f97bff9beb13108b0afaa16de81e5be44211cda936` |
| `ra4c01fc/evidence/producer-code/universal_table.py` | [ra4c01fc] `evidence/producer-code/universal_table.py`(폴더 `evidence/producer-code/`) | critical-window-rig | `a78486611b36ca9e3568be76b915563ba35370f47a55b5fc27c45c87982335db` |
| `ra4c01fc/exact_en_B.py` | [ra4c01fc] `evidence/peer/exact_en_B.py` | critical-window-rig | `6010354b1c6caf93633c8f80799a34db33ec6c6d1f9e79fedfa6cc95ec5c9e71` |
| `ra4c01fc/h_contain.jsonl` | [ra4c01fc] `evidence/peer/h_contain.jsonl` | critical-window-rig | `43a726fca13d155ed288220affb936356d432e6d91b81cd68dc3281fb1f1fda7` |
| `ra4c01fc/h_exact.py` | [ra4c01fc] `evidence/peer/h_exact.py` | critical-window-rig | `2eefee3c561de0ff72736069729b5fd4da2292fc55ca5cb3b0b3761df2586539` |
| `rad00a59/cert_S.py` | [rad00a59] `evidence/peer/cert_S.py` | self-consistent-constants | `d5ad4599a53cc334139dd3ae0705927ac8ca13d3333927741916efef23a9ddc8` |
| `rad00a59/cert_S.txt` | [rad00a59] `evidence/peer/cert_S.txt` | self-consistent-constants | `bd2f28a8cd8cdb870dafb933dd9dc794e828321208128573a266e05a4b3f5703` |
| `rad00a59/cert_S_tiers.py` | [rad00a59] `evidence/peer/cert_S_tiers.py` | self-consistent-constants | `f9ff4c01a639a44e67f8f893befb51cba55f26789bd05f4541862758223e800e` |
| `rad00a59/cert_S_tiers.txt` | [rad00a59] `evidence/peer/cert_S_tiers.txt` | self-consistent-constants | `e21c6b884ffb723536602c9bfe66f5c058033d1cdbaf2b20a9851a071b52498a` |
| `rad00a59/cert_table.py` | [rad00a59] `evidence/peer/cert_table.py` | self-consistent-constants | `fa45ed4a475e5be6409ea384f2fec9e3c212b67ec03cee056c57b73178dfc828` |
| `rad00a59/cert_table.txt` | [rad00a59] `evidence/peer/cert_table.txt` | self-consistent-constants | `f61718476b0939d54a20a444b07ae58d1dad0ff6cc91fba3a33fb628307edee7` |
| `rad00a59/rv_constants.py` | [rad00a59] `review/evidence/rv_constants.py` | self-consistent-constants | `ea361e6fe4c38335a725fa9e3fc7afa419e40e221a6f28b2f966ef6fa88d9f45` |
| `rad00a59/rv_constants.txt` | [rad00a59] `review/evidence/rv_constants.txt` | self-consistent-constants | `8359e4c63ba937f13672693b9b99e08179ea4dc7f844b72392e2f699e1608e2f` |
| `rad00a59/sc_bounds.py` | [rad00a59] `evidence/peer/sc_bounds.py` | self-consistent-constants | `2c8dbddc67f634ab195e3542f67b7873fd2141382e418cf98aba67eaa504fc27` |
| `rad00a59/sc_thresholds.py` | [rad00a59] `evidence/peer/sc_thresholds.py` | self-consistent-constants | `679455fb9ef470dae89ddb4160ce87ff23350a66457f36208ee0c3fc50a70196` |
| `rad00a59/sc_thresholds.txt` | [rad00a59] `evidence/peer/sc_thresholds.txt` | self-consistent-constants | `0afe5a922cc94eaa952d1cc57aa7f203fd07dd6cda8dd06ddd4be85af5b29938` |
| `rae1f209/analytic_bounds.out` | [rae1f209] `evidence/out/peer/analytic_bounds.out` | AR-integrals | `ca8a9ae2d8e6f159a66273133a98c06f847cc3fcbe8aa25667958570a9e8b2a8` |
| `rae1f209/analytic_bounds.py` | [rae1f209] `evidence/code/peer/analytic_bounds.py` | AR-integrals | `f73c407c17ecbab48bc751f435130b5348ed474b76bf6a335f3645a887d86227` |
| `rae1f209/rev_analytic.out` | [rae1f209] `review/evidence/rev_analytic.out` | AR-integrals | `f281c2e5804bc238389ea1f114c0c33b9992943311b791aa4779cc85cf04e4ef` |
| `rae1f209/rev_analytic.py` | [rae1f209] `review/evidence/rev_analytic.py` | AR-integrals | `76ec784851a9cc00b679bcd56666369052d2a8b7e6f1f8f7545565a395696edc` |
| `rb6a2cd0/border_mp.py` | [rb6a2cd0] `evidence/peer/border_mp.py` | band-LP | `1e4eb0cf86df614a0a248b3f75ff771e579390f2450a67adbf61707fa636aeaf` |
| `rb6a2cd0/localize_mp.py` | [rb6a2cd0] `evidence/peer/localize_mp.py` | band-LP | `044f4b2177310628c83ff1015abd7eea9c8abd3f735648f22802f73ba0368c20` |
| `rb6a2cd0/out_border_mp.txt` | [rb6a2cd0] `evidence/peer/out_border_mp.txt` | band-LP | `8e99964c26c8650930751942fb23d49217659b2594133499d0996fa280138736` |
| `rb6a2cd0/out_localize_16750_24099.txt` | [rb6a2cd0] `evidence/peer/out_localize_16750_24099.txt` | band-LP | `24044aada6764fa46fbc8e11e09464e141544d8dea0d6f2951beb8e402fa5023` |
| `rb6a2cd0/out_localize_24100_31449.txt` | [rb6a2cd0] `evidence/peer/out_localize_24100_31449.txt` | band-LP | `32eb29f229e575ccebce0eb08c242f913edc3cd23456bab474f8a4579abb1bb7` |
| `rb6a2cd0/out_localize_31450_38886.txt` | [rb6a2cd0] `evidence/peer/out_localize_31450_38886.txt` | band-LP | `a4ec5735f4a89ee06de355b668aca614675ad3abffc987d6ebe9f2a993107de0` |
| `rb6a2cd0/out_localize_9400_16749.txt` | [rb6a2cd0] `evidence/peer/out_localize_9400_16749.txt` | band-LP | `0fb0850d3e13c0e1da3b1e949eee8e8044eed6da32c443b81777a9701168f72a` |
| `rb6a2cd0/out_localize_mp.txt` | [rb6a2cd0] `evidence/peer/out_localize_mp.txt` | band-LP | `0aa959072d8b377b74d94990a0e8b04fc3ac6bb28bfad65ba1c97cc49d799406` |
| `rb6a2cd0/out_lp_check_6668_9466.txt` | [rb6a2cd0] `evidence/peer/out_lp_check_6668_9466.txt` | band-LP | `b0120ac6055eb3488250aa6e4e4855b79039980e5e00da55d0a099e17f65fb2d` |
| `rb6a2cd0/out_lp_pointwise.txt` | [rb6a2cd0] `evidence/peer/out_lp_pointwise.txt` | band-LP | `5683eeeeb2c0f6ccd5af6af253e5b48535ba8f5bd7d878b5cf0aa24211676ef8` |
| `rb6a2cd0/out_peer_thresholds.txt` | [rb6a2cd0] `evidence/peer/out_peer_thresholds.txt` | band-LP | `b8cc631adbc9c458a89df941f6630e0bee6304106ea7cf870b06fa291abf303b` |
| `rb6a2cd0/out_subband_check.txt` | [rb6a2cd0] `evidence/producer/work/out_subband_check.txt` | band-LP | `c0424da9100430a90e24f735f4add1c707b491285fa680b59786e4fb23534fa8` |
| `rb6a2cd0/peer_localize.py` | [rb6a2cd0] `evidence/peer/peer_localize.py` | band-LP | `c9e831756fe29f3c903f428171ac657074c3408b4c0a2bcb8fbdf32842091069` |
| `rb6a2cd0/peer_localize_check.py` | [rb6a2cd0] `evidence/peer/peer_localize_check.py` | band-LP | `a6c770c5bdd5149e4ab12ad1c4395898c5b74ad9a79350dbce43f33a83a68998` |
| `rb6a2cd0/peer_lp.py` | [rb6a2cd0] `evidence/peer/peer_lp.py` | band-LP | `936d7ebc15af0e11107f2a7dab030d12aebff9afbe412f808f271c45abe4bbcc` |
| `rb6a2cd0/peer_lp_check.py` | [rb6a2cd0] `evidence/peer/peer_lp_check.py` | band-LP | `c31c7c507775b374809a4d83c22187c482d813ba4bcc85fdc07c12d4ccfbe07b` |
| `rb6a2cd0/peer_ranges.py` | [rb6a2cd0] `evidence/peer/peer_ranges.py` | band-LP | `3327f3f26ad33d5086bd754aa3ef53882558d56e88ab9905f59266165da36f5e` |
| `rb6a2cd0/peer_thresholds.py` | [rb6a2cd0] `evidence/peer/peer_thresholds.py` | band-LP | `175934c7a04f1d137ea9ec207b9558a2946755c0a8a4fb1bd844564c119c91d1` |
| `rb6a2cd0/subband.py` | [rb6a2cd0] `evidence/producer/work/subband.py` | band-LP | `1a9247e4ae905de8b3b3428be4b406a78399a126e213430266e16ff739c75d09` |
| `rb6a2cd0/subband_check.py` | [rb6a2cd0] `evidence/producer/work/subband_check.py` | band-LP | `b9644862c7f7a8bf16f21a7dbe71ded57bea890bac9f11ffd69bfce7b366f2df` |
| `rb7effe0/blk3_stats.out` | [rb7effe0] `evidence/code/turn3/blk3_stats.out` | column-certificates-841-2000 | `546611ca1b8587fe2bcc53557979707154bdb0d650fc5b8d83a0fe791264c660` |
| `rb7effe0/blk3_stats.py` | [rb7effe0] `evidence/code/turn3/blk3_stats.py` | column-certificates-841-2000 | `b12173739ab47e24a2ac1fb7e97b465ff59edf982cf7fa50fe8b19e58cddc1f5` |
| `rb7effe0/block3_501_2000_all.json` | [rb7effe0] `evidence/code/turn3/block3_501_2000_all.json` | column-certificates-841-2000 | `0fcac5fef27b255718bf15fd0a91b909d4424a795e7e3444ea43f173a31c21a6` |
| `rb7effe0/certificate3.py` | [rb7effe0] `evidence/code/turn3/certificate3.py` | column-certificates-841-2000 | `11cb014fd1ae66db86767a020956a4b834bce457eee234552980588f8dee2ac6` |
| `rb7effe0/evidence/code/turn3/blk3_stats.out` | [rb7effe0] `evidence/code/turn3/blk3_stats.out`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `546611ca1b8587fe2bcc53557979707154bdb0d650fc5b8d83a0fe791264c660` |
| `rb7effe0/evidence/code/turn3/blk3_stats.py` | [rb7effe0] `evidence/code/turn3/blk3_stats.py`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `b12173739ab47e24a2ac1fb7e97b465ff59edf982cf7fa50fe8b19e58cddc1f5` |
| `rb7effe0/evidence/code/turn3/block3_501_2000_all.json` | [rb7effe0] `evidence/code/turn3/block3_501_2000_all.json`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `0fcac5fef27b255718bf15fd0a91b909d4424a795e7e3444ea43f173a31c21a6` |
| `rb7effe0/evidence/code/turn3/certificate2.py` | [rb7effe0] `evidence/code/turn3/certificate2.py`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `e52f9947538b67220e09822a2e46ba1d735de6add806fea2f3f68813d157c955` |
| `rb7effe0/evidence/code/turn3/certificate3.py` | [rb7effe0] `evidence/code/turn3/certificate3.py`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `11cb014fd1ae66db86767a020956a4b834bce457eee234552980588f8dee2ac6` |
| `rb7effe0/evidence/code/turn3/probe_circle.py` | [rb7effe0] `evidence/code/turn3/probe_circle.py`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `6c8d6a70ee8203c303e8d70e59d9f23835e49e1e36cac28c3811f36198521829` |
| `rb7effe0/evidence/code/turn3/probe_second_zero.out` | [rb7effe0] `evidence/code/turn3/probe_second_zero.out`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `57a175be9de9f8c537dec2dd0f97509481faaf4a52ce33f91d659306faf4b0a6` |
| `rb7effe0/evidence/code/turn3/probe_second_zero.py` | [rb7effe0] `evidence/code/turn3/probe_second_zero.py`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `9f2f504dc9fc9b736495c46c98e9f115f5a75475518ecca74755f8e3cfe1cf6e` |
| `rb7effe0/evidence/code/turn3/samples3.out` | [rb7effe0] `evidence/code/turn3/samples3.out`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `6ad61cc38b1ba57da2f136348e19cc72e8c9f322dd8a4ccf35187b5cbd8003b8` |
| `rb7effe0/evidence/code/turn3/validate_eps3.out` | [rb7effe0] `evidence/code/turn3/validate_eps3.out`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `9efca0abf0d2b5313ce6188214ae1ccd8f24c126a44fb056c487040c0149231c` |
| `rb7effe0/evidence/code/turn3/validate_eps3.py` | [rb7effe0] `evidence/code/turn3/validate_eps3.py`(폴더 `evidence/code/turn3/`) | column-certificates-841-2000 | `e06778b17ecea57bddcd9860a84af47dcf56113109cf32dcf396828aa9e9de1d` |
| `rb7effe0/review/evidence/cert/block_claims.out` | [rb7effe0] `review/evidence/cert/block_claims.out`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `59e30277a2479dbcf41473438e2c3d2ed7ac96602f3b72b77165c932001aafb6` |
| `rb7effe0/review/evidence/cert/block_claims.py` | [rb7effe0] `review/evidence/cert/block_claims.py`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `abd025efe77724798234007d88f706241d1bcbea49fb70e7cc20945bd11c7bae` |
| `rb7effe0/review/evidence/cert/nv_full.out` | [rb7effe0] `review/evidence/cert/nv_full.out`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `5fa2331f69c85fdac6db88b0cecaca8fa27ce7686b4ef85637962ae8aada1fba` |
| `rb7effe0/review/evidence/cert/nv_full.py` | [rb7effe0] `review/evidence/cert/nv_full.py`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `398ae647f72613c55c0d2b4d6e173938c5d94cdea2124385b75640719f2e147c` |
| `rb7effe0/review/evidence/cert/rerun_3000.out` | [rb7effe0] `review/evidence/cert/rerun_3000.out`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `c081f6f71f0cecce2f37fb7e7e43deee3906247268b5d2cd019e8f267a26651f` |
| `rb7effe0/review/evidence/cert/rerun_a.json` | [rb7effe0] `review/evidence/cert/rerun_a.json`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `0a1487aca5085dc1386bc783d59137f4c3b767700d05341a8f8f438909ac1855` |
| `rb7effe0/review/evidence/cert/rerun_b.json` | [rb7effe0] `review/evidence/cert/rerun_b.json`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `a68b7743f676b7b75f469ed15ddc29c8fbd3b347333ec9f141d887c9b6272284` |
| `rb7effe0/review/evidence/cert/rerun_b.out` | [rb7effe0] `review/evidence/cert/rerun_b.out`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `6a7ad9603d88ea0ecb725c081072dccb4a367726baa15ce9e07564eddf236189` |
| `rb7effe0/review/evidence/cert/rerun_big.out` | [rb7effe0] `review/evidence/cert/rerun_big.out`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `93ccf4fa1578b26f35fd484498b6b6fa6dfa2a3f73ad0275c7d6c39d5b01735d` |
| `rb7effe0/review/evidence/cert/rerun_c.json` | [rb7effe0] `review/evidence/cert/rerun_c.json`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `1ea76175589a91b6d03dc0c1e5e1a4075715daddc7b628d0370e986945d9174e` |
| `rb7effe0/review/evidence/cert/rerun_c.out` | [rb7effe0] `review/evidence/cert/rerun_c.out`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `7145f47dbfc96daba87c37347a505d96708807ae484e5ee67939f1f7d4a738be` |
| `rb7effe0/review/evidence/cert/sample10.txt` | [rb7effe0] `review/evidence/cert/sample10.txt`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `98c193b66b74f04940747cb1884509e9f75c4689fd2c882abd02366ded23af5c` |
| `rb7effe0/review/evidence/cert/sample_ks.txt` | [rb7effe0] `review/evidence/cert/sample_ks.txt`(폴더 `review/evidence/cert/`) | column-certificates-841-2000 | `be7d8ea4460f27c44b35572ae40be7f28e76123b7af6c49d1d26ba50a30dd59b` |
| `rb7effe0/review/evidence/check/bf_gf.out` | [rb7effe0] `review/evidence/check/bf_gf.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `85758fb4efc578bde90fc112bc4e2706d0b860b0f717a3b148d95f5fb2fd259a` |
| `rb7effe0/review/evidence/check/bf_gf.py` | [rb7effe0] `review/evidence/check/bf_gf.py`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `3e4e68b54328afe3404f85ff65fafa097ff724ecbeac057455306234ebcc052d` |
| `rb7effe0/review/evidence/check/e2e_sign.out` | [rb7effe0] `review/evidence/check/e2e_sign.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `98ce30d3ed55f07e8b0631d64f32edb96d5881ed63ff83eea201d84a64874ab2` |
| `rb7effe0/review/evidence/check/e2e_sign.py` | [rb7effe0] `review/evidence/check/e2e_sign.py`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `0e7f45a04125fe133103e6826841e920310e47de3a50d2db306c3c596bdc99d1` |
| `rb7effe0/review/evidence/check/finite_check.py` | [rb7effe0] `review/evidence/check/finite_check.py`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `3446088d764d86d5350b709d2854b8ac71bf6c02c38893db876ee88de92516d9` |
| `rb7effe0/review/evidence/check/finite_check_1000.out` | [rb7effe0] `review/evidence/check/finite_check_1000.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `353316e195283bbb8f0934c570dfa3150360f618d472ee34f63b346c510e008a` |
| `rb7effe0/review/evidence/check/finite_check_501.out` | [rb7effe0] `review/evidence/check/finite_check_501.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `02df88bce0d31a983b12873b015b18dda159983cb53bea1ee732593ae8febed3` |
| `rb7effe0/review/evidence/check/finite_check_840.out` | [rb7effe0] `review/evidence/check/finite_check_840.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `3f724baa41872110ec26b08b8401136c15cc38857b4ab7ae1e05da835d6de397` |
| `rb7effe0/review/evidence/check/fullprec.out` | [rb7effe0] `review/evidence/check/fullprec.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `04128353f33abba0d616ecbf6955ca2c3576b6bf7cbccee1c29943c88dc997fa` |
| `rb7effe0/review/evidence/check/fullprec.py` | [rb7effe0] `review/evidence/check/fullprec.py`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `26b7795075a96f872dbca3e685a327bcc89647f63529bbd99cbccca1b6957d26` |
| `rb7effe0/review/evidence/check/indep_1000.out` | [rb7effe0] `review/evidence/check/indep_1000.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `04bce255caaa01f83425d61cb3d7fa0504bd8667f0e9490445f249c45c03e510` |
| `rb7effe0/review/evidence/check/indep_501.out` | [rb7effe0] `review/evidence/check/indep_501.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `c6733b52c5cf3c2b81c36d6172751e928329ab2d1af809ce257d452e1a2a39f7` |
| `rb7effe0/review/evidence/check/indep_840.out` | [rb7effe0] `review/evidence/check/indep_840.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `c65a096a6d4991dbdfa971d8631bb28cfd2ceca50da9bda59dc460f45cc9894f` |
| `rb7effe0/review/evidence/check/indep_col.py` | [rb7effe0] `review/evidence/check/indep_col.py`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `9a33255a88379807d28a4ae45ccb6e109d2141f60f7d3fa40b08cc01f8411575` |
| `rb7effe0/review/evidence/check/misc_numbers.out` | [rb7effe0] `review/evidence/check/misc_numbers.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `bb53937350bd8c4d0eca01ba8b8f73d4d6156aee51a2de8714dedecda242c953` |
| `rb7effe0/review/evidence/check/misc_numbers.py` | [rb7effe0] `review/evidence/check/misc_numbers.py`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `cedc91bbaf77f95f45bef2f8897a09dd6b47e2821fcd14be027bb2fa46c4fdfc` |
| `rb7effe0/review/evidence/check/small_k_limits.out` | [rb7effe0] `review/evidence/check/small_k_limits.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `f4964f26f4cd74b8339e5d69fbf33de6819b7904ba94a5fc5611261a27f8988e` |
| `rb7effe0/review/evidence/check/small_k_limits.py` | [rb7effe0] `review/evidence/check/small_k_limits.py`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `44090cb13f7ceaf519539c06b071e3d2d841dc9b124a5b402c44ce85cb4bd051` |
| `rb7effe0/review/evidence/check/zero2.out` | [rb7effe0] `review/evidence/check/zero2.out`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `9d729ae3eea2afb727b35a4c1160d44425213681abecba1c800c19d0b78ca1c9` |
| `rb7effe0/review/evidence/check/zero2.py` | [rb7effe0] `review/evidence/check/zero2.py`(폴더 `review/evidence/check/`) | column-certificates-841-2000 | `23e65a6e8c2d6dcc540be1cf52f60b1b69537b0d8a95280eb3c4202e31690c8d` |
| `rb7effe0/samples3.out` | [rb7effe0] `evidence/code/turn3/samples3.out` | column-certificates-841-2000 | `6ad61cc38b1ba57da2f136348e19cc72e8c9f322dd8a4ccf35187b5cbd8003b8` |
| `rb7effe0/validate_eps3.out` | [rb7effe0] `evidence/code/turn3/validate_eps3.out` | column-certificates-841-2000 | `9efca0abf0d2b5313ce6188214ae1ccd8f24c126a44fb056c487040c0149231c` |
| `rb7effe0/validate_eps3.py` | [rb7effe0] `evidence/code/turn3/validate_eps3.py` | column-certificates-841-2000 | `e06778b17ecea57bddcd9860a84af47dcf56113109cf32dcf396828aa9e9de1d` |
| `rbeae3a3/exact_rows.py` | [rbeae3a3] `evidence/peer/exact_rows.py` | QL-small-n | `950c41d03470a6ea45267bbf89cf2ed09b79a47f2c022aa5d3ec668dcccd3448` |
| `rbeae3a3/exact_stream.py` | [rbeae3a3] `evidence/peer/exact_stream.py` | QL-small-n | `75167e0d75209bd5d65c15bdf2f12f88a36ad73d6965889c9a1e3b88ae22a37a` |
| `rbeae3a3/stream1000-rows.json.gz` | [rbeae3a3] `evidence/peer/stream1000-rows.json.gz` | QL-small-n | `1cb01856cb4ede38a2e36b3e361a8190273c884b3dd86e72121a1299c6a6747d` |
| `rbeae3a3/stream1000-summary.json` | [rbeae3a3] `evidence/peer/stream1000-summary.json` | QL-small-n | `830e54a2217353bf063fc32d9fea48bb24669c2ed5e47db6d821d47a2ef93c1e` |
| `rbeae3a3/streamR1000-summary.json` | [rbeae3a3] `evidence/peer/streamR1000-summary.json` | QL-small-n | `05a7b16c77960e90e1330710fe65e9f3d99106a5342ba6d74c8ddee357933a54` |
| `rc9aee43/batch-summary.json` | [rc9aee43] `evidence/producer/output/batch-summary.json` | column-certification-k500 | `a856a59f29d5d514b6a69624c0e751f687bbeb85eec325494173bb1ccd440794` |
| `rc9aee43/certificates-121-160.json` | [rc9aee43] `evidence/producer/output/certificates-121-160.json` | exact-n20000 | `a6d458dd12db4451c58c480427b291349322847a426a629e852a581b552293be` |
| `rc9aee43/evidence__peer__code__extend_columns.py` | [rc9aee43] `evidence/peer/code/extend_columns.py` | column-certification-k500 | `8f2bd38af768fcf830f89cee8c8edf466b02d683de54eb40fdd9211bd717ba38` |
| `rc9aee43/evidence__peer__code__indep_lastcar.py` | [rc9aee43] `evidence/peer/code/indep_lastcar.py` | column-certification-k500 | `25b2af15b9ed44c7c115c6c7621fc62ac3db1da4274e233d636d494bb7a0bff5` |
| `rc9aee43/evidence__peer__output__ext-161-360.json` | [rc9aee43] `evidence/peer/output/ext-161-360.json` | column-certification-k500 | `c9abcd880dc39e3496c127e01d160f6e3c5d4042d9378ed1d2589cd0f5698c52` |
| `rc9aee43/evidence__peer__output__ext-361-442.json` | [rc9aee43] `evidence/peer/output/ext-361-442.json` | column-certification-k500 | `a80b7b00c3b2c2dc9f3599752a19976900c43223107c5381adcd0b83a87167cb` |
| `rc9aee43/evidence__peer__output__ext-443-500.json` | [rc9aee43] `evidence/peer/output/ext-443-500.json` | column-certification-k500 | `dd008a1ca1bcd6a43aba377b282662716c35232226ce0bf5be7e502666e48001` |
| `rc9aee43/evidence__producer__code__positive_columns.py` | [rc9aee43] `evidence/producer/code/positive_columns.py` | column-certification-k500 | `2f1841a9bd301cfa541c3877e50ae0dfac10d84ed0b8434d3c3e35dff0c8065b` |
| `rc9aee43/evidence__producer__output__certificates-121-160.json` | [rc9aee43] `evidence/producer/output/certificates-121-160.json` | column-certification-k500 | `a6d458dd12db4451c58c480427b291349322847a426a629e852a581b552293be` |
| `rc9aee43/ext-161-360.json` | [rc9aee43] `evidence/peer/output/ext-161-360.json` | exact-n20000 | `c9abcd880dc39e3496c127e01d160f6e3c5d4042d9378ed1d2589cd0f5698c52` |
| `rc9aee43/ext-361-442.json` | [rc9aee43] `evidence/peer/output/ext-361-442.json` | exact-n20000 | `a80b7b00c3b2c2dc9f3599752a19976900c43223107c5381adcd0b83a87167cb` |
| `rc9aee43/ext-443-500.json` | [rc9aee43] `evidence/peer/output/ext-443-500.json` | exact-n20000 | `dd008a1ca1bcd6a43aba377b282662716c35232226ce0bf5be7e502666e48001` |
| `rc9aee43/extend_columns.py` | [rc9aee43] `evidence/peer/code/extend_columns.py` | exact-n20000 | `8f2bd38af768fcf830f89cee8c8edf466b02d683de54eb40fdd9211bd717ba38` |
| `rc9aee43/fixed-ratio-integer-check.json` | [rc9aee43] `evidence/producer/output/fixed-ratio-integer-check.json` | column-certification-k500 | `4943fb83735564908c32a593243118a784ad9e5db23cbd6110361463d4dac258` |
| `rc9aee43/indep-lastcar-121-140-160.json` | [rc9aee43] `evidence/peer/output/indep-lastcar-121-140-160.json` | column-certification-k500 | `27f49b58b4d0db7c42adf1d5bf73d495c0ae551f92d748b4f93e0b227843a2b3` |
| `rc9aee43/indep-lastcar-128.json` | [rc9aee43] `evidence/peer/output/indep-lastcar-128.json` | column-certification-k500 | `d50e0fa478f5ced7b4e7fa53bf55a49ff9b337c41587810d222dcdb76769fd8e` |
| `rc9aee43/indep-lastcar-161.json` | [rc9aee43] `evidence/peer/output/indep-lastcar-161.json` | column-certification-k500 | `6fe61c811236e3beafc106d3040fbae971aad951ee8df7c36d01d1eca4f12f02` |
| `rc9aee43/indep_lastcar.py` | [rc9aee43] `evidence/peer/code/indep_lastcar.py` | exact-n20000 | `25b2af15b9ed44c7c115c6c7621fc62ac3db1da4274e233d636d494bb7a0bff5` |
| `rc9aee43/positive_columns.py` | [rc9aee43] `evidence/producer/code/positive_columns.py` | exact-n20000 | `2f1841a9bd301cfa541c3877e50ae0dfac10d84ed0b8434d3c3e35dff0c8065b` |
| `rc9aee43/producer_positive_columns.py` | [rc9aee43] `evidence/peer/code/producer_positive_columns.py` | column-certification-k500 | `2f1841a9bd301cfa541c3877e50ae0dfac10d84ed0b8434d3c3e35dff0c8065b` |
| `rc9aee43/rerun-k500.json` | [rc9aee43] `review/evidence/rerun-k500.json` | exact-n20000 | `05a2a14bf32ebfa4c85247bfe88a0a832a8ade478dcc5abf9855bba0bb1f65d3` |
| `rc9aee43/rev-col-k150.json` | [rc9aee43] `review/evidence/rev-col-k150.json` | exact-n20000 | `dc3d0295ce0f3137af132724276dd10843534776742c8f177931aaa835cea30a` |
| `rc9aee43/rev-col-k200.json` | [rc9aee43] `review/evidence/rev-col-k200.json` | exact-n20000 | `d70b4cd57c0cf837ebe38943fbcb9ce4c4586473b6215467df9c209d4f890acc` |
| `rc9aee43/rowwise_left.py` | [rc9aee43] `evidence/peer/code/rowwise_left.py` | exact-n20000 | `c1843ee1f6da2a61c03a25ace5f48c119ef6ba614758d8f982cac6c98ade9dab` |
| `rc9aee43/rw-10000-a.json` | [rc9aee43] `evidence/peer/output/rw-10000-a.json` | exact-n20000 | `2ea522a697fd46bb5601478c2370969ab8e8b01a57f6c640c16535ba0e1e0379` |
| `rc9aee43/rw-10000-b.json` | [rc9aee43] `evidence/peer/output/rw-10000-b.json` | exact-n20000 | `108be3c453080fde7bc76f5c19765c7e1cda4f31c39a7b0cbf2f5671063675c0` |
| `rc9aee43/rw-10000-c.json` | [rc9aee43] `evidence/peer/output/rw-10000-c.json` | exact-n20000 | `1e94ec58086f74ff985b956269a63709aaa4180e3e26c2ee8b061c6861f77450` |
| `rc9aee43/rw-10000-d.json` | [rc9aee43] `evidence/peer/output/rw-10000-d.json` | exact-n20000 | `73e7200cc24a0a116291e89ca85e17fc1f1e715e2b27731ba2bec2991380f656` |
| `rc9aee43/rw-10000-e.json` | [rc9aee43] `evidence/peer/output/rw-10000-e.json` | exact-n20000 | `6a0d2acd39101ae731bd3d2116bd9653769900088c78c0022aab9d012886b7ab` |
| `rc9aee43/rw-10000-f.json` | [rc9aee43] `evidence/peer/output/rw-10000-f.json` | exact-n20000 | `7eb66255920443b453a78346e97d80e73648f6ecd1d7a618aabe6bbb889717d2` |
| `rc9aee43/rw-10000-g.json` | [rc9aee43] `evidence/peer/output/rw-10000-g.json` | exact-n20000 | `b86814c3f6801e47d71b829d667756c96214a3b28f537688000917b59bcce391` |
| `rc9aee43/summary-all.json` | [rc9aee43] `evidence/peer/output/summary-all.json` | exact-n20000 | `84d6483a29160237ef6a72fd26c7472e8ef56ed448e78348c3bea4b4264a472f` |
| `rc9aee43/summary-columns.json` | [rc9aee43] `evidence/peer/output/summary-columns.json` | column-certification-k500 | `615b7d8b287f28eaf784494d0bf0c53fa5a16e2280b29f1af6c9b0fdcd1da9a3` |
| `rc9aee43/verify_positive_columns.py` | [rc9aee43] `evidence/producer/code/verify_positive_columns.py` | column-certification-k500 | `f2034176db68d3fd3a2c63cf350d8a3824e2d0b64d42ff506f91c8262cd140d7` |
| `rce3dc75/audit_K1.py` | [rce3dc75] `evidence/peer/k1audit/audit_K1.py` | central-gap-rational-audit | `046403e1e541f6235f1d2ebba8102a76d71d3f6428c649fea548a798b82cc985` |
| `rce3dc75/audit_K1_out.json` | [rce3dc75] `evidence/peer/k1audit/audit_K1_out.json` | central-gap-rational-audit | `d1a13274ab6763febb5b95247c66e5db19d6fc95bda50b29e31f1f3f9701b525` |
| `rce3dc75/audit_reruns.txt` | [rce3dc75] `review/checks/data/audit_reruns.txt` | central-gap-rational-audit | `8ec261258d461ecc7d59cf2059affd3f47bc231331045631f39d9ff14685c299` |
| `rce3dc75/boundary-vertical-audit.json` | [rce3dc75] `evidence/producer/output/boundary-vertical-audit.json` | central-gap-rational-audit | `729f581878eaf6ac79e8c4e99565c96b48eaf73e27d992711ac7b3a12a6f19cf` |
| `rce3dc75/boundary_vertical_audit.py` | [rce3dc75] `evidence/producer/work/boundary_vertical_audit.py` | central-gap-rational-audit | `461489deee6f946a41f9099a2911616ba11fbfd943b7ee56c0ca0f182ef1bafd` |
| `rce3dc75/effective-constants-audit.json` | [rce3dc75] `evidence/producer/output/effective-constants-audit.json` | central-gap-rational-audit | `b059fec39635047c13b5409ca083544a5a7ab871d85b11d9b26abe86eca49427` |
| `rce3dc75/effective_constants_audit.py` | [rce3dc75] `evidence/producer/work/effective_constants_audit.py` | central-gap-rational-audit | `e58ff42dabd84501a6272994d24e144afa4e4b7806150f053eaf81edaaae4035` |
| `rce3dc75/evidence__peer__icert__icert.c` | [rce3dc75] `evidence/peer/icert/icert.c` | exact-n20000 | `f749602de27b8cf6bbcbe915d6d17ed5eecec9eb5a1dda40a7709e06f5b64d02` |
| `rce3dc75/evidence__peer__icert__icert_summary.json` | [rce3dc75] `evidence/peer/icert/icert_summary.json` | exact-n20000 | `3d00c51ad261b9fb06b02dfbd38f6639a60fe6925784ee01247d7c4ae19bb231` |
| `rce3dc75/evidence__peer__icert__out_8_10000.txt` | [rce3dc75] `evidence/peer/icert/out_8_10000.txt` | exact-n20000 | `f4f11f36eff2745672fe2ae39a407a851ddc7d9dd4e0b4d6f11fbeb611587f6e` |
| `rce3dc75/exact-first-constant.json` | [rce3dc75] `evidence/producer/output/exact-first-constant.json` | central-gap-rational-audit | `f23934a0f2faa41f42cf0fa1f8e9c64f04e0534cca66bfb70ff1ef0fe9128320` |
| `rce3dc75/exact_first_constant.py` | [rce3dc75] `evidence/producer/work/exact_first_constant.py` | central-gap-rational-audit | `f87de0a05ede42fae150d9b9cde2852a55539ef786c35389827bbdfece6d6eaf` |
| `rce3dc75/hermite-bounds-audit.json` | [rce3dc75] `evidence/producer/output/hermite-bounds-audit.json` | central-gap-rational-audit | `fd3e0afd6915e4a9986360fc62a21ae339eb039135b1b83df219eccc5bc7e8b9` |
| `rce3dc75/hermite-series.json` | [rce3dc75] `evidence/producer/output/hermite-series.json` | central-gap-rational-audit | `296ee4046281f4d81e38cdfb9c40da1f1e271201ec977eb1ad92553ce13b27a8` |
| `rce3dc75/hermite_bounds_audit.py` | [rce3dc75] `evidence/producer/work/hermite_bounds_audit.py` | central-gap-rational-audit | `ecff25870b7fd5d78398d78cfe81777235c5be1dd0cc1d72269ee78e34c1dfe8` |
| `rce3dc75/hermite_laurent.py` | [rce3dc75] `evidence/producer/work/hermite_laurent.py` | central-gap-rational-audit | `c24efd21e48ebb538ad4d7e24ea0e1ab35d2567e517ac87ecbbd9a7d1e79c7db` |
| `rce3dc75/hermite_series.py` | [rce3dc75] `evidence/producer/work/hermite_series.py` | central-gap-rational-audit | `39ec31386a3739600f2f117d85b9b5cf298deb55b8bcfa756a20490cbc408c9d` |
| `rce3dc75/icert.c` | [rce3dc75] `evidence/peer/icert/icert.c` | central-gap-integer | `f749602de27b8cf6bbcbe915d6d17ed5eecec9eb5a1dda40a7709e06f5b64d02` |
| `rce3dc75/icert_py.py` | [rce3dc75] `evidence/peer/icert/icert_py.py` | central-gap-integer | `3bcfcbcf96adb9d86753e205ca99ec697db3247f68a1fb6ae86d00454d2cc5bf` |
| `rce3dc75/icert_summary.json` | [rce3dc75] `evidence/peer/icert/icert_summary.json` | central-gap-integer | `3d00c51ad261b9fb06b02dfbd38f6639a60fe6925784ee01247d7c4ae19bb231` |
| `rce3dc75/make_rtable.py` | [rce3dc75] `evidence/peer/icert/make_rtable.py` | central-gap-integer | `2f934f002724e82813b5a46aa3f8781eee36a8ed9a77dbfd2415b5f2417543b4` |
| `rce3dc75/out_8_10000.txt` | [rce3dc75] `evidence/peer/icert/out_8_10000.txt` | central-gap-integer | `f4f11f36eff2745672fe2ae39a407a851ddc7d9dd4e0b4d6f11fbeb611587f6e` |
| `rce3dc75/out_small.txt` | [rce3dc75] `evidence/peer/icert/out_small.txt` | central-gap-integer | `7910bcee805edf646a9fed09bb410d2d7c8d56885d9458384e0724612d23a94e` |
| `rce3dc75/pyref_compare.json` | [rce3dc75] `evidence/peer/icert/pyref_compare.json` | central-gap-integer | `5f3a60c02d809da65951ece5d5227e36a971acd6030014822cb67e3307855e18` |
| `rce3dc75/real_comparison_audit.py` | [rce3dc75] `evidence/producer/work/real_comparison_audit.py` | central-gap-rational-audit | `b83055c43e9e3c48301cdd78037fc05b75c7e18647e561bc03d0303af122828e` |
| `rce3dc75/rev_icert_8_1000.out` | [rce3dc75] `review/checks/data/rev_icert_8_1000.out` | central-gap-integer | `c141b37cbc0af29f09ae0205ea0153ddca02e85860d23da91b454763c6dbd6f5` |
| `rce3dc75/rev_icert_big.out` | [rce3dc75] `review/checks/data/rev_icert_big.out` | central-gap-integer | `22357c092cb88a4bf7cf2f28f48fb42c665478783042390d420c0c39ef3ec463` |
| `rce3dc75/rev_icert_dense.out` | [rce3dc75] `review/checks/data/rev_icert_dense.out` | central-gap-integer | `f2a705c4f37e678148058f81d40e5cccc77168eef2b5dcd4abd2e4a482b0aa3b` |
| `rce3dc75/rev_icert_small.out` | [rce3dc75] `review/checks/data/rev_icert_small.out` | central-gap-integer | `557e358055b5f746173fe723c1c4e91541c73cf35b205a3a0b588b0352954328` |
| `rce3dc75/rev_icert_unpaired.py` | [rce3dc75] `review/checks/scripts/rev_icert_unpaired.py` | central-gap-integer | `df02d3a5434f3c76090c6a8abee76687b7d1b2d31591e588ae01a17e207a2f0e` |
| `rce3dc75/rev_icert_unpaired_fast.py` | [rce3dc75] `review/checks/scripts/rev_icert_unpaired_fast.py` | central-gap-integer | `ec167e0a3381cd5c1fc20a12b29e9f2e52bbda6181371840c55f9aa770c4971c` |
| `rce3dc75/rev_majorant_quad.out` | [rce3dc75] `review/checks/data/rev_majorant_quad.out` | central-gap-rational-audit | `464fca1c13e7d6a7264c85406e0b311dc98da088b47fbf80389865e7b6eda23c` |
| `rce3dc75/rev_majorant_quad.py` | [rce3dc75] `review/checks/scripts/rev_majorant_quad.py` | central-gap-rational-audit | `57500d88c52511d1c1ad6562d79b84f59edab3ae960aae0b0ff66827b6fc8cad` |
| `rce3dc75/rev_small_exact.py` | [rce3dc75] `review/checks/scripts/rev_small_exact.py` | central-gap-integer | `8dc54043c783385fb6e55a9339fcf4c3e11b4dca5d4bf73d6046bbbb7a90a648` |
| `rce3dc75/rev_small_exact_out.json` | [rce3dc75] `review/checks/data/rev_small_exact_out.json` | central-gap-integer | `86e4c97744d6567cf0847efc534fecc5f25f0b4471f9be5f87993c3fc00bd396` |
| `rce3dc75/rev_uhat_laurent.out` | [rce3dc75] `review/checks/data/rev_uhat_laurent.out` | central-gap-rational-audit | `4c96b8ee0d58750777212e7c73e87081c29e29d228767a862e4b8147c27d318e` |
| `rce3dc75/rev_uhat_laurent.py` | [rce3dc75] `review/checks/scripts/rev_uhat_laurent.py` | central-gap-rational-audit | `8879af929a3f7722c2e8c091838da42cfbd4e6e766261d60eb978a734053ae8e` |
| `rce3dc75/rtable.txt` | [rce3dc75] `evidence/peer/icert/rtable.txt` | central-gap-integer | `2022d6cf2ff7d572f0ba7c69c97e3112305aba200b17127b788699cb76d9462e` |
| `rce3dc75/summarize.py` | [rce3dc75] `evidence/peer/icert/summarize.py` | central-gap-integer | `d09b495349ca55bf0d34831435d946edd866809547f85c0edcd671de0e35dabe` |
| `rce3dc75/v_exact_small.py` | [rce3dc75] `evidence/peer/code/v_exact_small.py` | central-gap-integer | `71c74e860c9e1cf2caafa3537fae7062ac75112f9c86fae0897f02d412d0b475` |
| `rce3dc75/v_exact_small_out.json` | [rce3dc75] `evidence/peer/data/v_exact_small_out.json` | central-gap-integer | `2980f5394520dbca3f645e2c8bd7eca7abda83b10bbf5a34b42728aea450329a` |
| `rce3dc75/v_hermite.py` | [rce3dc75] `evidence/peer/code/v_hermite.py` | central-gap-rational-audit | `8330f4738705efc652f2618392ae54076017bc892e1a59e9e57910bbde662151` |
| `rce3dc75/v_majorants.py` | [rce3dc75] `evidence/peer/code/v_majorants.py` | central-gap-rational-audit | `03943e4dc45a6d416859c7f72cb9119b813dbdd0f760c203a5ee6134df4e9d18` |
| `rce3dc75/v_majorants_K1.py` | [rce3dc75] `evidence/peer/code/v_majorants_K1.py` | central-gap-rational-audit | `a0fd6b9b32991954783c053edefd0b6060471b3a952e71c3eef652abeb2cfafb` |
| `rce3dc75/v_small_rows.py` | [rce3dc75] `evidence/peer/code/v_small_rows.py` | central-gap-integer | `eec704e5b065ee4c6c7fdbac37fb58a6fca6b0fda5574d0db9ca55ff3ce7d043` |
| `rce3dc75/v_small_rows_out.json` | [rce3dc75] `evidence/peer/data/v_small_rows_out.json` | central-gap-integer | `f5294f5642c795ac4badea6fb498a53e458cf59e64cf0b53ca70307dc17c9522` |
| `rce3dc75/v_uhat_series.py` | [rce3dc75] `evidence/peer/code/v_uhat_series.py` | central-gap-rational-audit | `0136172ff03e16c05d9ae3dec89bb4a27d7ff71bd08c48aa003669c8821f3300` |
| `rce3dc75/validate_small.py` | [rce3dc75] `evidence/peer/icert/validate_small.py` | central-gap-integer | `0ab18b42c52c301b67bee4d4f99026352450bd1345bb4e698580556cdb4a9af5` |
| `rce3dc75/vertical-exact-constant.json` | [rce3dc75] `evidence/producer/output/vertical-exact-constant.json` | central-gap-rational-audit | `8764a5d03bbccef82522de9a9001f30497c4dd230bb2c07474cfcdb2cdbb3104` |
| `rce3dc75/vertical_error_audit.py` | [rce3dc75] `evidence/producer/work/vertical_error_audit.py` | central-gap-rational-audit | `ba674d731c12535fa4b456ac514c485ea55cc77b384c583e37bb2adef6acfdb4` |
| `rce3dc75/vertical_exact_constant.py` | [rce3dc75] `evidence/producer/work/vertical_exact_constant.py` | central-gap-rational-audit | `18328acb05ba4490e218da6c030faea628bbe59533083ec74231bd70603a4749` |
| `re71a735/bulk_majorants.py` | [re71a735] `evidence/peer/bulk_majorants.py` | four-families | `d1dd683c1a6cbf4cc9759af5b24d63ad5737303a6fbdc1a5ce6e7ecf397b3a70` |
| `re71a735/cf.py` | [re71a735] `evidence/peer/cf.py` | M-natural-integrals | `6b66c9bfd89fdfdebd1caf623c4a6b56b18ee9c92edc6f37b8d6bcdce56ddbb0` |
| `re71a735/edge_checks.py` | [re71a735] `evidence/peer/edge_checks.py` | four-families | `3128a79f35081ea2b2fc51cfad159c815dfd243dff99bde2a3441f8dda6eb082` |
| `re71a735/edge_checks_out.txt` | [re71a735] `evidence/peer/edge_checks_out.txt` | four-families | `749e36f16451ba934218b87c203fbbcf2eecf49bee500b2b4de0262793d5b2ce` |
| `re71a735/edge_mono.py` | [re71a735] `evidence/peer/edge_mono.py` | four-families | `f21fabada2293be7ad7103e92666d3f6b1258dfcbdab173ec61239f5ab43cd1c` |
| `re71a735/evidence__peer__cf.py` | [re71a735] `evidence/peer/cf.py` | four-families | `6b66c9bfd89fdfdebd1caf623c4a6b56b18ee9c92edc6f37b8d6bcdce56ddbb0` |
| `re71a735/evidence__peer__recheck_1a.py` | [re71a735] `evidence/peer/recheck_1a.py` | four-families | `8c49a8dfe698d663de195371cfacee06dd96bf793827a9937d3cfbd8daae9557` |
| `re71a735/evidence__peer__recheck_1a_out.txt` | [re71a735] `evidence/peer/recheck_1a_out.txt` | four-families | `415843f91a3ba2930dbd2a9e11eae46289472d7d1e4e912a0a8636ffe38b83f6` |
| `re71a735/families.py` | [re71a735] `evidence/peer/families.py` | four-families | `4c85b69e74bd9f675ef3e180ff179a2464a4f1c74656abc50da50a9703d6e482` |
| `re71a735/families_out.txt` | [re71a735] `evidence/peer/families_out.txt` | four-families | `cad700545012ba6f3e6a30823b486f82ade4a7e145b1a573733d16f47ca92a95` |
| `re71a735/flq_checks_out.txt` | [re71a735] `evidence/peer/flq_checks_out.txt` | four-families | `f59d6364944fa236305d7b0952c84c8f89a813136e5508a28e65f81d6fcef346` |
| `re71a735/flq_uniform.py` | [re71a735] `evidence/peer/flq_uniform.py` | four-families | `9d6101c1ac449defd56c88e837078f3c65c36ef0d9cff9b93fa0b4265cf40b65` |
| `re71a735/propM_proof.py` | [re71a735] `evidence/peer/propM_proof.py` | M-natural-integrals | `dab41075be265c9ee6d66f5c79d3c162b17ccf5532beee0d276ae0ac0a82e5b0` |
| `re71a735/propM_proof_out.txt` | [re71a735] `evidence/peer/propM_proof_out.txt` | M-natural-integrals | `1bf38fc1e66a5839139ea67141bcb668de2116b862bdddb4c2c51f7e50f657bc` |
| `re71a735/recheck_1a.py` | [re71a735] `evidence/peer/recheck_1a.py` | M-natural-integrals | `8c49a8dfe698d663de195371cfacee06dd96bf793827a9937d3cfbd8daae9557` |
| `re71a735/recheck_1a_out.txt` | [re71a735] `evidence/peer/recheck_1a_out.txt` | M-natural-integrals | `415843f91a3ba2930dbd2a9e11eae46289472d7d1e4e912a0a8636ffe38b83f6` |
| `re71a735/run_flq_checks.py` | [re71a735] `evidence/peer/run_flq_checks.py` | four-families | `307506c8508aa918db1458034ca66751f7fd16d6931cf75182c4a8092fea81b3` |
| `re71a735/thmC_float.py` | [re71a735] `evidence/peer/thmC_float.py` | four-families | `32cab62a1b6da0aa6c7b04ef3329edee50df718bd6e800733ede2a78a7ea69cd` |
| `re71a735/window_checks.py` | [re71a735] `evidence/peer/window_checks.py` | four-families | `10032646bf49101fafb356b43be08817008efcd78b2d5b4111f62f3dc9bc2da8` |
| `re71a735/window_checks_out.txt` | [re71a735] `evidence/peer/window_checks_out.txt` | four-families | `0de2be56040f3ff799bb65e777da158af6cd23dbcb26125ecef2873335c27891` |
| `re79cb4d/crosscheck_counts.py` | [re79cb4d] `evidence/peer/crosscheck_counts.py` | crossing-small-n | `f4a477031cc14457a57ebb10039547c74c48a3d1070ba6f4e180937ad7866d9a` |
| `re79cb4d/n1000_summary.json` | [re79cb4d] `evidence/peer/n1000_summary.json` | crossing-small-n | `3ba6a001ac3b2b5650c3b8a2626b03786243e50d96c6eb5a66568bb75a478763` |
| `re79cb4d/n1000_summary.py` | [re79cb4d] `evidence/peer/n1000_summary.py` | crossing-small-n | `1aeb20e596fd21f000401627c7e3d0853a85dc99da19121469e0b6b0c33b9ae3` |
| `re79cb4d/right_counts.py` | [re79cb4d] `evidence/peer/right_counts.py` | crossing-small-n | `121af724beab70e26c1a97e508de6beedaacd7f665341ebdfda4a58f7edc81e6` |
| `re79cb4d/right_counts2.py` | [re79cb4d] `evidence/peer/right_counts2.py` | crossing-small-n | `a07edd451907c7f141bc5609044ef9319abd732afee24a9dc806fb4d87c6cce2` |
| `rf451d83/aint_kfix.jsonl` | [rf451d83] `review/evidence/kappa/aint_kfix.jsonl` | xcert-partAB | `3e9f2a1eb539633caf882570059b2325dcbb5e0f704c9e9258880977d71f3667` |
| `rf451d83/asym.py` | [rf451d83] `evidence/code/asym.py` | xcert-partAB | `65dc3e2dd3a38d2ded6597fbf9bb05db6df2b08a63fd188b26370842e8f3beea` |
| `rf451d83/core.py` | [rf451d83] `evidence/code/core.py` | xcert-partAB | `1250af4d4ec02a8cfe9527edbffa8a254e72fea6297d06882625aad21502d7ca` |
| `rf451d83/envelope2.py` | [rf451d83] `evidence/code/envelope2.py` | xcert-partAB | `f12c96a85362ad335684597e10b236759eedb99ff041cb459d26a8115b6e24f9` |
| `rf451d83/envelope_int.py` | [rf451d83] `evidence/code/envelope_int.py` | xcert-partAB | `0ec3514baa45a7f8e736ba2814b5685b1f571742f817baf64ddf80181127a2c5` |
| `rf451d83/envelope_int_fix.py` | [rf451d83] `review/evidence/auditA23/envelope_int_fix.py` | xcert-partAB | `0cea761aff8a22d592d020fb21f8a20dadc97e49ef91a6c6a3066cf491d3ba57` |
| `rf451d83/envelope_walk2.jsonl` | [rf451d83] `evidence/results/partApp2/envelope_walk2.jsonl` | xcert-partAB | `e44464689ebbb9c39cfb4e0593334e16f14706283e3848c7cffd46058d4fc478` |
| `rf451d83/envelope_walk2_low.jsonl` | [rf451d83] `evidence/results/partApp2/envelope_walk2_low.jsonl` | xcert-partAB | `edb1940d9c2667f9bf30b981c8ea05c1f45a260601eef7482cf22329067ad1e0` |
| `rf451d83/envelope_walk2_mid.jsonl` | [rf451d83] `evidence/results/partApp2/envelope_walk2_mid.jsonl` | xcert-partAB | `fb19700054f41c7156acbdb2230f776067b14b1e8ae91de151ab8248ccda3d36` |
| `rf451d83/evidence/peer/fixed_App23/asym.py` | [rf451d83] `evidence/peer/fixed_App23/asym.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `65dc3e2dd3a38d2ded6597fbf9bb05db6df2b08a63fd188b26370842e8f3beea` |
| `rf451d83/evidence/peer/fixed_App23/envelope2.py` | [rf451d83] `evidence/peer/fixed_App23/envelope2.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `71e982102c0e051c9e5f7f2fed02a2942c808209b8b0534491934590696d6b75` |
| `rf451d83/evidence/peer/fixed_App23/envelope_int.py` | [rf451d83] `evidence/peer/fixed_App23/envelope_int.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `f01f190f3af55c9cfa8176acece9d6820a3a8368287d8678e9d03e56d86150bc` |
| `rf451d83/evidence/peer/fixed_App23/lemmaG.py` | [rf451d83] `evidence/peer/fixed_App23/lemmaG.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `cbe3b165efdfb0a6ad34ccbd800c416c07d9501c9a0dae8383c1cfbebcb3b83c` |
| `rf451d83/evidence/peer/fixed_App23/rerun_env.py` | [rf451d83] `evidence/peer/fixed_App23/rerun_env.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `6e0e06df99019dbfb3bfb8c5909bfdff9be8b488e22b7f3ed371942d2918f2ad` |
| `rf451d83/evidence/peer/fixed_App23/rerun_env_0.jsonl` | [rf451d83] `evidence/peer/fixed_App23/rerun_env_0.jsonl`(패턴 `evidence/peer/fixed_App23/rerun_env_*.jsonl`) | xcert-partAB | `2ef661074fbbd0f3ee76de294e6b209e5c7b08762f5396ae4f8b3289ee071a90` |
| `rf451d83/evidence/peer/fixed_App23/rerun_env_0.jsonl` | [rf451d83] `evidence/peer/fixed_App23/rerun_env_0.jsonl`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `2ef661074fbbd0f3ee76de294e6b209e5c7b08762f5396ae4f8b3289ee071a90` |
| `rf451d83/evidence/peer/fixed_App23/rerun_env_0.log` | [rf451d83] `evidence/peer/fixed_App23/rerun_env_0.log`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `6f04faddfcdadead9069dac6db55de62a32407d95f1282745af0c6d760aaaef2` |
| `rf451d83/evidence/peer/fixed_App23/rerun_env_1.jsonl` | [rf451d83] `evidence/peer/fixed_App23/rerun_env_1.jsonl`(패턴 `evidence/peer/fixed_App23/rerun_env_*.jsonl`) | xcert-partAB | `87d5d2cb6e0d19ad740f8fd7d0e1776fbfa16c8837f9f38a8cdf28af67a82f69` |
| `rf451d83/evidence/peer/fixed_App23/rerun_env_1.jsonl` | [rf451d83] `evidence/peer/fixed_App23/rerun_env_1.jsonl`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `87d5d2cb6e0d19ad740f8fd7d0e1776fbfa16c8837f9f38a8cdf28af67a82f69` |
| `rf451d83/evidence/peer/fixed_App23/rerun_env_1.log` | [rf451d83] `evidence/peer/fixed_App23/rerun_env_1.log`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `9ba433a474fd31b07e6db280c39150e61d5adfa5cb1b4fda7b265950a2258be6` |
| `rf451d83/evidence/peer/fixed_App23/sigma_bracket.py` | [rf451d83] `evidence/peer/fixed_App23/sigma_bracket.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `de1782e194ee0cf883ce0178c76733083180c31d76e962e88f72238576085ccd` |
| `rf451d83/evidence/peer/fixed_App23/tables.py` | [rf451d83] `evidence/peer/fixed_App23/tables.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `f30a0497937e3f2d352a6cb14ae0099dcbf2081b39e003852999a34aed7b671d` |
| `rf451d83/evidence/peer/fixed_App23/tables_cache.npz` | [rf451d83] `evidence/peer/fixed_App23/tables_cache.npz`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `bd1f82617585036e2dd2814a9859fe365715fe9057dadcb674f5156bc9145be9` |
| `rf451d83/evidence/peer/fixed_App23/tail_lemma.json` | [rf451d83] `evidence/peer/fixed_App23/tail_lemma.json`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `05611b2c24cd22cac56b2984e9558f991c957f6fd5451bcec850db73551ad6e7` |
| `rf451d83/evidence/peer/fixed_App23/tail_lemma.py` | [rf451d83] `evidence/peer/fixed_App23/tail_lemma.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `5493709c0537f6c099c4db4e271fd3493059fb45e926395f981249da0eed72b2` |
| `rf451d83/evidence/peer/fixed_App23/tail_lemma_patched.out` | [rf451d83] `evidence/peer/fixed_App23/tail_lemma_patched.out`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `5146702731d3fe4aa58822ea71c3ff531879a69b0d6e344d35cd1244aeb352f3` |
| `rf451d83/evidence/peer/fixed_App23/xcert.py` | [rf451d83] `evidence/peer/fixed_App23/xcert.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `636d3e802c248637762f8076fed08ac73f076a0b414c132408ab394d30c4f559` |
| `rf451d83/evidence/peer/fixed_App23/xcert_A.py` | [rf451d83] `evidence/peer/fixed_App23/xcert_A.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `6556daa99098d09fd684472d3e6c25e0f1bddcda362106d1d819e909fc4750ae` |
| `rf451d83/evidence/peer/fixed_App23/xcert_I.py` | [rf451d83] `evidence/peer/fixed_App23/xcert_I.py`(폴더 `evidence/peer/fixed_App23/`) | xcert-partAB | `da2820b3fb4ab46a350d70cda7a8a7d657c6876a7e74fdda8a362b91aaf4c031` |
| `rf451d83/evidence/peer/fixed_Upp/asym.py` | [rf451d83] `evidence/peer/fixed_Upp/asym.py`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `31e81cb342217fcf986efaabf0e49682cbecc5070c0c6680c96f7abf04f94a26` |
| `rf451d83/evidence/peer/fixed_Upp/lemmaG.py` | [rf451d83] `evidence/peer/fixed_Upp/lemmaG.py`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `cbe3b165efdfb0a6ad34ccbd800c416c07d9501c9a0dae8383c1cfbebcb3b83c` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_0.jsonl` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_0.jsonl`(패턴 `evidence/peer/fixed_Upp/rerun_fixed_*.jsonl`) | xcert-partAB | `a2c3c218a878068084512711d36477fb4969fc1a0514c8d77fc523f72320d8dd` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_0.jsonl` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_0.jsonl`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `a2c3c218a878068084512711d36477fb4969fc1a0514c8d77fc523f72320d8dd` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_0.log` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_0.log`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `1aabf49a36ee63756a3916cece9f81d61247d9c284d621965305a22d29e0fcf5` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_1.jsonl` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_1.jsonl`(패턴 `evidence/peer/fixed_Upp/rerun_fixed_*.jsonl`) | xcert-partAB | `64005f53f56e2e7dec1fbc6bfc6d7ea00d443116575e537387d7bf8f4c8993b4` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_1.jsonl` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_1.jsonl`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `64005f53f56e2e7dec1fbc6bfc6d7ea00d443116575e537387d7bf8f4c8993b4` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_1.log` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_1.log`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `67e3095b19e868bfbbdd04c82d50edc70d445201dab95e378008dadd2598798f` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_2.jsonl` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_2.jsonl`(패턴 `evidence/peer/fixed_Upp/rerun_fixed_*.jsonl`) | xcert-partAB | `e02843399869f99b00c663a4b3004f19ef3515f42334f7cc36ae8355e0c67795` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_2.jsonl` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_2.jsonl`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `e02843399869f99b00c663a4b3004f19ef3515f42334f7cc36ae8355e0c67795` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_fixed_2.log` | [rf451d83] `evidence/peer/fixed_Upp/rerun_fixed_2.log`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `ba4be52b4da8744c1ab844e7bb45eb83d56c68c8bfff817102944cb0404e594a` |
| `rf451d83/evidence/peer/fixed_Upp/rerun_walk.py` | [rf451d83] `evidence/peer/fixed_Upp/rerun_walk.py`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `c1aa8a6eb67e76b65c83a2dc5b9a17af733532f3f9bf8e752afe86fd8337d0ae` |
| `rf451d83/evidence/peer/fixed_Upp/sigma_bracket.py` | [rf451d83] `evidence/peer/fixed_Upp/sigma_bracket.py`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `de1782e194ee0cf883ce0178c76733083180c31d76e962e88f72238576085ccd` |
| `rf451d83/evidence/peer/fixed_Upp/xcert.py` | [rf451d83] `evidence/peer/fixed_Upp/xcert.py`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `636d3e802c248637762f8076fed08ac73f076a0b414c132408ab394d30c4f559` |
| `rf451d83/evidence/peer/fixed_Upp/xcert_A.py` | [rf451d83] `evidence/peer/fixed_Upp/xcert_A.py`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `6556daa99098d09fd684472d3e6c25e0f1bddcda362106d1d819e909fc4750ae` |
| `rf451d83/evidence/peer/fixed_Upp/xcert_I.py` | [rf451d83] `evidence/peer/fixed_Upp/xcert_I.py`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `da2820b3fb4ab46a350d70cda7a8a7d657c6876a7e74fdda8a362b91aaf4c031` |
| `rf451d83/evidence/peer/fixed_Upp/xcert_U.py` | [rf451d83] `evidence/peer/fixed_Upp/xcert_U.py`(폴더 `evidence/peer/fixed_Upp/`) | xcert-partAB | `24d03afd7834e0992c54ce28eeab8b570068688e96ba49dca297a6afd5df854d` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_a2.jsonl` | [rf451d83] `evidence/results/partA_int/xcertI_walk_a2.jsonl`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `602daab051b982b4962a227ed1b2bfbdc6898842ffa7d2802b7c2af2ff5ca896` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_a2.out` | [rf451d83] `evidence/results/partA_int/xcertI_walk_a2.out`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `5483fadf402bee26b1456265b36d62fba2bb777512a58df1acba2e4144ccb842` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_b3.jsonl` | [rf451d83] `evidence/results/partA_int/xcertI_walk_b3.jsonl`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `f8250c80a83bc4086d62fae086e1de5c35361de4b17db802615df347fb6110a0` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_b3.out` | [rf451d83] `evidence/results/partA_int/xcertI_walk_b3.out`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `40ed7f9ea5dfa9f8fc53d9e3ceca1a44ce9209a34e990b5b29b56ffc68419818` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c1.jsonl` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c1.jsonl`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `7b2cd8e048b76d013affab3fb1df6cbaa843bff29ff295dbd2adc28ebdf93335` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c1.out` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c1.out`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `b6f33c69d5e79c7588b9c385ba8ff551a349661223fa797ede2e869a586c6e8c` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c1a.jsonl` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c1a.jsonl`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `03aea365e995e12aee4c7898eb67bf8cf213924a0033e36cea916d3edb63851b` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c1a.out` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c1a.out`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `0b96bb40c8302b6049ed23afa540b98b3d6f89a34008c9f7d9525513c5295923` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c1b.jsonl` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c1b.jsonl`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `1bfb50a33711061ee8f7c34551e25183b7540c3d512594dbc1c60d70736d5d7b` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c1b.out` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c1b.out`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `bf2ed0d4b69def2f472022481318e1f925670fd808274c55548a7043fa5f57f0` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c2.jsonl` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c2.jsonl`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `96668f53d8890885629df85bfa45c4d7bb457bd3677969902a1a9878b865aa0d` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c2.out` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c2.out`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `22ab14082215014ae613cbb3c97f4e15ca472b3192f15b2e3f72f00e8b905a7a` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c2a.jsonl` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c2a.jsonl`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `de070fdfe16ace55e247295f9b917e5ef5c1e69634d6e66f1c42c6ba4756df1c` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c2a.out` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c2a.out`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `84d5cf7642f0013fd7004e8a45742857cc3fcae3b1a45a08b061bdb4ed00e2f5` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c2b.jsonl` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c2b.jsonl`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `17eb3b32bd6f9135a2a196db8343a933f3c46971b1209c42e4afd1e553a0edec` |
| `rf451d83/evidence/results/partA_int/xcertI_walk_c2b.out` | [rf451d83] `evidence/results/partA_int/xcertI_walk_c2b.out`(폴더 `evidence/results/partA_int/`) | xcert-partAB | `144c59aef7d2f43f3e8a6dc62d5458599b5ca141f1f81b9a33099cb597750a54` |
| `rf451d83/evidence/results/partB/log_m4r0.txt` | [rf451d83] `evidence/results/partB/log_m4r0.txt`(폴더 `evidence/results/partB/`) | xcert-partAB | `a987b705142e90e93dcf3b5ebc2c72baa1f9a7fddf0416103a8c1aed51e03bf5` |
| `rf451d83/evidence/results/partB/log_m4r1.txt` | [rf451d83] `evidence/results/partB/log_m4r1.txt`(폴더 `evidence/results/partB/`) | xcert-partAB | `c1424f3d43969362510ef8e39ae74c75f2ebcf98afc9af2482aa28f8e0b44acd` |
| `rf451d83/evidence/results/partB/log_m4r2.txt` | [rf451d83] `evidence/results/partB/log_m4r2.txt`(폴더 `evidence/results/partB/`) | xcert-partAB | `41f7744305986d28da81c4edda90aab574038e9f13196578c0d4c52a5a612fc1` |
| `rf451d83/evidence/results/partB/log_m4r3.txt` | [rf451d83] `evidence/results/partB/log_m4r3.txt`(폴더 `evidence/results/partB/`) | xcert-partAB | `4e8c1311e112aabf2e50efd36ea093cee97615bc17ae48746313194198f959ec` |
| `rf451d83/evidence/results/partB/log_r0.txt` | [rf451d83] `evidence/results/partB/log_r0.txt`(폴더 `evidence/results/partB/`) | xcert-partAB | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `rf451d83/evidence/results/partB/log_r0b.txt` | [rf451d83] `evidence/results/partB/log_r0b.txt`(폴더 `evidence/results/partB/`) | xcert-partAB | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `rf451d83/evidence/results/partB/log_r1.txt` | [rf451d83] `evidence/results/partB/log_r1.txt`(폴더 `evidence/results/partB/`) | xcert-partAB | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `rf451d83/evidence/results/partB/log_r1b.txt` | [rf451d83] `evidence/results/partB/log_r1b.txt`(폴더 `evidence/results/partB/`) | xcert-partAB | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `rf451d83/evidence/results/partB/xcert_501_5000_m4r0.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_m4r0.jsonl`(패턴 `evidence/results/partB/xcert_501_5000_*.jsonl`) | Q-fin-1130 | `653ab27b89eb2a815b8997fdd22b2acfefce835fd0803eeb33b215d4108c63a0` |
| `rf451d83/evidence/results/partB/xcert_501_5000_m4r0.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_m4r0.jsonl`(폴더 `evidence/results/partB/`) | xcert-partAB | `653ab27b89eb2a815b8997fdd22b2acfefce835fd0803eeb33b215d4108c63a0` |
| `rf451d83/evidence/results/partB/xcert_501_5000_m4r1.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_m4r1.jsonl`(패턴 `evidence/results/partB/xcert_501_5000_*.jsonl`) | Q-fin-1130 | `0c3b430978c66ac40db229b8ef63158c9b996633414d637d98e70ff5fc97dc0b` |
| `rf451d83/evidence/results/partB/xcert_501_5000_m4r1.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_m4r1.jsonl`(폴더 `evidence/results/partB/`) | xcert-partAB | `0c3b430978c66ac40db229b8ef63158c9b996633414d637d98e70ff5fc97dc0b` |
| `rf451d83/evidence/results/partB/xcert_501_5000_m4r2.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_m4r2.jsonl`(패턴 `evidence/results/partB/xcert_501_5000_*.jsonl`) | Q-fin-1130 | `7b24efd04e24306b588ad201507ad74669e2d47fa33efca2429456c392f1902a` |
| `rf451d83/evidence/results/partB/xcert_501_5000_m4r2.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_m4r2.jsonl`(폴더 `evidence/results/partB/`) | xcert-partAB | `7b24efd04e24306b588ad201507ad74669e2d47fa33efca2429456c392f1902a` |
| `rf451d83/evidence/results/partB/xcert_501_5000_m4r3.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_m4r3.jsonl`(패턴 `evidence/results/partB/xcert_501_5000_*.jsonl`) | Q-fin-1130 | `5ad3b675f9c5213c4e817a6a2cd6d5361f0da3084e44fea8ba54440eff6315ba` |
| `rf451d83/evidence/results/partB/xcert_501_5000_m4r3.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_m4r3.jsonl`(폴더 `evidence/results/partB/`) | xcert-partAB | `5ad3b675f9c5213c4e817a6a2cd6d5361f0da3084e44fea8ba54440eff6315ba` |
| `rf451d83/evidence/results/partB/xcert_501_5000_r0.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_r0.jsonl`(패턴 `evidence/results/partB/xcert_501_5000_*.jsonl`) | Q-fin-1130 | `354e1e4f9afeedcd0923c85832c58db3ae7f0a22d91db2a0ebb72e9099714487` |
| `rf451d83/evidence/results/partB/xcert_501_5000_r0.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_r0.jsonl`(폴더 `evidence/results/partB/`) | xcert-partAB | `354e1e4f9afeedcd0923c85832c58db3ae7f0a22d91db2a0ebb72e9099714487` |
| `rf451d83/evidence/results/partB/xcert_501_5000_r1.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_r1.jsonl`(패턴 `evidence/results/partB/xcert_501_5000_*.jsonl`) | Q-fin-1130 | `643619fb039215e796495f3f2bb010f397a83cc11cf41d8c80a12c54494b4592` |
| `rf451d83/evidence/results/partB/xcert_501_5000_r1.jsonl` | [rf451d83] `evidence/results/partB/xcert_501_5000_r1.jsonl`(폴더 `evidence/results/partB/`) | xcert-partAB | `643619fb039215e796495f3f2bb010f397a83cc11cf41d8c80a12c54494b4592` |
| `rf451d83/evidence__peer__fixed_App23__envelope_int.py` | [rf451d83] `evidence/peer/fixed_App23/envelope_int.py` | xcert-partAB | `f01f190f3af55c9cfa8176acece9d6820a3a8368287d8678e9d03e56d86150bc` |
| `rf451d83/kappa_fix_exact.py` | [rf451d83] `review/evidence/kappa/kappa_fix_exact.py` | xcert-partAB | `eeb257b0906ebc2823c914a4d255417f16090859376f85d1e5d2dd686f2442e8` |
| `rf451d83/lemmaG.py` | [rf451d83] `evidence/code/lemmaG.py` | xcert-partAB | `cbe3b165efdfb0a6ad34ccbd800c416c07d9501c9a0dae8383c1cfbebcb3b83c` |
| `rf451d83/make_tables.py` | [rf451d83] `evidence/code/make_tables.py` | xcert-partAB | `9442d21ab2429bc7f0c69ec351d1193486119054658348a6e0171c7ebac602e2` |
| `rf451d83/near_all.jsonl` | [rf451d83] `review/evidence/auditA23/near_all.jsonl` | xcert-partAB | `0b16654c7f560836ffce606cbe49327d63fae3d857e7171cda265275bc4e541a` |
| `rf451d83/partB_rerun.jsonl` | [rf451d83] `evidence/peer/partB_rerun.jsonl` | xcert-partAB | `c7e040f6897840035f5d0bc36260ce7d6591fd3f4f95ff3a19161f6157bc6650` |
| `rf451d83/report.md` | [rf451d83] `evidence/producer/report.md` | xcert-partAB | `ce57549f55ee5c308a184b0f10290e79f929235a61eb7bce1b1f785bf38e5597` |
| `rf451d83/rerun_kfix.jsonl` | [rf451d83] `review/evidence/auditB/rerun_kfix.jsonl` | xcert-partAB | `ac15ebade4ff28e23fc80cb291d8676cf9afa42b866615b4897d28ed1d5e3941` |
| `rf451d83/sigma_bracket.py` | [rf451d83] `evidence/code/sigma_bracket.py` | xcert-partAB | `de1782e194ee0cf883ce0178c76733083180c31d76e962e88f72238576085ccd` |
| `rf451d83/tables.py` | [rf451d83] `evidence/code/tables.py` | xcert-partAB | `f30a0497937e3f2d352a6cb14ae0099dcbf2081b39e003852999a34aed7b671d` |
| `rf451d83/tail_lemma.json` | [rf451d83] `evidence/results/partApp3/tail_lemma.json` | xcert-partAB | `1a65f3bd9ed34b554dfa2ea71da1cbe80396adbe3acf34917a14ae0f1de688de` |
| `rf451d83/tail_lemma.out` | [rf451d83] `evidence/results/partApp3/tail_lemma.out` | xcert-partAB | `5146702731d3fe4aa58822ea71c3ff531879a69b0d6e344d35cd1244aeb352f3` |
| `rf451d83/tail_lemma.py` | [rf451d83] `evidence/code/tail_lemma.py` | xcert-partAB | `56be2aabfda173c71ab6072dc0deeea04983359cd3883368d2de64c06924669f` |
| `rf451d83/truth.py` | [rf451d83] `evidence/peer/truth.py` | xcert-partAB | `2d478a24b9769ad9e44d19658e576d327726a579c11d3f8bcbef86b2c4ac88e4` |
| `rf451d83/truth_1000_2000.jsonl` | [rf451d83] `evidence/peer/truth_1000_2000.jsonl` | xcert-partAB | `bd735d4dbc25185177ec81d0f8770cac63b4d1704c818f3df46b366433fa7fda` |
| `rf451d83/truth_501.jsonl` | [rf451d83] `evidence/peer/truth_501.jsonl` | xcert-partAB | `a418080f72b64a43b2d8cc581e4f32154489b7a7d3ace90011772682b6ae0c16` |
| `rf451d83/xcert.py` | [rf451d83] `evidence/code/xcert.py` | xcert-partAB | `636d3e802c248637762f8076fed08ac73f076a0b414c132408ab394d30c4f559` |
| `rf451d83/xcert_I.py` | [rf451d83] `evidence/code/xcert_I.py` | xcert-partAB | `da2820b3fb4ab46a350d70cda7a8a7d657c6876a7e74fdda8a362b91aaf4c031` |
| `rf451d83/xcert_U.py` | [rf451d83] `evidence/code/xcert_U.py` | xcert-partAB | `24d03afd7834e0992c54ce28eeab8b570068688e96ba49dca297a6afd5df854d` |
| `rfc69320/peer_closed_form_constants.out` | [rfc69320] `evidence/peer/peer_closed_form_constants.out` | stored-table-check | `d669503014b0c1471b4cf11b649f4d102f7a3e83eddee05daf435b95da20393d` |
| `rfc69320/peer_closed_form_constants.py` | [rfc69320] `evidence/peer/peer_closed_form_constants.py` | stored-table-check | `37db3fc569c950537bbcf9a1c149f270413b1001cc98d1a850b369c554818087` |
| `rfc69320/peer_constants.out` | [rfc69320] `evidence/peer/peer_constants.out` | stored-table-check | `aab7337f9148ab89c6ccb511fe12d91842b60bca474ef096eafba4e35b63b4a2` |
| `rfc69320/peer_constants.py` | [rfc69320] `evidence/peer/peer_constants.py` | stored-table-check | `ddc407fbf4d0206ff4daeacd9abe3b9d4ffdb1ae502a6b0d39b25989d6e37f25` |
| `rfc69320/peer_iv_sanity.out` | [rfc69320] `evidence/peer/peer_iv_sanity.out` | stored-table-check | `3d5976e4077a5fccf155e66b6492afe844f3f113676106ca4c587d5f0b8e6d51` |
| `rfc69320/peer_numeric.out` | [rfc69320] `evidence/peer/peer_numeric.out` | stored-table-check | `6b91f5cf46e176762f1bdde3959f3d538fec38a4253cf999c2e97383447dbded` |
| `rfc69320/peer_numeric.py` | [rfc69320] `evidence/peer/peer_numeric.py` | stored-table-check | `79c94d1606081cf2b63a690371beafdb984832a413bed107b8b716d6252874a7` |
| `rfc69320/peer_table_geometry.out` | [rfc69320] `evidence/peer/peer_table_geometry.out` | stored-table-check | `7127173927990f6f49a85e35df30fda1d10e2ebefb285a30bcd0e9cf97cdfe29` |
| `rfc69320/peer_table_vs_closed_form.out` | [rfc69320] `evidence/peer/peer_table_vs_closed_form.out` | stored-table-check | `554f192778addbdb7b03b6e5ba7317201c8ee82ff5be2afcdb2fa5d31afebd33` |
| `rfc69320/peer_table_vs_closed_form.py` | [rfc69320] `evidence/peer/peer_table_vs_closed_form.py` | stored-table-check | `05a15f254b1a9934f4f43b97f3e9ef05ffb3d015c85bb074f4dd8ccfb45ef8a2` |
| `rfc69320/rv_code_exact.out` | [rfc69320] `review/evidence/rv_code_exact.out` | stored-table-check | `14bea9759dc4a321052c3cec5ce7e6d7d17d81522427bd690b2bd45e245dae12` |
| `rfc69320/rv_code_exact.py` | [rfc69320] `review/evidence/rv_code_exact.py` | stored-table-check | `857fde8471dd25dc66d752b2c0ee373db15bf29eeb1a9f52c3fb32ce2b7e2c7b` |
| `rfc69320/rv_constants.out` | [rfc69320] `review/evidence/rv_constants.out` | stored-table-check | `8c7abbeddd464cb0ee214b3d9f64aff4af4012715c1e8201411620d2220015bd` |
| `rfc69320/rv_constants.py` | [rfc69320] `review/evidence/rv_constants.py` | stored-table-check | `567293b5b78b9baa36f8d9157b3ca2353efea13416fdc808a71ec02548f833aa` |
| `rfc69320/rv_table_check.out` | [rfc69320] `review/evidence/rv_table_check.out` | stored-table-check | `016bb2212724670e687221ab4e3c8394b7c838e2209f0b5ac18303ad8ad6d61e` |
| `rfc69320/rv_table_check.py` | [rfc69320] `review/evidence/rv_table_check.py` | stored-table-check | `922b43e3a9043963191ee6d9f66f0f5117f40bafcd20ddaf80b824ae68527110` |

파일마다 원본의 SHA-256을 적었다. 복사 뒤 내용을 고치지 않았다.
