# 인계 V7a — 자료 묶음과 스크립트의 정리(2026-11-17 12:3x–13:xx)

보고 `수리_V7a.md`. 내 파일: `원고_자료/README.md`, `원고_자료/빠른_확인.py`, `scripts/_gen_재실행표.py`, `scripts/_재실행표_여유.json`, `scripts/명세v2_META.py`, `scripts/_의존_도달.py`, `scripts/_patch_README_세션파일.py`(README SHA 표의 등록 스크립트 — 파견문 9절 2항의 「등록 스크립트」), `원고_자료/세션_재계산/column_cert_iv/make_draft.py`·`moment_cert_iv/make_draft_v2.py`의 라벨 문자열, 그리고 `원고_자료/세션_재계산/` 아래 폴더·파일의 `대조v2/보관_재계산_옛판_1117/`로의 이동.

## 계약 변경

없음.

## 표 1. 새 라벨

없음.

## 표 2. 지운 라벨

없음(라벨을 지우는 단위가 아니다; 이미 지워진 라벨 27의 자리를 자료 묶음·스크립트에서 걷었다 — 보고 7절).

## 표 3. 옮긴·합친·격하한·바꾼 진술

없음.

## 표 4. 새 글자와 바뀐 글자

없음.

## 표 5. 바뀐 문턱·상수·범위

없음.

## 옮긴 폴더·파일(`원고_자료/세션_재계산/` → `대조v2/보관_재계산_옛판_1117/`; 253 파일, 21,807,028바이트; git 추적 밖, 안에 `README.md`)

| 이름 | 파일 수 | 바이트 | 옛 항목 |
|---|---|---|---|
| `AR_integrals/` | 2 | 5,915 | `D:AR-integrals` |
| `H_star_plus/` | 2 | 5,448 | `D:H-star-plus-interval` |
| `M_natural/` | 2 | 15,015 | `D:M-natural-integrals` |
| `Q_fin_1130/` | 12 | 1,081,320 | `D:Q-fin-1130` |
| `band_LP/` | 27 | 92,021 | `D:band-LP` |
| `band_check/` | 6 | 561,135 | `D:band-check` |
| `cumulative_logconcavity_n779/` | 7 | 66,671 | `D:cumulative-logconcavity` |
| `fiber_exhaustive/` | 2 | 6,213 | `D:fiber-enumeration` |
| `fiber_nonunimodal_bound/` | 2 | 19,617 | `D:fiber-nonunimodal-bound` |
| `four_families/` | 2 | 28,029 | `D:four-families`의 옛 판(`four_families_DDLnat/`가 대체) |
| `m1_column_reading/` | 2 | 5,655 | `D:m1-column-reading` |
| `newton_r61_169/` | 4 | 36,931 | `D:newton-m170` |
| `pair_one_variable/` | 2 | 12,114 | `D:pair-one-variable` |
| `prop_W_thirteen/` | 2 | 7,088 | `D:prop-W-thirteen` |
| `r89eb039_polar/` | 37 | 1,488,304 | `D:polar-blocks-488` |
| `r89eb039_polar_block_audit/` | 8 | 68,325 | `D:polar-blocks-488` |
| `r89eb039_polar_iv/` | 60 | 5,158,811 | `D:polar-blocks-488` |
| `r8a9b11e/` | 3 | 11,149 | `D:window-mass-constant`(후보 스물 밖의 스물한째; 보고 2.1) |
| `theorem_D_base/` | 2 | 4,460 | `D:theorem-D-base` |
| `theorem_U_constant/` | 3 | 11,231 | `D:theorem-U-constant` |
| `xcert_iv/` | 47 | 7,386,077 | `D:xcert-partAB` |
| `bprime_boxes/`의 `ivbox_lib.py`를 뺀 전부 | 17 | 5,731,669 | `D:bprime-boxes`(`ivbox_lib.py`는 `band_iv.py`의 부품이라 남김) |
| `band_boxes/readout_front.py`·`readout_front_out.txt` | 2 | 3,830 | `D:band-boxes` (나)(V3가 지움) |

