# 구조 압축 수리 V7a — 자료 묶음과 스크립트의 정리(9장 제거 물결, 세션 몫 가운데 작업자 몫; 2026-11-17 12:3x–13:xx)

## 1. 읽은 범위

- 파견문 `파견/구조압축_9장제거_파견문_1117.md` 1절·8절·9절 전문; 공통 안내 `파견/구조압축_수리_공통_1117.md` 2.8절·5절·6절·8절.
- 인계: `인계_H1.md` 「세션」 절 1–9항, `인계_U14.md` 「세션(먼저)」 절, `인계_V1.md` 「세션(V7)」 절, `인계_V3.md` 「세션」 절, `인계_V5.md` 「세션(V7·파이프라인·임자 없는 스크립트)」 절, `인계_V2.md` 「세션(V7)」 절, `인계_H1.md` 표 2, `인계_U14.md` 표 2. 결정 문서 `결정_K6_9장10장.md` 5.3절. `대조v2/장부_설계_세션결정.md` 결정 122·130.
- 현행 부록 D 아홉 파일(`장v2/부록D_장2·3·4·5A·5B(0바이트)·6(0바이트)·7A·7B·8·10.md`)의 「자료」 줄 전부와 머리 16개, `장v2/장11.md` 11.2 표 16행 — `원고_자료/세션_재계산/<폴더>` 토큰을 기계로 뽑고(아래 2.1) 그 자리들을 원문으로 읽었다.
- 내 파일 전문: `원고_자료/README.md`(2,026행; 표 밖 139행은 전문, 두 표는 기계로 열고 행별로 확인), `원고_자료/빠른_확인.py`(289행), `scripts/_gen_재실행표.py`(576행), `scripts/_재실행표_여유.json`(44행), `scripts/명세v2_META.py`(361행), `scripts/_의존_도달.py`(269행), `scripts/_patch_README_세션파일.py`(142행; README SHA 표의 등록 스크립트), `scripts/자료묶음_v2.py`(260행; 「파일 목록」 표의 생성기), `원고_자료/세션_재계산/*/make_draft*.py`의 라벨 자리, `원고_자료/세션_재계산/rerun_exactgrid_1116.sh`, `band_boxes/band_iv.py` 머리, `bprime_boxes/ivbox_lib.py`의 파일 읽기 자리, `four_families_DDLnat/결과_요약.md`·`변경.md`, 파이프라인 `scripts/_보관_tmp/_파이프라인_수리후_1115.sh`.
- 돌린 것(모두 읽기 전용이거나 임시 경로에 쓰는 것): `python -I scripts/자료묶음_v2.py --dry`; 자료묶음의 `collect()`로 「파일 목록」 표의 기대 행 집합을 계산해 현행 표와 대조; `python -I scripts/_의존_도달.py --d`; `python -I scripts/_gen_재실행표.py --out <임시 경로>`; `python -I 빠른_확인.py --list`; `band_boxes/band_summary.py`(저장값 읽기만, 1초; 임시 경로로 출력); `python -I -B 빠른_확인.py`(기본 14항목; 결과 아래 7절); `git ls-files`·`git status`·`git diff --numstat`.

## 2. 사안별 판단과 처리

### 2.1 보관할 폴더(파견문 9절 1항)

