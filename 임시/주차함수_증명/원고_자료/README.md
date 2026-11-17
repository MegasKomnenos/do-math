# 원고 자료 묶음

## 처음 돌려 볼 것

아래 두 검산은 각각 몇 초 안에 끝나고, 출력에 오른쪽 열의 문자열이 나오면 부록 D의 해당 값과 같다. `<묶음>`은 이 폴더(`원고_자료`)의 경로다. 시간은 이 기계(4코어, 다른 계산과 공유)에서 잰 것이다.

| 명령 | 부록 D 항목 | 기대 출력 | 시간 |
|---|---|---|---|
| `python -I <묶음>/세션_재계산/logconcavity_n80/lc_n80.py` | `D.{{D:logconcavity-failure-n80}}` | `first failure: (n, l) = (80, 40)`, `three integers equal to appendix D (D.logconcavity-failure-n80): True` | 1초 |
| `python -I <묶음>/세션_재계산/zeta_constants/zeta_iv.py 4000 4000` | `D.{{D:zeta-constants}}` | `z_{3/2}  in [2.6123753485619…, 2.6123753487472…]  subset of [2.61237, 2.61238]: True` 외 둘(`z_{-1/2}`, `z_{1/2}`) | 4–5초 |

첫 줄은 행의 로그오목성이 처음 깨지는 자리($n=80$, $\ell=40$)를 마지막 차 재귀의 정확 정수로 다시 만들고, 세 정수 $b_{80,39}$, $b_{80,40}$, $b_{80,41}$을 부록 D 결과 줄의 값과 비교한다. 무거운 계산의 축소판까지 차례로 돌리려면 `python -I <묶음>/빠른_확인.py`(아래 「재실행표와 빠른 확인」)를 쓴다.

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
- **실행 방식.** 모든 스크립트는 `python -I <경로>`로 돌린다. `-I`(격리 모드)는 환경 변수와 사용자 site-packages를 읽지 않으며, Python 3.11부터는 스크립트의 폴더도 `sys.path`에 넣지 않는다. 그래서 이 글의 재계산 스크립트 가운데 같은 폴더의 모듈을 읽는 것은 스스로 `__file__`의 폴더를 `sys.path`에 넣는다. 기록 코드 사본(`r…/` 폴더)은 바이트 사본이라 그 처리가 없으므로, 같은 폴더의 모듈을 읽는 사본(예: `rce3dc75/vertical_exact_constant.py`, `r13b0b8f/indep_cert2.py`)은 `python -E -s <경로>`로 돌린다(`-I`에서 `-P`만 뺀 것이라 환경 변수와 사용자 site-packages는 여전히 읽지 않고, 스크립트의 폴더만 `sys.path`에 들어간다). `빠른_확인.py`는 각 명령을 새 임시 폴더에서 `python -I -B`로 돌려 묶음 안에 `__pycache__`나 출력 파일을 만들지 않는다.

**다른 환경에서 돌려 본 결과.** WSL의 Ubuntu 20.04에서 `빠른_확인.py`를 돌리려 했으나, 네 번의 시도가 모두 가상 머신을 띄우는 단계에서 시간 초과로 끝났다(오류 코드 `Wsl/Service/CreateInstance/CreateVm/ERROR_TIMEOUT`; WSL 3.0.5.0, 커널 6.18.58.1-1; `wsl --shutdown` 뒤에도 같음). 그래서 리눅스에서의 실행은 확인하지 못했다. 대신 같은 기계에서 다음을 확인했다.

| 환경 | 결과(`python -I -B 빠른_확인.py`, 기본 32개) |
|---|---|
| Python 3.12.10, numpy 2.5.2, mpmath 1.3.0(기준 환경) | 32개 모두 일치, 520초 |
| Python 3.11.9, numpy 2.3.5, mpmath 1.3.0(이 기계에 따로 설치된 판) | 32개 모두 일치, 419초 |
| Python 3.9.25, numpy 1.26.4, mpmath 1.3.0(`uv`로 만든 가상 환경; WSL에서 시도하려던 `numpy<2` 조합) | 30개 일치, 2개 불일치(456초) |
| Python 3.8.20, numpy 1.24.4, mpmath 1.3.0(같은 방식) | 21개 일치, 11개 불일치(431초) |

네 줄은 모두 그 전의 항목 구성(기본 32개)에서 잰 것이다(기준 환경의 줄은 자기일관 상수 (4)의 합 항목을 빼고 모멘트 판정 항목을 열 $k=840$으로 바꾼 뒤 다른 계산과 코어를 나눠 쓰며 다시 잰 것). 지금의 구성은 기본 14개(`--all`도 같다 — 긴 항목이 없다)이고, 기준 환경에서 2026-11-17에 돌린 결과는 14개 모두 일치, 99초(다른 계산과 코어를 나눠 쓴 상태; 60초를 넘는 항목이 없어 `--fast`도 같은 14개다).

불일치는 모두 수치가 달라서가 아니라 스크립트가 중간에 멈춘 것이다. 원인은 둘이었고, 지금의 항목 구성에 남은 것은 하나다.

- **`math.nextafter`.** Python 3.9에 들어온 함수라 3.8에서는 `band_boxes/ivbox_lib.py`(띠 상자가 이것을 쓴다)를 비롯해 이 함수를 쓰는 스크립트를 읽는 단계에서 멈춘다. 3.8의 불일치 11개 가운데 9개다.

따라서 이 묶음의 파이썬 스크립트에는 Python 3.9 이상이 필요하다. 기준 환경(`requirements.txt`)의 판을 쓰는 것이 가장 안전하다.

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
| `r19de912/qr_cert2.c`(기록; 같은 기록의 `qr_cert3.c`도 같은 구조) | `D.{{D:exact-n20000}}` (ㄹ) | `cl /nologo /O2 /openmp /W3 qr_cert2.c`(기록 `build.bat`) | `icert.c`와 같다(`_umul128` 이식 필요, `-O2 -ffp-contract=off -fopenmp`) |
| `r15df76b/leftcert.c`(기록; `leftcert_build1.c`·`leftcert_build2.c`는 빌드 이력판) | `D.{{D:exact-n20000}}` (ㄴ) | `clang -O3 -march=native -D_CRT_SECURE_NO_WARNINGS`(Visual Studio 2022 동봉 clang 19.1.5; `unsigned __int128` 때문에 MSVC `cl`은 불가) | `-O2 -ffp-contract=off`. 판정은 정수 비교이고 부동소수는 진단 출력에만 쓰인다 |
| `pcertv.c`(기록 [r15df76b]; 이 묶음의 사본 `r15df76b/pcertv.c`) | `D.{{D:exact-n20000}}` | `clang -O2 -mavx2 -ffp-model=strict` | `gcc -O2 -mavx2 -ffp-contract=off -frounding-math`(`fesetround`로 방향 반올림) |
| `icert_rows.c`(기록 [r6b37c7e]·[r475ada3]; 이 묶음의 사본 `r475ada3/icert_rows.c`) | `D.{{D:band102-integer}}` | `clang -O2 -D_CRT_SECURE_NO_WARNINGS`(MSVC 19 환경의 clang 19.1.5) | `-O2 -ffp-contract=off`. `unsigned __int128`을 쓰는 정수 전용 프로그램이고 MSVC `cl`로는 빌드되지 않는다 |
| `lmcert_sweep.c`(기록 [r10ff8c2]; 이 묶음의 사본 `r10ff8c2/lmcert_sweep.c`) | `D.{{D:moment-certification}}` | MSVC 19.44 `cl /O2 /fp:precise`, 소스 안 `#pragma fp_contract(off)` | `-O2 -ffp-contract=off`. 반올림-최근접 binary64와 사전 오차 해석이므로 반올림 모드는 바꾸지 않는다 |

**GCC 시험.** WSL이 뜨지 않아 리눅스에서는 빌드하지 못했다. 대신 같은 기계의 MSYS2 GCC 16.2.0(대상 `x86_64-pc-cygwin`)으로 `c50iv.c`를 소스 수정 없이 위 표의 GCC 줄 옵션에 `-fno-fast-math`를 더해 빌드했고, 역어셈블에 `vfmadd` 명령은 없었다. 이 빌드로 두 실행을 했다.

- **$n\le60$ 실행.** `run_commands.txt` 3단계의 `60 5 2 59 16 2 t60 <표 폴더> -dumpall`이다. `exact_small.py`의 대조 출력은 구간 927개가 모두 정확 정수를 담는다고 보고했고, MSVC 빌드의 `runs/t60_exact_check.txt`와 바이트 단위로 같았다. 행 파일은 줄 끝 문자만 다르다.
- **$n\le20000$ 재인증의 탐침 B.** `20000 5 19522 19585 64 1 c20_probeB <표 폴더> -probe 19522 19523 19524`이다. 구간 덤프(1,431개 값)가 MSVC 빌드의 `runs/c20_probeB_dump.bin`과 비트 단위로 같았다.

기록의 C 프로그램은 다시 빌드해 보지 않았다.

## 재실행표와 빠른 확인

- **`재실행표.md`.** 부록 D의 항목마다 스크립트, 실행 명령, 기대 출력, 출력 파일과 SHA-256, 실행 시간, 산술 등급, 재실행 여부를 한 줄로 적은 대응표다. `scripts/_gen_재실행표.py`가 부록 D와 이 README의 표에서 만들며, 다시 돌리면 갱신된다. 아직 끝나지 않은 계산이 걸린 항목이 있으면 그 칸을 「(진행 중)」으로 둔다(지금은 없다; 끝나야 아는 값은 `[Dn:이름]` 자리표시자).
- **`빠른_확인.py`.** 각 항목의 축소판을 차례로 돌려 기대 출력(핵심 수치)과 맞춰 보고 한 줄씩 일치/불일치를 적는다. 축소판은 원 계산의 한 부분이다. 예를 들어 앞쪽 $q$ 몇 개, 최솟값이 나온 상자 하나, 열 몇 개를 돌리며, 원래 짧은 계산은 전체를 돌린다. 기대 문자열은 축소판을 한 번 돌려 얻은 값이고, 원 출력 파일의 해당 줄과 같음을 확인했다. binary64 방향 반올림으로 하계를 계산하는 항목(열 $2001$·$3130$의 한 걸음 판정)은 합산 순서나 FMA 사용에 따라 하계의 마지막 표시 자리가 환경마다 다를 수 있으므로, 판정 `True`와 함께 두 하계를 기대값과 상대 $10^{-5}$ 안에서 견준다. `--list`는 항목 목록, `--fast`는 60초를 넘는 항목을 뺀다. C 프로그램 항목 둘은 빌드된 `세션_재계산/c50_iv/c50iv.exe`(Windows x64)를 부른다. 기본 실행(14개)은 기준 환경에서 99초에 모두 일치했다(2026-11-17; 다른 계산과 코어를 나눠 쓴 상태). 긴 항목(`--all`에서만 도는 것)은 지금의 구성에 없다.
- **축소 인자.** 무거운 스크립트는 대부분 범위 인자가 이미 있다. 출력 파일을 스크립트 폴더에 쓰던 다음 스크립트에는 `--quick` 옵션(출력을 현재 폴더에 쓴다)이나 모드를 더했고, 옵션을 주지 않은 기본 실행의 동작과 출력은 바뀌지 않았다.
  - `window_mass_env/cert_Cb_iv.py`, `window_mass_env/cert_interval_iv.py`: `--quick`.
  - `r030ffae_window/work/cert_Cb_range.py`: `--quick`. 입력을 파일 자신의 폴더에서 읽고 결과 JSON을 현재 폴더에 쓴다. 이 파일은 더 이상 바이트 사본이 아니다.

## 세션이 만든 수정판(세션_재계산/)

`세션_재계산/`은 이 글을 쓴 세션이 부록 D 항목의 독립 재계산으로 만든 코드·입력·출력이다(기록의 파일이 아니라 세션이 만든 것). 아래 표가 파일과 SHA-256이고, 표 뒤의 문단이 폴더별 설명이다.