## 받는 작업자별 자리

### 세션 — 9건

1. **git.** `원고_자료/세션_재계산/band_boxes/readout_front.py`·`readout_front_out.txt`는 추적 파일이라 `git status`에 D — `git rm`. 그 밖의 옮긴 것은 모두 추적 밖(`.gitignore` `/임시/*/*`; `세션_재계산/`에서 추적되는 것은 `four_families_DDLnat/` 넷뿐이고 그것은 남아 있다). 내 수정 가운데 git이 보는 것: `원고_자료/README.md`(+75/−978), `scripts/_gen_재실행표.py`(+3/−132), `_patch_README_세션파일.py`(+6/−32), `_의존_도달.py`(+4/−30), `명세v2_META.py`(+7/−50); `빠른_확인.py`·`_재실행표_여유.json`·`make_draft*.py`는 추적 밖.
2. **파이프라인 재생성.** `_gen_재실행표.py`는 임시 경로로 돌려 16행(11.2 표와 같은 순서, 빈 칸 0)을 확인했고 `원고_자료/재실행표.md`(42행)는 쓰지 않았다 — 파이프라인이 다시 만든다. `자료묶음_v2.py --dry`는 「항목 320, 복사 614, 문제 0」; README 「파일 목록」 표는 그 614행과 같게 손으로 썼으므로 실제 실행은 표를 바꾸지 않을 것이다. `_의존_도달.py`는 파이프라인에 없다(고친 선택지 `--check-11-3`은 사라졌으니 어디서도 부르지 말 것).
3. **`세션_재계산/rerun_exactgrid_1116.sh`**(`D:band-boxes` 「자료」가 「실행 순서」로 가리킴): 8–22·27–31행이 옮긴 `bprime_boxes/test_lib.py`·`bprime_iv.py`·`bprime_summary.py`·`compare_record.py`를 부른다. 계산 폴더 파일이라 손대지 않았다. 선택지: (ㄱ) bprime 줄을 걷어 `band_boxes`만의 순서로 고친다(머리 주석의 「re-run D.bprime-boxes and D.band-boxes」도), (ㄴ) 실행 기록으로 두되 부록 D 「자료」 줄의 「실행 순서」 말을 `band_boxes` 부분으로 한정한다(부록 D는 U14/V3 뒤 임자가 없으니 세션). README `band_boxes` 문단은 「재실행 순서는 … 에 있다」로만 적어 어느 쪽에도 맞다.
4. **고아 기록 사본 폴더 23**(`원고_자료/r*/`; 591 파일, 193,296,836바이트): 「파일 목록」 표에서 사라진 뒤 어느 항목도 가리키지 않는다 — `r051bfe1`(4·11,289) `r059f11e`(11·116,577) `r0dc57fa`(8·23,297) `r207f124`(7·797,646) `r29c10cd`(2·3,662) `r2ec875c`(2·2,678) `r33475a7`(6·10,693) `r5909c9e`(23·458,293) `r5bbc534`(4·6,221) `r656206c`(5·8,193) `r690be93`(26·913,838) `r708d99c`(12·37,203) `r7798355`(2·16,227; 이번 전에도 표에 없던 폴더) `r845b205`(6·10,250) `r88bed8a`(4·10,610) `r89eb039`(85·6,629,019) `r9e782f5`(249·177,410,467; 결정 122 (1)의 씨앗 인증서) `rad00a59`(11·17,059) `rae1f209`(4·10,425) `rb6a2cd0`(20·26,294) `rbeae3a3`(5·2,585,072) `re79cb4d`(5·8,332) `rf451d83`(90·4,183,491). `자료묶음_v2.py`는 지우지 않으므로 처분은 세션(지우거나 `보관_자료_*`로). 아울러 표에 남은 기록 폴더 여덟(`r030ffae` 7, `r19de912` 3, `r475ada3` 3, `r6b37c7e` 3, `r81e7051` 5, `r8a9b11e` 2, `rce3dc75` 2, `re71a735` 5)에도 표에 없는 파일이 몇 개씩 있다(옛 항목이 가리키던 것) — 같은 자리에서 함께 가른다.
5. **README 「실행 환경」 표.** 네 환경(3.12·3.11·3.9·3.8)의 결과는 옛 항목 구성(기본 32개)의 측정값으로 두고 46행에 그렇게 적었다. 지금 구성 14개의 기준 환경 결과는 이번 실행값(보고 7절)으로 적었다. 다른 세 판을 다시 재려면 그 표를 갱신한다.
6. **장 번호 치환 때 `scripts/명세v2_META.py`.** `META[9]`는 지웠고 10·11장 번호는 그대로다. 치환 스크립트가 `META`의 키 `10`·`11`과 `"10.1"…"11.4"` 절 사전을 건드릴지는 세션 판단(읽는 스크립트가 없는 설계 기록). 그때 함께 가를 자리: 11장 scope·11.3 intro·`EXTRA_NOTES[11]`의 「두 증명」·「9장·10장 닫는 정리」, 10장 제목 「벌크의 둘째 증명(FLQ 경로)」, 6장 scope 「두 증명이 함께 쓰는」, intros 산문의 지운 라벨 이름(보고 2.5).
7. **`빠른_확인.py` 기본 구성 14개, `--all`도 14개(long 항목 없음).** README 84행에도 그렇게 적었다. 두 C 항목은 `c50_iv/c50iv.exe`가 묶음에 있어 돈다.
8. **`column_cert_iv/make_draft.py`**에 H1 전의 옛 라벨(`7:theorem-G-prime`·`7:theorem-C-moment`·`7:lemma-P-prime`·`7:qstar-implies-wlflat`·`7:cor-S-prime`)이 본문 틀에 남아 있다(라벨 문자열 세 자리만 고쳤다). 돌리지 않는 초안 생성기라 두었다 — 묶음 위생(결정 122 (2))의 자리.
9. **`__pycache__`.** `bprime_boxes/__pycache__/`(옮긴 `bprime_iv`의 pyc 포함)·`band_boxes/__pycache__/`는 옮기지 않았다. 묶음을 다시 쌀 때 지운다.