- **센 것.** 현행 부록 D 「자료」 줄과 11.2 표가 가리키는 `세션_재계산/` 경로를 정규식으로 뽑으면 폴더 16: `band_boxes`(`band_iv.py`), `bprime_boxes`(`ivbox_lib.py`만), `c50_iv`, `column_cert_iv`, `column_k500_iv/`, `critical_window_rerun/`, `four_families_DDLnat`, `icert_py_full`, `left_columns_k2_120`, `logconcavity_n80`, `moment_cert_iv`(27 파일), `r030ffae_window/work`, `window_mass_env`, `witness_offset_iv`, `zeta_constants`, 그리고 파일 `rerun_exactgrid_1116.sh`. 11.2 표는 `세션_재계산/`을 직접 가리키지 않는다(꺾쇠 「자료 이 글」로만). 디스크의 폴더 37 가운데 가리키지 않는 것은 **21**: 세션의 후보 스물에 `r8a9b11e`가 더해진다 — 파견문의 「`r8a9b11e`는 `D:zeta-constants` 출처」는 기록 폴더 `원고_자료/r8a9b11e/`(`records/r8a9b11e…/evidence/peer/cemaj_iv.py`)를 두고 한 말이고, `세션_재계산/r8a9b11e/`(`ul_iv_fixed.py`와 출력 둘)는 U14가 지운 `D:window-mass-constant`의 수정판 코드라 어느 항목도 가리키지 않는다(U14 인계 세션 절 3항의 「`r8a9b11e*`(옛 5B)」가 이것).
- **부품 가름.** `band_iv.py` 17–20행이 `../bprime_boxes`를 `sys.path`에 넣고 `ivbox_lib`를 import하며, `ivbox_lib.py` 32·178·181행은 `../r030ffae_window/work`의 `qenv_fix_*.npy`를, 219행은 `../window_mass_env/ia.py`를 읽는다 — 셋 다 남는 폴더다. `bprime_boxes`의 나머지(`bprime_iv.py`·`bprime_summary.py`·`compare_record.py`·`test_lib.py`·상자 JSON/NPY·로그·출력, 17 파일)는 지워진 `D:bprime-boxes`의 것이라 옮겼다. 남는 폴더 사이의 import는 그 밖에 `band_boxes/compare_record.py`→`ivbox_lib`뿐이고, 옮긴 폴더를 import하는 남는 스크립트는 없다(`import`·`sys.path`·`../` 전수: `four_families_DDLnat/families_iv.py` 12행의 `../M_natural/j_integrals_iv.py`는 docstring 주석이지 import가 아니다; 23–28행의 import는 표준·numpy·mpmath뿐).
- **`band_boxes/readout_front.py`·`readout_front_out.txt`.** V3가 `D:band-boxes` (나)를 지워 부록 D가 더 가리키지 않는다(V3 인계 세션 절 1항). 둘 다 git이 추적하던 파일이라 `mv` 뒤 `git status`에 D로 보인다(`git rm`은 세션).
- **한 일.** `shutil.move`로 `대조v2/보관_재계산_옛판_1117/` 아래에 같은 이름으로 옮겼다(결정 130 (ㄴ)의 `보관_재계산_옛판_1116/` 선례). 폴더 21 전부 + `bprime_boxes/`의 17 파일 + `band_boxes/readout_front.*` 2 = **253 파일, 21,807,028바이트**(폴더별 수는 인계 표). `__pycache__`는 옮기지 않았다. 보관 폴더에 `README.md` 한 장(어느 항목의 것이었고 어느 단위가 그 항목을 지웠는지의 표)을 두었다.
- **확인.** 옮긴 뒤 `band_boxes/band_summary.py`를 돌려(저장된 `box_*`·`tail_*`만 읽음, 1초) 출력이 `band_result.txt`와 줄 끝만 빼고 같음을 확인했다 — `ivbox_lib` import 경로가 살아 있다.
- **둔 것 — `rerun_exactgrid_1116.sh`.** `D:band-boxes` 「자료」 줄이 「실행 순서」로 가리키는 이 스크립트는 전반부에서 `bprime_boxes/`의 `test_lib.py`·`bprime_iv.py`·`bprime_summary.py`·`compare_record.py`를 부른다. 옮긴 뒤 그 줄들은 없는 파일을 가리킨다. 계산 폴더 파일이라 고치지 않았고 세션에 넘긴다(인계 세션 절 3항; 선택지는 bprime 줄을 걷어 내기 / 실행 기록으로 두기).

### 2.2 README(9절 2항)