| 경로 | SHA-256 |
|---|---|
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
| `세션_재계산/band_boxes/band_iv.py` | `58ace9e9c71dbb91d528ce7c9a025f601883e3fedeea19f44d7fe2ab45429cad` |
| `세션_재계산/band_boxes/band_result.txt` | `6a78d14f536e4124340f179fcbba3c4322d2cd554ecccff5bac1523eed29aced` |
| `세션_재계산/band_boxes/band_summary.py` | `30e56358f9fec897fb835bab34956b33be10625d7604f0c418998fd1163fca27` |
| `세션_재계산/band_boxes/box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.json` | `b1bca8298e8e01fc1816a9dd1ca1f15f93a6b48db9a362bade3c86a0a4d2c3b3` |
| `세션_재계산/band_boxes/box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.json` | `a2ca8c6a1348dab72b8d6ef547dc25113c75730f611870185d958df1a7dc2abd` |
| `세션_재계산/band_boxes/box_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.json` | `5f415fbd69bff5e01054c7d31c7c5c5af3d40b3866580961f22e00eb43c110de` |
| `세션_재계산/band_boxes/box_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.json` | `13ee21dc9667661408013d2019fbaaebbb41f47b0f93ee0052339931b2d12138` |
| `세션_재계산/band_boxes/compare_record.py` | `8f94619ba96abe12dd7be43fffdbbee17d89f3d76eff634d18146c3c8db0f029` |
| `세션_재계산/band_boxes/compare_record_out.txt` | `f9a45d11b8f11a16b3cfd9ed9ad1cf55b79e367c6a4982bad327719f3d553b51` |
| `세션_재계산/band_boxes/log_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.txt` | `8f23e4e1565a141442a301cfc092e1b95f71ecef2deeeebd00f9461e101e585e` |
| `세션_재계산/band_boxes/log_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.txt` | `37802894f7464cd12e7269b35c98471899fb7b0640c2b4a3d3ac07f29fafde47` |
| `세션_재계산/band_boxes/log_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.txt` | `52940ff8b4d0c2962b794725dcf9dfa60d896a6a127ab5f760d366ce19c66cfa` |
| `세션_재계산/band_boxes/log_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.txt` | `d5a267f7123a971cfbaab080c3d3697bf8699cd6efcfb4c9f20ae22f51b917fa` |
| `세션_재계산/band_boxes/run_all.sh` | `a748478f59a4bdb2a9bb8051e1061a83f26ac79513e05826299e7e13b8eb6f53` |
| `세션_재계산/band_boxes/tail_H_T12-25_k6668.txt` | `78ab06c7df2fcd10302d88b42900adfa23954d626c25ad80e9c5c535d48ee5b2` |
| `세션_재계산/window_mass_env/cert_Cb_iv.py` | `f5571b9bb9b776030127b7217e40d27e34ea34c660d8a24a7253340083a76ed9` |
| `세션_재계산/window_mass_env/cert_Cb_iv_out_1_2280.txt` | `722ba85fe918fe3374644b046f29fa86ec41f21224d538876190d0f672a76862` |
| `세션_재계산/window_mass_env/cert_Cb_iv_out_2280_3000.txt` | `abbf5befcc90d2fa84e72716de0b15fe8b9acec421c2f69d74d8d9391e9f2267` |
| `세션_재계산/window_mass_env/cert_Cb_iv_result_1_2280.json` | `acfcbbf03dff637b3ef0465ccabef28135d7d4f8b75838f4d8611e66b82a74e4` |
| `세션_재계산/window_mass_env/cert_Cb_iv_result_2280_3000.json` | `116247dc865033f243d3688ec8f1de81e4c95098541f17e44d825b392a90dc6f` |
| `세션_재계산/window_mass_env/cert_interval_iv.py` | `7e984da698b7f2659b9e57458b0affeb891ac230bdaf62619ebf2ec9beb15b95` |
| `세션_재계산/window_mass_env/cert_interval_iv_out.txt` | `873a8e1e388b509f763983268b35b1414c8d5b7f3da82b6e869807fbc0caa26b` |
| `세션_재계산/window_mass_env/cert_interval_iv_result.json` | `519b3951942ab1b8fda8d3d368857165d5e50ce9129100375ef29e64e90bc26e` |
| `세션_재계산/window_mass_env/check_table_iv.py` | `50d4f58b6ebfd42d99314fd7ea1394bb7fd52e62c0ddfee2d506af91132cca15` |
| `세션_재계산/window_mass_env/check_table_iv_out.txt` | `25ed03a972929fecaf7ca5093ed0803b65a9e810c36a214003ee991498d916e5` |
| `세션_재계산/window_mass_env/ia.py` | `8106bd07c5706bf495c74d03b6a6df3a8b0459f10491679bfcc037d1ef90f17c` |
| `세션_재계산/window_mass_env/summarize.py` | `19b7a064b313e8ff3897b32531baa1ba7a44a962a76a134dbeef072e2c95dc49` |
| `세션_재계산/window_mass_env/summarize_out.txt` | `0cac74a6c6282c86a3b3f350d310ad219a143c626683e61297f338a5d9c62d72` |
| `세션_재계산/window_mass_env/test_ia.py` | `dc529b08b7502d3ef78e619d6663ec85ab89ec26c5228b3c79edc8fd500563ce` |
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
| `세션_재계산/logconcavity_n80/lc_n80.py` | `0a195b472044a2468db2dfe897d070a079dcc9ef6c3167146e8442c5fa30b4a8` |
| `세션_재계산/logconcavity_n80/lc_n80_out.txt` | `61b9b0d36d942991838d9a261fe3fc2ba0be8f050a024e4a822dbe3b87726c14` |
| `세션_재계산/r030ffae_window/work/cert_Cb_range.py` | `68dce8b869b3ce49e16dced0002386be4900a6681eb72b4f1f97f56d46adbef3` |
| `세션_재계산/column_cert_iv/colcert_iv.py` | `904aba2d913e05a1688b9d8cf4cc3f80a9a0fc70bc58aa9410555806728adb06` |
| `세션_재계산/column_cert_iv/ivlib.py` | `5c9f30bbc004eb9e56d07663894a5356204838ced166914bc45d2f6aa333a5f3` |
| `세션_재계산/column_cert_iv/tables.py` | `9e014f10d9ea4899ead55b5dd3cc50bb9e9e243a6d51a7344048bdcd69772dc7` |
| `세션_재계산/column_cert_iv/summary.py` | `362369eaec3a604d9affbbf809f017e9da498c7fce08335d60ae51dec54f1af0` |
| `세션_재계산/column_cert_iv/crosscheck_review.py` | `784fa08ff11e3eb258298449c1fb770095fae43276deb8f490066339a67ef6af` |
| `세션_재계산/column_cert_iv/res_p0.jsonl` | `df0d5749ca95171f5db9f1a0010428d2cbb60482914776160279161c03e38a1b` |
| `세션_재계산/column_cert_iv/res_p1.jsonl` | `1a6ba31733bf2139725cc36ad8e367d26735d5ab1406de2f58645904bb5b3994` |
| `세션_재계산/column_cert_iv/res_ext_p0.jsonl` | `0d6d856230ef89adbdb378150c4d17d958466c195133f427514a55241ba499c7` |
| `세션_재계산/column_cert_iv/res_ext_p1.jsonl` | `f31f4569fafd83670af8dde60d7f10f0ebfff46761755e3a0248b9ba9feaeae0` |
| `세션_재계산/column_cert_iv/run_p0.log` | `5da97ac726ef84e9e66ebd9650b19e48f076127455c121912d62c192b5643542` |
| `세션_재계산/column_cert_iv/run_p1.log` | `13b159db96587a671e72b7152477c5efa2e338c1434c4b643a049688a1097a02` |
| `세션_재계산/column_cert_iv/run_ext_p0.log` | `9c85b4aae98ccd2a69019e840fc2181508fe68f27771b876f7e487c4cf34771f` |
| `세션_재계산/column_cert_iv/run_ext_p1.log` | `f8c7ef3cd8b9d1f7db4d156442259fdf9011e9486fb841b688e5d2580b4082c2` |
| `세션_재계산/column_cert_iv/summary_all_out.txt` | `8b1248be6e5953de80a165370e8b7d8cb21ab060f536b952e71d7aff9eb494f1` |
| `세션_재계산/column_cert_iv/summary_out.txt` | `839b7515197103cccd62e635ab1b45df4c2df2b39f05075e3db29ca1722ef844` |
| `세션_재계산/column_cert_iv/summary_ext_out.txt` | `a9968a67cf7c577a20dcd1eaed4e2be6007c5703d814e0695a07f0abbb767eae` |
| `세션_재계산/column_cert_iv/crosscheck_review_out.txt` | `44dcd354db92ffafb55ab97d67e2df4b00ab08053d17c84986f689bf447c2d69` |
| `세션_재계산/column_cert_iv/test_841.txt` | `bca53097a04768fce3ea515717f5e15fd314eafd37a77a4a8e828634b7b5f4a3` |
| `세션_재계산/column_cert_iv/test_1171.txt` | `76c6453d4a61251761ef54c0c0b0fd8d0dc31dea56b6c8d2d64ecfacda07c005` |
| `세션_재계산/column_cert_iv/test_2000.txt` | `fd74ac0d9a5c80ba079577bae41ea3dea7625cbed1f7bb236428f0249a1828dd` |
| `세션_재계산/column_cert_iv/tables_out.txt` | `a1222153291283b5b42e11d27d24bdef15d059df12f678c25361392c7c99f788` |
| `세션_재계산/moment_cert_iv/mcert_iv.py` | `edaf66b4da7b6e398bc388089fbfda8db8c08833bb078c9044eee12790282cd6` |
| `세션_재계산/moment_cert_iv/sweep_p0.jsonl` | `35a7571418e8676b5544a9fe6996ef5845112f132c1fdbe160684d1210fae310` |
| `세션_재계산/moment_cert_iv/sweep_p1.jsonl` | `ebc368d15af7246be28a383d2b858259fc5acc55ee2fe80c08970021626e3a4a` |
| `세션_재계산/moment_cert_iv/sweep_p0.log` | `a2128244ae858cbd41e291804c0bb4ce297e47fa0955326c6bfbe65074c6cfb0` |
| `세션_재계산/moment_cert_iv/sweep_p1.log` | `f94a55dafa47f5c0a530b61f4912b69ea122df6d8d6522fe3fe2cc6f6577ddf5` |
| `세션_재계산/moment_cert_iv/summarize.py` | `b0d3eb3d8e187becdaa70e5d454e7d8ec7477dc9d8d43d048a4468c7e19f21d0` |
| `세션_재계산/moment_cert_iv/summary.txt` | `1a23d1712a24edcc6c412eea890f8e0908bae90c0068ca54e5aacac00e3fefa7` |
| `세션_재계산/moment_cert_iv/compare.py` | `bd1625f90434e9157875b354537522f49c9bbf795f1083938b886b4eef2d70cc` |
| `세션_재계산/moment_cert_iv/compare_out.txt` | `e9ebd9ce22c1d66a32b342855fb00ecc839fc667364fbea83eae71b07727a142` |
| `세션_재계산/moment_cert_iv/compare_out.json` | `097c921869398ffbe24facb7321076a4512e641d757f0c9dd233610e64dd302b` |
| `세션_재계산/moment_cert_iv/test_exact.py` | `6785aa45ec4700318be3dd4051b710baa542a08fffcf6b14cd05dced08a44c4b` |
| `세션_재계산/moment_cert_iv/test_exact_out.txt` | `4a947810edafd3f9342acf815ce10b5a9023af694e3277ad12f13d563af77cc3` |
| `세션_재계산/moment_cert_iv/nM.py` | `8bfadc59da7fad9439385949aec22a0eaa4f59232c426928b659de0fc70ac93b` |
| `세션_재계산/moment_cert_iv/nM.json` | `51b38b5eca6deb47f61dabd342c94617fce720c90ceb6efa99f260b3a0a9515a` |
| `세션_재계산/moment_cert_iv/nM_out.txt` | `464a26d0caa84b1849ce6ccb658cf8f695d6af2a5ec122a8839b073646638ad4` |
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
| `세션_재계산/column_k500_iv/res/SHA256SUMS.txt` | `e486caf213a5f5ad1004b32eee596866c614e17d343a2067ee0ab695bae4d9da` |
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
| `세션_재계산/band_boxes/box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.npy` | `33ba1045bd75e4e4d1f71377965732553ac3d928937f8250e30fb07bea1811a9` |
| `세션_재계산/band_boxes/box_FH_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.npy` | `7f3f28353428fe41d4cb56f4d31ba7cbb78ba879531cb8eb341c603a060232e4` |
| `세션_재계산/band_boxes/box_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p0.npy` | `8c647395f73eaf14a9e83b566d0171117fcda5ad3d6ce172368a1cb88d973dfc` |
| `세션_재계산/band_boxes/box_H_T12-25_k6668_RK1.04_RNU1.03_NY6000_p1.npy` | `2e14190758d6b15f0726e363e5f0a1faea26633fb95e3d9ab7675b5e23b71de9` |
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
| `세션_재계산/moment_cert_iv/run_ct.sh` | `baa8cdc4e8aa9070df4579a8cc66e38db6e1518c8bc0a2876cf29ed32fc48a1c` |
| `세션_재계산/moment_cert_iv/summarize_nb.py` | `828744f9384cd1897dbd7cfd1b70d5ba7a0d6569bb264428eb6b7380d4da3ad1` |
| `세션_재계산/moment_cert_iv/summary_noblas.txt` | `43c1443a6149eddb2e73163ffcdfb2452443c15ac0f1d78367532ccf3a42f05a` |
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
| `세션_재계산/four_families_DDLnat/families_iv.py` | `b86be966704f15123901ecf95184d2e0e295ba06e9fef2cd610202be415e373a` |
| `세션_재계산/four_families_DDLnat/families_iv_out.txt` | `4094775b52b616692a34a2e5cb9496a2c798496ba02be56810ec7fa3ba8fb0a4` |
| `세션_재계산/band_boxes/ivbox_lib.py` | `ab5ef70f632caa0f9a4813e2455b10f0751fdf4f158dc8ea591f6fb9a6bd1f9b` |
| `세션_재계산/critical_window_rerun/contain_rerun.py` | `c01dcfe3375ec8517b8f8ca0310617838e56afd4253f5d32ada86a564bf34e7a` |
| `세션_재계산/critical_window_rerun/contain_rerun_out.txt` | `02f130488fbbf7e38c9fe77a2c6c8f6f176e373819d7311e54a187133ba61f11` |