### 지도 갱신 작업자 — 0건

내 파일은 지도에 들지 않는다.

### 번역(U18 알림) — 1건(알림)

`원고_자료/README.md`의 영어판이 `영어/` 아래에 있다면 같은 자리(처음 돌려 볼 것 두 행, 실행 환경, 재실행표와 빠른 확인, 세션이 만든 수정판 절 머리·SHA 표·문단, 파일 목록 표)가 바뀌었다. 나는 `영어/`를 열지 않았다.

### V6(장부·부록 A·B·C·구조표) — 0건

닿는 것 없음.

## 덧붙임(13:1x) — 세션 절 3항의 처분

세션 절 3항(`rerun_exactgrid_1116.sh`의 bprime 줄)은 닫혔다: W9가 `D:band-boxes` 「자료」에서 그 가리킴을 지웠고(인계_W9 세션 절 2항), 나는 `rerun_exactgrid_1116.sh`·`rerun_exactgrid_1116_log.txt`(2 파일, 2,252바이트; git 추적 밖)를 `대조v2/보관_재계산_옛판_1117/`로 옮기고 README SHA 표 두 행(281–282)과 `band_boxes` 문단·PARAS의 한 문장을 걷었다. 옮긴 것 합계 255 파일·21,809,280바이트. `자료묶음_v2.py --dry`는 「항목 320, 복사 614, 문제 0」 그대로(두 파일은 「파일 목록」이 아니라 SHA 표에 있었다; W9의 「614 → 613」은 해당 없음). 세션이 더 할 일: 없음(번역 쪽은 W9 인계 3항이 이미 적었다). README 207,976바이트(CR 0).
