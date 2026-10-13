# reading-limits 조사 인계

조사 A1~A3는 완료했다. **13-C의 읽기 한도 절과 L01은 미인증**이다. `reading-boundaries.json`은 실제 관측, 설치 코드의 정적 계약, 미정인 운전 프로필을 분리한다. 제품·문서·시험 수정은 없다.

현재 정본 SKILL 14행은 GLOSSARY 전문 → README operating-model → start-guide의 순서를 정하고, 긴 문서를 연속 구간으로 회수하도록 한다. README 148행은 초기화-운전의 공개 절차로 이어진다. 독립-운영, 초기화-효율과-정비, CLI 실행 계약은 해당 단계가 소비하는 경계를 설명한다. 24개 문서 크기 목록은 하나의 shell 출력 배정이 아니다. README 구간의 원 개행을 포함한 크기는 21~32행 2,707 bytes, 33~211행 25,312 bytes다. 파일 크기와 전문 회수·독해는 별도다.

내부 10역할은 공통+역할 문서를 `contracts.render_prompt`에 넣고, `prepare_role_input`은 문서·맥락·schema·framing을 포함한 전체 UTF-8 프롬프트의 입력 용량을 검사한다. ModelRunner가 input.txt를 쓰고 worker가 stdin으로 전달한다. 두 공급자의 argv도 현재 원문에서 확인했다. 이전 10역할 분석의 순서/전달 성질을 재사용하며 새 역할 시험이나 모델 호출은 하지 않았다. 역사 model_runner와 계약/운영-점검.md는 현재 해시가 다르다. 변경된 writer는 현재 65~93행, 역할 문서는 현 모집단/크기로 연결했고 역사 판본의 불변을 주장하지 않는다. 독립-운영.md는 설치 복구 AI에게 지급하는 문서가 아니라 운영자 설명이다.

현재 task의 조상 프로세스는 설치 Codex 경로이며 `--version`은 0.162.1이다. 활성 `tools.exec_command`의 개별 출력과 `functions.exec`의 합산 출력은 모두 token 예산이다. ASCII·한글·accent·결합문자·emoji가 든 비밀 없는 80행 fixture 두 개를 사용했다. 개별 400-token 출력은 exit 0과 END:080을 보존하면서 중간을 잘랐다. 각 10행/개별 1,000-token, 네 결과/합산 2,400-token 호출 16개는 전 160행의 순서·내용을 정확히 받았다. 검산은 개행 형식과 문자 정규화를 구별한다. 별도 합산 150-token 호출에서는 온전한 내부 두 결과가 최종 모델 출력에서 잘려 178-token 누락 표시가 나왔다. 저장된 내부 객체와 모델에 도달한 전문은 서로 다르다. 수신의 사실도 독해·준수나 후속 history 보존의 증명은 아니다.

이 관측은 SKILL의 '실제로 받은 마지막 부분 다음'을 마지막 표시 꼬리로 해석하면 공백을 놓칠 수 있음을 드러낸다. END:080 다음 81행으로 진행해도 빠진 중간은 회수되지 않는다. '연속해서 온전히 받은 접두 구간'을 기준으로 다음 범위를 정하고 모든 공백·합산 절단을 확인하도록 좁은 문서 교정을 배정할 수 있다. 실제 운영 AI가 이미 이 오류를 범했다고 주장하지 않는다. B-20의 AI 준수 한계도 보존한다.

설치 Claude Code는 2.1.289다. 배포 실행 파일의 필요한 비밀 없는 구현 구간에서 Read의 기본 25,000 token, 전체 파일 입력 262,144 bytes, 선택 구간 입력 guard, PARTIAL 접두 paging/긴 행 문자 접두 처리, offset/limit 오류를 확인했다. 설명 template의 2,000행과 실제 `limit=undefined` 기본값을 구분했다. SDK/session의 fileReadingLimits override가 가능하므로 기본값을 다른 운전 세션의 유효값으로 만들지 않는다. 로컬 user/project/local 설정의 관련 env와 bashOutputMaxChars는 없고 확인한 기본 managed 파일도 없다. Claude의 실제 Read·Bash·PowerShell 호출은 하지 않았다.

현재 공식 문서의 Read 설명은 설치 정적 구현의 25,000 token/256 KiB 구분과 대조할 수 있다. allow_large는 2.1.296 이후 설명으로 현 설치에 소급하지 않는다. [Claude 도구 문서](https://code.claude.com/docs/en/tools-reference), [환경 변수](https://code.claude.com/docs/en/env-vars). 공식 Codex 자료의 tool_output_token_limit는 개별 출력의 history token 예산이며 고정 byte 상한이 아니다. [Codex 설정 참조](https://learn.chatgpt.com/docs/config-file/config-reference), [공식 schema](https://developers.openai.com/codex/config-schema.json). URL·조회 시각·짧은 원문·판본 한계는 public-sources.json에 있다. Claude shell의 character window도 Read token과 구별하며 실제 shell 세션에 적용된 값은 미확인이다.

Manager에게 필요한 결정은 세 가지다. (1) 공급자별 실제 운전 host/tool/model/한 번의 호출 및 합산 예산을 지정한다. 개발 task의 도구를 운영자·manager 도구와 같다고 가정하지 않는다. (2) 원문의 byte 비교를 유지해 권위 있는 출력-byte 계약을 얻을지, 위임 권한 안에서 실제 token/character 단위와 전 구간 수신 기준으로 요구 개정을 결정할지 판단한다. 권한이 없으면 사용자에게 정확히 상신하고 미충족을 유지한다. (3) 머리·꼬리 절단에 맞춘 최소 읽기 문구 교정을 배정한다. 고정된 Claude 운전 세션에서 fixture의 실제 Read 호출과 유효 override를 보존하는 후속 작업은 조건이 갖춰질 때만 진행한다. 새 유료 세션이 자동 승인된 것으로 해석하지 않는다.

향후 검사는 실제 읽는 각 문서/구간의 원 판본·전 문자/행 범위·최종 출력에 연결한다. unknown cap, 잘못된 단위, 끝표지뿐인 출력, 합산 절단, 중복/누락 boundary, 긴 한 행의 문자 접두를 반례로 둔다. 기존 structure/test_doc_code.py가 명령·필드 검사와 읽기 한도 종결을 구별하는 상태를 유지한다. 비교 가능한 경계 없이 새 AST 추론기나 거대한 호스트 장치를 만들지 않는다. 새 byte 상한을 실험에서 추정하지 않는다.

시작 20입력과 발견 시 기록한 고정 의존 파일, 두 실행 파일의 종료 비교에서 불일치는 없다. 다른 task의 변경 파일은 읽기·지문에서 제외했다. 전체 제품 불변/host-smoke/다른 문서 패킷/G7 성공을 주장하지 않는다. 초반 helper의 argv 구분 오류와 과도한 합산 출력은 investigation-events.json에 구분했으며, 실제 성공 help/version 및 좁은 원문/fixture 출력으로 교체했다. 공식 제품 검사·미러 생성·graph 갱신·Git 작업은 수행하지 않았다.
