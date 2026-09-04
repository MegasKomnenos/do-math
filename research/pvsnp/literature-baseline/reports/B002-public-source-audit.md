# B002 공개 자료원 감사

조사 기준 시각은 2026-09-04 KST이다. API 요청과 독립 재검사는 같은 날 20:03–20:21 KST에 소규모로 실행했다. 이 보고서는 추천·인용 점수를 핵심성 판정으로 사용하지 않는다.

## 1. 조사 질문과 판정 단위

질문은 네 가지다.

1. B002의 63개 분야·6,233 occurrence·분야당 최대 100건이 실제 원시 파일과 일치하는가?
2. MathSciNet의 MSC·인용순·상위 100 제한이 어떤 문헌 유형과 역사적 분류를 놓칠 수 있는가?
3. zbMATH Open, DBLP, OpenAlex, arXiv와 ECCC, DROPS/LIPIcs, Theory of Computing, STOC·FOCS·CCC 공식 페이지가 그 누락을 실제 식별자·제목·분류·venue로 보완하는가?
4. 공개 조사로 닫히지 않는 독립 누락이 입증되어 인증 B003 사용자 묶음이 필요한가?

여기서 `occurrence`는 분야 export의 레코드 수이고, 서로 다른 분야에 중복 출현할 수 있다. `핵심성`은 제목·내용·분야 역할과 원문을 읽어 판정할 후속 단계이며, 이 감사는 공개 자료원이 누락 후보를 회수하는 능력과 한계를 판정한다.

## 2. B002 원자료 대조

정본은 [`manifests/B002.json`](../manifests/B002.json), 검색표는 [`batches/B002-queries.tsv`](../batches/B002-queries.tsv), 원시는 `intake/B002/mathscinet/`이다. manifest를 다시 집계한 결과는 다음과 같다.

| 항목 | 실제 값 | 대조 근거 |
|---|---:|---|
| 분야 artifact | 63 | `B002.json`의 `artifacts` 배열 |
| export occurrence 합 | 6,233 | `record_count` 합계 |
| 분야당 100건 | 60개 분야 | `record_count=100` |
| 전체 결과가 100건 미만인 분야 | `19: 89`, `85: 85`, `97: 59` | manifest의 `total_results=record_count` |
| 전체 hit 합 | 61,500 | audit 보고서와 manifest의 `total_results` 합 |

검색표의 컴퓨터과학 행은 `68-00 OR 68-01 OR 68-02`이고, manifest의 실제 MathSciNet 표현은 `pcsc:(68-00 OR 68-01 OR 68-02)`, 전체 결과 2,131건, export 100건이다. 자동화 감사는 00·01·03에서 수동 export와 MR 키 집합·순서·LF 정규화 BibTeX 전체 바이트가 일치했고, 단위 검사 8건과 dry-run(`pending=0`, `skipped=63`)을 통과했다고 기록한다([`B002-automation-audit.md`](B002-automation-audit.md)). 따라서 이 감사에서 B002 수집 실패를 주장할 근거는 없다.

그러나 원시 `intake/B002/mathscinet/68/mathscinet.bib`를 다시 세면 `@book=100`, `@article=0`, `@inproceedings=0`이다. 표본은 다음과 같다.

| MR 번호 | 제목 | 원시 기록의 출판 맥락 | `MRCLASS` |
|---|---|---|---|
| MR1251285 | *Computational complexity* (Papadimitriou) | 1994 Addison–Wesley 단행본 | `68Q15 (68-02 68Q25)` |
| MR2500087 | *Computational complexity: A modern approach* (Arora–Barak) | 2009 Cambridge University Press 단행본 | `68-01 (03D15 68Q15 68Q17 68Q25 81P68 94A60)` |
| MR1479636 | *Complexity and real computation* (Blum–Cucker–Shub–Smale) | 1998 Springer 단행본 | `68Q15 (03D15 13P99 14P99 65Y20 68-02)` |
| MR1440179 | *Algebraic complexity theory* (Bürgisser–Clausen–Shokrollahi) | 1997 Springer 단행본 | `68-02 (12Y05 65Y20 68Q05 68Q15 68Q25 68Q40)` |

