ScienceDirect PDF의 기존 CLI thread에서 근거 오류와 남은 원문 회수 방법을 재검토한다. 자신의 사본·전용 브라우저·근거 디렉터리만 사용한다. 기존 source·권한 계약과 사용자 세 기준을 유지하며, 다른 자료원 자동 fallback·별도 IdP 로그인·API 자격·토큰 위조는 사용하지 않는다.

독립 검토는 criteria_b03_pdfft_render_probe.py의 loopback handler가 /pdfft.htm 이외 모든 경로에 직접 404를 반환하는 것을 확인했다. criteria-b03-pdfft-render.json의 404 host는 127.0.0.1이고 안정 이미지에도 같은 로컬 호스트의 페이지 부재가 보인다. 약 3시간 전에 저장한 HTML을 재생한 것이므로 이 기록으로 원 ScienceDirect signed pdfft의 서버 404나 토큰 유효성을 주장할 수 없다. 먼저 보고·criteria-review·검증 문서의 해당 원인 판단을 바로잡고, 원 근거 파일은 지우거나 현재 관측으로 덮지 않는다.

현재 실제 Preface 문헌에서 제공되는 View PDF와 내장 제어를 다시 확인한다. 문헌 정체성·실제 프록시 도착·signed URL 발급 시각과 클릭 시각을 결속한다. 입력 직전·응답 직후·안정 화면을 모두 실제로 캡처하고 직접 이미지 판독한다. 새로 발급된 링크를 즉시 정상 UI에서 누르는 경로, 새 탭/팝업/내장 PDF viewer/다운로드 이벤트/원 응답 관찰 등 제공자와 브라우저가 실제 제공하는 방법을 대조한다. 로컬 replay의 자원 경로 실패, 오래된 서명 링크 만료 가능성, 다른 문헌 링크, 브라우저 자체 오류와 실제 원격 HTTP 상태를 각각 구분한다. 실제 원문 회수 근거는 정상 source 호출의 PDF 바이트·문헌 ID/제목·페이지 대조여야 한다.

기술적 관찰 오류를 고칠 때는 실제 publisher 요청을 보존한다. 로컬 HTML 재생은 오프라인 해석 근거로만 쓰고, 로컬 서버가 만든 HTTP 상태를 publisher 상태로 바꾸지 않는다. 정상 공개 PDF 양성 대조로 같은 소유 브라우저의 PDF 처리 경로를 검증할 수 있다. Headed/headless, 내부 viewer와 다운로드 동작을 필요에 따라 비교하되 기존 사용자 브라우저나 등록 MCP는 건드리지 않는다. 접근 제한 응답을 우회하거나 이미 거부된 인증을 다시 시도하지 않는다.

현재 실제 View PDF의 같은 문헌 HTML 복귀와 53,074바이트 HTML 관측은 별도의 증거다. 해결되기 전에는 fulltext_unresolved를 유지하고, 로컬 404의 정정만으로 PDF가 복원됐다고 하지 않는다. 실익 있는 방법을 실행하거나 현재 권한에서 더 진행할 수 없는 구체적 이유를 입증한 때에만 최종 반환한다.

코드 합병 주의도 반영한다. 자신의 sciencedirect.py에는 다른 sciencedirect-export 사본의 selected_export_choice/native_search_citation 및 정확한 검색행 선택·상단 Export fallback이 없다. 원본 통합은 주 세션이 양쪽 hunk를 합친다. 다른 사본을 수정하지 말고 이번 수정이 건드린 함수·회귀와 합병 시 보존할 항목을 보고한다. doc_id가 ISSN/ISBN 구조만 검사한다면 체크섬까지 검증한다고 표현하지 않는다. 확인되지 않은 문법 거부를 추가하지 않는다.