- **SHA 표(「세션이 만든 수정판」).** 옮긴 경로의 행 218을 걷었다(599행 → 383행). `four_families_DDLnat/families_iv.py`·`families_iv_out.txt`의 행이 없었으므로(V1이 부록 D에 올린 뒤 등록되지 않음) SHA-256을 계산해 두 행을 더했다.
- **설명 문단.** 옮긴 폴더의 문단 15를 걷었다(그 가운데 700행 `M_natural/j_integrals.py` 문단은 디스크에 없던 파일을 적은 묵은 문단). `bprime_boxes` 문단을 `ivbox_lib.py`만의 문단으로 다시 썼고(구간 산술 서술과 $\Omega$·봉투 표 읽기 방식은 그대로), `band_boxes` 문단의 「`bprime_boxes/ivbox_lib.py`를 통해 같은 정확 정의」·「두 폴더의 재실행 순서」를 한 폴더의 말로, `column_cert_iv` 문단의 「열 841–2000 열별 갱신 인증서 항목」을 「열 $501\le k\le2000$의」로 고쳤다. `four_families_DDLnat` 문단을 새로 적었다(`결과_요약.md`·`변경.md`에서 읽은 사실만: 2026-11-17, 93초, 바뀐 함수 `DDL` 하나).
- **절 머리(94행).** `ul_iv_fixed.py`(지워진 `D:window-mass-constant`) 이야기였던 절 머리를 `세션_재계산/`의 일반 설명 두 문장으로 바꿨다.
- **「처음 돌려 볼 것」(5–16행).** 여섯 행 가운데 지워진 항목의 넷(`fiber_exhaustive`·`prop_W_thirteen`·`cumulative_logconcavity_n779`·`band_check`)을 걷어 두 행(n80·제타)만 남기고 머리 문장을 「두 검산」으로, 「현재 폴더에 작은 파일을 쓰는 것이 있으므로 빈 작업 폴더에서」는 남는 둘이 파일을 쓰지 않으므로(`open(` 0) 뺐다. 16행의 「다섯째 줄은 누적 로그오목성 …」 문장을 뺐다.
- **「실행 환경」(46–53행).** 51행 `np.ldexp` 문단(`band_LP/bandlib.py`만의 사정)을 뺐고(V1 인계), 50행 `math.nextafter` 문단에서 옮긴 `Q_fin_1130/*` 두 파일 이름을 뺐다. 네 환경의 표는 그 전의 항목 구성(기본 32개)에서 잰 측정값이라 그대로 두고, 46행을 「네 줄은 모두 그 전의 항목 구성(기본 32개)에서 잰 것이다 … 지금의 구성은 …」로 다시 적어 지금의 구성과 이번 실행 결과(아래 7절)를 적었다. 53행의 「Windows에서는 numpy 2 이상도 필요하다」는 `band_LP`에서 온 요구라 뺐고, 「열 판독 항목(`--all`에서만 돈다) … 212초」 문장(지워진 `m1_column_reading`)을 뺐다.
- **「컴파일 옵션」 표 68행.** `qr_cert2.c` 행의 항목 열에서 `D.{{D:m1-column-reading}}`을 뺐다(`D.{{D:exact-n20000}} (ㄹ)`만 남음).
- **「재실행표와 빠른 확인」(84–90행).** 84행의 `--all` 설명(열 판독)과 「기본 실행(긴 항목을 뺀 32개) … 520초 … 약 12분」을 지금의 구성과 이번 실행값으로; 「축소 인자」 목록에서 `band_LP`·`cumulative_logconcavity_n779`·`r89eb039_polar` 세 줄을 뺐다.
- **「파일 목록」 표(756–2024행).** 이 표는 `scripts/자료묶음_v2.py`가 부록 D 「자료」 줄에서 만든다(기록 파일의 사본과 SHA). 생성기의 `collect()`와 `main()`의 행 만들기를 그대로 재현해(복사만 하지 않음) 기대 행 614를 얻었고, 현행 1,265행과 대조하니 **빠질 행 629, 더할 행 0, 라벨이 바뀌는 행 61**(`column-certificates-841-2000`→`501-2000` 52, `bprime-boxes`→`band-boxes` 2(`wKrig.npy`·`xKrig.npy`), `fiber-enumeration`→`logconcavity-failure-n80` 4(r81e7051의 `explore.py` 등), `M-natural-integrals`→`four-families` 2(re71a735의 `cf.py`·`recheck_1a.py`)), SHA가 다른 행 0, 묶음에 없는 파일 0이었다. 생성기가 쓸 표 그대로를 썼다(`--dry`는 「항목 320, 복사 614, 문제 0」). 복사는 하지 않았다(필요한 파일이 모두 이미 묶음에 있다).
- **등록 스크립트 `scripts/_patch_README_세션파일.py`.** `PARAS`(폴더별 설명 문단의 정본)에서 옮긴 폴더의 문단 14를 빼고, `bprime_boxes/bprime_iv.py` 항목을 `bprime_boxes/ivbox_lib.py` 항목으로, `band_boxes`·`column_cert_iv` 문단을 README와 같은 새 글로, `four_families_DDLnat/families_iv.py` 문단을 더했다(README의 문단과 같은 글). 이로써 다시 돌려도 옮긴 폴더를 다시 등록하지 않는다. 파견문이 든 `scripts/_readme_sha_mismatch_1116.py`는 없다.
- **전수.** README에서 「9장」·「첫째 증명」·「둘째 증명」·「두 증명」·지운 D 라벨 27개·개명 전 이름·옮긴 폴더 이름·`readout_front`·`1.009` 모두 0(아래 7절). `band_check`가 두 번 남는 649행은 기록 파일 `r475ada3/out_band_check.txt`(`D:band102-integer`의 자료)의 이름이다.