이는 “MSC 68 검색이 비어 있다”는 뜻이 아니다. B002가 실제로 100건을 회수했지만, 해당 분야의 인용순 첫 페이지가 단행본으로 포화되어 STOC·FOCS·CCC의 proceedings와 ECCC report가 이 표본에 나타나지 않는다는 관찰이다. 원시 표본은 학회록이 B002에 전혀 없다고 증명하지 않으며, **상위 100 표본에서 확인되지 않는다**고만 판정한다.

## 3. 공개 API의 실제 소규모 요청

### 3.1 zbMATH Open

실행 endpoint:

```text
GET https://api.zbmath.org/document/_search?search_string=ti%3A%22P%20versus%20NP%22&page=0&results_per_page=3
```

독립 재검사 응답 시각은 응답의 `status.time_stamp`가 `2026-09-04T11:21:05Z`(20:21:05 KST)였다. HTTP 200, `status.execution=successful request`, `nr_total_results=17`, `nr_request_results=3`이었다. 요청한 첫 세 식별자는 다음과 같다.

| zbMATH id | Zbl identifier | 제목 | 유형 | MSC |
|---:|---|---|---|---|
| 5787962 | 1194.68001 | *The P versus NP problem* | serial article | `68-01`, `68Q15` |
| 6516614 | 1326.68140 | *The importance of the P versus NP question* | journal article | `68Q15` |
| 5817628 | 1208.68129 | *P versus NP and geometry* | journal article | `68Q15`, `14Q99` |

