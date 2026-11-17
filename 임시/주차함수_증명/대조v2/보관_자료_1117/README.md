# 보관 — 고아가 된 기록 사본 폴더(2026-11-17, 세션 V7)

9장 제거 물결(V1–V5)과 그 앞 물결들이 부록 D 항목을 지운 뒤, 현행 부록 D(항목 16)의 「자료」 줄과 `원고_자료/README.md` 「파일 목록」(614행)이 더 가리키지 않게 된 `원고_자료/<기록 식별자>/` 폴더 23개를 지우지 않고 여기로 옮긴 것이다(결정 130 (ㄴ)의 선례; `보관_재계산_옛판_1117/`과 같은 처리; 이 폴더는 git 추적 밖이다). 옮긴 날짜·단위: 2026-11-17 13시대, 세션. 「옛 항목」은 커밋 `fbf8a575`의 README 「파일 목록」(1,265행)에서 그 폴더의 파일을 「자료」로 들던 부록 D 항목의 라벨이다(지금은 모두 지워진 라벨이거나, 남은 항목이 더는 그 파일을 들지 않는다). 남은 기록 폴더 18개(`r030ffae`·`r10ff8c2`·`r13b0b8f`·`r15524fd`·`r15df76b`·`r19de912`·`r475ada3`·`r59c82d7`·`r6373c70`·`r6b37c7e`·`r81e7051`·`r8a9b11e`·`ra4c01fc`·`rb7effe0`·`rc9aee43`·`rce3dc75`·`re71a735`·`rfc69320`)는 그대로 `원고_자료/`에 있다. 기록의 식별자 `[r…]`는 글(장·부록 B·C·장부)에 인용으로 남을 수 있다 — 그것은 연구 기록을 가리키는 것이고 이 사본 폴더를 가리키는 것이 아니다.

| 폴더 | 파일 수 | 바이트 | 옛 항목(fbf8a575 README 기준) |
|---|---|---|---|
| `r051bfe1/` | 4 | 11,289 | tilt-sum-small-k |
| `r059f11e/` | 11 | 116,577 | cumulative-logconcavity |
| `r0dc57fa/` | 8 | 23,297 | tail-T1-partAB |
| `r207f124/` | 7 | 797,646 | Q-fin-1130 |
| `r29c10cd/` | 2 | 3,662 | prop-W-thirteen |
| `r2ec875c/` | 2 | 2,678 | m1-column-reading |
| `r33475a7/` | 6 | 10,693 | H-star-plus-interval |
| `r5909c9e/` | 23 | 458,293 | pair-one-variable |
| `r5bbc534/` | 4 | 6,221 | theorem-D-base |
| `r656206c/` | 5 | 8,193 | crossing-small-n |
| `r690be93/` | 26 | 913,838 | bernstein-signs |
| `r708d99c/` | 12 | 37,203 | newton-m170 |
| `r7798355/` | 2 | 16,227 | (옛 README 파일 목록에 없던 폴더) |
| `r845b205/` | 6 | 10,250 | theorem-U-constant |
| `r88bed8a/` | 4 | 10,610 | fiber-nonunimodal-bound |
| `r89eb039/` | 85 | 6,629,019 | polar-blocks-488 |
| `r9e782f5/` | 249 | 177,410,467 | seed-certificates-k120 |
| `rad00a59/` | 11 | 17,059 | self-consistent-constants |
| `rae1f209/` | 4 | 10,425 | AR-integrals |
| `rb6a2cd0/` | 20 | 26,294 | band-LP |
| `rbeae3a3/` | 5 | 2,585,072 | QL-small-n |
| `re79cb4d/` | 5 | 8,332 | crossing-small-n |
| `rf451d83/` | 90 | 4,183,491 | Q-fin-1130·xcert-partAB |
| **합** | **591** | **193,296,836** | |

- **`장v2_tmp_1114/`** (2026-11-17 17:2x 이동; 원래 `장v2/_tmp/`) — 2026-11-14 편집 세션의 작업 재료 열셋(편집전·편집 사본, 독해 보고, 불변식 결과, 수식 목록 스크립트·JSON, 이해 노트·편집 노트, md2pdf 로그). 옛 판이라 지운 글자·라벨(`D:bprime-boxes`, $s^{\mathrm{env}}$ 등)이 남아 검토자의 전수 검색에 걸렸다(21차 R12 5절). 조립기·생성기·검사기는 이 폴더를 읽지 않는다(`scripts/_D5_잠정채움.py`·`_patch_5A_94행.py`·`장부v2_4절_재생성2.py`의 `_tmp` 언급은 끝난 일회용 스크립트의 것).

- **`세션_재계산_미등재_1117/`** (2026-11-17 21:xx 이동; 원래 `원고_자료/세션_재계산/` 아래 같은 상대 경로) — 22차 R12 4절·5절과 ZD2 인계 「세션」 1·9: 부록 D.moment-certification에서 뺀 첫째 범위(A3; 열 501–840)의 출력 `sweep_ct_A3_s0..3.jsonl/.log` 여덟과 그 샤드 기동 스크립트 `handoff_A3.py`·`launch_handoff.py`; 부록 D 항목 본문을 만들던 작업 스크립트 `make_draft*.py` 다섯(moment_cert_iv 둘·column_k500_iv·column_cert_iv·icert_py_full); 작업 메모 `four_families_DDLnat/변경.md`·`결과_요약.md`. 자료 묶음·README SHA 표에서 함께 뺐다.