`세션_재계산/zeta_constants/zeta_iv.py`는 부록 D의 Riemann 제타 상수 항목이 적은 방법을 mpmath 구간 산술(소수 30자리)로 다시 돌려 $\mathsf z_{3/2}$·$\mathsf z_{-1/2}$·$\mathsf z_{1/2}$의 구간을 확인한다(2026-11-13 세션; 인자는 부분합 항 수 $C$ 둘, 기본 4000). 함수 `z32`는 부분합 $S=\sum_{j<C}j^{-3/2}$에 항목 식 줄의 사다리꼴 하계 $2C^{-1/2}+\tfrac12C^{-3/2}$와 중점 상계 $2(C-\tfrac12)^{-1/2}$를 더하고, $\mathsf z_{-1/2}$·$\mathsf z_{1/2}$는 Euler–Maclaurin 공식과 첫 생략항의 나머지 상하계로 감싼다. `python -I zeta_iv.py 4000 4000`의 출력 `zeta_iv_out.txt`는 $\mathsf z_{3/2}\in[2.61237534856\ldots,2.61237534874\ldots]$, $\mathsf z_{-1/2}\in[-0.20788622497838\ldots,-0.20788622497735\ldots]$, $\mathsf z_{1/2}\in[-1.4603545088095868\ldots,-1.4603545088095855\ldots]$이고, 셋 다 확인하는 진술의 구간 안에 있다.

`세션_재계산/r030ffae_window/`는 부록 D의 창의 수준 질량 하계 항목의 셀 검사를 시험 함수 격자를 한 점 늘려($0\le i\le12927$) 다시 돌린 것이다(2026-11-13 세션). `work/`는 기록 [r030ffae] `evidence/peer/rerun/work/`의 코드 사본에 늘린 표 `xKrig.npy`·`wKrig.npy`(기록의 표는 `xKrig_orig.npy`·`wKrig_orig.npy`; 처음 12,927개 값은 비트 단위로 같다)와 결과 JSON을 더한 것이고, `NEW_*.out`이 실행 출력이다.

`세션_재계산/band_boxes/ivbox_lib.py`는 같은 폴더의 `band_iv.py`가 쓰는 구간 성분이다. 스칼라는 mpmath `iv`(소수 34자리), 리만 합 벡터는 binary64의 정확 반올림 사칙연산·제곱근만 써서 1 ulp 바깥 밀기와 합의 $1-10^{-11}$ 인자로 아래로 민다. $\Omega$의 하계는 `window_mass_env/ia.py`의 정확 정의(격자 $i\mathsf K^{-2/3}$·절점값·절점 기울기의 구간)에서 조각별 3차 계수의 바깥 괄호를 만들어 쓰며 조각별 비증가를 구간으로 확인한다. 저장된 봉투 표 $\hat{\mathcal T}$는 저장값을 정확한 점 $\xi^{\mathcal T}_i=0.0005\,i$에 둔 선형 보간으로 읽는다.

`세션_재계산/band_boxes/`는 부록 D의 띠 정리의 상자 검사 항목을 같은 구간 산술로 다시 계산한 것이다. 상자 안의 모든 경우 가름과 되먹임 폭의 점별 범위를 함께 고려해 식 (8.23) 자체를 아래에서 막는다. `band_iv.py`가 계산, `band_summary.py`가 요약, `run_all.sh`가 실행 순서이고, `compare_record.py`가 기록의 상자 값과 대조한다. $\Omega$는 같은 폴더의 `ivbox_lib.py`의 정확 정의를 쓴다.

`세션_재계산/window_mass_env/`는 부록 D의 창의 수준 질량 하계 항목의 셀 검사((가) $q\le2999$, (나) 구간 열일곱 개)를 구간 산술로 다시 계산한 것이다(2026-11-13 세션). `ia.py`가 바깥 반올림 구간(binary64의 정확 반올림 사칙연산·제곱근만 사용)과 $\Omega$의 Hermite 조각·봉투 표·정확 표(mpmath `iv` 25–40자리)를 만들고(세 제타 상수 $\zeta(\frac12)$, $\zeta(-\frac12)$, $\zeta(\frac32)$는 `zeta_constants/zeta_iv_out.txt`의 인증 구간을 바깥쪽으로 넓혀 넣는다), `cert_interval_iv.py`·`cert_Cb_iv.py`가 두 검사를 돌리며, `check_table_iv.py`가 저장된 봉투 표의 하계 조건을 다시 확인하고, `test_ia.py`가 기록의 값이 구간 안에 듦을 확인한다. 출력은 `*_out*.txt`와 `*_result*.json`, 요약은 `summarize_out.txt`.

`세션_재계산/critical_window_rerun/`은 부록 D의 임계 창 인증 항목의 44개 상자를 이 글의 코드로 다시 돌린 것이다. `rig_*.py`·`ivio.py`가 계산 코드, `orig/`가 기록의 원본, `boxes.py`·`common.py`·`rerun_boxes.py`·`launch_rerun.py`·`recert_first.py`·`postrun.py`가 상자 모임·실행기·기동기·첫 셀 재인증·뒤처리 기동기다. 이 글의 코드가 기록의 코드와 다른 넷(실수축 나머지의 지수 상수, $\hat x$ 셀의 격자, 둘러싸기 식 세 곳, $(e^w-1)/w$의 1·2계 도함수 급수의 계수)은 부록 D 항목의 「독립 재계산」에 적혀 있다. $\hat x$ 셀은 십진 격자 $[1.4+0.2i,1.6+0.2i]$를 품는 바깥 구간으로 두고 Taylor 중심·반지름이 셀을 품게 하며 끝점·중심·반지름·여유를 정확한 이진값으로 저장한다. `verify_exact_cover.py`는 저장된 인증서만 읽어 $\mathrm{ku}$ 타일링과 $\mathrm{ku}_{\mathrm{top}}^3\cdot10001\ge1$, 셀의 격자 포함, Taylor 영역의 셀 포함, 여유의 양수성을 허용 오차 없는 유리수로 검사한다(출력 `verify_exact_cover_out.txt`). 인증서는 `cert/`, 상자 자료는 `cache/`, 실행 기록은 `logs/`, 요약은 `summarize.py`→`summary_out.txt`, `_test_exact_grid.py`는 두 셀 시험, `check_fixes.py`→`check_fixes_out.txt`는 코드 자체 검사(둘러싸기의 포함, 급수 상수, 감마 상계, 상자 모임)다. `contain_rerun.py`는 이 글의 인증서가 기록 [ra4c01fc] §8.2 표본(상자 여섯, 154,089개 위치)의 참값을 담는지 확인한다(2026-11-18 세션; 출력 `contain_rerun_out.txt` — 실패 0, 최소 여유 $3.037	imes10^{-4}$; 자료 묶음의 기록 사본 `ra4c01fc/exact_en_B.py`를 불러 쓴다).

`세션_재계산/c50_iv/`는 부록 D의 $20001\le n\le50000$의 오른쪽 절반 인증과 $n\le20000$의 재인증 항목을 본문의 마지막 차 재귀에서 새로 쓴 C 프로그램 `c50iv.c`로 다시 인증한 것이다(2026-11-13 세션). 아래 끝은 아래 반올림 패스, 위 끝은 위 반올림 패스로 따로 계산하는 binary64 방향 반올림 구간이고, 표 $\mathrm{Bor}$·$\mathrm{hB}$는 `make_tables_iv.py`가 mpmath `iv` 40자리로 포위해 바깥 반올림한 이진 표다. 빌드는 `build.bat`(MSVC `/O2 /fp:strict /arch:AVX /openmp`; 어셈블리에 FMA 명령이 없음을 확인). `runs/`에 C20·C50의 요약과 행 파일, $n\le300$의 정확 정수 대조(`exact_small.py`), 넘는 수 재귀 참조 대조(`probe_undercount.py`)의 출력이 있다. 명령은 `run_commands.txt`. 미결 위치 0, 최대 상대 폭 $2.25\times10^{-12}$.

`세션_재계산/logconcavity_n80/lc_n80.py`는 부록 D의 행 로그오목성 항목(`D.{{D:logconcavity-failure-n80}}`)을 짧게 다시 확인하는 정확 정수 검산이다(2026-11-13, 이 글). 마지막 차 재귀로 $0\le\ell\le79$의 모든 열을 $n\le80$까지 파이썬 정수로 계산하고(포화값으로 채우지 않는다), 행마다 $\sum_\ell b_{n,\ell}=(n+1)^{n-1}$과 $A_{n,0}=n!$을 확인한 뒤 모든 내부 첨자에서 $b_{n,\ell}^2\ge b_{n,\ell-1}b_{n,\ell+1}$을 정수 비교로 판정한다. 깨지는 자리는 $(n,\ell)=(80,40)$ 하나이고 $n\le79$에는 없다. 세 정수 $b_{80,39}$, $b_{80,40}$, $b_{80,41}$은 부록 D 결과 줄의 값과 같고, 유리수 분리자 $25928/25000$의 두 교차곱 부등식도 성립한다. 출력은 `lc_n80_out.txt`(약 1초).

`세션_재계산/column_cert_iv/`는 부록 D의 열 $501\le k\le2000$의 열별 갱신 인증서 항목을 라이브러리 함수 가정 없이 방향 반올림 구간으로 다시 계산한 것이다(2026-11-13 세션). `colcert_iv.py`가 열 $501\le k\le2000$마다 열별 갱신 인증서(기록의 정리 G′)의 조건 (a)(b)(c)를 확인한다: 소인 질량과 창 계수의 양의 재귀는 아래 끝·위 끝 두 줄의 binary64 구간(연산마다 바깥 밀기, 내적은 짝지은 합 나무와 끝의 $(1\mp2^{-53})^{-(d+1)}$ 인자), 원 위의 격자값은 `ivlib.py`의 자기 구현 구간 FFT(실부·허부 상자, 회전 인자는 mpmath `iv` 표), 주편각은 $\arctan$ 포위, 스칼라 조립은 mpmath `iv` 소수 40자리다. $k$에 무관한 표(Borel 수, $n\le2000$의 소인 질량, 회전 인자)는 `tables.py`가 `_cache/bor_pr0.npy`·`_cache/twiddle_2p21.npy`로 만든다(약 1.5분; 33 MB라 묶음에 넣지 않고 다시 만든다). 실행은 `python -I colcert_iv.py --ks 841-2000 --part 0 --nparts 2 --batch 16 --out res_p0.jsonl`과 `--part 1`(각 2.9시간), 열 501–840은 `--ks 501-840 … --out res_ext_p0.jsonl`과 `--part 1`(각 16분)이다. 열별 성분과 판정은 `res_*.jsonl`(binary64 값을 왕복 가능한 전체 자리로), 실행 기록은 `run_*.log`, 요약은 `summary.py`(`summary_all_out.txt`: 1500열 모두 성공, 최소 $\mathfrak b_0=0.03478$, 최소 여유 $0.02722$, $V$ 위 끝은 저장값 곱의 $1.000007$배 이하), 기록 검토의 40자리 값과의 대조는 `crosscheck_review.py` → `crosscheck_review_out.txt`, numpy FFT와의 대조는 `test_841.txt`·`test_1171.txt`·`test_2000.txt`다.

`세션_재계산/moment_cert_iv/`는 부록 D의 모멘트 판정 항목(재귀 인증)을 구간 산술로 다시 계산한 것이다(2026-11-13~15 세션). `mcert_iv.py`는 재귀 (7.1)과 모멘트 재귀 (7.2)에 $\hat{\mathfrak a}_n$을 곱해 나눗셈 없는 네 양의 재귀로 바꾸고, 필요한 끝점만 binary64 구간으로 계산한다(아래 끝 $\hat{\mathfrak a}$, $\hat{\mathfrak a}\mathfrak Z^\flat$, $\hat{\mathfrak a}\mathfrak Z$; 위 끝 $\hat{\mathfrak a}$, $\hat{\mathfrak a}\mathfrak Z^{\mathrm H}$). 항목이 쓰는 본 실행은 BLAS 없는 연산 수 한계 판(`sweep_nb … --count`)이다. 각 합을 numpy 원소별 곱과 원소별 덧셈의 짝지은 나무로 계산하고 한 항이 겪는 반올림 횟수 $r$을 세어 끝에서 $(1\pm\mathsf p)^r$로 넓히며, 저장값이 모두 $[2^{-400},2^{400}]$ 안임을 확인하고(벗어나면 척도 $\beta$를 고쳐 다시 돈다), 스칼라 연산은 한 ulp 밖으로 민다. 초등함수와 기록의 binary64 판정식(부록 D 모멘트 판정 항목의 「식」 줄)은 쓰지 않고 $\mathbb E>0$을 직접 판정한다. (A5) 1160열 40,638,833개 위치 전부 통과(실패 0; 프로세스 1개 `mcert_iv.py sweep_nb A5 sweep_ct_A5.jsonl --low --count`; `sweep_ct_A5.jsonl`과 로그). 기록의 (A3) 340열(열 $501\le k\le840$)도 같은 판으로 통과했으나 본문이 그 범위를 쓰지 않아 항목과 묶음에서 뺐다(2026-11-17 22차; `sweep_ct_mp.py`는 그때 쓴 샤드 도구다). `summarize_nb.py`→`summary_noblas.txt`(범위별 집계와 BLAS 판과의 판정 대조). 대조 실행으로, 같은 재귀의 합을 행렬곱으로 계산한 뒤 덧셈 순서·융합 여부와 무관한 한계 $(1\pm u)^{m+1}$($m=6n+3$)로 넓힌 판(`sweep 0 2`·`sweep 1 2`)이 기록의 다섯 실행 A1–A5(글이 쓰는 범위는 A5이고, 나머지 넷은 어느 장도 쓰지 않는 추가 계산이다) 7619열 60,703,015개 위치에서 전부 통과했고(프로세스 2개로 약 2시간 10분, CPU 합 15,164초; `sweep_p0.jsonl`·`sweep_p1.jsonl`과 로그), 항목의 1160열에서 두 판의 열별 최솟값 하계는 상대 $1.1\times10^{-9}$ 안에서 같다. `summarize.py`→`summary.txt`(BLAS 판의 범위별 집계), `compare.py`→`compare_out.txt`(기록의 여덟 열 대조: 인쇄값이 모두 구간 안), `test_exact.py`→`test_exact_out.txt`(작은 열의 정확 유리수 포함), `test_count.py`→`test_count_out.txt`(연산 수 한계 판의 나무 깊이 검증, 작은 열의 포함 검사, BLAS 판과의 세 열 대조), `nM.py`→`nM.json`·`nM_out.txt`(열별 문턱 $n_{\mathrm M}(k)$의 정확 유리수 재계산; 1160열 모두 기록과 같음).