ID 5787962 단건 endpoint(`GET https://api.zbmath.org/document/5787962`)도 200으로 확인했다. Cook의 2006년 *The Millennium Prize Problems* 수록 글(87–104쪽), AMS/Clay Mathematics Institute 출판, MSC `68-01`·`68Q15`를 반환했다. 즉 zbMATH는 MathSciNet의 MSC 결과를 단순 복제하는 것만이 아니라 Zbl 식별자·문서 유형·역사적 출판 맥락을 독립적으로 제공한다. 검색 문법과 필드(`ti`, `cc`, `dt` 등)는 공식 검색 도움말([zbMATH General Help](https://zbmath.org/general-help/))에 공개되어 있고, REST 조건은 [공식 API 약관](https://api.zbmath.org/)에 있다. API 루트가 먼저 이용약관 동의를 요구한다는 점, 트래픽 제어·권리 조건, 일부 제3자 초록이 API에 포함되지 않을 수 있다는 점은 한계다. 따라서 한 번의 query 결과를 전수성 증거로 쓰지 않고, 분야·문서 유형을 분할해 사용한다.

### 3.2 DBLP

실행 endpoint 1:

```text
GET https://dblp.org/search/publ/api?q=geometric%20complexity%20theory&format=json&h=5
```

HTTP 200, API 상태 `200 OK`, `hits.@total=50`, `@sent=5`, `@first=0`이었다. 반환 표본에는 다음이 포함됐다.

| DBLP id/key | 제목 | venue·연도 | 유형 |
|---:|---|---|---|
| 6788476 / `journals/corr/abs-0908-1932` | *On P vs. NP, Geometric Complexity Theory, Explicit Proofs and the Complexity Barrier* | CoRR, 2009 | Informal and Other Publications |
| 7184270 / `journals/corr/abs-0704-0229` | *Geometric Complexity Theory VI: the flip via saturated and positive integer programming in representation theory and algebraic geometry* | CoRR, 2007 | Informal and Other Publications |
| 92965 / `journals/jsc/DuttaGIJL26` | *Geometric complexity theory for product-plus-power* | J. Symb. Comput., 2026 | Journal Articles |

실행 endpoint 2:

```text
GET https://dblp.org/search/publ/api?q=Witness%20Encryption%20NP-Hardness%20Learning&format=json&h=3
```

HTTP 200, `hits.@total=2`, `@sent=2`였다. 같은 제목이 `conf/coco/GoldbergK25`의 **CCC 2025**와 `journals/eccc/GoldbergK25`의 **Electronic Colloquium on Computational Complexity 2025**로 각각 나타났다. 이는 학회판·기술보고판의 관계를 공개 서지로 발견할 수 있다는 실제 예이며, 두 판본을 자동 병합해서는 안 된다는 근거이기도 하다.

DBLP의 공식 FAQ는 publication·person·venue API, JSON/XML 응답과 `h`/`f` 페이지네이션을 설명한다([DBLP Search API FAQ](https://dblp.org/faq/13501473.html)). 검색 hit 상한은 1,000이므로 넓은 query는 venue·연도·저자 등으로 나눠야 한다. DBLP는 bibliographic metadata이며 증명·초록·원문이나 peer-review 판정의 근거가 아니다.

### 3.3 OpenAlex

두 요청을 실행했다.

```text
GET https://api.openalex.org/works?filter=title.search:geometric%20complexity%20theory&per-page=3
GET https://api.openalex.org/works?filter=doi:10.1109/focs.2015.20
```

첫 응답은 `meta.count=136`, 3건 반환이었다.

| OpenAlex id | 제목 | 연도 | source/유형 | DOI |
|---|---|---:|---|---|
| W2074207216 | *Geometric Complexity Theory I: An Approach to the P vs. NP and Related Problems* | 2001 | SIAM Journal on Computing / article | `10.1137/S009753970038715X` |
| W1995509652 | *Geometric Complexity Theory II: Towards Explicit Obstructions for Embeddings among Class Varieties* | 2008 | SIAM Journal on Computing / article | `10.1137/080718115` |
| W2007666181 | *Geometric complexity theory and tensor rank* | 2011 | source 미지정 / article | `10.1145/1993636.1993704` |

두 번째 응답은 `meta.count=1`로 DOI `10.1109/FOCS.2015.20`의 *Indistinguishability Obfuscation from Functional Encryption*을 `type=conference-paper`로 반환했다. 따라서 OpenAlex는 DOI 연결과 conference-paper 유형을 공개적으로 보완하지만, source 누락처럼 metadata가 불완전할 수 있다. API 문서는 search/filter/sort, paging과 cursor, 10,000건 page 한계를 설명한다([OpenAlex API](https://help.openalex.org/api/), [paging](https://help.openalex.org/api/paging/)). `count`, relevance, citation은 후보 확장용이며 핵심성이나 완전성의 증거가 아니다.

### 3.4 arXiv

실행 endpoint:

```text
GET https://export.arxiv.org/api/query?search_query=all:%22P%20vs%20NP%22&start=0&max_results=3
```

HTTP 200, `opensearch:totalResults=65`, `itemsPerPage=3`, 응답 `updated=2026-09-04T11:04:22Z`였다. 반환된 세 최신 record는 모두 exact version과 범주를 드러냈다.

| arXiv record | 제목 | primary category |
|---|---|---|
| `arXiv:0805.2170v6` | *Independence of P vs. NP in regards to oracle relativizations* | `cs.CC` |
| `arXiv:0908.1932v2` | *On P vs. NP, Geometric Complexity Theory, Explicit Proofs and the Complexity Barrier* | `cs.CC` |
| `arXiv:2401.08668v3` | *Thermodynamic Perspectives on Computational Complexity: Exploring the P vs. NP Problem* | `cs.IT` |

arXiv API는 metadata·검색·pagination을 제공하지만 posting은 peer review가 아니며, OAI 수확은 article item별 최신 version 중심이다. 공식 문서는 API·OAI·RSS 경로를 설명하고 datestamp가 제출일과 다를 수 있음을 고지한다([arXiv API Access](https://info.arxiv.org/help/api/index.html), [arXiv OAI-PMH](https://info.arxiv.org/help/oa/index.html)). 따라서 `vN`, history, journal reference를 별도로 기록하고, arXiv만으로 출판 상태나 주장 진위를 확정하지 않는다.

## 4. 공식 venue·repository 페이지가 보완하는 기록

공개 페이지를 실제로 열어 제목·분류·venue·출판 맥락을 확인했다.

| 자료원과 실제 record | 확인한 사실 | B002 누락 유형에 대한 역할 |
|---|---|---|
| [ECCC TR04-062](https://eccc.weizmann.ac.il/report/2004/062/) | Stasys Jukna, *On the P versus NP intersected with co-NP question in communication complexity*; report와 Revision 1, keywords `best-partition protocols`, `Communication complexity`, 2004 | MathSciNet 상위 100에서 보이지 않은 technical report·revision·통신복잡도 경로를 직접 회수 |
| [ECCC TR23-199](https://eccc.weizmann.ac.il/report/2023/199/) | Pich–Santhanam, *Towards P ≠ NP from Extended Frege Lower Bounds*, 2023; proof complexity와 Boolean circuit lower bounds를 명시 | 증명복잡도·회로 하계의 최신 frontier를 report 번호와 revision으로 고정 |
| [DROPS CCC 2025 record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.34) | *Witness Encryption and NP-Hardness of Learning*, DOI `10.4230/LIPIcs.CCC.2025.34`, LIPIcs vol. 339, pages `34:1–34:43`, CCC 2025; OA | CCC proceedings의 DOI·volume·conference context·원문 링크를 제공 |
| [DROPS CCC series](https://drops.dagstuhl.de/entities/conference/CCC) | CCC 2022–2026 volume이 LIPIcs에 연결되고 2025는 volume 339로 표시 | 연도별 proceedings 전개와 DBLP·arXiv 판본 연결의 기준 |
| [Theory of Computing GS010](https://www.theoryofcomputing.org/articles/gs010/) | Bläser–Ikenmeyer, *Introduction to Geometric Complexity Theory*, Graduate Survey 10, 166 pages, 2025; categories에 complexity·geometric/algebraic complexity·representation theory | 수학 중심 MSC 검색에서 흩어지는 GCT 종합·이론CS survey를 venue archive에서 직접 발견 |
| [STOC 2025 TOC](https://acm-stoc.org/stoc2025/toc.html) | ACM 공식 proceedings page에 57th STOC record가 있고 Ryan Williams의 *Simulating Time with Square-Root Space*가 P 대 PSPACE 맥락을 명시 | ACM 학회록의 최신 논문·세부 초록을 MathSciNet 분야 첫 페이지와 독립 대조 |
| [FOCS 2024 accepted papers](https://focs.computer.org/2024/accepted-papers-for-focs-2024/) | 공식 행사 페이지에 *Polynomial Calculus sizes over the Boolean and Fourier bases are incomparable*, 그리고 communication complexity·algebraic computation·streaming algorithms 주제가 나타남 | FOCS의 proof/communication/algebraic complexity 가지를 venue·program 단위로 보완 |
| [FOCS 2024 proceedings](https://ieee-focs.org/FOCS-2024-Papers/content/start.html) | IEEE Computer Society Conference Publishing Services의 proceedings, IEEE catalog `CFP24053-ART`, ISBN `979-8-3315-1674-1` | 학회록이 단순 발표 목록이 아니라 출판된 proceedings임을 판본 정보로 확인 |
| [CCC 공식 archive/scope](https://computationalcomplexity.org/general.html) | CCC가 계산복잡도의 결정론·비결정론·무작위·양자, Boolean·algebraic·continuous model, proof/descriptive complexity 등을 범위로 명시; 2015년 이후 LIPIcs 출판 | MSC 68 상위 100보다 넓은 계산복잡도 연구 전선과 역사적 IEEE→LIPIcs venue 전환을 닫음 |

이 표의 venue 페이지는 문헌의 수학적 진위를 확정하지 않는다. ECCC는 technical report, arXiv는 preprint, 학회 proceedings는 해당 판본의 primary publication이라는 식으로 출판 지위를 구별한다. CCC 공식 설명도 2010년까지 IEEE 계열 paper proceedings, 2015년 이후 LIPIcs라는 역사적 전환을 명시한다. [DROPS About](https://drops.dagstuhl.de/docs/about) 역시 LIPIcs가 informatics conference proceedings series이며 공개 metadata·DOI를 제공한다고 설명한다.

## 5. MathSciNet 누락 유형의 판정

확정 사실과 그로부터의 추론을 구분한다.

### 확정 사실

- B002는 63개 MSC 분야에서 6,233 occurrence를 저장했고, 60개 분야는 정확히 100건이다.
- MSC `68`의 원시 상위 100은 전부 `@book`이고 `@inproceedings`가 없다.
- zbMATH·DBLP·OpenAlex·arXiv의 위 query는 각각 실제 식별자·제목·문서 유형/범주/venue를 반환했다.
- DBLP는 CCC 2025와 ECCC 2025의 같은 제목을 별도 record로 반환했다.
- ECCC·DROPS·Theory of Computing·STOC·FOCS·CCC 공식 페이지는 report revision, LIPIcs DOI/volume, survey category, conference proceedings와 program/abstract를 직접 제공한다.

### 관찰

- B002 검색식은 MSC 대분류의 `-00/-01/-02` 기준 핵심층만 사용한다. ECCC report 번호, arXiv category, ACM/IEEE conference venue, LIPIcs series는 검색 조건에 없다.
- `citation order`의 첫 페이지는 핵심 문헌의 완전한 목록이 아니라 해당 MSC 결과에서 높은 인용의 표본이다. 특히 컴퓨터과학 분야에서 표준 단행본이 먼저 나오면 최근·학회 중심 문헌이 뒤로 밀릴 수 있다.
- 역사적 MSC는 `MRCLASS`의 괄호 속 연결 분류로만 남을 수 있다. 예를 들어 MR2500087은 주분류 `68-01`과 `03D15`, `68Q15`, `81P68`, `94A60`를 함께 갖는다. 따라서 현재 MSC 하나만으로 문헌의 실제 이론적 역할을 모두 복원할 수 없다.

### 추론

- 위 관찰과 독립 공개 record를 종합하면, **B002 수집의 무결성**과 **문헌 우주의 포괄성**은 다른 판정이다. 전자는 통과했고 후자는 공개 누락 검사가 추가로 필요하다.
- 학회록·ECCC·arXiv의 독립 식별자와 venue 맥락은 공개 자료원 조합으로 먼저 닫을 수 있다. 그러므로 이 누락 유형을 인증 DB 검색으로 바로 이관하는 것은 현재 근거상 과잉이다.
- 공개 자료원은 metadata·검색 회수 증거이며 원문 주장·정정·peer review·판본 동일성을 대신하지 않는다. 후보 선별 후 공식 원문을 한 건씩 읽는 후속 작업이 필요하다.

## 6. 공개 후속 조사 범위

B003 사용자 묶음으로 만들지 않고 AI 공개 조사에서 수행할 범위는 다음과 같다.

1. DBLP venue stream/API에서 STOC·FOCS·CCC 및 관련 venue를 연도별로 나눠 수확한다. API `h≤1000` 제한을 지키고 query·first/last hit·응답 시각을 보존한다.
2. CCC는 2015년 이후 LIPIcs volume, 2010년 이전 역사적 IEEE proceedings, 2011–2014 전환기 archive를 별도 판본으로 연결한다. 학회판·ECCC·arXiv·저널판을 자동 병합하지 않는다.
3. ECCC에서 P vs NP, circuit/proof complexity, barriers, average-case, communication, algebraic, quantum 등의 제목·keyword·연도 경로를 소규모로 나눠 report number와 revision을 기록한다.
4. arXiv `cs.CC`와 인접 범주를 exact version으로 검색하고, DBLP·Crossref·공식 venue에서 출판 관계를 확인한다.
5. zbMATH에서 `ti`, `ab`, `cc`, `dt`를 조합해 MathSciNet의 MSC 가족과 독립적인 title/abstract·문서유형 검색을 반복한다. API 요청은 공개 조건·트래픽 제한 안에서 소규모로 유지한다.
6. Theory of Computing archive와 Graduate Surveys, DROPS/LIPIcs의 CCC·ITCS·ICALP·SAT 등 실제 관련 volume을 먼저 조사하고, STOC·FOCS 공식 archive는 제목·program·proceedings 식별용으로 쓴다.
7. 후보별 DOI·revision·venue가 정해진 뒤 Crossref/OpenAlex/Unpaywall은 판본과 공개 원문 위치를 보완하는 데만 사용한다. citation count·추천 순위는 핵심성 결정에 사용하지 않는다.

이 범위는 공개 자료원이 회수할 수 있는 **누락 후보의 발견·식별·판본 연결**이다. 원문 대량 다운로드, PDF 전수 수집, 인증 DB 크리덴셜 사용은 포함하지 않는다.

## 7. 인증 B003 필요 여부

**현재 판정: 불필요.** 이유는 다음과 같다.

- 인증 B003이 정당화되려면 공개 경로로 닫히지 않은 독립 누락을 구체적 후보와 함께 제시해야 한다. 이번 감사에서는 그러한 후보를 확인하지 못했다.
- B002의 구조적 공백은 MathSciNet의 실패가 아니라 `MSC + citation-order + top-100` 수확 설계의 한계다. DBLP·zbMATH·arXiv·ECCC·DROPS·Theory of Computing·공식 STOC/FOCS/CCC 페이지가 각 공백의 공개 보완 경로를 이미 제공한다.
- Web of Science/Scopus/PQDT/인증 ACM·IEEE 검색은 독립 색인·인용망·학위논문 범위를 추가할 수 있지만, “있으면 더 넓다”는 이유만으로 현재 사용자 묶음을 열지 않는다. 공개 후속 조사 뒤에도 (a) 공개 색인에 존재하지 않는 특정 후보가 남거나, (b) 조사 완료 조건이 독점 DB의 전수 결과를 명시적으로 요구하거나, (c) 특정 학위논문·학회록의 서지 record가 공개 자료원에서 재현되지 않을 때만 B003을 설계한다.

따라서 다음 상태는 `B003 미개설, 공개 후속 조사 open`이다. 이는 문헌 집합이 이미 완결됐다는 뜻이 아니며, 인증 검색 없이도 먼저 수행 가능한 누락 검사를 분리한다는 뜻이다.

## 8. 남은 불확실성·실패와 미실행

- DBLP의 첫 `P vs NP` literal query는 일시적으로 HTTP 503을 반환했다. 같은 API의 `geometric complexity theory`와 `Witness Encryption...` query는 HTTP 200으로 재실행됐으므로, 503을 결과 없음으로 해석하지 않았다. 이는 **실패**이지 결과 없음이 아니다.
- OpenAlex의 `search=P vs NP`는 full-text 검색으로 넓은 결과(`meta.count=462,577`)를 반환해 title 후보 수로 사용하지 않았다. 이후 `filter=title.search:geometric complexity theory`와 DOI 단건으로 범위를 닫았다. 넓은 응답은 실패가 아니지만 목적에 맞지 않는 검색 결과다.
- zbMATH API root는 약관 동의 HTML을 반환했고, endpoint 요청은 성공했다. API 약관·트래픽·권리 조건의 세부 승인은 이 감사에서 사용자 크리덴셜로 우회하지 않았다.
- 이 감사는 MathSciNet 결과 전체를 공개 DB와 record-by-record deduplicate하지 않았다. 따라서 공개 자료원에 같은 작업이 있더라도 동일 작업·판본·정정 관계는 후속 후보별 대조가 필요하다.
- ECCC·DROPS·Theory of Computing·STOC·FOCS·CCC 페이지에서 확인한 것은 제목·분류·venue·출판 맥락과 공개 접근 경로다. 해당 문헌의 모든 정리·증명을 독립 재검증하지 않았다.
- 인증 자료원 자체를 검색하지 않았다. 그러므로 인증 DB에만 존재하는 후보가 없다고 주장하지 않는다. 현재 근거는 “아직 특정되지 않았으며, 공개 보완선을 먼저 소진해야 한다”는 판정이다.