### 2.3 `빠른_확인.py`(9절 3항)

- 항목 33 가운데 지워진 항목의 19를 뺐다: 9장 쪽 다섯(`머리합-여유`·`열-판독`·`띠LP-가나`·`띠LP-다-최소근처`·`띠LP-라-최소근처`), H1의 아홉에 속하는 여섯(`열세-항`·`정리D-기저`·`Q_fin-두열`·`Q_fin-정확정수`·`극영역-첫구간`·`정리U-상수`), U14의 열넷에 속하는 여덟(`섬유-전수`·`띠-검사`·`띠-검사-기록코드`·`띠-검사-판독`·`B'-상자-최악`·`B'-꼬리`·`누적로그오목-780창`·`Newton-r60`). 남은 14: n80, 제타, 창질량 셋, 띠상자 다섯, 모멘트-열840, 열인증-841, C구간 둘.
- `열인증-841`의 `label`을 `column-certificates-501-2000`으로(항목 이름과 `--ks 841-841`은 계산 범위라 그대로). 띠상자 다섯의 기대 문자열(111·123행 등)은 계산된 값이라 그대로이고 「threshold」를 적는 자리는 없다.
- docstring의 `--all` 설명에서 「열 판독 약 3–4분」을 빼고 「지금의 항목 구성에는 없다」로. `--all`·`long` 기제 자체는 두었다.
- 돌린 결과: 아래 7절(기본 14항목 전부).

### 2.4 재실행표 생성기와 여유 JSON(9절 4항)

- `CONFIG`에서 지워진 항목 19의 행을 뺐다(9장 셋 `H-star-plus-interval`·`band-LP`·`pair-one-variable`, 이미 죽은 `AR-integrals`·`m1-column-reading`, H1의 `theorem-U-constant`·`theorem-D-base`·`prop-W-thirteen`·`xcert-partAB`·`polar-blocks-488`·`Q-fin-1130`, U14의 `fiber-enumeration`·`fiber-nonunimodal-bound`·`cumulative-logconcavity`·`newton-m170`·`window-mass-constant`·`band-check`·`bprime-boxes`·`M-natural-integrals`). 키 `column-certificates-841-2000`→`column-certificates-501-2000`(그 행의 명령에는 `--ks 501-840` 실행 둘과 `summary.py 501-2000`이 이미 들어 있었다 — H1 인계 4항이 적은 대로의 꼴). `four-families` 행의 경로를 `four_families/`→`four_families_DDLnat/`로(부록 D가 가리키는 재계산 폴더).
- `_재실행표_여유.json`: 현행 16 밖의 키 26을 빼고 `column-certificates-841-2000` 키를 개명. `band-boxes` 행은 세션이 12:2x에 고친 「$1.0097628$ 대 문턱 $1$(상자 하계 최솟값; 여유 $0.976\%$)」 그대로임을 확인(바꾸지 않음).
- `python -I scripts/_gen_재실행표.py --out <임시>`: 「항목 16개, 진행 중 0개, README 표에 없는 출력 0개」; 표의 16행이 11.2 표의 16 라벨과 순서까지 같고, 행 안에 「(계산 뒤 채움)」·「(인자 확인 필요)」·「(묶음에 없음)」 0. `원고_자료/재실행표.md`(42행)는 쓰지 않았다(세션 파이프라인).

