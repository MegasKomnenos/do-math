# DOI 없는 B002 이론CS 후보의 DBLP 공개 대조 가능성

검토일: 2026-09-04 KST. DBLP 공식 Search API(`https://dblp.org/search/publ/api`)에 `format=json`, `h=1`인 저빈도 10개 요청을 보냈다. PDF·인증·크리덴셜·대량 수집은 하지 않았다.

## 실행 결과

다음 query는 각각 한 요청만 실행했으나, 이 실행 환경에서는 모두 DBLP 응답을 받지 못했다. 그러므로 **검색 실패**이며, DBLP에 결과가 없다는 뜻이 아니다. 주 실행 뒤 PowerShell `Invoke-RestMethod`로 Cook query를, `curl`로 canonical record JSON을 독립 재시도했을 때도 원격 호스트가 TLS 전송을 reset했다. HTTP 0건·404 응답이 아니라 응답 본문 전의 transport failure다.

1. `Computational Complexity Papadimitriou` — B002 MR1251285
2. `Communication Complexity Kushilevitz Nisan` — B002 MR1426129
3. `Descriptive Complexity Immerman` — B002 MR1732784
4. `Exact Exponential Algorithms Fomin Kratsch` — B002 MR3234973
5. `Fundamentals of Parameterized Complexity Downey Fellows` — B002 MR3154461
6. `The Complexity of Theorem-Proving Procedures Cook` — 공개 TCS 씨앗
7. `Reducibility among Combinatorial Problems Karp` — 공개 TCS 씨앗
8. `Hardness vs Randomness Nisan Wigderson` — 공개 TCS 씨앗
9. `Quantum lower bounds by polynomials Beals` — 공개 TCS 씨앗
10. `Towards P not equal NP from Extended Frege Lower Bounds` — ECCC TR23-199 씨앗

각 요청은 도구 수준에서 실패했으므로 title/author/year/venue/DBLP URL을 반환하지 않았고, exact-title 오탐·B002 중복 여부도 DBLP로 판정하지 않았다. 이는 **실행 실패 10/10**, 결과 없음 0/10이다.

## 기존 공개 record와 판본 경계

DBLP가 복구되면 검색 result는 서지 후보 발견에만 쓴다. B002 단행본, STOC/FOCS/CCC proceedings, ECCC technical report, arXiv preprint, 저널판은 제목이 같아도 자동 병합하지 않는다. 예를 들어 Cook은 [ACM DOI](https://doi.org/10.1145/800157.805047), Karp은 [Springer record](https://link.springer.com/book/10.1007/978-1-4684-2001-2), Pich–Santhanam은 [ECCC TR23-199](https://eccc.weizmann.ac.il/report/2023/199/)로 각각 별도 출판 객체를 확인할 수 있다.

검색엔진을 통한 공식 DBLP HTML record의 독립 대조는 Cook 1971에서 성공했다. [DBLP `conf/stoc/Cook71`](https://dblp.org/rec/conf/stoc/Cook71)은 저자, 제목, STOC 1971, 151–158쪽, DOI와 DBLP key를 제공한다. 이는 DBLP에 해당 record가 실제로 있음을 보이지만 Search API 10건의 성공으로 바꾸지는 않는다.

따라서 현재 판정은 **DBLP 공식 metadata는 개별 HTML record에서 사용할 수 있지만, 이 작업환경의 Search/record API 연결은 현재 transport failure라 전수 자동 대조에 사용할 수 없음**이다. 공개 웹의 개별 record와 다른 색인을 먼저 사용하고, 재시도할 때는 query 하나씩 `h≤3`로 유지해 API status·returned title·DBLP key·venue/year를 보존한다. 현재 이 실패만으로 사용자 행동을 열지는 않는다.
