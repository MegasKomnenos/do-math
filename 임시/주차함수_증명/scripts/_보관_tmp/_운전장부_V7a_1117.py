# -*- coding: utf-8 -*-
"""운전 장부: V7a 회수 기록. 2026-11-17 12:5x."""
import io
P = r"C:\math\임시\주차함수_증명\대조v2\구조압축\운전_장부.md"
s = io.open(P, encoding="utf-8").read()
m = "- **V7a(자료 묶음·스크립트 정리)**"
assert m not in s
add = (
    m + " 12:5x 회수 — 완료. 일곱 사안 전부 처리, 다르게 간 것 0, 스스로 찾은 것 7(보고 3절). **옮긴 것**(`원고_자료/세션_재계산/` → `대조v2/보관_재계산_옛판_1117/`; 합 253파일·21,807,028B; 안에 README 한 장): 후보 스물 + `r8a9b11e`(지워진 `D:window-mass-constant`의 `ul_iv_fixed.py`; 파견문의 「`D:zeta-constants` 출처」는 기록 폴더 `원고_자료/r8a9b11e/` 이야기) + `bprime_boxes`의 `ivbox_lib.py`를 뺀 전부(`band_iv.py`가 import; 그것이 읽는 `r030ffae_window/work`·`window_mass_env`도 남음) + `band_boxes/readout_front.*`. 남는 폴더 15(세션 확인 일치). 남는 폴더 사이에 옮긴 것을 import하는 스크립트 0; `band_summary.py` 출력 일치. **고친 파일**: README 2,026→1,123행(384,422→208,326B; SHA 표 599→383, 「파일 목록」 표 1,265→614 — `자료묶음_v2.py --dry` 「항목 320, 복사 614, 문제 0」; `four_families_DDLnat` 추가; 「처음 돌려 볼 것」·실행 환경 문단·설명 문단 15 삭제), `빠른_확인.py` 289→195행(14 항목 전부 일치, 99초), `_gen_재실행표.py` 576→447행(CONFIG 19 삭제·키 개명·`four_families_DDLnat/` 경로; 임시 출력 16행·빈 칸 0), `_재실행표_여유.json` 44→18행, `명세v2_META.py` 361→318행(`META[9]`·`EXTRA_NOTES[9]` 삭제, D_items 16 제거, `for` 고침; 11장 절 사전은 읽는 스크립트가 없어 그대로 — 「9장」 2·「둘째 증명」 2·「두 증명」 5 잔존은 설계 산문), `_의존_도달.py` 269→243행(`--check-11-3`·`labels_in_11_3()`·`--all` 연결 삭제; **ROOTS의 `9:old-7-46` 제거** — 인계가 짚지 않은 자리; `--d` 부록 D 16 모두 닿음·경고 0), `_patch_README_세션파일.py` PARAS 25→12, `column_cert_iv/make_draft.py`·`moment_cert_iv/make_draft_v2.py` 라벨 개명(돌리지 않음). 전수 검색 0(「9장」·첫째/둘째 증명·두 증명·지운 D 라벨 27·옮긴 폴더 이름·readout_front·1.009; META 예외). CR 0(세션 확인 일치). **세션이 먼저 알 것**: (1) `band_boxes/readout_front.*`는 추적 파일 → `git rm`; (2) `세션_재계산/rerun_exactgrid_1116.sh`가 옮긴 `bprime_boxes` 스크립트 넷을 부름 — 부록 D 「자료」 줄 쪽 판단은 W9에 전달(스크립트는 세션); (3) 고아 기록 사본 폴더 23(`원고_자료/r*/`; 591파일·193,296,836B; `r9e782f5/` 177MB 씨앗 인증서 포함)이 어느 항목도 가리키지 않음 — 처분은 세션(V7: 추적 밖이라 `대조v2/보관_자료_1117/`로 이동 예정, W9가 「자료」 줄을 확정한 뒤). 그 밖 세션 절 5–9(README 환경 표는 옛 구성 측정으로 둠; META의 10·11 번호는 치환 때; `빠른_확인.py` 기본 14·`--all` 14; `column_cert_iv/make_draft.py` 본문 틀의 옛 라벨은 묶음 위생 자리; `__pycache__` 둘). 인계 세션 9·번역 1. 보고 수리_V7a.md·인계 인계_V7a.md.\n"
)
s = s.rstrip("\n") + "\n" + add
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