### 2.5 `scripts/명세v2_META.py`(9절 5항)

- **읽는 쪽.** `grep`으로 `명세v2_META`를 import하거나 이름을 든 스크립트는 지난 루프의 일회성 패치(`_patch_META_*.py`·`_patch_1장_*.py`·`_patch_5장_*.py`·`_patch_8장_봉투기록.py`·`_sweep_식별자.py`)뿐이고 `조립_v2.py`·`_gen_의존지도_1절.py`·생성기는 읽지 않는다. 따라서 **11장 절 사전(`{"11.3": "공유 입력과 고유 입력", "11.4": "문헌"}`)과 7.8 intro의 「11.3을 가리키는 한 문장」은 설계 기록으로 그대로 두었다**(파견문의 지시대로).
- **한 것.** (ㄱ) `META[9]` 전체(제목·범위·경중·절 사전·intros·order·D_items)와 `EXTRA_NOTES[9]`, `EXTRA_NOTES.setdefault(9, …)` 한 줄을 지웠다(「9장 삭제」만 반영; 10·11장 번호는 그대로). (ㄴ) `D_items`에서 지워진 라벨 16을 뺐다 — H1의 아홉 가운데 있던 여덟(`theorem-U-constant`·`theorem-D-base`·`prop-W-thirteen`·`seed-certificates-k120`·`self-consistent-constants`·`xcert-partAB`·`polar-blocks-488`·`Q-fin-1130`; `tilt-sum-small-k`는 META에 없었음), U14의 열넷 가운데 있던 여덟(`fiber-enumeration`·`fiber-nonunimodal-bound`·`cumulative-logconcavity`·`crossing-small-n`·`newton-m170`·`tail-T1-partAB`·`bernstein-signs`·`M-natural-integrals`; 나머지는 META[9]와 함께 지워졌거나 META에 없었음). (ㄷ) `band102-integer`의 `for`를 `{{7:old-6-13}}`에서 `{{4:analytic-transfer}}·{{7:integer-strips}}·{{4:hermite-nu}}`로, `moment-certification`의 `for`를 `{{7:theorem-C-moment}}`에서 `{{7:old-6-9}}`로. (ㄹ) 7.8 intro의 「9장·10장이 각각 그것을 닫는다」→「10장이 그것을 닫는다」, 8장 scope의 「9장과 10장이 함께 기대는 입력이다」→「10장이 기대는 입력이다」(없는 장을 가리키는 두 자리). 개명 전 이름 `column-certificates-841-2000`은 META에 없었다.
- **둔 것.** `D_items`에 남은 둘째 판 설계 때의 라벨 다섯(`sharp-546-certificates`·`thirteen-piece-envelope`·`lemma-H-interval`·`lemma-V-coefficients`·`v-negative-k3131`)은 장v2에 생긴 적이 없는 설계 라벨이라 「지운 라벨」이 아니어서 두었다. intros·notes의 산문에 남은 지운 라벨 이름(2.2·2.5 intro의 `fiber-*`, 4장 notes의 `crossing-small-n`, 5.5·5.6 intro의 설계 라벨 등)과 10장 제목 「벌크의 둘째 증명(FLQ 경로)」·「두 증명 사슬의 하나」, 6장 scope 「두 증명이 함께 쓰는」, 11장 scope·11.3 intro·`EXTRA_NOTES[11]`의 「두 증명」·「9장·10장 닫는 정리」는 읽는 스크립트가 없는 설계 기록이라 두었다(남은 수: 「9장」 2 — 11.3 intro와 `EXTRA_NOTES[11]`; 「둘째 증명」 2; 「두 증명」 5). 세션이 장 번호 치환 때 META를 다시 보면 그때 함께 가를 자리다.

### 2.6 `scripts/_의존_도달.py`(9절 6항)

