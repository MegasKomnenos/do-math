# B002 초기 핵심층 검토: MSC 68–97 배정 분야와 이론 컴퓨터과학 공개 씨앗

검토일: 2026-09-04 KST  
상태: **초기 선별 완료.** 이것은 `covered` 판정이나 최종 핵심층 승인이 아니다.

## 1. 범위, 원자료, 판정 방법

이 보고서는 배정된 MSC `68, 70, 74, 76, 78, 80, 81, 82, 83, 85, 86, 90, 91, 92, 93, 94, 97`만 다룬다. `B002-candidates.jsonl`의 모든 후보 행을 JSON으로 파싱하고, 각 후보의 `provenance[].field_code`가 이 목록에 있는 출현을 기계적으로 추출했다. 그 뒤 각 출현의 원문 `TITLE`, `AUTHOR` 또는 `EDITOR`, `YEAR`, `MRCLASS`, BibTeX 유형, 출판 필드를 다시 읽었다. 정규화 제목, 인용순, 관계 후보, 이 보고서 이전의 요약은 핵심성 근거로 사용하지 않았다.

| MSC | 실제 출현 | 고유 MR 후보 | 원문 유형 (book/article/나머지) | 전체 결과를 저장했는가 |
|---|---:|---:|---:|---|
| 68 | 100 | 100 | 100 / 0 / 0 | 아니오, 2,131 중 상위 100 |
| 70 | 100 | 100 | 89 / 7 / 4 | 아니오, 781 중 상위 100 |
| 74 | 100 | 100 | 95 / 4 / 1 | 아니오, 542 중 상위 100 |
| 76 | 100 | 100 | 91 / 6 / 3 | 아니오, 940 중 상위 100 |
| 78 | 100 | 100 | 96 / 3 / 1 | 아니오, 438 중 상위 100 |
| 80 | 100 | 100 | 88 / 7 / 5 | 아니오, 157 중 상위 100 |
| 81 | 100 | 100 | 87 / 11 / 2 | 아니오, 4,313 중 상위 100 |
| 82 | 100 | 100 | 78 / 15 / 7 | 아니오, 1,868 중 상위 100 |
| 83 | 100 | 100 | 84 / 12 / 4 | 아니오, 930 중 상위 100 |
| 85 | 85 | 85 | 64 / 15 / 6 | 예, 85 전건 |
| 86 | 100 | 100 | 68 / 23 / 9 | 아니오, 210 중 상위 100 |
| 90 | 100 | 100 | 95 / 4 / 1 | 아니오, 3,258 중 상위 100 |
| 91 | 100 | 100 | 95 / 2 / 3 | 아니오, 1,759 중 상위 100 |
| 92 | 100 | 100 | 94 / 5 / 1 | 아니오, 708 중 상위 100 |
| 93 | 100 | 100 | 94 / 5 / 1 | 아니오, 2,930 중 상위 100 |
| 94 | 100 | 100 | 73 / 4 / 23 | 아니오, 1,281 중 상위 100 |
| 97 | 59 | 59 | 15 / 30 / 14 | 예, 59 전건 |
| **합계** | **1,644** | **1,573** | — | `85`, `97`만 전건 |

`1,644` 출현과 분야별 수의 합은 일치한다. 분야를 가로질러 중복된 MR이 있으므로 고유 MR 수는 1,573이다. 분야 표의 `나머지`는 `incollection`, `inproceedings`, `proceedings`다. 특히 `68`의 100건은 모두 `book`이다. 이 사실은 B002의 해당 표본에 원 논문·학회판이 없다는 관찰일 뿐, 그 분야에 그런 문헌이 없다는 결론이 아니다.

아래의 “공개 대조”는 해당 URL에서 제목·저자·출판처/문서유형 또는 venue를 대조한 범위다. DOI는 출판사 landing page로 연결되는 영구 식별자이며, Crossref 공개 API 응답으로도 제목·유형·출판처를 대조했다. 원문 PDF를 대량 내려받거나 정리·증명을 판독하지 않았다. 따라서 “역할”은 제목, MRCLASS, 출판 맥락과 공식 record가 지지하는 초기 분야 역할이며, 수학적 주장이나 후속 채택의 검증이 아니다.

## 2. 분야별 B002 후보와 초기 처분

