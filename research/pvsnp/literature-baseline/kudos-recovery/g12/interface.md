g12은 날짜 미확정인 Kobayashi의 26쪽 저자 preprint를 회수한다. 원 배정과 판본 관계는 `assignment.json` 및 입력 JSONL이 정본이며, 이 문서는 실제 브라우저 관찰과 재개 방법을 기록한다.

KUDOS의 `https://kudos.knu.ac.kr/pages/index.htm`을 새 Chrome context에서 열고 `로그아웃` 링크가 보이는지 확인했다. 저장 상태는 보호된 bootstrap에서만 읽었다. 인증값을 fixture에 넣지 않았다. 홈페이지에서 실제 Summon anchor의 href를 읽어 전자자원 검색으로 이동했다.

저자 페이지 `https://www.ms.u-tokyo.ac.jp/~toshi/pub/19.html`의 `preprint version(pdf)` 링크는 `https://www.ms.u-tokyo.ac.jp/~toshi/texpdf/19-pro-ceed-preprint.pdf`다. 관측 anchor에서 읽은 URL을 context.request.get으로 내려받았다. 26쪽 PDF의 전체 SHA가 등록된 로컬 원문과 같으므로 원본을 참조한다. 페이지 본문의1992년·59–75쪽은 관련 출판본에만 기록하며 preprint의 year는 null이다.

Summon 입력은 `input[name=q]:visible`이다. 실제 Enter 검색이 발생시킨 `/api/search` 응답에서 허용한 서지 필드만 보존한다. 정확한 제목의 따옴표 검색은 기본 보유 범위0건이며 화면의 `도서관 비구독 자료 포함` 링크를 클릭하면8건이다. 응답의 original_query와 s.ho=f를 대조했다. 결과의 `button[data-aid=quick-look-button]:visible`8개를 각각 눌렀고 `[data-aid=quick-look-modal]` 본문을 보존했다. 닫기는 `button[data-aid=quick-look-close-btn]`다. 전역 role=dialog는 중첩된 두 요소에 대응하므로 이 실제 모달 경계를 사용한다. 제목+Kobayashi 검색은 확장 범위21건/21수신이며 전체 서지를 검토했다. 외부 Syndetics 부가정보의 로딩 표시는 논문 자체 초록 필드와 구별했다.

KUDOS 학술DB `https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542`에서 `#search_order`에 MathSciNet을 넣고 Enter를 눌렀다. 검색된 유일한 `바로가기`가 연 새 페이지의 `#searchTextInput`에 MR1190750을 넣고 Enter를 누르면 상세로 직접 이동한다. 실제 상세 경로는 `/mathscinet/article`이었다. MR번호·1992·59–75쪽과 Shvartsman의 Review를 읽었다. Article 표시는 href 없는 span이었다. 이 별도 판본의 서평은 추가 근거다.

재개는 저장 증거를 먼저 검토한다. `python research/pvsnp/literature-baseline/kudos-recovery/g12/resume.py`는 유효한 완료 결과를 검사해 재사용하고, 미완료이면 collected.json과 human-review.json을 소비한다. collected.json이 없으면 위 UI를 실행한다. `--refresh`는 실제 수집을 다시 실행하며 새 증거는 내용주소로 보존한다. 원자료가 달라지면 기존 직접 검토를 재사용하지 말고 새 자료를 직접 읽어 human-review.json을 갱신한다. 전체 완료 검사는 `python research/pvsnp/literature-baseline/kudos-recovery/check_recovery.py --assignment research/pvsnp/literature-baseline/kudos-recovery/g12/assignment.json`이다.

초기 진단에서 Summon bx_open_url의 중첩 res_dat token이 도구 출력에 포함됐다. 원시 응답은 보호된 g12 디렉터리에 옮겼으며 공개 fixture는 정제했다. 토큰의 로그인 권한 여부는 확인하지 않았다. `audit.json`은 값 없이 관측 구조와 검사 범위를 기록한다. 이전 도구 출력 자체가 삭제됐다는 뜻은 아니다.
