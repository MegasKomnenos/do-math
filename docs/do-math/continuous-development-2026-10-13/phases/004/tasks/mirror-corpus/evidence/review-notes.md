# mirror-corpus 수리와 인도 판정

기존 생성기의 `verbatim`에 `do-math/scripts/tests/corpus/*`를 추가해 phase 003 F2의 원문 치환을 수리했다. 최종 정본과 미러는 각각 17항목·44파일·200872바이트이며 모든 경로와 SHA256이 같다. 정본 corpus의 원자료, manifest, 역사 verdict는 시작부터 불변이다. 각 트리의 명시 SHA 참조 41개가 일치하고 미선언 파일도 없다. 실제 생성 전에는 Claude help 두 파일만 달랐으며 `corpus-before-*.diff`가 `CLAUDE.md`에서 `AGENTS.md`로 바뀐 위치를 보여 준다.

## 기존 규칙과 필요한 변경

2fc686ac7f215222702519dfaf10e6e1ec961171의 실제 도입 diff에서 `transform`이 `verbatim`을 UTF-8 BOM 제거와 치환보다 먼저 적용하고 `build_target`이 그 결과 바이트를 쓰는 것을 확인했다. 현재 구현도 같은 경계를 제공한다. 이 기능은 유지하고 규칙의 적용 범위만 늘렸다. 생성기 본문과 overlay manifest는 바꾸지 않았다. corpus 외부 지시문의 치환도 유지한다. PR15의 다른 범위는 이번 검토 대상이 아니다.

기존 생성기 시험에 실제 저장소 규칙을 읽는 두 시험을 추가했다. corpus의 manifest·help·JSONL·Lean·미래 중첩 SKILL.md 경로에서는 BOM·CRLF·문서명·경로·frontmatter를 포함한 입력 바이트와 출력이 같아야 한다. corpus 밖 do-math 지시문, 비슷한 이름의 corpus-extra 및 다른 스킬에서는 명시한 런타임 치환 결과와 같아야 한다. 수리 전 2시험 중 corpus 보존 시험의 5개 하위 사례가 실패했고 외부 치환 대조군은 통과했다. 규칙 수정 후 디렉터리의 유일한 test_*.py를 직접 실행해 22개 전부 통과했다.

공식 생성 전 계획은 4개 허용 파일의 갱신만 예측했고 실제 생성도 같았다. 양쪽 공식 run_tests.py는 지정한 구조·재생·대역 계약 모듈에서 각각 14선택/14통과, exit 0이었다. 선택과 실제 row의 중복·누락은 없고 skip·오류·fixture 실패도 없다. 각 실행의 Python 864개 해시는 최종 판본과 같고, 전후 전체 소스 2624개 중 해당 실행의 .timings.json만 달랐다. 이후 비용 캐시 하나만 공식 생성기로 맞췄다. 최종 --check는 1297파일 drift 없음, skill-only는 verified다. 이 검사는 G4~G7의 전체 관문을 대신하지 않는다.

## A3에 남은 실제 Git 속성 경계

루트에서 `/` 상대 경로로 88파일의 `git hash-object --no-filters`와 기본 clean 경로를 대조했다. 정본·미러 manifest 두 파일만 다르다. 각각 raw object ID는 db61141dd64a6637124b623410517768fc031fe0이고 clean object ID는 89d1c078a9cf96b5b9b1c25c9d29484ad9f07fd4다. 이는 읽기 전용 clean 관찰이며 stage/commit/checkout의 실행 결과가 아니다.

원인은 corpus 안의 .gitattributes 3행 `manifest.json text eol=lf whitespace`다. 이 파일은 a0b0cc2e030b49229573aea4bf617845f27c44e5에서 도입됐고 현재도 같다. 허용된 상위 do-math/.gitattributes에 corpus 전용 `-text -eol`을 잠시 적용해 관찰해도 하위 manifest 규칙이 우선하여 같은 변환이 남았다. 관찰 직후 상위 파일의 원바이트를 복원했으며 전후 SHA가 같다. 효과 없는 상위 규칙은 제품 변경으로 남기지 않았다.

phase.json은 상위 .gitattributes만 쓰도록 허용하며 objective는 정본 corpus 전체를 읽기 전용으로 지정한다. 따라서 실제 수정 위치인 `.claude/skills/do-math/scripts/tests/corpus/.gitattributes`를 바꾸지 않았다. 후속 work가 이 파일의 쓰기 권한을 받아 manifest의 text 예외를 `manifest.json -text whitespace`로 고치고, 공식 생성 후 같은 clean 대조를 수행해야 한다. 제안 패치는 proposed-corpus-attributes.diff에 있으며 아직 적용·검증된 제품 수정은 아니다. A3는 fail이고 작업 상태는 partial이다.

이전 manager의 Lean·scheduler 두 추가 차이는 경로 표기에 따라 재현된다. Git 2.50.0.windows.2에서 역슬래시 절대 경로를 hash-object에 전달하면 clean 값이 변하지만, `/` 상대 경로나 `/` 절대 경로는 원바이트와 같다. attribute-probe.json은 동일 파일의 세 표기와 실제 argv·stdout·exit를 보존한다. 이전 명령의 정확한 argv가 저장되지 않았으므로 그 실행이 어느 표기를 썼는지는 단정하지 않는다. 현재 올바른 경로 표기의 실제 raw 불일치는 manifest이며 다른 두 녹화를 재작성할 이유는 없다.

## 이전 근거와 후속 책임

phase 003 종료 해시 2254개는 이번 시작 판본과 전부 같았다. 현재 변경 9개는 changes.json에 전후 SHA로 구별했다. 그중 phase 003의 62개 변경과 겹치는 것은 양쪽 비용 캐시와 신규 미러 help 3개다. 나머지 59개 phase 003 변경은 그대로다. 기존 미러 help 수리는 이번 변경이며 정본과 역사 녹화를 새 성공으로 덮지 않았다.

수리 전 공식 4선택/2통과/2실패 원보고를 재사용했다. 그 보고의 Python 864개와 초기 corpus가 현재 시작 상태와 같으며, 규칙은 phase 003 검수 Git 판본의 CRLF 작업트리 바이트와 같다. phase 003 source-final에는 규칙 파일 해시가 없다는 사실도 verification.json에 명시했다. 첫 자체 검산은 이 해시가 있다고 가정해 assertion에 실패했다. 실패 출력과 당시 verify.py를 verification-command에 보존했고, 실제 Git 원문을 대조하는 후속 검산으로 교정했다. 제품 시험을 반복하지 않았으며 최종 검산의 exit 1은 남은 두 manifest clean 불일치 때문이다.

역할 schema·worker·adapter·parser·smoke 호출 경로는 불변이고 모델 호출은 추가하지 않았다. 따라서 context C12가 승인한 Claude maintenance와 background의 한정 근거를 유지한다. Codex schema HTTP 400, 별도 실제 연쇄, G7/G8 전체와 최종 review는 남는다. manager가 이 보고의 발견을 처분하고 후속 속성 수리와 제품 커밋을 판단한다.

산문은 objective·protocol의 정해진 반환 계약과 실제 근거를 대조해 점검했다. writing-skills의 실제 과제 검증과 write-for-reader의 품질·명료성 원칙을 적용했다. 별도 모델 독해 및 .codex/writing-flow 기록은 이번 배정의 모델 호출 금지와 쓰기 범위에 포함되지 않으므로 실행하지 않았다. 독립 독해를 완료했다고 주장하지 않는다.
