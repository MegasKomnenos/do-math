# B002 기준 핵심층 초기 검토: MSC 34–65 배정 분야

기준 시각: 2026-09-04 KST  
상태: **초기 선별 완료; `covered`·최종 핵심층 승인 아님.**

## 판정 경계와 스캔 증거

이 검토는 `catalog/B002-candidates.jsonl`을 다시 파싱해 provenance의 `field_code`가 아래 23개인 출현을 모두 읽은 결과다. 각 출현에서 제목, 저자/편집자, 연도, `MRCLASS`, BibTeX 유형, 출판 맥락을 대조했다. B002에는 초록·원문이 없으므로, 아래의 “역할”은 서지·공식 소개에서 확인한 범위의 초기 판정이다. 원문을 읽었다거나 원 성과의 수학적 내용을 검증했다고 뜻하지 않는다.

| MSC | B002 출현 / MathSciNet 총 hit | B002 유형 | 절단 |
|---|---:|---|---|
| 34 | 100 / 1,570 | book 96, article 4 | 상위 100 |
| 35 | 100 / 2,081 | book 97, article 3 | 상위 100 |
| 37 | 100 / 646 | book 86, incollection 9, article 5 | 상위 100 |
| 39 | 100 / 244 | book 80, article 16, incollection 4 | 상위 100 |
| 40 | 100 / 132 | book 80, article 17, incollection 3 | 상위 100 |
| 41 | 100 / 538 | book 88, article 7, incollection 5 | 상위 100 |
| 42 | 100 / 770 | book 90, article 7, incollection 3 | 상위 100 |
| 43 | 100 / 156 | book 80, incollection 12, article 8 | 상위 100 |
| 44 | 100 / 162 | book 86, article 7, incollection 7 | 상위 100 |
| 45 | 100 / 198 | book 96, article 2, incollection 2 | 상위 100 |
| 46 | 100 / 1,493 | book 99, article 1 | 상위 100 |
| 47 | 100 / 1,248 | book 98, article 2 | 상위 100 |
| 49 | 100 / 1,386 | book 100 | 상위 100 |
| 51 | 100 / 784 | book 96, incollection 3, article 1 | 상위 100 |
| 52 | 100 / 369 | book 80, incollection 17, article 3 | 상위 100 |
| 53 | 100 / 948 | book 93, article 4, incollection 3 | 상위 100 |
| 54 | 100 / 669 | book 91, incollection 6, article 3 | 상위 100 |
| 55 | 100 / 430 | book 90, article 5, incollection 4, inproceedings 1 | 상위 100 |
| 57 | 100 / 512 | book 85, incollection 8, article 7 | 상위 100 |
| 58 | 100 / 913 | book 96, article 2, incollection 2 | 상위 100 |
| 60 | 100 / 2,323 | book 100 | 상위 100 |
| 62 | 100 / 3,651 | book 92, article 8 | 상위 100 |
| 65 | 100 / 2,808 | book 95, incollection 5 | 상위 100 |
| **합계** | **2,300 / 24,031** | 출현 기준 | 전 분야 절단 |

`총 hit`은 분야별 수집 metadata의 검색 결과 수이며, 분야 사이의 같은 MR 레코드는 합계에서 중복 계산했다. 따라서 2,300은 고유 문헌 수가 아니라 실제로 스캔한 **분야-출현 수**다. B002 전체의 정규화·분야 통계는 [B002 정규화 감사](B002-normalization-audit.md)와 [정규화 계약](../catalog/B002-normalization-contract.md)을 정본으로 한다.

공개 대조는 각 분야에서 아래 채택 후보 하나에 하였다. DOI가 있는 경우 DOI가 가리킨 출판사 landing page에서 제목·저자·판본/설명 범위를 확인했다. DOI resolver가 자동 요청을 거부한 AMS·Wiley·SIAM 항목도 각 공식 landing URL로 도달함을 대조했으며, 이는 원문 접근이나 내용 판독이 아니다. 46은 DOI가 없는 B002 레코드라 Elsevier 공식 상품 페이지로 대조했다. 51은 Springer 공식 landing page로 대조했다.

