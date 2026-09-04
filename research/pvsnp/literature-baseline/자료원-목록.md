# P vs NP 문헌조사 자료원 목록

조사일: 2026-09-04 KST

이 목록은 자료원 유형이나 지표로 자동 선별한 결과가 아니다. KUDOS 현행 목록, 각 서비스의 실제 범위, 제공 목록의 실물, P vs NP 및 전 분야 조사에서 맡을 역할과 다른 자료원과의 중복을 직접 대조한 결과다. 자료원의 선정은 그 안의 모든 문헌을 채택한다는 뜻이 아니다.

## 1. 인증 발견 자료원

인증 검색은 이 여섯 인터페이스로 한정한다. Web of Science Core Collection과 CPCI는 KUDOS에서는 별도 항목이지만 한 인터페이스에서 함께 운용한다. 검색식·투입 위치·사용자 직접 수행 또는 승인된 브라우저 자동화 여부는 현재 조사 묶음이 정한다.

| ID | 자료원 | 이 조사에서 찾을 것 | 선택한 이유 | 원시 출력 |
|---|---|---|---|---|
| `mathscinet` | [MathSciNet](https://mathscinet.ams.org/mathscinet) | MSC별 표준 교재·종합·핵심 원 성과·리뷰, P vs NP 직접·인접 수학, 전후방 인용 | MSC를 직접 검색하고 책·학위논문·논문·리뷰를 함께 다루는 수학 전문 색인 | BibTeX 우선, 불가하면 EndNote 또는 공유 목록 |
| `wos` | [Web of Science Core Collection + CPCI](https://www.webofscience.com) | 전 분야 핵심 저널·책·학회록, 직접 주제, cited-reference와 citing works | 수학 전문 색인과 다른 선별 범위와 인용망을 제공하고 CPCI가 학회록을 보완 | RIS 또는 plain text의 Full Record and Cited References, 불가하면 Excel |
| `scopus` | [Scopus](https://www.scopus.com) | 전 분야 논문·책·학회록, 직접 주제, references·cited by·secondary documents | Web of Science와 색인 범위와 저자·문헌 매칭이 달라 독립 누락 검사에 유효 | CSV 우선. DOI·초록·키워드·참고문헌·인용 수 포함 |
| `acm-dl` | [ACM Digital Library](https://dl.acm.org) | JACM·TOCT·TALG·TOCL, STOC와 SIGACT 계열, 계산복잡도·알고리즘·논리 | ACM 원문 컬렉션과 Guide to Computing Literature가 저널·학회록·책·기술보고를 함께 연결 | BibTeX 또는 EndNote/ACM Ref |
| `ieee-xplore` | [IEEE Xplore / IEL](https://ieeexplore.ieee.org) | FOCS, 과거 CCC, LICS, IEEE Transactions on Information Theory와 관련 이론 논문 | KUDOS 2026 제공 목록에서 FOCS 전신부터 현행 학회록과 과거 CCC 수록을 확인 | citation export. PDF는 B001에서 받지 않음 |
| `pqdt` | [PQDT Global](https://search.proquest.com/pqdtglobal) | P vs NP·복잡도 하계·장벽·인접 방법의 석·박사 학위논문과 참고문헌·보충자료 | 저널·학회 논문보다 긴 논증, 부정 결과와 후속 과제를 담는 비저널 연구를 보완 | RIS 또는 DB가 제공하는 citation export |

### 검색하지 않는 KUDOS 항목의 처리

KUDOS 공식 목록에는 128개 항목이 있지만 모두 문헌 발견 DB는 아니다. 다음 항목은 첫 발견 검색에서 제외한다.

- EndNote·Mendeley·RefWorks·Grammarly·Turnitin·iThenticate 같은 관리·작성 도구
- JCR·InCites·SciVal·S2 Journal 같은 평가·분석 도구
- 의학·법률·신문·기업·임상·예술처럼 현대 수학과 이론 컴퓨터과학의 독립 조사 우주가 아닌 전문 서비스
- 선정된 여섯 색인과 거의 같은 후보를 제공하면서 독립적인 수학·이론CS 분류나 인용망이 없는 광역 원문 플랫폼

제외는 그 서비스의 자료가 무가치하다는 뜻이 아니다. 선별 문헌의 원문이 그 플랫폼에 있을 때는 원문 경로로 사용한다.

## 2. AI 공개 주자료원

AI가 직접 검색한다. 사용자는 이 자료원에서 export를 만들지 않는다.

| 자료원 | 맡는 범위 | 운용 방식 |
|---|---|---|
| [zbMATH Open](https://zbmath.org/) | MSC2020 전 분야의 문헌·리뷰·serial·책·소프트웨어 | MathSciNet과 독립 대조하고 분야별 기준 핵심층·식별자를 찾는다. |
| [arXiv](https://arxiv.org/) | 수학·이론CS 최신 프리프린트와 판본 이력 | 범주·검색어·인용망으로 최신 전선을 찾고 `arXiv:<id>vN`을 고정한다. |
| [DBLP](https://dblp.org/) | 컴퓨터과학 저널·학회·저자·venue 서지 | ACM·IEEE·DROPS의 누락과 판본 중복을 대조한다. |
| [ECCC](https://eccc.weizmann.ac.il/) | 계산복잡도 기술보고·survey·revision | 회로·증명·대수·평균 경우·통신·양자 등 최신 복잡도 결과를 직접 찾는다. |
| [DROPS/LIPIcs](https://drops.dagstuhl.de/entities/series/LIPIcs) | CCC·ICALP·ITCS·RANDOM·SAT·STACS·ITP 등 공개 학회록과 artifact | 학회·연도별 원문과 DOI를 고정하고 DBLP·arXiv 판본과 연결한다. |
| [Theory of Computing](https://theoryofcomputing.org/) | 동료심사 이론CS 논문·survey·exposition | 전체 archive와 Graduate Surveys를 조사하고 arXiv·Crossref 판본을 연결한다. |

## 3. 후보별 보완 자료원

이 자료원들은 전 분야에 같은 검색을 반복하지 않는다. 주자료원에서 후보가 생겼거나 독립 누락 검사가 필요할 때 AI가 연다.

| 역할 | 자료원 | 사용 시점 |
|---|---|---|
| DOI·판본·정정 | [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), [Crossmark](https://www.crossref.org/services/crossmark/) | DOI를 가진 후보의 서지, relation, correction·retraction 상태 확인 |
| 전 분야 연결 그래프 | [OpenAlex](https://help.openalex.org/), [Semantic Scholar](https://www.semanticscholar.org/product/api) | 다른 색인에서 빠진 관련 작업·저자·source 후보 탐색. 추천·인용 순위는 판정으로 사용하지 않음 |
| 독립 인용 관계 | [OpenCitations](https://opencitations.net/) | 핵심 작업의 incoming/outgoing citation 교차검산 |
| 공개 원문 탐색 | [Unpaywall](https://unpaywall.org/products/), [CORE](https://core.ac.uk/) | DOI의 공개 판본과 기관·분야 저장소의 공개 원고 탐색 |
| 역사·유럽 수학 원문 | [Project Euclid](https://projecteuclid.org/), [EuDML](https://eudml.org/), [Numdam](https://www.numdam.org/) | 선별한 역사 수학 문헌과 공개 판본 확보 |
| 형식 증명 | [mathlib](https://github.com/leanprover-community/mathlib4), [AFP](https://isa-afp.org/), [Mathematical Components](https://math-comp.github.io/) | 관련 정리가 실제로 존재할 때 정확한 선언·release·도구체인 확인 |
| 코드·데이터·보존 | [GitHub](https://github.com/), [Zenodo](https://zenodo.org/), [Software Heritage](https://www.softwareheritage.org/) | 문헌이 사용하는 코드·데이터의 release·commit·DOI·SWHID 고정 |

일반 웹 검색은 후보 발견과 누락 검사의 별도 경로다. 검색 결과 snippet이나 AI 요약은 근거로 채택하지 않고 원 운영기관·원문으로 이동한다.

## 4. 원문 확보 자료원

KUDOS의 AMS·CUP·De Gruyter·JSTOR·OUP·ScienceDirect·Springer·Taylor & Francis·Wiley·AIP·APS·IOP와 KNU FRIC·개별 구독은 선별 후보의 원문 확보에 사용한다. SIAM, 학회·저널 공식 사이트, 저자·기관 공개본도 같은 역할을 맡는다.

출판사 플랫폼마다 광역 키워드 검색을 반복하지 않는다. DOI·제목·저자·정확한 판본으로 원문을 찾는다. 원문 경로가 실패할 때만 다른 허용 경로로 이동한다.

## 5. 실제 수록 대조

KUDOS의 공개 제공 목록에서 다음을 직접 확인했다.

- [ACM Open 2026](https://kudos.knu.ac.kr/download/db/ACM%20Open%20TitleList%282026%29.xlsx): *Journal of the ACM*, *ACM Transactions on Computation Theory*, *ACM Transactions on Algorithms*, *ACM Transactions on Computational Logic*.
- [IEL 2026](https://kudos.knu.ac.kr/download/db/IEL%20Title%20List%282026%29.xlsx): 1960년대 이후 FOCS 전신과 FOCS, 과거 IEEE CCC 학회록.
- [Springer eJournal 2026](https://kudos.knu.ac.kr/download/db/Springer%20eJournal%20TitleList%282026%29.xlsx): *Computational Complexity*, *Foundations of Computational Mathematics*.
- [ScienceDirect 2025](https://kudos.knu.ac.kr/download/db/lists/ScienceDirect%20TitleList%282025%29.xlsx): *Journal of Computer and System Sciences*, *Information and Computation*, *Theoretical Computer Science*, *Journal of Complexity*, *Advances in Mathematics*, *Journal of Combinatorial Theory*.
- [CUP 2026](https://kudos.knu.ac.kr/download/db/lists/CUP%20TitleList%282026%29.xlsx): *Journal of Symbolic Logic*, *Review of Symbolic Logic*, *Combinatorics, Probability and Computing*, *Compositio Mathematica*.
- [Wiley 2026](https://kudos.knu.ac.kr/download/db/lists/Wiley%20TitleList%282026%29.xlsx): *Random Structures & Algorithms*, *Journal of Graph Theory*, *Bulletin of the London Mathematical Society*, *Journal of the London Mathematical Society*.
- [JSTOR 2026](https://kudos.knu.ac.kr/download/db/JSTOR%20Archival%20TitleList%282026%29.xlsx): *Annals of Mathematics*와 *Journal of Symbolic Logic*의 역사 archive.

## 6. 이용 경계

[KUDOS 공식 목록](https://kudos.knu.ac.kr/eng/sub.htm?nav_code=eng1643175350)은 로그인 없이 128개 항목과 제공 목록을 공개하므로 목록 확인에는 크리덴셜을 쓰지 않았다. 인증 검색은 사용자가 직접 수행한다.

KUDOS의 같은 페이지는 특정 전자자원에서 30건 이상의 논문·저널, 책·저널 전건, 프로그램이나 서지관리도구를 통한 자동 대량 원문 다운로드를 공정 이용 위반으로 명시한다. [IEEE Xplore의 현행 법적 안내](https://ieeexplore.ieee.org/Xplorehelp/overview-of-ieee-xplore/legal-information)도 로봇·지능형 에이전트의 검색과 체계적 다운로드를 금지한다. 따라서 원문은 자동 수집하지 않고 AI가 선별한 뒤 허용 범위에서 개별 확보한다. 서지정보 export 자동화 여부는 자료원별 조건과 사용자의 명시적 결정을 현재 조사 묶음에 기록한다.

공개 자료원의 공식 근거와 한계는 [`../../../docs/wayfinder/pvsnp-재설계/합리화-자료원-외부근거.md`](../../../docs/wayfinder/pvsnp-재설계/합리화-자료원-외부근거.md)에 있다.
