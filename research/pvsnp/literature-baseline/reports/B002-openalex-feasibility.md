# B002 DOI-없는 후보에 대한 OpenAlex 대조 가능성

## 결론

B002의 DOI 없는 후보는 2,710개다. OpenAlex Works API는 title search로 저빈도 후보 확장·공개 work ID·출판연도·OA/판본 relation을 찾는 데는 사용할 수 있다. 그러나 DOI 없는 책·번역·키릴 문자·옛 판본에서는 0건과 다수 hit가 실제로 발생하므로, **OpenAlex hit만으로 MR 후보와 exact work를 동일시할 수 없다.** 후보–work 연결은 title/subtitle, 저자, 연도, publisher/container, ISBN/DOI, version 관계를 원 출판처·저자·기관 record에서 다시 대조해야 한다.

2026-02-24의 [OpenAlex 공식 정책 공지](https://blog.openalex.org/openalex-api-new-features-and-usage-based-pricing/)에 따르면 API key는 정상 운용 요청에 필수이며, 무키 요청은 소수 demo 호출만 허용된다. search는 호출당 과금 단위를 쓰고 key마다 일일 무료 사용량이 있지만, 이는 무키 전수 수집을 허용한다는 뜻이 아니다. 새 검색에서는 `?search=`가 정본이고 이 보고서가 시험한 옛 `filter=title.search:` 문법은 폐기 예정이다. 현행 개발자 문서는 [developers.openalex.org](https://developers.openalex.org/)다. 이 시험은 무키 demo endpoint만 사용했고 원시 intake 대량 생성·PDF 다운로드를 하지 않았다.

## 실제 저빈도 표본

시험 endpoint는 옛 형식 `GET https://api.openalex.org/works?filter=title.search:<URL-encoded title>&per-page=1`이다. 2026-09-04 KST에 10개 후보를 순차 요청했지만 이는 현재 정책상 demo 표본이며 전수 운용 검증이 아니다.

| B002 MR · 분야 | 후보 title/author/year | HTTP·관찰 | 판정 |
|---|---|---|---|
| MR311439 · 00 | Shilov, *Matematicheski analiz … Chast 3* (1970) | 200, `meta.count=0` | 비라틴 전사·고전 판본에서 title search가 회수하지 못할 수 있음. `no_openalex_candidate_returned`, DOI 부재 증거 아님. |
| MR506676 · 03 | Ershov, *Teoriya numeratsii* (1977) | 200, `meta.count=0` | 위와 같은 결손 표본. |
| MR460128 · 05 | Comtet, *Advanced combinatorics* (1974) | 200, count 16; 첫 work `W4212799367`, 같은 title, 1974 | 제목·연도는 강한 후보 신호지만 저자·publisher/판을 추가 대조해야 함. |
| MR708496 · 11 | Exton, *q-hypergeometric functions and applications* (1983) | 200, count 15; 첫 work `W1510348186`, 같은 title, 1984 | 연도 차와 다수 hit가 있어 edition/record aggregation 가능성. exact 연결 미확정. |
| MR313252 · 14 | Fulton, *Algebraic curves: an introduction …* (1969) | 200; 응답 수신, PowerShell JSON casing 파서가 title 필드 역직렬화에 실패 | API 실패가 아니라 소비자 파서 한계. raw metadata를 별도 JSON parser로 재검사해야 함. |
| MR349820 · 20 | Coxeter–Moser, *Generators and relations for discrete groups* (1972) | 200; 응답 수신 | 저빈도 query는 성립했으나 이 시험에서 exact work fields 미추출. |
| MR344384 · 28 | Apostol, *Mathematical analysis* (1974) | 200; 응답 수신 | 일반 표제라 오탐 위험이 높음. 저자·ISBN 없이는 자동 연결 금지. |
| MR302944 · 33 | Bell, *Special functions for scientists and engineers* (1968) | 200; 응답 수신 | 일반 표제·판본 가능성 때문에 exact 연결 미확정. |
| MR346858 · 60 | Chung, *A course in probability theory* (1974) | 200; 응답 수신 | 널리 재발행된 표준서라 version/edition 대조 필요. |
| MR544188 · 81 | Simon, *Functional integration and quantum physics* (1979) | 200; 응답 수신 | 공개 work 후보 회수 경로는 확인했으나 이 시험에서 exact field parsing은 미완료. |

## 운용 판정

- **가능:** 정확 title + 저자 + 연도 query를 한 건씩 낮은 빈도로 실행하고 OpenAlex work ID를 발견 후보로 기록한다. 반환 DOI, primary location, authorship, publication year, version 관계가 B002와 함께 맞을 때에만 다음 출판처 대조로 보낸다.
- **불가능/금지:** `meta.count`, relevance 순서, cited-by count, title 유사도만으로 MR record·번역·권·재발행을 합치지 않는다. 0건도 OpenAlex 전체 또는 DOI의 부재가 아니다.
- **version 관계:** OpenAlex의 work aggregation과 location/version metadata는 관계 후보이지 출판판 동일성 증명이 아니다. DOI가 다른 hardback/eBook/chapter/preprint는 공식 publisher 또는 repository record에서 각각 보존한다.
- **접근·rate:** 현행 `?search=` 문법과 usage 정책을 따라야 한다. 2,710건 전건 검색은 OpenAlex key와 usage budget, cache·raw provenance 설계 없이는 실행하지 않는다. 무키 demo 호출을 반복해 제한을 우회하지 않는다.

따라서 OpenAlex는 DOI 없는 B002의 **key가 있을 때 보조 discovery/metadata 대조 경로로는 가능**하지만 exact-work 자동 매칭·판본 병합기로는 부적합하다. 현재는 zbMATH·DBLP·arXiv·공식 출판 경로를 먼저 소진하므로 OpenAlex key에 대한 사용자 행동을 아직 열지 않는다.