- `--check-11-3` 선택지, `labels_in_11_3()`, docstring의 그 줄, `--all`이 그것을 켜던 자리를 지웠다. 더불어 **`ROOTS`에 9장의 닫는 정리 `9:old-7-46`이 들어 있어**(파견문·인계가 짚지 않은 자리) 그대로면 「정의되지 않은 라벨 인용」 경고가 났을 것이라 `["1:main-theorem", "10:old-8-37"]`로 줄였고, docstring의 「그 두 증명」을 「그 증명」으로.
- `python -I scripts/_의존_도달.py --d`: 진술 271, 닿음 258, 닿지 않음 13(이것은 장 파일의 현황이지 내 파일의 일이 아니다; 목록은 세션이 `--list`로 본다), 부록 D 16 항목 모두 「닿음; 닿는 본문이 인용: 예」, 경고 0.
- 파이프라인 `_파이프라인_수리후_1115.sh`는 `_의존_도달.py`를 부르지 않는다(전문 확인) — 고칠 줄 없음.

### 2.7 `make_draft*.py`(9절 7항)

- `column_cert_iv/make_draft.py` 16·316·318행, `moment_cert_iv/make_draft_v2.py` 90행의 `column-certificates-841-2000`→`501-2000`(네 자리; 그 파일들에 남은 수 0). `xcert_iv/make_draft.py`는 폴더째 보관으로 갔으므로 손대지 않았다. 돌리지 않았다.
- 둔 것: `column_cert_iv/make_draft.py`의 본문 틀에는 H1이 바꾼 옛 라벨(`7:theorem-G-prime`·`7:theorem-C-moment`·`7:lemma-P-prime`·`7:qstar-implies-wlflat`·`7:cor-S-prime`)과 옛 범위 서술이 남아 있다 — 초안 생성기는 다시 돌리지 않는 것이 규칙(H1 인계 6항)이라 그대로 두고 적어 둔다.

## 3. 스스로 발견한 것

1. `세션_재계산/r8a9b11e/`(2.1) — 후보 스물에 없던 스물한째 폴더.
2. `_의존_도달.py`의 `ROOTS`에 든 `9:old-7-46`(2.6).
3. README SHA 표에 `four_families_DDLnat` 두 파일의 행이 없었다(V1이 부록 D 「자료」 줄에 올린 뒤 아무도 등록하지 않음) — 더했다(2.2).
4. README 700행의 `M_natural/j_integrals.py` 문단은 디스크에 없는 파일(폴더에는 `j_integrals_iv.py`만)의 묵은 문단이었다 — 폴더와 함께 걷혔다.
5. 「파일 목록」 표의 라벨이 바뀌는 행 61(2.2) — 특히 `r030ffae/…wKrig.npy`·`xKrig.npy`는 지워진 `bprime-boxes`가 아니라 `band-boxes`의 입력으로, `r81e7051/explore.py` 등은 `fiber-enumeration`이 아니라 `logconcavity-failure-n80`의 자료로 다시 붙는다.
6. `rerun_exactgrid_1116.sh`가 옮긴 `bprime_boxes` 스크립트를 부른다(2.1; 세션 몫).
7. 묶음의 기록 사본 폴더 `원고_자료/r*/` 가운데 **23 폴더(591 파일, 193,296,836바이트)** 가 이제 어느 항목의 「파일 목록」 행에도 없다(`r9e782f5/` 177 MB의 씨앗 인증서 119개 등; 목록은 인계 세션 절). `자료묶음_v2.py`는 복사만 하고 지우지 않으므로 그대로 남아 있다 — 지울지는 세션(결정 122의 묶음 정책 자리). `r7798355/`는 이번 전에도 표에 없던 폴더다.

## 4. 다른 영역에 닿는 것