`세션_재계산/column_k500_iv/`는 부록 D의 열 인증($121\le k\le500$) 항목을 이 글의 새 구현으로 380열 전부 다시 인증한 것이다(2026-11-13 세션). `lastcar_iv.py`는 세 재귀 G·H·E를 쓰지 않고 마지막 차 재귀 $n\mathfrak e_n=\mathfrak x\sum_j\min(j+1,y)\mathfrak e_j\mathfrak e_{n-1-j}$ 하나를 정확한 큰 정수 합성곱의 온라인 분할 정복(Kronecker 포장; 큰 크기는 `decimal`의 수론 변환, 부정확 반올림은 트랩)으로 160비트 고정소수점 정수 구간에서 계산하며, 반올림은 계수를 확정할 때 한 번(아래 끝은 내림, 위 끝은 올림)뿐이라 끝점이 직접 합과 비트 단위로 같다. 연속한 열 10개가 하나의 정확한 이진 유리수 $\mathfrak x=e^{-1}(1+c/\bar k)$를 공유한다. `colk500.py`(`--worker i --nworkers 2`)가 열별 판정·최소 인증 여유·시간을 `res/k<k>.json`에 쓰고(380개; 해시 목록 `res/SHA256SUMS.txt`), `summarize.py`→`summary_out.txt`(380열 실패 0, 직접 비교 20,368,570개·비 비교 10,302,655개, 최소 인증 여유 $1.3778\times10^{-5}$($k=500$, $n=2k+1$)), `compare_indep.py`→`compare_indep_out.txt`(기록 검토의 다섯 열과 판정·최대 폭 일치, $k=121$은 모든 끝점 동일; 열별 최소 여유가 기록과 상대 $1.1\times10^{-35}$ 안), `test_small.py`→`test_small_out.txt`($n\le7$ 전수·$n\le120$ 정확 개수 포함, 분할 정복과 직접 합의 일치). 두 프로세스 각 약 9500초(공유 기계, 벽시계 2.7시간; `run_w0.log`·`run_w1.log`).

`세션_재계산/left_columns_k2_120/`는 부록 D의 모든 $n\le20000$의 단봉성 항목 (ㄱ) 가운데 열 $2\le k\le120$($\max(2k+1,12)\le n\le10000$)을 기록 [rc9aee43]의 열 인증 코드(`code/positive_columns.py`, 바이트 그대로의 사본)의 열 계산으로 다시 인증한 것이다(2026-11-15 세션). `code/left_columns.py`가 용량 $1\le y\le121$의 열을 열별 이진 유리 반지름(`code/radii.json`)으로 한 번씩 계산하고 이웃 세 열을 정확한 유리수 배율의 구간으로 한 반지름에 맞추어 비교하며, 출력은 `results_k2_70.jsonl`·`results_k71_120.jsonl`과 `summary.json`(비교 1,175,466개, 실패 0, 최소 인증 여유 $1.2608\times10^{-4}$, $k=6$, $n=13$)이다. `code/exact_check.py`→`exact_check.json`은 $n\le300$의 정확 정수(정리 2.6의 재귀)와 전수 대조, `indep/`는 기록의 독립 프로그램 `indep_lastcar.py`(사본)와 그 재귀로 최소 여유를 재는 `indep_margin.py`를 표본 열 $k\in\{2,3,7,30,60,120\}$에 돌린 것이다. 첫 실행(범위 $2k+1$부터; $n=5,7,9,11$의 네 예외가 드러남)의 결과는 `logs/firstpass/`에 있다.

`세션_재계산/witness_offset_iv/`는 부록 D의 모든 $n\le20000$의 단봉성 항목 (ㅂ), 곧 명제 witness-position-bound(5.1절)가 확인하는 증인 위치 차 $n+1-\ell^\ast_n-0.59963(n+1)^{2/3}-1.24847(n+1)^{1/3}$을 기록 [r19de912]의 행 자료(자료 묶음의 사본 `r19de912/evidence__peer__cert__v2run20000-rows.tsv`의 봉우리 열 `mode_ell_mid`)에서 방향 반올림 구간(mpmath `iv`, 소수 30자리)으로 다시 계산한 것이다(2026-11-15 세션). 기록의 계산 `mode_offset.py`는 binary64 최근접 반올림의 배정밀도 평가였다. `code/witness_offset_iv.py`는 두 상수를 십진 문자열의 구간으로, 두 지수 $2/3$·$1/3$을 정수 나눗셈의 구간으로 두고 두 범위 $50\le n\le900$·$901\le n\le20000$마다 구간 아래 끝의 최솟값과 위 끝의 최댓값을 이진 유리수 그대로의 분수와 소수 열다섯 자리(아래 끝 내림·위 끝 올림)로 `witness_offset_iv.json`에 적고, 진술의 구간 $[0.85,1.99]$ 안에 드는지를 정확한 유리수 비교로 판정한다(두 범위 $[0.889979773145161,1.986242781217464]$·$[0.850826875264814,1.875832792791377]$, 모두 안에 듦, 최소 여유 $8.27\times10^{-4}$, 구간 폭 $7.5\times10^{-28}$ 이하, 약 10초). `code/summarize.py`가 부록 D 항목과 재실행표에 적는 꼴(바깥쪽 세 자리 $[0.889,1.987]$·$[0.850,1.876]$)로 요약하고, 실행 명령·시각·환경은 `logs/commands.txt`, 설명은 `README_run.md`에 있다.

`세션_재계산/icert_py_full/`는 부록 D의 가운데 증가의 정수 인증 항목의 독립 재계산, 곧 기록 검토의 Python 큰 정수 구현 `rev_icert_unpaired_fast.py`(사본; `CERT` 경로 한 줄만 기록 사본으로 바꿈)를 $1001\le k\le10000$의 9000열 전부에 돌려 `icert.c`의 출력 `out_8_10000.txt`와 비트 단위로 대조한 것이다(2026-11-13~16 세션). `worker.py W i`가 프로세스 $W$개 가운데 $i$번째 몫을 100열 묶음으로 자식 프로세스에 돌리고 묶음마다 `out_<k1>_<k2>.txt`에 열별 JSON 한 줄(`k`, `bit_identical_to_C`, `ok`, `sec`)을 남기며, `launch.py W`가 프로세스를 띄우고(`launches.txt`에 이력, 끊긴 묶음의 `.part`는 완결된 줄만 거둠) `stop.py`가 멈춘다. 작업자 1→4→2→3개로 돌리다 2026-11-15 13:51 멈추고 21:00 4개로 다시 띄워 2026-11-16 08:01 끝났다(정지 기간에는 자료 묶음 밖의 세션 구현이 같은 열의 잠정 판정을 냈고, 원본의 결과와 열마다 같다). `summarize.py`→`summary.json`: 9000열 전부, 결측 0, 비트 불일치 0, `ok` 거짓 0, 중복 0, 열별 시간 합 573,393.5초(159.28시간; 다른 계산과 코어를 나눠 쓴 구간이 있다), 출력 파일 96개, 열당 최대 421초($k=9537$). `README_run.md`에 실행·정지·재기동 기록이 있다.

`세션_재계산/four_families_DDLnat/families_iv.py`는 부록 D의 네 가족의 첫 열 검사 항목의 모든 값(여유, 하계, 가장자리, 보조정리 조건, 단조성 표본)을 mpmath 구간 산술(소수 30자리)로 다시 계산한다(2026-11-17 세션). 실행은 폴더 안에서 `python -I families_iv.py > families_iv_out.txt`(약 100초)이고 출력은 `families_iv_out.txt`다. 이 판이 바꾼 함수 `DDL`의 전후와 결과 요약 메모(`변경.md`·`결과_요약.md`)는 묶음 밖 `대조v2/보관_자료_1117/세션_재계산_미등재_1117/four_families_DDLnat/`에 있다.

## 파일 목록