| MSC | B002에서 실제 확인한 후보와 초기 역할 | 공개 대조 URL 및 확인 범위 | P vs NP에 대한 초기 처분·결손·다음 공개 검색 |
|---|---|---|---|
| `68` Computer science | **MR2500087**, Arora–Barak, *Computational complexity* (2009), book, `68-01 (03D15 68Q15 68Q17 68Q25 81P68 94A60)`: 표준 입문 후보. **MR1440179**, Bürgisser–Clausen–Shokrollahi, *Algebraic complexity theory* (1997), book, `68-02 (...) 68Q15 68Q40`: 대수적 복잡도 기준 전거 후보. **MR1426129**, Kushilevitz–Nisan, *Communication complexity* (1997), book, `68Q15 (...) 94C10`: 통신복잡도 기준 전거 후보. **MR1732784**, Immerman, *Descriptive complexity* (1999), book, `68Q19`: 기술복잡도 기준 전거 후보. | [Cambridge: Arora–Barak DOI](https://doi.org/10.1017/CBO9780511804090), [Springer: algebraic complexity DOI](https://doi.org/10.1007/978-3-662-03338-8), [Springer: descriptive complexity DOI](https://doi.org/10.1007/978-1-4612-0539-5). 제목·저자·단행본 출판 식별만 대조했다. | 표준 전거 후보는 있다. 상위 100에는 원 성과·장벽 비판·STOC/FOCS/CCC/ECCC 판본이 **B002에서 확인되지 않는다**. §3의 공개 venue 씨앗으로 보완하고, DBLP venue/year, ECCC keyword, DROPS series, arXiv `cs.CC`를 분리 검색한다. |
| `70` Mechanics of particles and systems | **MR997295**, Arnol'd, *Mathematical methods of classical mechanics* (1989), book, `58Fxx (70-02 70H05)`: 고전역학 표준 전거 후보. | [Springer DOI](https://doi.org/10.1007/978-1-4757-2063-1): 제목·저자·book·Springer New York을 대조했다. | P vs NP의 표준 전거·survey·원 성과는 B002에서 확인 못함. 계산 시뮬레이션의 시간복잡도는 별도 문제이며, P 대 NP 주장으로 전이하지 않는다. 다음에는 zbMATH `cc:70* AND (complexity OR computation)`과 계산역학 venue를 후보 발견용으로만 검색한다. |
| `74` Mechanics of deformable solids | **MR1762655**, Haupt, *Continuum mechanics and theory of materials* (2000), book, `74-02 (74Axx 74Bxx 74Cxx 74Dxx)`: 분야 입문·종합 후보. | [Springer DOI](https://doi.org/10.1007/978-3-662-04109-3): 제목·저자·book·Springer Berlin Heidelberg을 대조했다. | P vs NP 직접 역할은 B002에서 확인 못함. 유한요소/재료 계산의 난도는 해당 연속·수치 모형의 문제다. 다음에는 `74S05`, `65M/65N`과 discrete optimization 연결을 제목·초록 단위로 검사한다. |
| `76` Fluid mechanics | **MR917480**, Canuto–Hussaini–Quarteroni–Zang, *Spectral methods in fluid dynamics* (1988), book, `76-08 (65-02 76-02)`: 계산유체 방법의 기준 전거 후보. **MR1744638**, Batchelor, *An introduction to fluid dynamics* (1999), book, `76-01`: 입문 후보. | [Springer DOI: Spectral methods](https://doi.org/10.1007/978-3-642-84108-8): 제목·저자·book·출판처를 대조했다. | P vs NP 직접 전거·survey·원 성과는 B002에서 확인 못함. Navier–Stokes의 해석적 존재·매끄러움, 수치 비용, 이산 계산복잡도는 구별해야 한다. 다음에는 `76M*`과 complexity title query를 별도 실행한다. |
| `78` Optics, electromagnetic theory | **MR1113261**, Kravtsov–Orlov, *Geometrical optics of inhomogeneous media* (1990), book, `78-02 (78A05 78A25 78A45)`: 분야 종합 후보. | [Springer DOI](https://doi.org/10.1007/978-3-642-84031-9): 제목·저자·book·출판처를 대조했다. | P vs NP 직접 역할은 B002에서 확인 못함. 전자기 역문제·파동 계산을 회로/SAT 복잡도와 동일시하지 않는다. 다음에는 `78M*`의 algorithmic inverse-problem 문헌을 제목·초록으로 선별한다. |
| `80` Classical thermodynamics, heat transfer | **MR725673**, Owen, *A first course in the mathematical foundations of thermodynamics* (1984), book, `80-01 (00A69 80A05)`: 입문 전거 후보. | [Springer DOI](https://doi.org/10.1007/978-1-4613-9505-8): 제목·저자·textbook·출판처를 대조했다. | P vs NP 직접 전거·survey·원 성과는 B002에서 확인 못함. 열역학적 계산 관점은 계산모형의 물리적 비용을 다룰 수 있으나 복잡도 계급 분리의 증명은 아니다. 다음에는 `80*`와 `thermodynamic computing`을 분리 검색한다. |
| `81` Quantum theory | **MR1796805**, Nielsen–Chuang, *Quantum computation and quantum information* (2000), book, `81P68 (68-01 68-02 68Q05 81-02)`: 양자 계산의 표준 전거 후보. B002 안에 양자 정보·계산의 분류 연결은 실제로 있다. | [Springer DOI: Bratteli–Robinson, *Operator algebras and quantum statistical mechanics*](https://doi.org/10.1007/978-3-662-02520-8)는 이 MSC 표본의 독립 출판 대조로 제목·book·출판처를 확인했다. Nielsen–Chuang의 특정 내용은 이 검토에서 원문 판독하지 않았다. | 양자복잡도(BQP 등)는 P 대 NP와 다른 클래스 관계다. B002에 P=NP 또는 P≠NP를 해결하는 양자 원 성과는 확인 못함. 다음에는 arXiv `quant-ph`와 `cs.CC`를 교차하고, 고전 P/NP와 양자 상·하계를 같은 결론으로 쓰지 않는다. |
| `82` Statistical mechanics, structure of matter | **MR793553**, Ellis, *Entropy, large deviations, and statistical mechanics* (1985), book, `82A05 (60K35 82-02)`: 확률·통계역학 종합 후보. | [Springer DOI](https://doi.org/10.1007/978-1-4613-8533-2): 제목·저자·book·출판처를 대조했다. | P vs NP 직접 전거·survey·원 성과는 B002에서 확인 못함. spin system의 계산 난도와 P/NP 계급 명제는 연결 논문이 있을 때만 결합한다. 다음에는 partition-function/approximation complexity로 검색을 좁힌다. |
| `83` Relativity and gravitational theory | **MR757180**, Wald, *General relativity* (1984), book, `83-02 (83-01)`: 표준 종합 후보. | [University of Chicago Press DOI](https://doi.org/10.7208/chicago/9780226870373.001.0001): 제목·저자·monograph·출판처를 대조했다. | P vs NP 직접 전거·survey·원 성과는 B002에서 확인 못함. 시공간 계산/물리적 계산 모형은 별도 가설 영역이다. 다음에는 complexity가 명시된 title/abstract만 후보로 유지한다. |
| `85` Astronomy and astrophysics | **MR1841976**, Padmanabhan, *Theoretical astrophysics. Vol. II* (2001), book, `85-01`: 분야 종합 후보. | [Cambridge DOI](https://doi.org/10.1017/CBO9780511840159): 제목·저자·monograph·출판처를 대조했다. | 이 분야는 B002가 전건 85개를 저장했지만, P vs NP 직접 전거·survey·원 성과는 확인 못함. 전건 저장은 분야의 P vs NP 포괄성을 뜻하지 않는다. 다음에는 계산천문/추론 문제를 직접 언급하는 공개 record만 추가 탐색한다. |
| `86` Geophysics | **MR1488700**, Sato–Fehler, *Seismic wave propagation and scattering in the heterogeneous earth* (1998), book, `86A15 (74-01 74J05 86-01)`: 지구물리 파동·산란 종합 후보. | [Springer DOI](https://doi.org/10.1007/978-1-4612-2202-6): 제목·저자·book·출판처를 대조했다. | P vs NP 직접 전거·survey·원 성과는 B002에서 확인 못함. 역산·파형 계산은 응용 모형의 난도이고, 환원 또는 계급 명제가 확인되기 전에는 직접 연결이 아니다. 다음에는 seismic inversion과 computational complexity의 교집합을 검색한다. |
| `90` Operations research, mathematical programming | **MR1261419**, Grötschel–Lovász–Schrijver, *Geometric algorithms and combinatorial optimization* (1993), book, `90-02 (52C07 90C27)`: 조합최적화·알고리즘 기준 전거 후보. **MR663728**, Papadimitriou–Steiglitz, *Combinatorial optimization: algorithms and complexity* (1982), book, `90Cxx (68C25 90-02)`: 직접 인접 입문 후보. | [Springer DOI](https://doi.org/10.1007/978-3-642-78240-4): 첫 후보의 제목·저자·book·출판처를 대조했다. | NP-완전 최적화 문제의 적용 경로는 강하지만, B002 상위 표본에는 Cook/Karp류 원 성과가 확인되지 않는다. 다음에는 §3의 Karp 원판을 기준점으로 OR 문제별 환원/근사 장벽을 분리 검색한다. |
| `91` Game theory, economics, finance | **MR3525052**, Roughgarden, *Twenty lectures on algorithmic game theory* (2016), book, `91-01 (91A10 91A80)`: 알고리즘 게임이론 입문 후보. | [Cambridge DOI](https://doi.org/10.1017/CBO9781316779309): 제목·저자·monograph·출판처를 대조했다. | P vs NP 직접 전거·survey·원 성과는 B002에서 확인 못함. equilibrium 계산의 난도(PP​AD 등 포함)는 P 대 NP와 같지 않다. 다음에는 `cs.GT`와 `91A*`를 교차하되 클래스와 환원을 명시적으로 분리한다. |
| `92` Biology and other natural sciences | **MR1007836**, Murray, *Mathematical biology* (1989), book, `92-01 (...) 92A08 92A15`: 분야 입문 후보. **MR1790966**, Pevzner, *Computational molecular biology* (2000), book, `92-01 (92-02 92D20)`: 계산생물학 인접 후보. | [Springer DOI: Murray](https://doi.org/10.1007/978-3-662-08539-4): 제목·저자·book·출판처를 대조했다. | P vs NP 직접 전거·survey·원 성과는 B002에서 확인 못함. 생물정보학의 개별 NP-hard 문제는 문제별 환원 확인이 필요하다. 다음에는 공개 bioinformatics venue에서 `NP-complete`, `parameterized`, `approximation`을 분리 검색한다. |
| `93` Systems theory; control | **MR1640001**, Sontag, *Mathematical control theory* (1998), book, `93-01 (49-01 93-02)`: 표준 입문·종합 후보. **MR2521445**, Tabuada, *Verification and control of hybrid systems* (2009), book, `93-02 (68-02 68Q60 93A30 93C30)`: 형식검증 인접 후보. | [Springer DOI: Sontag](https://doi.org/10.1007/978-1-4612-0577-7): 제목·저자·book·출판처를 대조했다. | P vs NP 직접 전거·survey·원 성과는 B002에서 확인 못함. hybrid-system verification의 decidability/complexity는 P 대 NP와 다른 명제일 수 있다. 다음에는 `68Q60`, `93C30`과 complexity를 함께 검색한다. |
| `94` Information and communication theory, circuits | **MR1881185**, Goldreich, *Foundations of cryptography* (2001), book, `94A60 (68-01 68P25 94-01)`: 암호·평균경우 난도의 기준 전거 후보. **MR1704235**, Vollmer, *Introduction to circuit complexity* (1999), book, `68Q15 (68Q05 68Q10 94-02 94C05)`: 회로복잡도 기준 전거 후보. | [Cambridge DOI: Goldreich](https://doi.org/10.1017/CBO9780511546891), [Springer DOI: Vollmer](https://doi.org/10.1007/978-3-662-03927-4). 제목·저자·단행본 출판 식별을 대조했다. | 직접 인접 기준 전거는 있다. 다만 암호 가정·one-way function·평균경우 결과와 최악경우 P 대 NP 분리는 유지한다. 상위 표본에서 그 관계의 원 성과·비판은 확인 못함; CCC/ECCC/STOC 판본을 후속 대조한다. |
| `97` Mathematics education | **MR2265412**, Hitt–Harel–Selden (eds.), *Research in collegiate mathematics education. VI* (2006), book, `00A99 (97-02)`: 교육연구 수록집 후보. | [AMS DOI](https://doi.org/10.1090/cbmath/013): 제목·편집자·edited-book·AMS 출판을 대조했다. | 이 분야는 B002가 전건 59개를 저장했지만, P vs NP의 표준 전거·survey·원 성과는 확인 못함. 교육용 설명 문헌은 연구 명제의 증거가 아니다. 다음 공개 검색은 P vs NP 교육·오개념 연구로 한정하고, 결과가 있어도 수학적 핵심층과 분리 보관한다. |

표의 “확인 못함”은 **해당 B002 표본을 실제로 읽어 역할에 맞는 후보를 찾지 못했다**는 뜻이다. 인증 DB, B002 밖의 문헌, 또는 아직 실행하지 않은 다음 검색에서 그런 역할이 전혀 없다는 뜻은 아니다. 반대로 표의 후보도 제목·분류·출판 맥락만으로 채택하지 않는다. 초록과 필요한 원문을 읽고, 정확한 명제·방법·후속 사용·비판을 판정한 뒤에만 최종 핵심층으로 승격할 수 있다.

## 3. MSC 68과 독립된 이론 컴퓨터과학 공개 씨앗

`분야-검색표.md`의 ACM CCS `Theory of computation`/`Mathematics of computing` 및 arXiv `cs.CC`는 MSC `68` 표본의 대체물이 아니다. 특히 B002 68의 단행본 편향이 가리는 학회판·기술보고·공개 survey를 별도로 발견하는 씨앗이다. 다음 record는 제목, 저자, 판본/venue와 공개 접근 경로를 원 운영기관 또는 출판사에서 확인했다.

| 방향 | 실제 공개 후보와 판본 경로 | B002 중복 여부와 초기 역할 |
|---|---|---|
| NP-완전성·환원·SAT | Stephen A. Cook, *The Complexity of Theorem-Proving Procedures*, STOC 1971, [ACM DOI landing page](https://doi.org/10.1145/800157.805047). Richard M. Karp, *Reducibility among Combinatorial Problems*, *Complexity of Computer Computations* (1972), 85–103, [Springer chapter/volume record](https://link.springer.com/book/10.1007/978-1-4684-2001-2). Springer의 목차는 Karp 장의 제목과 쪽을 명시한다. | 두 제목은 B002 5,472 후보의 정확 제목 검색에서 **0건**이었다. 둘은 원 성과의 공개 서지·출판 경로 후보이지, 이 보고서가 정리 내용을 재증명한 것은 아니다. |
| 상대화 장벽 | Baker–Gill–Solovay, *Relativizations of the P =? NP Question* (1975), [SIAM DOI landing page](https://doi.org/10.1137/0204037). | B002 exact-title 0건. 장벽 문헌으로 후보화하며, 상대화가 모든 가능한 기법의 불가능성이라는 과장으로 쓰지 않는다. |
| 증명복잡도·회로하계·worst/average·암호 경계 | Pich–Santhanam, *Towards P ≠ NP from Extended Frege Lower Bounds*, [ECCC TR23-199](https://eccc.weizmann.ac.il/report/2023/199/). ECCC record는 저자·2023-12-09 공개 시각·기술보고 번호를 제공하고, 초록은 Extended Frege lower bound와 Boolean circuit lower bound의 조건부 연결을 명시한다. | B002 exact-title 0건. technical report이며 journal/conference 판본으로 자동 병합하지 않는다. “P≠NP를 증명했다”가 아니라 조건부 연결·연구 경계 후보로 기록한다. |
| 대수·기하 복잡도 및 비판 | Bläser–Ikenmeyer, *Introduction to Geometric Complexity Theory*, [Theory of Computing Graduate Survey 10](https://www.theoryofcomputing.org/articles/gs010/) (2025), DOI `10.4086/toc.gs.2025.010`. ToC는 166쪽, GCT·algebraic complexity 분류, permanent-vs-determinant 및 occurrence obstruction의 부정 결과를 명시한다. | B002 exact-title 0건. 공개 survey 후보다. B002의 MR1440179은 대수복잡도 단행본이지만 같은 판본이 아니므로 중복 병합하지 않는다. |
| 통신복잡도 | Stasys Jukna, *On the P versus NP intersected with co-NP question in communication complexity*, [ECCC TR04-062](https://eccc.weizmann.ac.il/report/2004/062/). | B002 exact-title 0건. report와 revision 상태를 ECCC record로 따로 보존한다. B002 MR1426129는 표준 단행본이지만 같은 출판 객체가 아니다. |
| 암호·평균경우·학습·meta-complexity | Goldberg–Kabanets, *Witness Encryption and NP-Hardness of Learning*, [DROPS/LIPIcs CCC 2025 record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.34), DOI `10.4230/LIPIcs.CCC.2025.34`. DROPS는 CCC 2025, LIPIcs 339, 34:1–34:43, 저자, CC-BY 및 ACM 분류 “Computational complexity and cryptography”를 명시한다. | B002 exact-title 0건. 공개 proceedings 판본이며 ECCC/arXiv/저널판과 자동 병합하지 않는다. 이 결과는 witness encryption·NP-hardness of learning의 관계를 다루므로 P 대 NP 결론으로 환원하지 않는다. |

공개 venue의 실제 검색 경로는 다음처럼 재현한다. 각 요청은 소량으로 수행하고 응답 시각·페이지네이션·exact version을 별도 기록한다.

1. DBLP Search API에서 venue와 연도를 먼저 고정한다. 예: `https://dblp.org/search/publ/api?q=venue%3ACCC%3A+year%3A2025&format=json&h=100`; STOC·FOCS·ICALP·ITCS·SAT도 같은 방식으로 분리한다. DBLP는 서지 발견·판본 후보용이며 증명 내용이나 peer review의 근거가 아니다.
2. ECCC에서 `P versus NP`, `proof complexity`, `circuit lower bounds`, `average case`, `communication complexity`, `algebraic complexity`, `randomness`를 각각 검색해 report number와 revision을 보존한다. 위 TR23-199와 TR04-062가 실제 성공 record다.
3. DROPS/LIPIcs의 [CCC series](https://drops.dagstuhl.de/entities/conference/CCC), ITCS·ICALP·SAT series에서 conference/year를 고정해 DOI record를 확인한다. CCC 2025의 위 record는 이 경로의 성공 예다.
4. Theory of Computing의 [Graduate Surveys](https://www.theoryofcomputing.org/graduate-surveys.html)와 article archive에서 `complexity`, `circuit`, `proof`, `algebraic`, `randomness`를 검색한다. GS010은 실제 성공 record다.
5. arXiv API에서 `cat:cs.CC`를 시작점으로 하고 `cs.CR`, `cs.LO`, `cs.DS`, `cs.DM`, `cs.IT`, `cs.GT`, `cs.PL`, `cs.PF`, `cs.SC`, `cs.NA`, `cs.CG`, `cs.DC`, `quant-ph`를 필요한 문제에만 교차한다. `arXiv:<id>vN`, submission history, DOI/venue를 함께 기록한다. [arXiv API 안내](https://info.arxiv.org/help/api/index.html)는 metadata 검색 API의 범위를 설명하지만 preprint의 peer-review 상태를 보증하지 않는다.

이 표는 회로하계·증명복잡도·대수복잡도·통신복잡도·암호/평균경우·학습/meta-complexity의 실제 공개 진입점을 확인했다. 랜덤성/derandomization, 질의·자료구조, PCP/근사, exact/fine-grained/parameterized complexity, SAT archive, 기술복잡도, 양자·비균일 계산은 **검색 씨앗은 설정했지만 이 보고서에서 개별 공개 record를 추가 확인하지 않았다**. 이는 미실행이며 결과 없음이 아니다.

## 4. 판정 경계와 남은 결손

확정 사실은 B002의 1,644 출현·1,573 고유 MR 후보, 위 표의 원문 서지 필드, 그리고 링크한 공개 record가 제공한 제목·저자·document type·venue/DOI다. 초기 추론은 B002의 68 표본이 단행본으로 포화되어 공개 venue 조사가 필요하고, 90·94·81이 P vs NP와 각각 최적화·암호/회로·양자라는 서로 다른 방식으로 인접한다는 것이다.

다음 항목은 아직 미확정이다.

- 어느 후보가 최종 핵심층인지, 어떤 판본들이 동일 작업인지, 정정·철회·후속 비판이 있는지.
- 각 원 성과·장벽·survey의 정리와 증명, 그리고 P vs NP·평균경우·무작위·양자·비균일·응용 문제 사이의 정확한 논리 관계.
- 위 공개 검색을 소진한 뒤에도 인증 자료원에서만 재현되는 특정 학회록·학위논문·인용 관계가 남는지.

따라서 현 처분은 **공개 후보 탐색을 계속하되 `covered`로 닫지 않음**이다. 인증 DB 검색은 이 보고서에서 실행하지 않았고, PDF·원문 대량 수집도 실행하지 않았다. 공개 검색 실패, 검색 결과 없음, 아직 실행하지 않은 검색을 서로 바꾸어 기록하지 않았다.