- 세션: `git rm`(readout_front 둘), `rerun_exactgrid_1116.sh`의 bprime 줄, 고아 기록 사본 폴더 23의 처분, 재실행표·조립 등 파이프라인 재생성, README 환경 표의 측정 갱신 여부, 장 번호 치환 뒤 META 재점검(인계 「세션」 절).
- V6(장부·부록 A·B·C·구조표): 닿는 것 없음(내 파일은 어느 장·장부도 가리키지 않는다). 부록 B의 기록 목록은 「파일 목록」의 고아 폴더 처분과 무관하다(부록 B는 인용된 기록, 묶음은 자료 파일).
- 지도·번역: 닿는 것 없음(영어 쪽 `영어/`에 자료 묶음 README의 번역이 있다면 세션의 번역 정책; 내가 열지 않았다).

## 5. 인계 요약

계약 변경 없음. 인계 `인계_V7a.md`: 표 1–5는 모두 「없음」(라벨·진술·글자·문턱을 만지는 단위가 아니다). 받는 작업자별: 세션 9건, 지도 0, 번역 0(알림 1), V6 0.

## 6. 확인하지 못한 것과 정하지 못한 것

- 빠른 확인은 기본 14항목만 돌렸다(`--all`은 기본과 같다 — long 항목이 없다). 무거운 재계산(`sh run_all.sh`, `colcert_iv.py --ks 841-2000` 전체 등)은 돌리지 않았다.
- `make_draft*.py`는 돌리지 않았다(규칙). `자료묶음_v2.py`의 실제 실행(복사)도 하지 않았다 — 기대 행 614가 모두 묶음에 이미 있음을 확인했으므로 손으로 쓴 표가 생성기의 출력과 같다(세션이 파이프라인에서 `--dry`로 「문제 0」을 다시 본다).
- README 「실행 환경」의 네 환경 표는 옛 구성(32개)의 측정값으로 남겼다. 지금 구성(14개)으로 다른 세 판(3.11·3.9·3.8)을 다시 재지는 않았다 — 환경이 이 기계에 그대로 있는지 확인하지 않았고 파견 범위 밖이다. 세션이 다시 재려면 그 표를 바꾼다.
- META의 설계 산문에 남은 「두 증명」·지운 라벨 이름(2.5 「둔 것」)은 읽는 스크립트가 없어 두었다.
- `원고_자료/r*/` 고아 폴더 23은 지우지 않았다(세션 결정 자리).

## 7. 전수 검색

범위: 내 파일 여섯(`원고_자료/README.md`, `빠른_확인.py`, `scripts/_gen_재실행표.py`, `_재실행표_여유.json`, `_의존_도달.py`, `_patch_README_세션파일.py`) + `명세v2_META.py` + 두 `make_draft`.

| 검색한 문자열 | 남은 수 | 남은 자리와 까닭 |
|---|---|---|
| 「9장」·「첫째 증명」·「둘째 증명」·「두 증명」·「두 길」 | 여섯 파일 0; META 「9장」 2·「둘째 증명」 2·「두 증명」 5 | META: 11장 scope·11.3 intro·`EXTRA_NOTES[11]`(파견문이 두라고 한 11장 사전과 같은 블록), 10장 제목·weights, 6장 scope — 읽는 스크립트 없는 설계 기록(2.5) |
| `{{9:`·`9:` 라벨 | 모두 0 | `_의존_도달.py`의 `9:old-7-46`도 지움 |
| 지운 D 라벨 27(`H-star-plus-interval`·`band-LP`·`pair-one-variable`·`AR-integrals`·`m1-column-reading`·H1의 아홉·U14의 열넷·`column-certificates-841-2000`) | 여섯 파일 0; META는 2.5의 설계 산문 자리만 | README 649행 `out_band_check.txt`는 기록 파일 이름(라벨 아님) |
| 옮긴 폴더 이름 21 + `bprime_iv`·`readout_front` | 여섯 파일 0 | — |
| `1.009`(문턱) | 0 | `빠른_확인.py`의 `1.0091044897`·`1.00942285566`은 계산값 |
| `--all`의 「열 판독」 | 0 | — |

