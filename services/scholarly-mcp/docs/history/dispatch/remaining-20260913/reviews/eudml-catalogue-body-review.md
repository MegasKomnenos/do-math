# 책 목차를 전문으로 분류한 판정 정정

Root가 실제 책204358의8,336바이트 원 XML을 다시 검사했다. body 아래에는 book-part14개와 각각 book-part-meta, book-part-id, title-group/title, self-uri만 있다. p·table·formula·section·장 본문은 없고 full-book/part 링크15개는 외부 GDZ다. 따라서 책 metadata와 목차 확보는 성공이지만 fulltext available과 이 부분의 not_reproduced 판정은 틀렸다.

Root 원본에는 이미 최소 수리를 적용했다. eudml.py의 has_native_body는 현재 문헌의 직접 body/book-body에서 시작해 구조 컨테이너를 순회하고 metadata·목차·ID·링크만 있는 하위 구조를 본문으로 세지 않는다. 글자 수 임계값은 없다. metadata/supplementary는 available이고 해당 책의 fulltext는 not_offered다. 실제 article body/sec/p와 중첩 book-part body/p 양성, 공급자 ID 대체 거부는 유지된다. 원본7검사와 실제 XML을 새 원본 SDK에 재생한6판정이 통과했고 전체631검사도 통과했다.

근거는 root-user-criteria-20260913T0715Z/eudml-book-merge/result.json, eudml/book-20260913T125115Z의 잘못된 available 재현, eudml/book-20260913T130058Z의 수리 후 partial/not_offered다. 두 SDK 실행은 저장된 실제 원 응답 재생이며 새 EuDML 원격 성공이 아니다. 전후·안정 이미지와 report-private.json이 있다. 원자료는 자기 task의 book-layout-204358-live1-response-body.bin이다.

이번 후속은 이 구체 판정·보고·사본의 정정이다. 현재 원본의 해당 eudml.py/test/fixture 수리만 자기 사본에 대조·반영하고, 실제 원 XML과 위 이미지도 직접 읽어 report/result/criteria-review/visual-review/changes를 갱신한다. 기존 타임아웃 수리·책 ID·14장 metadata와 source504 이력을 보존한다. 이 항목을 restored로 바로잡되 책 본문 자체를 새로 얻었다고 하지 않는다. API나 GDZ를 다시 호출할 필요는 없으며 새 원격 요청을 하지 않는다. 실제 source-owned navigation의 캡처 실패도 성공으로 바꾸지 않는다.

원본·Git·root private 자료는 읽기만 한다. 기존 자격 파일을 출력하거나 넓게 내용 검색하지 않는다. 등록 MCP/Codex/사용자 브라우저를 재시작하지 않는다. 이 정정과 사본 회귀를 마친 뒤에만 최종 반환한다.