다음 검색은 **아직 실행하지 않은 공개 누락 검색**이다. `zbMATH Open`의 Classification/one-line search와 [공식 검색 안내](https://zbmath.org/frequently-asked-questions/), [arXiv 고급 검색](https://arxiv.org/search/advanced), [ECCC](https://eccc.weizmann.ac.il/)를 쓴다. 각 식에서 MSC와 주제어를 함께 넣고, 결과가 있더라도 제목·초록·원 논문/공식 venue를 따로 확인해야 한다.

## 분야별 초기 후보와 결손

### 34 — Ordinary differential equations

- **초기 후보:** `MR2961944`, Gerald Teschl, *Ordinary Differential Equations and Dynamical Systems* (2012, book, `34-01 (37-01 39-01)`, AMS *Graduate Studies in Mathematics* 140). ODE의 기초·동역학을 잇는 입문 전거 후보다. AMS는 이 책을 초급 대학원생용 self-contained introduction으로 소개하고 초기값 문제, 동역학계, chaos를 범위로 명시한다([공식 페이지](https://bookstore.ams.org/gsm-140/)).
- **결손:** B002에서 P vs NP와 직접 연결되는 ODE 계산복잡도, 경계/하계 또는 원 성과는 확인 못함. 원문 미판독이다.
- **다음 공개 검색:** zbMATH Open `MSC 34` + `computational complexity OR algorithmic complexity`; arXiv `cat:math.DS AND (complexity OR computability)`.

### 35 — Partial differential equations

- **초기 후보:** `MR2597943`, Lawrence C. Evans, *Partial Differential Equations* (2010, book, `35-01`, AMS GSM 19). PDE의 표준 입문/종합 후보이며 [AMS 공식 페이지](https://bookstore.ams.org/gsm-19/)와 DOI [10.1090/gsm/019](https://doi.org/10.1090/gsm/019)로 판본·출판처를 대조했다.
- **결손:** B002에서 복잡도 이론에 쓰일 특정 PDE 해법의 계산 난도, 부정 결과 또는 비판은 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 35` + `computational complexity`; arXiv `math.AP`/`math.NA`에서 `complexity lower bound`.

### 37 — Dynamical systems and ergodic theory

- **초기 후보:** `MR2961944` (위 34와 동일; 37 출현 rank 16, `37-01`)를 동역학 입문 후보로 중복 보존한다. AMS 공식 설명은 동역학계·안정성·chaos의 장을 명시한다([공식 페이지](https://bookstore.ams.org/gsm-140/)). 보조적으로 `MR1723992`, Ludwig Arnold, *Random Dynamical Systems* (1998, book, `37Hxx (37-02 60H10)`, Springer Monographs)도 B002에 있다; [Springer/DOI](https://doi.org/10.1007/978-3-662-12878-7)에서 서지 범위를 대조했다.
- **결손:** 표본에서 계산가능성, symbolic dynamics의 복잡도, ergodic-theory 원 성과·반례를 핵심층으로 채택할 근거는 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 37` + `computability OR computational complexity`; arXiv `math.DS` + `symbolic dynamics complexity`.

### 39 — Difference and functional equations

- **초기 후보:** `MR2467621`, Marek Kuczma, *An Introduction to the Theory of Functional Equations and Inequalities* (2009, book, `39-02 (39Bxx)`, Birkhäuser). 함수방정식의 표준 종합 후보다. [Springer 공식 페이지](https://link.springer.com/book/10.1007/978-3-7643-8749-5)에서 제목·저자·판본을 대조했다.
- **결손:** 계산복잡도와 관련한 함수방정식/차분방정식의 원 성과·경계는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 39` + `computational complexity`; arXiv `math.DS` + `difference equations algorithm`.

### 40 — Sequences, series, summability

- **초기 후보:** `MR2073637`, Jacob Korevaar, *Tauberian Theory* (2004, book, `11M45 (… 40-02 40-03 40E05 42-02)`, Springer *Grundlehren* 329). 수열·합산법의 고급 종합 후보다. [Springer/DOI](https://doi.org/10.1007/978-3-662-10225-1)에서 출판 기록을 대조했다.
- **결손:** B002에서 복잡도 경계에 기여하는 수렴/합산 원 성과나 반례는 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 40` + `computability OR complexity`; arXiv `math.CA` + `effective summability`.

### 41 — Approximations and expansions

- **초기 후보:** `MR1261635`, Ronald A. DeVore·George G. Lorentz, *Constructive Approximation* (1993, book, `41-02 (41A10 41A15 41A35 41A36 42A10)`, Springer) — 근사론의 기초 종합 후보. 또한 `MR2354721`, Felipe Cucker·Ding-Xuan Zhou, *Learning Theory: An Approximation Theory Viewpoint* (2007, book, `41-02 (… 68Q32 68T05 …)`, Cambridge Monographs 24)는 계산·학습 접점의 보조 후보다. Cambridge는 후자 페이지에서 제목·저자·시리즈를 확인한다([공식 페이지](https://www.cambridge.org/core/books/learning-theory/B39A58737BCA537565FDBC07014AE2B4)).
- **결손:** P vs NP의 회로/학습 장벽, 근사 난이도 원 성과의 역할은 이 B002 표본만으로 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 41` + `computational learning OR approximation hardness`; ECCC `approximation complexity`.

### 42 — Harmonic analysis on Euclidean spaces

- **초기 후보:** `MR3243734`, Loukas Grafakos, *Classical Fourier Analysis* (2014, book, `42-01 (42Bxx)`, Springer GTM 249). 유클리드 Fourier 해석의 입문/종합 후보다. [Springer/DOI](https://doi.org/10.1007/978-1-4939-1194-3)에서 판본을 대조했다.
- **결손:** Fourier 분석이 회로·통신·학습 복잡도에 주는 특정 하계/장벽은 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 42` + `Boolean function OR computational complexity`; arXiv `cs.CC` + `Fourier analysis`.

### 43 — Abstract harmonic analysis

- **초기 후보:** `MR1038803`, Walter Rudin, *Fourier Analysis on Groups* (1990, book, `43-02 (01A75)`, Wiley Classics Library). 군 위 Fourier 해석의 표준 전거 후보다. [Wiley/DOI](https://doi.org/10.1002/9781118165621)에서 제목·저자·출판 객체를 대조했다.
- **결손:** 군/표현론적 방법의 P vs NP 원 성과·비판·경계는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 43` + `complexity`; arXiv `cs.CC` + `noncommutative Fourier complexity`.

### 44 — Integral transforms, operational calculus

- **초기 후보:** `MR1716143`, Joel L. Schiff, *The Laplace Transform* (1999, book, `44A10 (44-01)`, Springer UTM). 변환론의 입문 전거 후보다. [Springer/DOI](https://doi.org/10.1007/978-0-387-22757-3)에서 서지·출판 맥락을 대조했다.
- **결손:** 변환 알고리즘의 복잡도 또는 P vs NP 경계는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 44` + `algorithmic complexity`; arXiv `cs.CC OR cs.NA` + `integral transform complexity`.

### 45 — Integral equations

- **초기 후보:** `MR3184286`, Rainer Kress, *Linear Integral Equations*, 3판 (2014, book, `45A05 (45-02 45L05 47G10 65R20)`, Springer AMS 82). 선형 적분방정식의 표준 종합 후보다. [Springer/DOI](https://doi.org/10.1007/978-1-4614-9593-2)에서 3판과 분류를 대조했다.
- **결손:** 적분방정식 계산 난도·불가능성 또는 원 성과는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 45` + `information based complexity OR computational complexity`; arXiv `math.NA` + `integral equation complexity`.

### 46 — Functional analysis

- **초기 후보:** `MR2424078`, Robert A. Adams·John J. F. Fournier, *Sobolev Spaces*, 2판 (2003, book, `46E35 (46-01 46-02 46B70 46Exx)`, Elsevier/Academic Press, *Pure and Applied Mathematics* 140). 함수해석·PDE 재진입을 위한 기초 후보다. [Elsevier 공식 페이지](https://shop.elsevier.com/books/sobolev-spaces/adams/978-0-12-044143-3)는 저자, 2판, 출판일과 다루는 Sobolev 공간 범위를 확인한다.
- **결손:** B002에서 계산복잡도에 특유한 Banach-space 방법, 원 하계, 비판은 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 46` + `computational complexity OR proof complexity`; arXiv `math.FA` + `complexity`.

### 47 — Operator theory

- **초기 후보:** `MR787404`, Klaus Deimling, *Nonlinear Functional Analysis* (1985, book, `47-01 (47Hxx 55M25 58-01 58Cxx)`, Springer-Verlag Berlin). 비선형 연산자·고정점 계열의 입문/종합 후보이며 47 출현을 유지한다. [Springer/DOI](https://doi.org/10.1007/978-3-662-00547-7)에서 출판 객체를 대조했다.
- **결손:** 연산자 이론의 계산복잡도, 양자 계산과의 구체적 경계, 원 성과는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 47` + `computational complexity`; arXiv `quant-ph OR cs.CC` + `operator lower bound`.

### 49 — Calculus of variations and optimal control; optimization

- **초기 후보:** `MR1491362`, R. Tyrrell Rockafellar·Roger J.-B. Wets, *Variational Analysis* (1998, book, `49-02 (46N10 47N10 49J52 49K40 90C30)`, Springer *Grundlehren* 317). 변분해석·최적화의 기준 종합 후보다. [Springer/DOI](https://doi.org/10.1007/978-3-642-02431-3)에서 출판 기록을 대조했다.
- **결손:** NP-hardness, 근사 경계, 최적화 원 성과/후속 비판은 이 100권의 거의 전부 book 표본에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 49` + `NP-hard OR computational complexity`; arXiv `cs.CC OR cs.DS` + `optimization hardness`.

### 51 — Geometry

- **초기 후보:** `MR1761093`, Robin Hartshorne, *Geometry: Euclid and Beyond* (2000, book, `51-01 (01A20 01A55 51-02)`, Springer UTM). 기하 기초·공리·좌표화 재진입 후보다. Springer의 [공식 페이지](https://link.springer.com/book/10.1007/978-0-387-22676-7)는 저자, UTM, 2000 저작권 및 장 구성을 확인한다.
- **결손:** 계산기하/복잡도와 접하는 원 성과·경계는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 51` + `computational geometry complexity`; arXiv `cs.CG` + `lower bound`.

### 52 — Convex and discrete geometry

- **초기 후보:** `MR936633`, Martin Grötschel·László Lovász·Alexander Schrijver, *Geometric Algorithms and Combinatorial Optimization* (1988, book, `90C27 (05-02 52-02 68Q25)`, Springer, *Algorithms and Combinatorics* 2). B002 안에서 52와 68Q25를 함께 가진 명시적 알고리즘/조합최적화 교량 후보다. [Springer/DOI](https://doi.org/10.1007/978-3-642-97881-4)에서 제목·저자·출판 객체를 대조했다.
- **결손:** 이 책의 어느 정리·환원·복잡도 경계가 P vs NP 핵심층에 실제로 필요한지는 원문과 인용망을 읽기 전에는 판정 못함. 원 성과·후속 비판도 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 52` + `NP-complete OR extension complexity`; ECCC `extended formulations` 및 arXiv `cs.CG`.

### 53 — Differential geometry

- **초기 후보:** `MR3469435`, Peter Petersen, *Riemannian Geometry*, 3판 (2016, book, `53-01 (53C20 53C21 53C23)`, Springer GTM 171). 미분기하의 표준 입문/종합 후보다. [Springer/DOI](https://doi.org/10.1007/978-3-319-26654-1)에서 3판·시리즈·저자를 대조했다.
- **결손:** 기하적 복잡도 이론 또는 P vs NP 장벽에 직접 기여하는 53 원 성과·비판은 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 53` + `geometric complexity theory`; arXiv `cs.CC` + `geometric complexity theory`.

### 54 — General topology

- **초기 후보:** `MR1224675`, Glen E. Bredon, *Topology and Geometry* (1993, book, `55-01 (54-01 57-01)`, Springer GTM 139). 54·55·57에 실제로 반복 출현한 위상/기하 재진입 후보다. [Springer/DOI](https://doi.org/10.1007/978-1-4757-6848-0)에서 제목·저자·시리즈를 대조했다.
- **결손:** 일반위상에서 계산복잡도 또는 형식화와 연결되는 원 성과·경계는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 54` + `computability OR computational complexity`; arXiv `math.GN` + `effective topology`.

### 55 — Algebraic topology

- **초기 후보:** `MR1867354`, Allen Hatcher, *Algebraic Topology* (2002, book, `55-01 (55-00)`, Cambridge University Press). 대수위상의 입문 기준 전거 후보다. 저자가 유지하는 [공개 원문 페이지](https://pi.math.cornell.edu/~hatcher/AT/ATpage.html)는 저작·판본·장별 자료를 제공한다. 계산적 보조 후보 `MR2572029`, Herbert Edelsbrunner·John L. Harer, *Computational Topology* (2010, book, `00-02 (05C10 52-02 55-02 57-02 65D18 68U05)`, AMS)는 52·55·57에 중복 출현하고 [AMS/DOI](https://doi.org/10.1090/mbk/069)로 대조했다.
- **결손:** P vs NP에 필요한 대수위상 알고리즘의 난도·하계와 원 성과/비판은 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 55` + `computational complexity`; arXiv `cs.CG` + `computational topology complexity`.

### 57 — Manifolds and cell complexes

- **초기 후보:** `MR1930091`, John M. Lee, *Introduction to Smooth Manifolds* (2003, book, `58-01 (53-01 57-01)`, Springer GTM 218). 53·57·58에 실제 반복 출현한 매니폴드 기초 후보다. [Springer/DOI](https://doi.org/10.1007/978-0-387-21752-9)에서 서지와 출판 맥락을 대조했다.
- **결손:** cell complex/매니폴드 문제의 계산 난도·원 성과·반례는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 57` + `algorithmic complexity`; arXiv `cs.CG` + `manifold complexity`.

### 58 — Global analysis, analysis on manifolds

- **초기 후보:** `MR960687`, Ralph Abraham·Jerrold E. Marsden·Tudor Ratiu, *Manifolds, Tensor Analysis, and Applications* (1988, book, `58-01`, Springer *Applied Mathematical Sciences* 75). 전역해석의 입문/도구 전거 후보다. [Springer/DOI](https://doi.org/10.1007/978-1-4612-1029-0)에서 제목·저자·시리즈를 대조했다. 위 `MR1930091`도 58에 중복 출현한다.
- **결손:** 전역해석의 계산복잡도 또는 P vs NP 관련 원 성과/장벽은 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 58` + `computational complexity`; arXiv `math.DG` + `complexity`.

### 60 — Probability theory and stochastic processes

- **초기 후보:** `MR1876169`, Olav Kallenberg, *Foundations of Modern Probability* (2002, book, `60-01`, Springer). 확률의 표준 종합 후보이며 [Springer/DOI](https://doi.org/10.1007/978-1-4757-4015-8)로 대조했다. P vs NP 인접 보조 후보 `MR1885388`, Noga Alon·Joel H. Spencer, *The Probabilistic Method* (2000, book, `60-02 (05C80 60C05 60F99 60G42)`, Wiley, DOI [10.1002/0471722154](https://doi.org/10.1002/0471722154))도 실제 B002 출현이다.
- **결손:** 확률적 복잡도, derandomization, 평균 경우 난이도의 원 성과·장벽·비판은 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 60` + `derandomization OR average-case complexity`; ECCC 및 arXiv `cs.CC`.

### 62 — Statistics

- **초기 후보:** `MR1652247`, A. W. van der Vaart, *Asymptotic Statistics* (1998, book, `62-02 (62E20 62F05 62F12 62G07 62G09 62G20)`, Cambridge Series in Statistical and Probabilistic Mathematics 3). 통계 추론의 고급 종합 후보다. [Cambridge 공식 페이지](https://www.cambridge.org/core/books/asymptotic-statistics/A3C7DAD3F7E66A1FA60E9C8FE132EE1D)에서 제목·저자·출판 객체를 대조했다.
- **결손:** 통계 계산복잡도, 학습 난도 또는 P vs NP에 대한 원 성과·하계·비판은 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 62` + `computational complexity`; arXiv `stat.TH OR cs.LG` + `statistical computational lower bounds`.

### 65 — Numerical analysis

- **초기 후보:** `MR1990645`, Yousef Saad, *Iterative Methods for Sparse Linear Systems* (2003, book, `65-01 (65F10 65F50)`, SIAM). 수치선형대수의 재진입 후보다. [SIAM/DOI](https://doi.org/10.1137/1.9780898718003)에서 제목·저자·출판 객체를 대조했다.
- **결손:** numerical complexity/information-based complexity의 원 성과, 수치 방법의 하계·경계는 B002에서 확인 못함.
- **다음 공개 검색:** zbMATH Open `MSC 65` + `information based complexity OR computational complexity`; arXiv `math.NA` + `complexity lower bound`.

## 공통 결론과 다음 우선순위

**관찰:** 이 분야군의 B002는 각 분야의 `-00/-01/-02` 검색 상위 100이며 2,300 출현 중 압도적으로 단행본이다. 49·60은 각각 100/100이 book이다. 그러므로 이 표본은 표준 전거를 찾는 데에는 유용하지만, 논문·학회록·프리프린트에 흔한 P vs NP의 원 성과, 반례, 장벽, 정정, 후속 비판을 부재라고 결론낼 수 없다.

**중복:** `MR2961944`는 34·37·39, `MR2073637`는 40·42, `MR1224675`는 54·55·57, `MR2572029`는 52·55·57, `MR1930091`는 53·57·58에 실제 출현한다. 이 중복은 병합이나 채택 확정이 아니라, 후속 판독을 한 작업에서 여러 분야에 재사용할 수 있는 신호다.

**추론:** P vs NP와 가장 직접적인 공개 누락 검사를 먼저 열 분야는 52(기하 알고리즘·조합최적화), 60(확률 방법·무작위성), 41(학습/근사), 53(geometric complexity theory), 55/57(계산위상) 및 65(계산/정보 기반 수치복잡도)다. 34–51과 54·58·62도 먼 분야라는 이유로 제외하지 않으며, 위 검색식을 같은 공개 절차로 실행한다.

**미확정:** 이 보고서는 공개 누락 검색의 결과가 아니다. 각 “다음 공개 검색”은 미실행 상태이고, 결과 없음·검색 실패·부분 export를 아직 주장하지 않는다. B002에서 확인 못한 역할은 B002 표본에서 **긍정적으로 확인하지 못했다**는 뜻이지 해당 분야에 자료가 없다는 뜻이 아니다. 후속 후보를 채택하려면 공식 서지/venue와 초록 또는 원문을 대조하고, 원 성과·비판·경계의 경우 원문 판독과 인용망 검토를 별도로 기록해야 한다.