빠른 확인(`python -I -B 빠른_확인.py`, 기본 14항목, 기준 환경 Python 3.12.10·numpy 2.5.2·mpmath 1.3.0, 다른 작업자들과 코어를 나눠 쓰는 상태): Python 3.12.10 (Windows AMD64), numpy 2.5.2, mpmath 1.3.0; 항목 14개 — **일치 14 / 14, 불일치 0; 전체 99 s**(n80 0.2 s, 제타 0.7 s, 창질량-가-q50 2.4 s, 창질량-나-i0 49.0 s, 창질량-기록코드-b31 0.4 s, 띠상자 다섯 2.8–5.8 s, 모멘트-열840 16.4 s, 열인증-841 7.6 s, C구간-n60 1.2 s, C20-탐침B 2.1 s). 60초를 넘는 항목이 없어 `--fast`·`--all`도 같은 14개다. 출력은 임시 폴더에만 썼다.

CR 바이트 0과 파일 크기(파이썬 바이트 셈; 끝에 확인): `README.md` 208,326바이트(CR 0, 1123행); `빠른_확인.py` 12,332바이트(CR 0, 195행); `_gen_재실행표.py` 29,710바이트(CR 0, 447행); `_재실행표_여유.json` 3,036바이트(CR 0, 18행); `명세v2_META.py` 48,432바이트(CR 0, 318행); `_의존_도달.py` 10,607바이트(CR 0, 243행); `_patch_README_세션파일.py` 17,721바이트(CR 0, 120행); `make_draft.py` 24,361바이트(CR 0, 324행); `make_draft_v2.py` 9,241바이트(CR 0, 149행); `README.md` 3,671바이트(CR 0, 31행); `인계_V7a.md` 8,115바이트(CR 0, 81행) — 모두 CR 0.

## 8. 덧붙임 — `rerun_exactgrid_1116.sh`·`_log.txt`의 처분(13:1x; 세션이 전한 W9 인계 세션 절 2항·X3 인계)

- **확인한 것.** 현행 `장v2/부록D_장8.md` 51행 `D:band-boxes` 「자료」 끝이 W9의 고친 꼴 — 「실행은 기록 방식 `python -I band_iv.py box H 12 25 6668 0 2`·`… 1 2`를 먼저 돌린 뒤 `run_all.sh`가 `fbox H 12 25 6668`의 두 프로세스와 꼬리 `tail H 12 25 6668`을 차례로 돌린다」 — 이고 `rerun_exactgrid` 언급이 장v2 전체에 0임을 `grep`으로 확인했다. 두 파일은 git 추적 밖이다(`git ls-files`에 없음). X3 인계도 「13:02 판부터 부록 D가 인용하지 않음, 보존 의무 없음」.
- **판단.** 어느 항목도 가리키지 않고 머리 주석과 8–15·23–27행이 지워진 `D.bprime-boxes`와 옮겨진 `bprime_*.py`를 부르므로 2.1의 가름 기준(「부록 D가 가리키지 않는 것은 옮긴다」) 그대로 옮긴다 — W9의 권고와 같다.
- **한 일.** 둘을 `대조v2/보관_재계산_옛판_1117/`로 옮겼다(2 파일, 2,252바이트; 보관 README에 한 행 추가, 합계 255 파일·21,809,280바이트). README SHA 표의 두 행(281–282행) 삭제, README `band_boxes` 문단과 `_patch_README_세션파일.py` PARAS의 같은 문단에서 「재실행 순서는 `세션_재계산/rerun_exactgrid_1116.sh`(기록 …)에 있다」 문장 삭제(문단에 「`run_all.sh`가 실행 순서이고」가 이미 있다). `세션_재계산/` 루트에 파일 0.
- **셈.** `자료묶음_v2.py --dry`는 **「항목 320, 복사 614, 문제 0」으로 614 그대로**다 — W9가 적은 「614 → 613」은 맞지 않는데, 이 두 파일은 「파일 목록」 표(기록 사본; `자료묶음_v2.py`가 `원고_자료/…` 경로를 건너뛴다)가 아니라 「세션이 만든 수정판」 SHA 표에 있었기 때문이다(그 표 383 → 381행). 전수: `rerun_exactgrid` README·PARAS·장v2 0.
- 크기(CR 0): README 207,976바이트(1,121행), `_patch_README_세션파일.py` 17,608, 보관 README 4,112. `git status`: readout_front 둘은 지금 「D 」(색인에 지움이 올라 있음 — 세션이 `git rm`을 한 듯)로 보인다.