| 경로 | 출처(기록·원 경로) | 부록 D 항목 | SHA-256 |
|---|---|---|---|
| `r030ffae/FIXED_cert_Cb_1_2080.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_1_2080.out` | window-mass-env | `fbdbc0d9c6e41cc3d06c5497842aaa645c98d471e2ef4574f17d68de54bac29d` |
| `r030ffae/FIXED_cert_Cb_2080_2621.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_2080_2621.out` | window-mass-env | `3e11d73a425ac6e47ceae21c610fc6c0aa1268b8b30370c60f4fed8a2e2d9ca4` |
| `r030ffae/FIXED_cert_Cb_2621_3000.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_2621_3000.out` | window-mass-env | `53443ba751bd73925874a66c24d7fbd7ec67301d60a958f1dc5443f67fcf5af9` |
| `r030ffae/FIXED_cert_Cb_result_1_2080.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_result_1_2080.json` | window-mass-env | `d53f5100782f83c3f43656a79c924aa2dd424ba4dd6632bb6fc7613dd04dc3cf` |
| `r030ffae/FIXED_cert_Cb_result_2080_2621.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_result_2080_2621.json` | window-mass-env | `a184fbaf9dae626c7021ab009fc0c699a2df1b351bb79a632b992641d1c7e7b2` |
| `r030ffae/FIXED_cert_Cb_result_2621_3000.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_Cb_result_2621_3000.json` | window-mass-env | `f9ebcaad8c969d4103fc63c1592136821bcc282956b5956a03a85fc2820829b0` |
| `r030ffae/FIXED_cert_interval.out` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_interval.out` | window-mass-env | `fd3fa7a870f7cef03f04059b336be837756859f3f751b2fc6dad130ad141378d` |
| `r030ffae/FIXED_cert_interval_result.json` | [r030ffae] `evidence/peer/rerun/work/FIXED_cert_interval_result.json` | window-mass-env | `b039497680fb1f0ebac2d44701d1a14394b0f0ecb0b8ac4856fc18b56336363d` |
| `r030ffae/LOWH_cert_assembly_T0.48_k6668.out` | [r030ffae] `evidence/peer/rerun/work/LOWH_cert_assembly_T0.48_k6668.out` | band-boxes | `c36cbe45437af3890dda5af0ed370314f7ecdc6136a0b63059f8fb8e89490c2e` |
| `r030ffae/LOWH_cert_assembly_result_T0.48_k6668.json` | [r030ffae] `evidence/peer/rerun/work/LOWH_cert_assembly_result_T0.48_k6668.json` | band-boxes | `121a7c6572043263a4bef23e8da2fe3dcdd8eeb3bc8d2dd2994c2d30b74df68f` |
| `r030ffae/REVIEW_LOWH_T0.48_k6668.out` | [r030ffae] `review/evidence/REVIEW_LOWH_T0.48_k6668.out` | band-boxes | `9084778d9d65294cd58343a763d5d6e7221eaf10b97f39e4c7eb27bbf051eccf` |
| `r030ffae/build_env_fixed.py` | [r030ffae] `evidence/peer/rerun/work/build_env_fixed.py` | window-mass-env | `c1396fd7d3d982ca0c4ce8d0758785e6015711faf3fcb9e2c5a35ac4a1cd2c68` |
| `r030ffae/build_env_profile.py` | [r030ffae] `evidence/peer/rerun/work/build_env_profile.py` | window-mass-env | `a9d05c7eb9ada573d2a5fa61742e8d9c51927830de7cd2f45de69ff274635ca5` |
| `r030ffae/cert_Cb_range.py` | [r030ffae] `evidence/peer/rerun/work/cert_Cb_range.py` | window-mass-env | `895e2fac0f7f86fae7a977f7306dc2ae6bc2936386f74446989e6fb14707f0e2` |
| `r030ffae/cert_assembly_lowH.py` | [r030ffae] `evidence/peer/rerun/work/cert_assembly_lowH.py` | band-boxes | `26f2e8989cfa86fb6b83c71dc6885e20294d01dc1d834fcbd0f9b7d0a15c4f6c` |
| `r030ffae/cert_assembly_mono.py` | [r030ffae] `evidence/peer/rerun/work/cert_assembly_mono.py` | band-boxes | `d5e3c4ec4fbee044fafb11c507765317bb2be83a909fd7f8bfba023f721966bd` |
| `r030ffae/cert_lib.py` | [r030ffae] `evidence/peer/rerun/work/cert_lib.py` | window-mass-env | `0ff3452340fdcf81dde638f29a8d0c7b3bb7fd905a7d4eecc31d1065b26ccb87` |
| `r030ffae/cert_lib_fixed.py` | [r030ffae] `evidence/peer/rerun/work/cert_lib_fixed.py` | window-mass-env | `18bbfcfe0a370fce8cf50015011ffb35538b118addf7897fa43bfbeef97402e7` |
| `r030ffae/design.json` | [r030ffae] `evidence/peer/rerun/work/design.json` | window-mass-env | `5ca7ca94ea05873420053508c14ddec9562d60fb18c65d7ed2173afc0c12da7f` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_v.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_v.npy` | band-boxes | `64402ee14c829cdf9c8ffe4ce30796c03b4b56cd3329a7af5c7679150a097869` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_v.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_v.npy` | stored-table-check | `64402ee14c829cdf9c8ffe4ce30796c03b4b56cd3329a7af5c7679150a097869` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_x.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_x.npy` | band-boxes | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
| `r030ffae/evidence__peer__rerun__work__qenv_fix_x.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_x.npy` | stored-table-check | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
| `r030ffae/evidence__peer__rerun__work__wKrig.npy` | [r030ffae] `evidence/peer/rerun/work/wKrig.npy` | band-boxes | `8e047df2647393e22c7fbfb157fd1dcfa9de2bdd25aa06f6586ad603d52eb609` |
| `r030ffae/evidence__peer__rerun__work__xKrig.npy` | [r030ffae] `evidence/peer/rerun/work/xKrig.npy` | band-boxes | `16f6fbc8fa801ba6e4e66e6336d943a0736096d00940406a300c599eda724287` |
| `r030ffae/fixes.py` | [r030ffae] `evidence/peer/rerun/work/fixes.py` | window-mass-env | `36c741e815fe403c9551c5accb4a08717b7895270f0a5467f9a0161be0b6ee9f` |
| `r030ffae/qenv_fix_v.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_v.npy` | window-mass-env | `64402ee14c829cdf9c8ffe4ce30796c03b4b56cd3329a7af5c7679150a097869` |
| `r030ffae/qenv_fix_x.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_fix_x.npy` | window-mass-env | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
| `r030ffae/qenv_rig_v.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_rig_v.npy` | window-mass-env | `094be37b7cfbf8a8e1c475d178c22e8de70b62308c3bcd54e735009fed6eec64` |
| `r030ffae/qenv_rig_x.npy` | [r030ffae] `evidence/peer/rerun/work/qenv_rig_x.npy` | window-mass-env | `05247f9d5ee1a5e9235a12113d8c904a22ecacdf798069270c9b32679abe0b3e` |
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
| `r10ff8c2/block3_501_2000_all.json` | [r10ff8c2] `evidence/peer/block3_501_2000_all.json` | moment-certification | `0fcac5fef27b255718bf15fd0a91b909d4424a795e7e3444ea43f173a31c21a6` |
| `r10ff8c2/brute.py` | [r10ff8c2] `evidence/peer/brute.py` | moment-certification | `7a6b3733cdcc7c9773b96e79f3dee32156f2b4ff238ca7fb13559c7b5e5124d7` |
| `r10ff8c2/c_results.txt` | [r10ff8c2] `evidence/peer/c_results.txt` | moment-certification | `df9445998924c14c0b63df35d17f33ba8fee884e131069a64ff1d7a38d456af4` |
| `r10ff8c2/cover_check.py` | [r10ff8c2] `review/checks/scripts/cover_check.py` | moment-certification | `c247453b821af27fd23c2ecd544c5ccfe0e19c45efef593b0c00355989248df2` |
| `r10ff8c2/cover_check_out.txt` | [r10ff8c2] `review/checks/cover_check_out.txt` | moment-certification | `dea801401bc5a47139a90d96285a2f82672603b260a7c6dc05dfa244d456ebb9` |
| `r10ff8c2/coverage.py` | [r10ff8c2] `evidence/peer/coverage.py` | moment-certification | `8c5e93eaaff4c91700706583afb09dc7cffac6d8862b0cdded1ed17f3808ac0b` |
| `r10ff8c2/coverage_out.txt` | [r10ff8c2] `evidence/peer/coverage_out.txt` | moment-certification | `b53b6a0e9f8f1cc25283d7fe8135d15f02a4a3ddfe1654ddcd940a71c79aa0ae` |
| `r10ff8c2/evidence__peer__block3_501_2000_all.json` | [r10ff8c2] `evidence/peer/block3_501_2000_all.json` | column-certificates-501-2000 | `0fcac5fef27b255718bf15fd0a91b909d4424a795e7e3444ea43f173a31c21a6` |
| `r10ff8c2/exact_cols.py` | [r10ff8c2] `evidence/peer/exact_cols.py` | moment-certification | `2d6febab3aebc4f5422cd3abaf3c93be1f296830353b152eb761087947f1d058` |
| `r10ff8c2/identities.py` | [r10ff8c2] `evidence/peer/identities.py` | moment-certification | `7fbb74baa785a2c0682411321a689bcfa972219950ac3f22d3eb7a875b01ea1e` |
| `r10ff8c2/iv_results.txt` | [r10ff8c2] `review/checks/iv/iv_results.txt` | moment-certification | `f090b121608ad8f99ca56ba927389957283ac79578ce9ea3cadb8c363b788c4c` |
| `r10ff8c2/ivcert.c` | [r10ff8c2] `review/checks/iv/ivcert.c` | moment-certification | `0ecd0e8baba546d1fbe43211d18053ea17a7fdf6bcd5f4e12d44de5189426483` |
| `r10ff8c2/lmcert_sweep.c` | [r10ff8c2] `evidence/producer/lmcert_sweep.c` | moment-certification | `4203421474b9e2c6b6c9fde59cb1639e780ad7754c222aea36c04715f25ee74d` |
| `r10ff8c2/nj_summaries.txt` | [r10ff8c2] `evidence/peer/nj_summaries.txt` | moment-certification | `d87781d016a0b0afb15880bb4b8367ef205fa2fa0f094cce916f32cdd09dff88` |
| `r10ff8c2/notes_errors.md` | [r10ff8c2] `evidence/producer/notes_errors.md` | moment-certification | `b1541cefd8ab26d5fb45cd6c9010fac81d72a49d8567192f1a497d38cad4d454` |
| `r10ff8c2/np_results.txt` | [r10ff8c2] `evidence/peer/np_results.txt` | moment-certification | `0f5044826e9f629fd3b0530dfb30ea3f7b3fbb0dafd008e23141b2952772ce56` |
| `r10ff8c2/npcheck.py` | [r10ff8c2] `evidence/peer/npcheck.py` | moment-certification | `ecd8d4e45c1c4eb34bb7932ff3130d18f9d5180e0299a5b874eaac71cf8ef3df` |
| `r10ff8c2/win_0.txt` | [r10ff8c2] `evidence/producer/cert/win_0.txt` | moment-certification | `825c7df6d3249eb61db747d3bd287cef87dc11b892ced1a3b8e661983a6cdad9` |
| `r10ff8c2/win_1.txt` | [r10ff8c2] `evidence/producer/cert/win_1.txt` | moment-certification | `f3eeee0cbef73c9e63c973c64db6dd90ff21368ad43ed9fd7b817ba6a19eeac1` |
| `r10ff8c2/win_2.txt` | [r10ff8c2] `evidence/producer/cert/win_2.txt` | moment-certification | `0f5d9011aaf58f71c8e8f7a7a641db94c9afe79bf2b16183d094fe16038c5c01` |
| `r10ff8c2/win_3.txt` | [r10ff8c2] `evidence/producer/cert/win_3.txt` | moment-certification | `7f14d9dbad354afcea75b99e20a5a85e797011b15da79a95ceab34f37ade0513` |
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
| `r13b0b8f/tsv_crosscheck_Aplus.json` | [r13b0b8f] `evidence/peer/tsv_crosscheck_Aplus.json` | band-A-certification | `5e7f011521a5011ec48620bb2c3732c985cf7bfac8aa56005d244a32dfb80eac` |
| `r13b0b8f/verification.json` | [r13b0b8f] `evidence/producer/output/verification.json` | band-A-certification | `80a80d0793310830c5cd40c392f3d0f6e34ac7f6aa01745bd98b88ac26202379` |
| `r15524fd/counts.json` | [r15524fd] `evidence/counts.json` | logconcavity-failure-n80 | `a3f8a62dc3fe4b43c638898857a3c4624ca5c162cc63a3b778eba4aeebc5b74b` |
| `r15524fd/logconcavity-witness.json` | [r15524fd] `evidence/logconcavity-witness.json` | logconcavity-failure-n80 | `df8353362aef69656b7d53c3e52aea1d7e59726f21fcc5e65811c6e874924935` |
| `r15df76b/audit_run10k.json` | [r15df76b] `evidence/peer/checks/audit_run10k.json` | exact-n20000 | `186b15705b03b01a3e7c0229b33e019772e08c79554131c19c56e134e347b08f` |
| `r15df76b/audit_run10k.py` | [r15df76b] `evidence/peer/code/audit_run10k.py` | exact-n20000 | `c6952163a67a855ce093f320a3be4c40ae3b369e3e4932e0e0fd039e566935e1` |
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
| `r15df76b/pv10k_k1601-2900.tsv` | [r15df76b] `evidence/peer/run10k/pv10k_k1601-2900.tsv` | exact-n20000 | `b88dbe4b48af3924127ea77de0d4c37b227a303cf5af660be8ac64fe8056b3ee` |
| `r15df76b/pv10k_k2-1600.tsv` | [r15df76b] `evidence/peer/run10k/pv10k_k2-1600.tsv` | exact-n20000 | `75da519e5682bd82e268d42612ccb54fa5d30c902dfde13b354283c3e329e20a` |
| `r15df76b/pv10k_k2901-4000.tsv` | [r15df76b] `evidence/peer/run10k/pv10k_k2901-4000.tsv` | exact-n20000 | `9d07083188168efec836e7517ebc997d5cffc86b61b03a73306051f029d9ca31` |
| `r15df76b/pv10k_k4001-5000.tsv` | [r15df76b] `evidence/peer/run10k/pv10k_k4001-5000.tsv` | exact-n20000 | `e1085ff44b8bd9c77472200cde8ee16144bcdbf470e1ae79bb7650f4dc8bb93a` |
| `r15df76b/pv_k2-2501.tsv` | [r15df76b] `evidence/peer/run/pv_k2-2501.tsv` | exact-n20000 | `592b512365fa8a439021e823924dccf6fd9032fba3e59ffa329a09bfbd2130de` |
| `r15df76b/pv_k2502-5001.tsv` | [r15df76b] `evidence/peer/run/pv_k2502-5001.tsv` | exact-n20000 | `578283961124f731776f8d6f7d3a559e368092e088a19d2aa0a0c19fef8a016b` |
| `r15df76b/pv_k5002-7501.tsv` | [r15df76b] `evidence/peer/run/pv_k5002-7501.tsv` | exact-n20000 | `3e25e06296b3273cee5b80e4eb39838759b177fe8c4ac3ee5a086ec9e26a4576` |
| `r15df76b/pv_k7502-10000.tsv` | [r15df76b] `evidence/peer/run/pv_k7502-10000.tsv` | exact-n20000 | `ceadd1b8949c3e026019edfc012be8fd9d42851188c2c709a539f50f8c85bc92` |
| `r15df76b/small20000_k2-250.tsv` | [r15df76b] `evidence/producer/run2/small20000_k2-250.tsv` | exact-n20000 | `9d52e8d0bd97ba19d2a35aaed4269b889a34c407d3f05e60d88ce3f8100dc0bf` |
| `r15df76b/small20000_k251-500.tsv` | [r15df76b] `evidence/producer/run2/small20000_k251-500.tsv` | exact-n20000 | `beef52e25117b4be25ff70c421d7036bc1b2411adbced3989e7570b3be1130de` |
| `r19de912/certify_right_half.py` | [r19de912] `evidence/producer/certify_right_half.py` | exact-n20000 | `130d1fded0625c8ef7ad9834b87b796b1a01e365ccb951260b4d2ba016185492` |
| `r19de912/class-hashes.txt` | [r19de912] `evidence/peer/cert/class-hashes.txt` | exact-n20000 | `92b1fe42e59b542d813c0a5dad2cee5b7725f2fa5456f465e00f43d2f634b238` |
| `r19de912/gen_s.py` | [r19de912] `evidence/peer/cert/gen_s.py` | exact-n20000 | `1e435ad8eb6202b9aada4a4354ad40bcb63d4f7d3eedfd8c7641ba0d76f1149c` |
| `r19de912/mode_offset.json` | [r19de912] `evidence/peer/checks/mode_offset.json` | exact-n20000 | `69e8f0908be8f91e4a7b8d012593599505084afca22a2cd222cb3e0d21096b95` |
| `r19de912/mode_offset.py` | [r19de912] `evidence/peer/checks/mode_offset.py` | exact-n20000 | `73c23a56b3ee0bcfe9636d9de1a30fa0b435491268de05e696e5f7e29f70376e` |
| `r19de912/producer-rerun-summary.json` | [r19de912] `evidence/peer/checks/producer-rerun-summary.json` | exact-n20000 | `4ada1ef3687bd6660dc50888235a4bb3b6f753cd9ca03a06a9c3cdec02eee087` |
| `r19de912/qr_cert2.c` | [r19de912] `evidence/peer/cert/qr_cert2.c` | exact-n20000 | `7b611e838f8d20d5970cf8ca597b0263e9deae3b12e8d66b426b68a319cb1ab4` |
| `r19de912/review/evidence/peer-rerun/rr2000-class.sha256` | [r19de912] `review/evidence/peer-rerun/rr2000-class.sha256`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `c4865cd10180c3fe078c88f2b9af3b6d529e03d45c033e0d078b860a3b64e40f` |
| `r19de912/review/evidence/peer-rerun/rr2000-summary.json` | [r19de912] `review/evidence/peer-rerun/rr2000-summary.json`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `c81c69d041497bf76ec3d4412bd9382303c02dacd73e90d35835895f8cab11bc` |
| `r19de912/review/evidence/peer-rerun/rr20000-rows.sha256` | [r19de912] `review/evidence/peer-rerun/rr20000-rows.sha256`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `ce99d4996d95f77e50ba303a75f0252cb0fab905b798848a6f6562a27ac25af8` |
| `r19de912/review/evidence/peer-rerun/rr20000-summary.json` | [r19de912] `review/evidence/peer-rerun/rr20000-summary.json`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `aa7797b6d0cad17da78f4ebc10aa0c32955f910acd28ea21b6558c97fbc6dc19` |
| `r19de912/review/evidence/peer-rerun/rr20000.log` | [r19de912] `review/evidence/peer-rerun/rr20000.log`(폴더 `review/evidence/peer-rerun/`) | exact-n20000 | `ef836d26ff49bcecefe19bed41f219de99ae66b20accd8342595571f7417fedc` |
| `r19de912/right-half-certificate-2000.json` | [r19de912] `evidence/producer/right-half-certificate-2000.json` | exact-n20000 | `165c71d0e7ee9a1b5c1dd8ba79d049ad2dbc5e36580d707e1b1ad475540d85d0` |
| `r19de912/v2run20000-rows.tsv` | [r19de912] `evidence/peer/cert/v2run20000-rows.tsv` | exact-n20000 | `d35451d1431a6167228c41a5fb688d097de76cc043470b10a95487c88b838f48` |
| `r19de912/v2run20000-summary.json` | [r19de912] `evidence/peer/cert/v2run20000-summary.json` | exact-n20000 | `c47472c68f463654a09ab5d6071c9681f43b3743eb6b9fb28dc150a74ac10e31` |
| `r19de912/v2run20000.log` | [r19de912] `evidence/peer/cert/v2run20000.log` | exact-n20000 | `aa0fcd6a0e130d597ba4ac5d7282e24e816b6e5830dfd79f4a604b839bd0fdae` |
| `r475ada3/audit_band.py` | [r475ada3] `evidence/producer/band/audit_band.py` | band102-integer | `3a1b12169f4b3b6de6dc9dba2709e2518720736ff9b2936fd657eac0092a69ab` |
| `r475ada3/audit_band_nu20_23.txt` | [r475ada3] `evidence/producer/band/audit_band_nu20_23.txt` | band102-integer | `ee8eb87ec9b0737c1a44c42372b126a8b0c3b57b99df56ff9e7f3a45615967ab` |
| `r475ada3/audit_band_run.txt` | [r475ada3] `evidence/peer/repro/audit_band_run.txt` | band102-integer | `f64345812da75a5c6eb2c5264b70b665bcff50ebafe2bd7a29e0091d2506f3bd` |
| `r475ada3/audit_diag.py` | [r475ada3] `evidence/producer/code/audit_diag.py` | band102-integer | `99f6ceb66c7c2dbd1572d45d9580cf8e9680bc89de444ca1538aa346dd3fb2d1` |
| `r475ada3/audit_diag_run.txt` | [r475ada3] `evidence/peer/repro/audit_diag_run.txt` | band102-integer | `2d45ffbbcb379ed570e52cd1029321a0e0e8b2250c8b104f5d0479c50d874858` |
| `r475ada3/audit_f1_f2.json` | [r475ada3] `evidence/peer/icert/audit_f1_f2.json` | band102-integer | `087463e6a621e14d155b27c79b3c4d89f9f2d75700560bd45f3ae629484aa621` |
| `r475ada3/audit_f2.py` | [r475ada3] `evidence/peer/icert/audit_f2.py` | band102-integer | `0696899204964006d788f25442a482780674e48b0062b7523deb0a7711d60348` |
| `r475ada3/audit_param.py` | [r475ada3] `evidence/peer/repro/audit_param.py` | band102-integer | `9befd93d9f33aed3ef16f8e86b59e34d7dcb967b9c9564a6afe329ef346e96d4` |
| `r475ada3/audit_param_K11100_nu20_40.txt` | [r475ada3] `evidence/peer/repro/audit_param_K11100_nu20_40.txt` | band102-integer | `cec3eb46f3338eb1c5ee68351684f4cdce8491058050399682fe42557aae69ca` |
| `r475ada3/hermite_exact.py` | [r475ada3] `evidence/producer/code/hermite_exact.py` | band102-integer | `63be858f55d1912e1aedada0a7d86a92dbb91c527a220679c28c577aadaba484` |
| `r475ada3/icert_rows.c` | [r475ada3] `evidence/peer/icert/icert_rows.c` | band102-integer | `97856048e2c6f24e66e4959a331a27e34a6fe45a996e7258e82e5fcbf2196b38` |
| `r475ada3/mine_param_K11100.txt` | [r475ada3] `review/checks/audit/mine_param_K11100.txt` | band102-integer | `cec3eb46f3338eb1c5ee68351684f4cdce8491058050399682fe42557aae69ca` |
| `r475ada3/nk_strip2.txt` | [r475ada3] `evidence/peer/icert/nk_strip2.txt` | band102-integer | `fea04f1964690820d029e37128e3d4feb80f7a9a41534b3a912d4ae4027ba73b` |
| `r475ada3/out_band_check.txt` | [r475ada3] `evidence/peer/icert/out_band_check.txt` | band102-integer | `ffd8896215c200e01098106b7f6a1c70eedff646e52a1e43ffc211398b15acf1` |
| `r475ada3/out_s2_a.txt` | [r475ada3] `evidence/peer/icert/out_s2_a.txt` | band102-integer | `c17db983e9a1bd24a57d75a605afa7386ba6862ab481f9cf06f1463b6e9b212e` |
| `r475ada3/out_s2_b.txt` | [r475ada3] `evidence/peer/icert/out_s2_b.txt` | band102-integer | `f0304375b5e558389a517b4184037551611dc8c8abae340f8d0f7c0f7f0cae02` |
| `r475ada3/out_s2_c.txt` | [r475ada3] `evidence/peer/icert/out_s2_c.txt` | band102-integer | `01f218f38c8bbd9acb60ce2220beceb1369ac9e9155b87239a59c8026df159ed` |
| `r475ada3/out_selftest.txt` | [r475ada3] `evidence/peer/icert/out_selftest.txt` | band102-integer | `e90c40a5b5c8e1d4c9fff172a5cb6d6544f16705a89265c0886c2520c4da9750` |
| `r475ada3/out_strip.txt` | [r475ada3] `evidence/peer/icert/out_strip.txt` | band102-integer | `ef039bb83e3064d9d2fd02e281f8c00145475d55b4e0f398a6fafc944e2b366a` |
| `r475ada3/review/checks/icert/my_s2_hi.txt` | [r475ada3] `review/checks/icert/my_s2_hi.txt`(폴더 `review/checks/icert/`) | band102-integer | `9b12166167627fbe8d088c6cca5eba4bdb8d837c6725c3f30afee495937fe91f` |
| `r475ada3/review/checks/icert/my_s2_lo.txt` | [r475ada3] `review/checks/icert/my_s2_lo.txt`(폴더 `review/checks/icert/`) | band102-integer | `b3093a90603f5b41456a9dbc206b8fa08446dfac69ce31cb215cdc3072c59a7c` |
| `r475ada3/review/checks/icert/my_s2_mid.txt` | [r475ada3] `review/checks/icert/my_s2_mid.txt`(폴더 `review/checks/icert/`) | band102-integer | `f16fd10bcbc7cb8ede4683112f2f97c7725ff17f2275ba27d3c1c6bc0d5b8685` |
| `r475ada3/review/checks/icert/my_strip.txt` | [r475ada3] `review/checks/icert/my_strip.txt`(폴더 `review/checks/icert/`) | band102-integer | `196c0fbb9ef522c76fde44602d8523cfd7f2888db0921d10b39d168032ce0691` |
| `r475ada3/review/checks/icert/rv_cover.py` | [r475ada3] `review/checks/icert/rv_cover.py`(폴더 `review/checks/icert/`) | band102-integer | `b64f2db9c4928f96d3c76be6ca81c7c135b2eea8a2399ee6a6be8f9c6e1f582f` |
| `r475ada3/review/checks/icert/rv_cover_out.txt` | [r475ada3] `review/checks/icert/rv_cover_out.txt`(폴더 `review/checks/icert/`) | band102-integer | `35f5d46cfb1525c91a2c4c191c2642f7216d08277cb6335e88444dde46dacabc` |
| `r475ada3/review/checks/icert/rv_rerun_compare.txt` | [r475ada3] `review/checks/icert/rv_rerun_compare.txt`(폴더 `review/checks/icert/`) | band102-integer | `199def62a6942fb0d3b19e96f257fc64ec14760c6b98c3cf0ba9037a1120d154` |
| `r475ada3/uv_5_19.json` | [r475ada3] `evidence/producer/band/uv_5_19.json` | band102-integer | `f72e575f254f43418b5943ae78e295125156e6b3ea4fffe47096338127de8c1a` |
| `r475ada3/uv_general.py` | [r475ada3] `evidence/peer/repro/uv_general.py` | band102-integer | `43cf662deb14267e75cff8213b086cfe36fb1c80eecafb57852b3c20ce4b7351` |
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
| `r6373c70/exact-rows-300.json` | [r6373c70] `evidence/peer/output/exact-rows-300.json` | exact-n20000 | `deb310f9cdba17f8ba203df70d234865c22857fce1e1191a5c2b5bee83c6d7eb` |
| `r6373c70/exact_rows.py` | [r6373c70] `evidence/peer/code/exact_rows.py` | exact-n20000 | `ab2b6fe8ad97850d22402c8e5821c24b9ba430738acef2622bf631b455db19fb` |
| `r6373c70/my_exact_rows.py` | [r6373c70] `review/evidence/code/my_exact_rows.py` | exact-n20000 | `1f54ed8f982674391bd82de823334cb5f470a9029ddbe57a4208b93548851408` |
| `r6b37c7e/audit_monotone_check.py` | [r6b37c7e] `evidence/peer/audit_monotone_check.py` | band102-integer | `56b3f94445a1befb4669d13d65cb53e926a599b0b571728e3061efcfaf3cc9de` |
| `r6b37c7e/audit_monotone_check.txt` | [r6b37c7e] `evidence/peer/out/audit_monotone_check.txt` | band102-integer | `a57ba2379aa78ff0a0c0ae54662cd42709f96bb16d1468b4bd8c9f62882dd320` |
| `r6b37c7e/audit_param_ext2.py` | [r6b37c7e] `evidence/producer/audit/audit_param_ext2.py` | band102-integer | `75063d44015c4fe6e7974f645cf9a17fb9b492160bf7eefc92b5dfc8b09ad3a6` |
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
| `r6b37c7e/rerun_audit_K14000_nu97_100.txt` | [r6b37c7e] `evidence/peer/out/rerun_audit_K14000_nu97_100.txt` | band102-integer | `e089b980e16d0e9e07c8fac409b5e11cb27012ae212d6f52dcdf550131a883c1` |
| `r6b37c7e/rerun_audit_summary.txt` | [r6b37c7e] `evidence/peer/out/rerun_audit_summary.txt` | band102-integer | `36ee4563d930302e264d047f9972cf6255d321d4dd046a7f3a082512ddefa790` |
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
| `r6b37c7e/uv_general_ext.py` | [r6b37c7e] `evidence/producer/audit/uv_general_ext.py` | band102-integer | `c0c6dc7f4dcc816a8110e63a1e81a87c918a7381a33f868ae716da223913298f` |
| `r81e7051/computation-summary.json` | [r81e7051] `evidence/producer/output/computation-summary.json` | logconcavity-failure-n80 | `cc488c04238c1d0a054898050cd1324836e3d0f1bee90b85864a5c6d8cb4eaa4` |
| `r81e7051/counts.json` | [r81e7051] `evidence/producer/output/counts.json` | logconcavity-failure-n80 | `d6f43779914a31973dbc969590e5088e671c6339db7e2c1930b946d2f0a6dca8` |
| `r81e7051/explore.py` | [r81e7051] `evidence/producer/work/explore.py` | logconcavity-failure-n80 | `746a0aa105ee49e3abf5cd79d455081093407b0792ff48bbf1525645160d68c2` |
| `r81e7051/peer-checks.json` | [r81e7051] `evidence/peer-checks.json` | logconcavity-failure-n80 | `303bcacd5630727b4fbeb5813d4e4c98bb63f8c6d9c3f0e2c7025ee6b761e28c` |
| `r81e7051/peer_verify.py` | [r81e7051] `evidence/peer_verify.py` | logconcavity-failure-n80 | `78ad8795c72c105b5b4db8d0c4cc16f05677668092953473bef4c0042e7b444c` |
| `r81e7051/structure-checks.json` | [r81e7051] `evidence/producer/output/structure-checks.json` | logconcavity-failure-n80 | `4f55114c67a2e90168ee075cba72b0f3d00f7967f9e1b7cae0fd0c20f47c021e` |
| `r8a9b11e/cemaj_iv.py` | [r8a9b11e] `evidence/peer/cemaj_iv.py` | zeta-constants | `1e2efc48b3ca11526501d382fb43885da47a4985bacfffa6c8fccafa02ff4893` |
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
| `rb7effe0/blk3_stats.out` | [rb7effe0] `evidence/code/turn3/blk3_stats.out` | column-certificates-501-2000 | `546611ca1b8587fe2bcc53557979707154bdb0d650fc5b8d83a0fe791264c660` |
| `rb7effe0/blk3_stats.py` | [rb7effe0] `evidence/code/turn3/blk3_stats.py` | column-certificates-501-2000 | `b12173739ab47e24a2ac1fb7e97b465ff59edf982cf7fa50fe8b19e58cddc1f5` |
| `rb7effe0/block3_501_2000_all.json` | [rb7effe0] `evidence/code/turn3/block3_501_2000_all.json` | column-certificates-501-2000 | `0fcac5fef27b255718bf15fd0a91b909d4424a795e7e3444ea43f173a31c21a6` |
| `rb7effe0/certificate3.py` | [rb7effe0] `evidence/code/turn3/certificate3.py` | column-certificates-501-2000 | `11cb014fd1ae66db86767a020956a4b834bce457eee234552980588f8dee2ac6` |
| `rb7effe0/evidence/code/turn3/blk3_stats.out` | [rb7effe0] `evidence/code/turn3/blk3_stats.out`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `546611ca1b8587fe2bcc53557979707154bdb0d650fc5b8d83a0fe791264c660` |
| `rb7effe0/evidence/code/turn3/blk3_stats.py` | [rb7effe0] `evidence/code/turn3/blk3_stats.py`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `b12173739ab47e24a2ac1fb7e97b465ff59edf982cf7fa50fe8b19e58cddc1f5` |
| `rb7effe0/evidence/code/turn3/block3_501_2000_all.json` | [rb7effe0] `evidence/code/turn3/block3_501_2000_all.json`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `0fcac5fef27b255718bf15fd0a91b909d4424a795e7e3444ea43f173a31c21a6` |
| `rb7effe0/evidence/code/turn3/certificate2.py` | [rb7effe0] `evidence/code/turn3/certificate2.py`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `e52f9947538b67220e09822a2e46ba1d735de6add806fea2f3f68813d157c955` |
| `rb7effe0/evidence/code/turn3/certificate3.py` | [rb7effe0] `evidence/code/turn3/certificate3.py`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `11cb014fd1ae66db86767a020956a4b834bce457eee234552980588f8dee2ac6` |
| `rb7effe0/evidence/code/turn3/probe_circle.py` | [rb7effe0] `evidence/code/turn3/probe_circle.py`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `6c8d6a70ee8203c303e8d70e59d9f23835e49e1e36cac28c3811f36198521829` |
| `rb7effe0/evidence/code/turn3/probe_second_zero.out` | [rb7effe0] `evidence/code/turn3/probe_second_zero.out`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `57a175be9de9f8c537dec2dd0f97509481faaf4a52ce33f91d659306faf4b0a6` |
| `rb7effe0/evidence/code/turn3/probe_second_zero.py` | [rb7effe0] `evidence/code/turn3/probe_second_zero.py`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `9f2f504dc9fc9b736495c46c98e9f115f5a75475518ecca74755f8e3cfe1cf6e` |
| `rb7effe0/evidence/code/turn3/samples3.out` | [rb7effe0] `evidence/code/turn3/samples3.out`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `6ad61cc38b1ba57da2f136348e19cc72e8c9f322dd8a4ccf35187b5cbd8003b8` |
| `rb7effe0/evidence/code/turn3/validate_eps3.out` | [rb7effe0] `evidence/code/turn3/validate_eps3.out`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `9efca0abf0d2b5313ce6188214ae1ccd8f24c126a44fb056c487040c0149231c` |
| `rb7effe0/evidence/code/turn3/validate_eps3.py` | [rb7effe0] `evidence/code/turn3/validate_eps3.py`(폴더 `evidence/code/turn3/`) | column-certificates-501-2000 | `e06778b17ecea57bddcd9860a84af47dcf56113109cf32dcf396828aa9e9de1d` |
| `rb7effe0/review/evidence/cert/block_claims.out` | [rb7effe0] `review/evidence/cert/block_claims.out`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `59e30277a2479dbcf41473438e2c3d2ed7ac96602f3b72b77165c932001aafb6` |
| `rb7effe0/review/evidence/cert/block_claims.py` | [rb7effe0] `review/evidence/cert/block_claims.py`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `abd025efe77724798234007d88f706241d1bcbea49fb70e7cc20945bd11c7bae` |
| `rb7effe0/review/evidence/cert/nv_full.out` | [rb7effe0] `review/evidence/cert/nv_full.out`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `5fa2331f69c85fdac6db88b0cecaca8fa27ce7686b4ef85637962ae8aada1fba` |
| `rb7effe0/review/evidence/cert/nv_full.py` | [rb7effe0] `review/evidence/cert/nv_full.py`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `398ae647f72613c55c0d2b4d6e173938c5d94cdea2124385b75640719f2e147c` |
| `rb7effe0/review/evidence/cert/rerun_3000.out` | [rb7effe0] `review/evidence/cert/rerun_3000.out`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `c081f6f71f0cecce2f37fb7e7e43deee3906247268b5d2cd019e8f267a26651f` |
| `rb7effe0/review/evidence/cert/rerun_a.json` | [rb7effe0] `review/evidence/cert/rerun_a.json`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `0a1487aca5085dc1386bc783d59137f4c3b767700d05341a8f8f438909ac1855` |
| `rb7effe0/review/evidence/cert/rerun_b.json` | [rb7effe0] `review/evidence/cert/rerun_b.json`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `a68b7743f676b7b75f469ed15ddc29c8fbd3b347333ec9f141d887c9b6272284` |
| `rb7effe0/review/evidence/cert/rerun_b.out` | [rb7effe0] `review/evidence/cert/rerun_b.out`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `6a7ad9603d88ea0ecb725c081072dccb4a367726baa15ce9e07564eddf236189` |
| `rb7effe0/review/evidence/cert/rerun_big.out` | [rb7effe0] `review/evidence/cert/rerun_big.out`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `93ccf4fa1578b26f35fd484498b6b6fa6dfa2a3f73ad0275c7d6c39d5b01735d` |
| `rb7effe0/review/evidence/cert/rerun_c.json` | [rb7effe0] `review/evidence/cert/rerun_c.json`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `1ea76175589a91b6d03dc0c1e5e1a4075715daddc7b628d0370e986945d9174e` |
| `rb7effe0/review/evidence/cert/rerun_c.out` | [rb7effe0] `review/evidence/cert/rerun_c.out`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `7145f47dbfc96daba87c37347a505d96708807ae484e5ee67939f1f7d4a738be` |
| `rb7effe0/review/evidence/cert/sample10.txt` | [rb7effe0] `review/evidence/cert/sample10.txt`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `98c193b66b74f04940747cb1884509e9f75c4689fd2c882abd02366ded23af5c` |
| `rb7effe0/review/evidence/cert/sample_ks.txt` | [rb7effe0] `review/evidence/cert/sample_ks.txt`(폴더 `review/evidence/cert/`) | column-certificates-501-2000 | `be7d8ea4460f27c44b35572ae40be7f28e76123b7af6c49d1d26ba50a30dd59b` |
| `rb7effe0/review/evidence/check/bf_gf.out` | [rb7effe0] `review/evidence/check/bf_gf.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `85758fb4efc578bde90fc112bc4e2706d0b860b0f717a3b148d95f5fb2fd259a` |
| `rb7effe0/review/evidence/check/bf_gf.py` | [rb7effe0] `review/evidence/check/bf_gf.py`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `3e4e68b54328afe3404f85ff65fafa097ff724ecbeac057455306234ebcc052d` |
| `rb7effe0/review/evidence/check/e2e_sign.out` | [rb7effe0] `review/evidence/check/e2e_sign.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `98ce30d3ed55f07e8b0631d64f32edb96d5881ed63ff83eea201d84a64874ab2` |
| `rb7effe0/review/evidence/check/e2e_sign.py` | [rb7effe0] `review/evidence/check/e2e_sign.py`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `0e7f45a04125fe133103e6826841e920310e47de3a50d2db306c3c596bdc99d1` |
| `rb7effe0/review/evidence/check/finite_check.py` | [rb7effe0] `review/evidence/check/finite_check.py`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `3446088d764d86d5350b709d2854b8ac71bf6c02c38893db876ee88de92516d9` |
| `rb7effe0/review/evidence/check/finite_check_1000.out` | [rb7effe0] `review/evidence/check/finite_check_1000.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `353316e195283bbb8f0934c570dfa3150360f618d472ee34f63b346c510e008a` |
| `rb7effe0/review/evidence/check/finite_check_501.out` | [rb7effe0] `review/evidence/check/finite_check_501.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `02df88bce0d31a983b12873b015b18dda159983cb53bea1ee732593ae8febed3` |
| `rb7effe0/review/evidence/check/finite_check_840.out` | [rb7effe0] `review/evidence/check/finite_check_840.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `3f724baa41872110ec26b08b8401136c15cc38857b4ab7ae1e05da835d6de397` |
| `rb7effe0/review/evidence/check/fullprec.out` | [rb7effe0] `review/evidence/check/fullprec.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `04128353f33abba0d616ecbf6955ca2c3576b6bf7cbccee1c29943c88dc997fa` |
| `rb7effe0/review/evidence/check/fullprec.py` | [rb7effe0] `review/evidence/check/fullprec.py`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `26b7795075a96f872dbca3e685a327bcc89647f63529bbd99cbccca1b6957d26` |
| `rb7effe0/review/evidence/check/indep_1000.out` | [rb7effe0] `review/evidence/check/indep_1000.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `04bce255caaa01f83425d61cb3d7fa0504bd8667f0e9490445f249c45c03e510` |
| `rb7effe0/review/evidence/check/indep_501.out` | [rb7effe0] `review/evidence/check/indep_501.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `c6733b52c5cf3c2b81c36d6172751e928329ab2d1af809ce257d452e1a2a39f7` |
| `rb7effe0/review/evidence/check/indep_840.out` | [rb7effe0] `review/evidence/check/indep_840.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `c65a096a6d4991dbdfa971d8631bb28cfd2ceca50da9bda59dc460f45cc9894f` |
| `rb7effe0/review/evidence/check/indep_col.py` | [rb7effe0] `review/evidence/check/indep_col.py`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `9a33255a88379807d28a4ae45ccb6e109d2141f60f7d3fa40b08cc01f8411575` |
| `rb7effe0/review/evidence/check/misc_numbers.out` | [rb7effe0] `review/evidence/check/misc_numbers.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `bb53937350bd8c4d0eca01ba8b8f73d4d6156aee51a2de8714dedecda242c953` |
| `rb7effe0/review/evidence/check/misc_numbers.py` | [rb7effe0] `review/evidence/check/misc_numbers.py`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `cedc91bbaf77f95f45bef2f8897a09dd6b47e2821fcd14be027bb2fa46c4fdfc` |
| `rb7effe0/review/evidence/check/small_k_limits.out` | [rb7effe0] `review/evidence/check/small_k_limits.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `f4964f26f4cd74b8339e5d69fbf33de6819b7904ba94a5fc5611261a27f8988e` |
| `rb7effe0/review/evidence/check/small_k_limits.py` | [rb7effe0] `review/evidence/check/small_k_limits.py`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `44090cb13f7ceaf519539c06b071e3d2d841dc9b124a5b402c44ce85cb4bd051` |
| `rb7effe0/review/evidence/check/zero2.out` | [rb7effe0] `review/evidence/check/zero2.out`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `9d729ae3eea2afb727b35a4c1160d44425213681abecba1c800c19d0b78ca1c9` |
| `rb7effe0/review/evidence/check/zero2.py` | [rb7effe0] `review/evidence/check/zero2.py`(폴더 `review/evidence/check/`) | column-certificates-501-2000 | `23e65a6e8c2d6dcc540be1cf52f60b1b69537b0d8a95280eb3c4202e31690c8d` |
| `rb7effe0/samples3.out` | [rb7effe0] `evidence/code/turn3/samples3.out` | column-certificates-501-2000 | `6ad61cc38b1ba57da2f136348e19cc72e8c9f322dd8a4ccf35187b5cbd8003b8` |
| `rb7effe0/validate_eps3.out` | [rb7effe0] `evidence/code/turn3/validate_eps3.out` | column-certificates-501-2000 | `9efca0abf0d2b5313ce6188214ae1ccd8f24c126a44fb056c487040c0149231c` |
| `rb7effe0/validate_eps3.py` | [rb7effe0] `evidence/code/turn3/validate_eps3.py` | column-certificates-501-2000 | `e06778b17ecea57bddcd9860a84af47dcf56113109cf32dcf396828aa9e9de1d` |
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
| `rc9aee43/indep-rowwise-10000.json` | [rc9aee43] `evidence/peer/output/indep-rowwise-10000.json` | exact-n20000 | `544a624abd01cc84d099461e858c3e861847d152fe43018f97d5ea876151ff4d` |
| `rc9aee43/indep_lastcar.py` | [rc9aee43] `evidence/peer/code/indep_lastcar.py` | exact-n20000 | `25b2af15b9ed44c7c115c6c7621fc62ac3db1da4274e233d636d494bb7a0bff5` |
| `rc9aee43/indep_rowwise.py` | [rc9aee43] `evidence/peer/code/indep_rowwise.py` | exact-n20000 | `6621258c870a679ede89c9e17172f19ec43f4e51cc2455529749328a5328b3af` |
| `rc9aee43/positive_columns.py` | [rc9aee43] `evidence/producer/code/positive_columns.py` | exact-n20000 | `2f1841a9bd301cfa541c3877e50ae0dfac10d84ed0b8434d3c3e35dff0c8065b` |
| `rc9aee43/producer_positive_columns.py` | [rc9aee43] `evidence/peer/code/producer_positive_columns.py` | column-certification-k500 | `2f1841a9bd301cfa541c3877e50ae0dfac10d84ed0b8434d3c3e35dff0c8065b` |
| `rc9aee43/rerun-k500.json` | [rc9aee43] `review/evidence/rerun-k500.json` | exact-n20000 | `05a2a14bf32ebfa4c85247bfe88a0a832a8ade478dcc5abf9855bba0bb1f65d3` |
| `rc9aee43/rev-col-k150.json` | [rc9aee43] `review/evidence/rev-col-k150.json` | exact-n20000 | `dc3d0295ce0f3137af132724276dd10843534776742c8f177931aaa835cea30a` |
| `rc9aee43/rev-col-k200.json` | [rc9aee43] `review/evidence/rev-col-k200.json` | exact-n20000 | `d70b4cd57c0cf837ebe38943fbcb9ce4c4586473b6215467df9c209d4f890acc` |
| `rc9aee43/rev-rows-a.json` | [rc9aee43] `review/evidence/rev-rows-a.json` | exact-n20000 | `32e9f5042510bd734e4aa53946116f9b05c62252fffd70dadf2a299a6fb08a29` |
| `rc9aee43/rev_column_full.py` | [rc9aee43] `review/evidence/rev_column_full.py` | column-certification-k500 | `180d7dad463edf065e907e78709d37e3cb74237b922903b4ed5769dbd6474d4a` |
| `rc9aee43/rev_interval.py` | [rc9aee43] `review/evidence/rev_interval.py` | exact-n20000 | `76a90d1a7e4d33654cdc28f8bf81a0f54f6162b8b02b115c58a93852d6191323` |
| `rc9aee43/rev_rows.py` | [rc9aee43] `review/evidence/rev_rows.py` | exact-n20000 | `d21e7ccb69e52f23785d6c97a50b542a65caaa9b96d2af0cbac140342cae8a15` |
| `rc9aee43/review__evidence__rerun-k500.json` | [rc9aee43] `review/evidence/rerun-k500.json` | column-certification-k500 | `05a2a14bf32ebfa4c85247bfe88a0a832a8ade478dcc5abf9855bba0bb1f65d3` |
| `rc9aee43/review__evidence__rev-col-k150.json` | [rc9aee43] `review/evidence/rev-col-k150.json` | column-certification-k500 | `dc3d0295ce0f3137af132724276dd10843534776742c8f177931aaa835cea30a` |
| `rc9aee43/review__evidence__rev-col-k200.json` | [rc9aee43] `review/evidence/rev-col-k200.json` | column-certification-k500 | `d70b4cd57c0cf837ebe38943fbcb9ce4c4586473b6215467df9c209d4f890acc` |
| `rc9aee43/review__evidence__rev_interval.py` | [rc9aee43] `review/evidence/rev_interval.py` | column-certification-k500 | `76a90d1a7e4d33654cdc28f8bf81a0f54f6162b8b02b115c58a93852d6191323` |
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
| `rce3dc75/evidence__peer__icert__icert.c` | [rce3dc75] `evidence/peer/icert/icert.c` | exact-n20000 | `f749602de27b8cf6bbcbe915d6d17ed5eecec9eb5a1dda40a7709e06f5b64d02` |
| `rce3dc75/evidence__peer__icert__icert_summary.json` | [rce3dc75] `evidence/peer/icert/icert_summary.json` | exact-n20000 | `3d00c51ad261b9fb06b02dfbd38f6639a60fe6925784ee01247d7c4ae19bb231` |
| `rce3dc75/evidence__peer__icert__out_8_10000.txt` | [rce3dc75] `evidence/peer/icert/out_8_10000.txt` | exact-n20000 | `f4f11f36eff2745672fe2ae39a407a851ddc7d9dd4e0b4d6f11fbeb611587f6e` |
| `rce3dc75/exact-first-constant.json` | [rce3dc75] `evidence/producer/output/exact-first-constant.json` | central-gap-rational-audit | `f23934a0f2faa41f42cf0fa1f8e9c64f04e0534cca66bfb70ff1ef0fe9128320` |
| `rce3dc75/exact_first_constant.py` | [rce3dc75] `evidence/producer/work/exact_first_constant.py` | central-gap-rational-audit | `f87de0a05ede42fae150d9b9cde2852a55539ef786c35389827bbdfece6d6eaf` |
| `rce3dc75/hermite-series.json` | [rce3dc75] `evidence/producer/output/hermite-series.json` | central-gap-rational-audit | `296ee4046281f4d81e38cdfb9c40da1f1e271201ec977eb1ad92553ce13b27a8` |
| `rce3dc75/hermite_laurent.py` | [rce3dc75] `evidence/producer/work/hermite_laurent.py` | central-gap-rational-audit | `c24efd21e48ebb538ad4d7e24ea0e1ab35d2567e517ac87ecbbd9a7d1e79c7db` |
| `rce3dc75/hermite_series.py` | [rce3dc75] `evidence/producer/work/hermite_series.py` | central-gap-rational-audit | `39ec31386a3739600f2f117d85b9b5cf298deb55b8bcfa756a20490cbc408c9d` |
| `rce3dc75/icert.c` | [rce3dc75] `evidence/peer/icert/icert.c` | central-gap-integer | `f749602de27b8cf6bbcbe915d6d17ed5eecec9eb5a1dda40a7709e06f5b64d02` |
| `rce3dc75/icert_py.py` | [rce3dc75] `evidence/peer/icert/icert_py.py` | central-gap-integer | `3bcfcbcf96adb9d86753e205ca99ec697db3247f68a1fb6ae86d00454d2cc5bf` |
| `rce3dc75/icert_summary.json` | [rce3dc75] `evidence/peer/icert/icert_summary.json` | central-gap-integer | `3d00c51ad261b9fb06b02dfbd38f6639a60fe6925784ee01247d7c4ae19bb231` |
| `rce3dc75/make_rtable.py` | [rce3dc75] `evidence/peer/icert/make_rtable.py` | central-gap-integer | `2f934f002724e82813b5a46aa3f8781eee36a8ed9a77dbfd2415b5f2417543b4` |
| `rce3dc75/out_8_10000.txt` | [rce3dc75] `evidence/peer/icert/out_8_10000.txt` | central-gap-integer | `f4f11f36eff2745672fe2ae39a407a851ddc7d9dd4e0b4d6f11fbeb611587f6e` |
| `rce3dc75/out_small.txt` | [rce3dc75] `evidence/peer/icert/out_small.txt` | central-gap-integer | `7910bcee805edf646a9fed09bb410d2d7c8d56885d9458384e0724612d23a94e` |
| `rce3dc75/pyref_compare.json` | [rce3dc75] `evidence/peer/icert/pyref_compare.json` | central-gap-integer | `5f3a60c02d809da65951ece5d5227e36a971acd6030014822cb67e3307855e18` |
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
| `rce3dc75/v_hermite_k10000_out.json` | [rce3dc75] `evidence/peer/data/v_hermite_k10000_out.json` | central-gap-rational-audit | `ad40d6ad2c55a5257d81d21465fcf6ecec2e0aab1a0b30418223bac00ba4a22a` |
| `rce3dc75/v_majorants_K1.py` | [rce3dc75] `evidence/peer/code/v_majorants_K1.py` | central-gap-rational-audit | `a0fd6b9b32991954783c053edefd0b6060471b3a952e71c3eef652abeb2cfafb` |
| `rce3dc75/v_small_rows.py` | [rce3dc75] `evidence/peer/code/v_small_rows.py` | central-gap-integer | `eec704e5b065ee4c6c7fdbac37fb58a6fca6b0fda5574d0db9ca55ff3ce7d043` |
| `rce3dc75/v_small_rows_out.json` | [rce3dc75] `evidence/peer/data/v_small_rows_out.json` | central-gap-integer | `f5294f5642c795ac4badea6fb498a53e458cf59e64cf0b53ca70307dc17c9522` |
| `rce3dc75/v_uhat_series.py` | [rce3dc75] `evidence/peer/code/v_uhat_series.py` | central-gap-rational-audit | `0136172ff03e16c05d9ae3dec89bb4a27d7ff71bd08c48aa003669c8821f3300` |
| `rce3dc75/validate_small.py` | [rce3dc75] `evidence/peer/icert/validate_small.py` | central-gap-integer | `0ab18b42c52c301b67bee4d4f99026352450bd1345bb4e698580556cdb4a9af5` |
| `rce3dc75/vertical-exact-constant.json` | [rce3dc75] `evidence/producer/output/vertical-exact-constant.json` | central-gap-rational-audit | `8764a5d03bbccef82522de9a9001f30497c4dd230bb2c07474cfcdb2cdbb3104` |
| `rce3dc75/vertical_exact_constant.py` | [rce3dc75] `evidence/producer/work/vertical_exact_constant.py` | central-gap-rational-audit | `18328acb05ba4490e218da6c030faea628bbe59533083ec74231bd70603a4749` |
| `re71a735/bulk_majorants.py` | [re71a735] `evidence/peer/bulk_majorants.py` | four-families | `d1dd683c1a6cbf4cc9759af5b24d63ad5737303a6fbdc1a5ce6e7ecf397b3a70` |
| `re71a735/cf.py` | [re71a735] `evidence/peer/cf.py` | four-families | `6b66c9bfd89fdfdebd1caf623c4a6b56b18ee9c92edc6f37b8d6bcdce56ddbb0` |
| `re71a735/edge_checks.py` | [re71a735] `evidence/peer/edge_checks.py` | four-families | `3128a79f35081ea2b2fc51cfad159c815dfd243dff99bde2a3441f8dda6eb082` |
| `re71a735/edge_checks_out.txt` | [re71a735] `evidence/peer/edge_checks_out.txt` | four-families | `749e36f16451ba934218b87c203fbbcf2eecf49bee500b2b4de0262793d5b2ce` |
| `re71a735/edge_mono.py` | [re71a735] `evidence/peer/edge_mono.py` | four-families | `f21fabada2293be7ad7103e92666d3f6b1258dfcbdab173ec61239f5ab43cd1c` |
| `re71a735/families.py` | [re71a735] `evidence/peer/families.py` | four-families | `4c85b69e74bd9f675ef3e180ff179a2464a4f1c74656abc50da50a9703d6e482` |
| `re71a735/families_out.txt` | [re71a735] `evidence/peer/families_out.txt` | four-families | `cad700545012ba6f3e6a30823b486f82ade4a7e145b1a573733d16f47ca92a95` |
| `re71a735/flq_checks_out.txt` | [re71a735] `evidence/peer/flq_checks_out.txt` | four-families | `f59d6364944fa236305d7b0952c84c8f89a813136e5508a28e65f81d6fcef346` |
| `re71a735/flq_uniform.py` | [re71a735] `evidence/peer/flq_uniform.py` | four-families | `9d6101c1ac449defd56c88e837078f3c65c36ef0d9cff9b93fa0b4265cf40b65` |
| `re71a735/recheck_1a.py` | [re71a735] `evidence/peer/recheck_1a.py` | four-families | `8c49a8dfe698d663de195371cfacee06dd96bf793827a9937d3cfbd8daae9557` |
| `re71a735/recheck_1a_out.txt` | [re71a735] `evidence/peer/recheck_1a_out.txt` | four-families | `415843f91a3ba2930dbd2a9e11eae46289472d7d1e4e912a0a8636ffe38b83f6` |
| `re71a735/run_flq_checks.py` | [re71a735] `evidence/peer/run_flq_checks.py` | four-families | `307506c8508aa918db1458034ca66751f7fd16d6931cf75182c4a8092fea81b3` |
| `re71a735/thmC_float.py` | [re71a735] `evidence/peer/thmC_float.py` | four-families | `32cab62a1b6da0aa6c7b04ef3329edee50df718bd6e800733ede2a78a7ea69cd` |
| `re71a735/window_checks.py` | [re71a735] `evidence/peer/window_checks.py` | four-families | `10032646bf49101fafb356b43be08817008efcd78b2d5b4111f62f3dc9bc2da8` |
| `re71a735/window_checks_out.txt` | [re71a735] `evidence/peer/window_checks_out.txt` | four-families | `0de2be56040f3ff799bb65e777da158af6cd23dbcb26125ecef2873335c27891` |
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
