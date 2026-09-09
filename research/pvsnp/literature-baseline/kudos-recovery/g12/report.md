g12의 배정1건은 검증을 통과했다. `VER-c654aca561b693097c66a740`의 문헌·판본 동일성을 확인했고, 26쪽 저자 preprint 원문을 확보했다. 초록은 확인한 출처 범위에서 `not_found`다. 미처리·미해결·남은 작업은0건이다. 결과 정본은 `results/VER-c654aca561b693097c66a740.json`, 전체 검사 결과는 `final-check.json`이다.

저자 페이지의 명시적 preprint PDF 링크에서 내려받은 파일은 기존 원문 `originals/paper-summary/03e45d574d66af5430fc846a6be99778811758dc2668cc44bd9a4f7920daa957.pdf`와 전체 SHA256이 같다. 첫 면의 제목·Toshiyuki KOBAYASHI, 연속26쪽과 마지막 참고문헌을 확인했다. 페이지1·2·26 이미지를 직접 읽었고 전체 페이지의 텍스트·순서·구성을 대조했다. 날짜는 확정되지 않아 null을 유지한다. 저자 페이지와 MR1190750의1992년·59–75쪽은 `same_work_different_version`인 관련 출판본의 정보다.

초록 확인 범위는 저자 페이지, 실제 preprint PDF, KUDOS를 통해 찾은 MathSciNet MR1190750, Summon의 정확한 제목 검색과 확장 제목·저자 검색이다. 정확한 제목의 보유 범위는0건, 비구독 포함은8건이었다.8개 Quick Look을 모두 읽었다.7개 같은 제목 레코드는 출판본/회의록 서지이며 초록이 없었고, 부모 책의 초록 필드는 목차였다. 확장 제목+Kobayashi 검색은21건/21수신이며 같은7건과 다른 제목의14건이다. MR 기록은 별도 출판본의 독립 서평자 Shvartsman을 명시한다. 원문은 도입부와 Question A-0에서 시작해 예시·정의로 이어지므로 도입부를 임의의 초록으로 자르지 않았다. 이 판정은 확인한 범위에 대한 부재이며 인터넷 전체의 부재를 주장하지 않는다.

실제 수집 실행은 `runs/20260909T001643Z-21484/`에 시작 시각·PID21484·명령·당시 코드 SHA와 결과를 남겼다. 이 실행의 검색3회, 저자출처 방문1회, PDF 다운로드1회, 기존 근거 재사용2회가 기록돼 있다. MathSciNet의 선행 UI 탐색은 별도 저장한 실물 근거를 재사용했으며 그 탐색 횟수를 이 실행의 호출 수에 더하지 않았다. 최종 저장 증거 재판정은 `runs/20260909T002136Z-24596/`이며 브라우저 호출0회·근거20개 재사용으로 전체 완료를 확인했다. 이후 같은 진입점의 완료 결과 재사용도 전체 검사 통과를 확인했다.

`test_recovery.py`의12개 시험이 exit0으로 통과했다. 실제 저자 HTML,26쪽 PDF, Summon7·8건 fixture와 수집 package를 사용했다. 최초 인식6건 실패→7개 통과, 재개2건 실패→9개 통과, 변경 근거 결박·정확한 제외 사유·실행 호출수3건 실패→12개 통과를 `tdd/`에 보존했다. 명령과 exit code는 `tdd/executions.json`에 있다. 구조를 바꾼0건·미수신 페이지·해시 변경 시험은 실제 서비스 장애를 관측했다는 주장과 구별한다. 초록의 의미상 부재는 시험만으로 결정하지 않고 `human-review.json`의 직접 검토로 판정했으며, 검토한 출처의 경로·SHA를 결박했다.

전체 검사 명령은 다음과 같고 exit0, passed=true, complete=true다.

```text
python research/pvsnp/literature-baseline/kudos-recovery/check_recovery.py --assignment research/pvsnp/literature-baseline/kudos-recovery/g12/assignment.json
```

`work-queue.json`의 papers_with_remaining_work는0이다. 재개 명령은 `python research/pvsnp/literature-baseline/kudos-recovery/g12/resume.py`다. 새 출처나 원문 판본이 제시되면 대응 조사와 직접 검토를 다시 열고 같은 진입점으로 재검사한다. 공통 계약·검사기·입력·다른 작업자 영역은 수정하지 않았다. 편입과 Git commit/push는 루트가 맡는다.

초기 탐색에서 Summon 응답의 중첩 res_dat token이 도구 출력에 포함됐다. 원시 응답1개는 보호된 `.credentials/kudos-recovery/g12/`에 옮겼고 공개 자료는 허용한 서지 필드만 보존했다. token의 로그인 권한 여부는 미확인이다. `audit.json`에는 값 없이 URL host·매개변수 키 구조·보존 범위와 검사 결과를 적었다. 공개 작업 파일51개를 실제 ID/PW 및 길이12이상 저장 쿠키값과 비교한 결과 일치0건이었다. 이전 도구 출력 자체를 삭제했다는 뜻은 아니다.
