# B002 초기 핵심층 검토 — MSC 00–33

기준 시각: 2026-09-04 KST
판정 범위: MSC `00, 01, 03, 05, 06, 08, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 26, 28, 30, 31, 32, 33`의 B002 출현만.

## 결론

**초기 선별은 완료했지만, 어느 후보도 이 보고서만으로 `covered` 또는 최종 핵심층 승인 상태가 되지 않는다.** B002의 지정 분야 출현 2,289건을 모두 기계적으로 다시 읽었다. 각 출현에서 MR ID, 제목, 저자·편집자, 연도, `MRCLASS`, entry type, 출판사·저널·series·DOI 필드를 확인했다. 출현 수는 아래 분야별 수와 일치한다. 같은 MR이 다른 분야에 나온 경우에는 한 후보로 합치지 않고 해당 분야에 다시 보였다.

선별은 제목·분류·출판 맥락이 보여 주는 역할의 **초기 후보화**다. 특히 표준서의 존재는 그 책이 P 대 NP의 정리·장벽·비판을 다룬다는 증명이 아니다. 원문 또는 신뢰할 만한 초록을 읽지 않은 경우에는 그 사실을 명시했다. 인용순, 검색 snippet, 인용 수는 판정 근거로 사용하지 않았다.

### 공개 대조의 범위와 표기

각 분야의 `공개 대조`는 아래 링크의 DOI resolver 또는 출판사 landing page를 2026-09-04에 개별 요청해 식별자·제목의 독립 서지 경로가 존재하는지를 확인한 것이다. `302`는 DOI resolver가 landing page로 넘겼다는 확인일 뿐, 원문을 판독했다는 뜻이 아니다. `200`은 출판사 landing page의 HTTP 응답만 확인했다. DOI 연결이 없는 후보나 직접 역할이 없는 분야는 그 한계를 그대로 기록하고, 다음 zbMATH Open 검색식을 제시한다. zbMATH 검색 필드와 공개 API의 사용 경계는 [zbMATH General Help](https://zbmath.org/general-help/)와 [API 안내](https://api.zbmath.org/)를 기준으로 한다.

`B002에서 확인 못함`은 “그 분야에 관련 문헌이 없다”가 아니라 **이 `-00/-01/-02`, 인용순 상위 100 표본에서 이 역할의 후보를 확인하지 못했다**는 상태다. `검색 실패`는 0건과 다르다.

아래 `초기 후보`는 역할을 함께 쓴 하나의 실제 B002 레코드다. 한 분야에서 표준 전거·종합·원 성과 중 하나만 적었다면, 나머지 역할은 이 초기 표본에서 **확인 못함**이며 빈칸을 유사한 책으로 채우지 않았다.

## 분야별 전건 스캔과 초기 처분

### 00 — General and overarching topics; collections (100 출현)

- **초기 후보:** `MR2247919`, Hoory–Linial–Wigderson, *Expander graphs and their applications* (2006, article, `68Q15 (00-02 05C25 05C80 60G50 68Q17 68R10)`). 확장 그래프의 survey 성격으로 무작위성·하계의 방법 배경 후보로 남긴다. P 대 NP의 직접 해법·장벽 문헌으로는 판정하지 않았다. [DOI resolver](https://doi.org/10.1090/s0273-0979-06-01126-8) 응답은 302였다.
- **없는 역할:** B002 표본에서 P 대 NP 자체의 표준 전거·원 성과를 확인하지 못했다.
- **다음 공개 검색:** `ti:"P versus NP" AND cc:68Q15`; `ti:expander AND ab:(complexity OR derandomization)`.

### 01 — History and biography (100 출현)

- **초기 후보:** `MR2895611`, Mancosu–Zach–Badesa, “The development of mathematical logic from Russell to Tarski, 1900–1935” (2009, book chapter, `03-03 (01-02 01A60)`). 계산가능성 이전의 논리 형성사를 확인할 역사적 맥락 후보다. P/NP의 역사 또는 Cook–Levin의 수용사를 다룬다는 판정은 아직 없다. [Oxford DOI landing](https://doi.org/10.1093/acprof:oso/9780195137316.003.0029) 응답은 302였다.
- **없는 역할:** P 대 NP, NP-완전성, 계산복잡도의 역사 survey는 B002에서 확인 못함.
- **다음 공개 검색:** `ti:("P versus NP" OR "NP-complete" OR "computational complexity") AND cc:01Axx`.

### 03 — Mathematical logic and foundations (100 출현)

- **초기 후보:** `MR1366417`, Krajíček, *Bounded arithmetic, propositional logic, and complexity theory* (1995, book, `03-02 (03D15 03Fxx 68Q15)`). 제목과 복수 분류가 bounded arithmetic·proof complexity·complexity theory의 접점을 직접 가리킨다. 이 분야의 **핵심 비판·경계 후보**로 보존한다. 원문 미판독이므로 특정 lower bound나 P≠NP 함의는 주장하지 않는다.
- **보조 후보:** `MR2102513`, Libkin, *Elements of finite model theory* (2004, book, `03-01 (03C13 68-01 68Q19)`)은 descriptive/finite-model-complexity의 표준 입문 후보다. [Springer landing](https://link.springer.com/book/10.1007/978-3-662-07003-1) 응답은 200이었다.
- **다음 공개 검색:** `ti:("bounded arithmetic" OR "proof complexity") AND cc:03D15`; `ti:"P versus NP" AND cc:03D15`.

### 05 — Combinatorics (100 출현)

- **초기 후보:** `MR2483235`, Flajolet–Sedgewick, *Analytic combinatorics* (2009, book, `05-02 (05A15 05A16 60C05 60E10 82-01)`). 조합적 계수·생성함수 분석의 표준 전거 후보이며, average-case/counting 경계의 방법 토대로만 남긴다. P 대 NP의 직접 survey나 counting-hardness 결과라는 판정은 아니다. [Cambridge DOI landing](https://doi.org/10.1017/CBO9780511801655) 응답은 302였다.
- **없는 역할:** NP-완전성, #P, PCP·근사 난이도의 B002 핵심 원 성과는 확인 못함.
- **다음 공개 검색:** `ti:("counting complexity" OR "approximation hardness" OR "PCP") AND cc:05`; `ab:(SAT OR CSP) AND cc:05`.

### 06 — Order, lattices, ordered algebraic structures (100 출현)

- **초기 후보:** `MR2895965`, Jukna, *Boolean function complexity* (2012, book, `68Q17 (06-02 06E30 68-02 68Q15 94C10)`). Boolean function complexity와 circuit lower bounds의 직접 접점 때문에 **회로 하계·장벽 검토 후보**다. 실제 장벽 서술과 후속 비판은 미판독이다. [Springer DOI landing](https://doi.org/10.1007/978-3-642-24508-4) 응답은 302였다.
- **다음 공개 검색:** `ti:("Boolean function complexity" OR "circuit lower bounds") AND cc:(06E30 OR 68Q17)`.

### 08 — General algebraic systems (100 출현)

- **초기 후보:** `MR4273453`, Bodirsky, *Complexity of infinite-domain constraint satisfaction* (2021, book, `08-02 (03Cxx 08A70 68Qxx)`). CSP complexity의 표준·종합 후보로 남긴다. CSP dichotomy가 P 대 NP 자체를 해결한다는 식의 연결은 하지 않는다. [Cambridge DOI landing](https://doi.org/10.1017/9781107337534) 응답은 302였다.
- **보조 후보:** `MR1887177`, Denecke–Wismath, *Universal algebra and applications in theoretical computer science* (2002, book, `08-01 (08A70 68Q42 68Q45 68Q70)`)는 보편대수–이론CS 연결의 입문 후보다.
- **다음 공개 검색:** `ti:("constraint satisfaction" OR CSP) AND cc:(08A70 OR 68Qxx)`.

### 11 — Number theory (100 출현)

- **초기 후보:** `MR2289012`, Tao–Vu, *Additive combinatorics* (2006, book, `11-02 (05-02 05D10 11B13 11P70 11P82 28D05 37A45)`). 조합론·수론의 표준 종합 후보이나, P 대 NP에 직접 기여한다고는 확인하지 않았다. [Cambridge DOI landing](https://doi.org/10.1017/cbo9780511755149) 응답은 302였다.
- **없는 역할:** 수론 알고리즘·암호학의 P 대 NP 경계 또는 원 성과는 B002에서 확인 못함.
- **다음 공개 검색:** `ti:("computational number theory" OR cryptography) AND ab:(complexity OR "NP-hard")`.

### 12 — Field theory and polynomials (100 출현)

- **초기 후보:** `MR659083`, Grigor'ev, “Lower bounds in the algebraic complexity of computations” (1982, article, `68C25 (12-02 68C20)`). 제목·분류가 algebraic complexity lower bounds를 직접 가리켜 **핵심 원 성과 후보**로 남긴다. 정리 내용·모형·후속 반박은 원문 미판독이다.
- **공개 대조:** 이 기사에는 B002 DOI가 없다. B002의 같은 분야 표준 다항식 전거 `MR2082772`, *Polynomials*는 [Springer landing](https://link.springer.com/book/10.1007/978-3-642-03980-5)에서 200을 확인했지만, 이는 Grigor'ev 논문의 내용 대조가 아니다.
- **다음 공개 검색:** `ti:("algebraic complexity" OR "arithmetic circuit") AND cc:(12 OR 68C20)`; `au:Grigoriev AND ti:"Lower bounds"`.

### 13 — Commutative algebra (100 출현)

- **초기 후보:** `MR3330490`, Cox–Little–O'Shea, *Ideals, varieties, and algorithms*, 4판 (2015, book, `13P10 (13-01 14-01 14Qxx 68W30)`). Gröbner-basis와 계산대수기하의 표준 입문 전거 후보다. GCT나 P 대 NP에 대한 직접 주장으로 읽지 않는다. [Springer DOI landing](https://doi.org/10.1007/978-3-319-16721-3) 응답은 302였다.
- **다음 공개 검색:** `ti:("computational commutative algebra" OR "Groebner basis") AND ab:(complexity OR circuit)`.

### 14 — Algebraic geometry (100 출현)

- **초기 후보:** `MR3330490` (위 Cox–Little–O'Shea; 이 분야에도 provenance가 있음). 계산대수기하의 공통 입문 후보로 분야 간 중복을 유지한다. B002에는 GCT의 원 논문·종합을 확인하지 못했다.
- **공개 대조:** `MR1182558`, Harris, *Algebraic geometry*의 [Springer landing](https://link.springer.com/book/10.1007/978-1-4757-2189-8) 응답은 200이었다. 이는 분야 표준서의 서지 대조이며 GCT 내용 대조가 아니다.
- **다음 공개 검색:** `ti:"geometric complexity theory"`; `ab:(permanent AND determinant) AND cc:14`.

### 15 — Linear and multilinear algebra; matrix theory (100 출현)

- **초기 후보:** `MR2865915`, Landsberg, *Tensors: geometry and applications* (2012, book, `15-01 (14N05 15A69 20G05)`). tensor rank·대수기하의 방법 전거 후보다. GCT와의 정확한 역할과 lower-bound 결과는 원문 미판독이다. [AMS DOI landing](https://doi.org/10.1090/gsm/128) 응답은 302였다.
- **다음 공개 검색:** `ti:(tensor OR "tensor rank") AND ab:(complexity OR permanent OR determinant)`.

### 16 — Associative rings and algebras (100 출현)

- **초기 후보:** `MR2124127`, Kanel-Belov–Rowen, *Computational aspects of polynomial identities* (2005, book, `16-02 (15A75 16N20 16P90 16R10 16R30 16W55)`). noncommutative/algebraic computation의 인접 방법 후보로 남긴다. P 대 NP·arithmetic lower bound의 직접 기여는 확인하지 않았다.
- **공개 대조:** 직접 후보의 DOI는 B002에 없다. 같은 B002 분야의 표준 전거 `MR1269324`, Weibel, *An introduction to homological algebra*는 [Cambridge DOI landing](https://doi.org/10.1017/cbo9781139644136) 응답이 302였다. 이는 분야 표본의 독립 서지 대조일 뿐 후보 내용 대조가 아니다.
- **다음 공개 검색:** `ti:("polynomial identity" OR "noncommutative computation") AND ab:complexity`.

### 17 — Nonassociative rings and algebras (100 출현)

- **초기 후보:** `MR1743970`, de Graaf, *Lie algebras: theory and algorithms* (2000, book, `17Bxx (17-01 17-02 17-08 68W30)`). 계산 Lie 대수의 표준/방법 후보다. P 대 NP의 직접 경계는 B002 서지만으로 확인하지 못했다. [Elsevier DOI landing](https://doi.org/10.1016/S0924-6509(00)80040-9) 응답은 302였다.
- **다음 공개 검색:** `ti:("Lie algebra" AND algorithm) AND ab:complexity`.

### 18 — Category theory; homological algebra (100 출현)

- **초기 후보:** `MR1094561`, Barr–Wells, *Category theory for computing science* (1990, book, `18-01 (68Q45 68Q55 68R10)`). 계산 의미론·category theory의 표준 입문 후보다. complexity-class separation의 기여는 확인하지 않았다.
- **공개 대조:** 이 후보의 B002 DOI는 없다. `MR2455920`, Rotman, *An introduction to homological algebra*는 [Springer DOI landing](https://doi.org/10.1007/b98977) 응답이 302이었다. 이는 분야 표본의 독립 서지 대조다.
- **다음 공개 검색:** `ti:(category OR categorical) AND ab:("computational complexity" OR circuit)`.

### 19 — K-theory (89 출현; 이 분야만 B002가 전체 hit를 저장)

- **B002에서 확인 못함:** P 대 NP, GCT, 회로·산술 lower bound에 실제로 기여하는 표준 전거·survey·원 성과를 B002의 89건에서 확인하지 못했다. K-theory를 먼 분야라는 이유로 제외하지는 않는다.
- **공개 대조:** B002의 표준 분야 전거 `MR3076731`, Weibel, *The K-book*은 [AMS DOI landing](https://doi.org/10.1090/gsm/145) 응답이 302이었다. 이 사실은 P 대 NP 관련성의 부정 증명이 아니다.
- **다음 공개 검색:** `ti:(K-theory OR "algebraic K-theory") AND ("geometric complexity theory" OR "arithmetic circuit" OR permanent)`.

### 20 — Group theory and generalizations (100 출현)

- **초기 후보:** `MR2129747`, Holt–Eick–O'Brien, *Handbook of computational group theory* (2005, book, `20-01 (20-04 68Q42 68Q70 68W30)`). 알고리즘 군론의 표준 전거 후보다. 이 책을 P=NP 또는 군론적 난이도 결과의 근거로 쓰지 않는다. [CRC DOI landing](https://doi.org/10.1201/9781420035216) 응답은 302였다.
- **다음 공개 검색:** `ti:("computational group theory" OR "group isomorphism") AND ab:(complexity OR "NP-hard")`.

### 22 — Topological groups, Lie groups (100 출현)

- **B002에서 확인 못함:** 직접 P 대 NP/회로·산술 복잡도 후보는 확인 못함. Lie representation theory가 GCT에 연결될 가능성은 열어 둔다.
- **공개 대조:** B002의 `MR1090825`, Raghunathan, *Discrete subgroups of semisimple Lie groups*의 [Springer DOI landing](https://doi.org/10.1007/978-3-642-51445-6)를 공개 서지 경로로 기록했다. 이 항목의 P 대 NP 관련성은 미확정이다.
- **다음 공개 검색:** `ti:("Lie group" OR representation) AND ("geometric complexity theory" OR permanent OR determinant)`.

### 26 — Real functions (100 출현)

- **B002에서 확인 못함:** real-computation complexity 또는 P 대 NP 경계의 표준 전거·원 성과는 확인 못함.
- **공개 대조:** B002의 `MR1916029`, Krantz–Parks, *A primer of real analytic functions*은 [Springer landing](https://link.springer.com/book/10.1007/978-0-8176-8134-0)에서 200을 확인했다. 이는 분야 표준서의 대조일 뿐 관련성 부정 증명은 아니다.
- **다음 공개 검색:** `ti:("real computation" OR "complexity theory of real functions")`; `ab:(BSS OR "Blum Shub Smale") AND cc:26`.

### 28 — Measure and integration (100 출현)

- **B002에서 확인 못함:** 무작위성·평균 경우·측도 복잡도와 P 대 NP의 직접 연결을 설명하는 B002 기준 전거는 확인 못함.
- **공개 대조:** B002의 `MR2118797`, Falconer, *Fractal geometry*는 [Wiley DOI landing](https://doi.org/10.1002/0470013850) 응답이 302이었다.
- **다음 공개 검색:** `ab:("computational complexity" AND measure)`, `ti:(randomness OR "algorithmic randomness") AND cc:28`.

### 30 — Functions of a complex variable (100 출현)

- **B002에서 확인 못함:** 복소해석을 P 대 NP 장벽·원 성과에 연결하는 기준 후보는 확인 못함. `MR3450072` (Trogdon–Olver, 2016)의 수치 특수함수 계산은 발견했으나 P 대 NP 역할을 추정하지 않았다.
- **공개 대조:** B002의 `MR1424469`, Whittaker–Watson, *A course of modern analysis*는 [Cambridge DOI landing](https://doi.org/10.1017/cbo9780511608759) 응답이 302이었다.
- **다음 공개 검색:** `ab:("arithmetic circuit" OR "algebraic complexity") AND cc:30`.

### 31 — Potential theory (100 출현)

- **B002에서 확인 못함:** potential theory의 P 대 NP 직접 전거·survey·원 성과는 확인 못함. `MR2816628`의 finite/infinite networks는 제목만으로 계산복잡도 기여를 확정할 수 없어 채택하지 않았다.
- **공개 대조:** B002의 `MR1334766`, Ransford, *Potential theory in the complex plane*는 [Cambridge DOI landing](https://doi.org/10.1017/cbo9780511623776) 응답이 302이었다.
- **다음 공개 검색:** `ab:("computational complexity" AND "potential theory")`; `ti:(network AND complexity) AND cc:31`.

### 32 — Several complex variables and analytic spaces (100 출현)

- **B002에서 확인 못함:** GCT 또는 algebraic-complexity와 실제로 연결되는 standard/survey/original result는 확인 못함. `MR2030225`, *Compact complex surfaces*는 분야 표준 survey지만 P 대 NP 역할 후보로 채택하지 않았다.
- **공개 대조:** [Springer landing for MR2030225](https://link.springer.com/book/10.1007/978-3-642-57739-0)는 200이었다.
- **다음 공개 검색:** `("geometric complexity theory" OR "arithmetic circuit") AND cc:(32 OR 14)`.

### 33 — Special functions (100 출현)

- **B002에서 확인 못함:** special-function evaluation의 계산 복잡도와 P 대 NP의 직접 경계를 다루는 표준·survey·원 성과는 확인 못함. `MR1406797`, Zhang–Jin, *Computation of special functions*은 계산 자료 후보이나 제목·분류만으로 complexity-theoretic 역할을 확정하지 않았다.
- **공개 대조:** B002의 `MR2128719`, Gasper–Rahman, *Basic hypergeometric series*는 [Cambridge DOI landing](https://doi.org/10.1017/cbo9780511526251) 응답이 302이었다.
- **다음 공개 검색:** `ti:("computation of special functions" OR "complexity of special functions")`; `ab:(arithmetic OR bit-complexity) AND cc:33`.

## 공통 중복·한계·후속 우선순위

### 확인한 중복

- `MR3330490`은 `13`과 `14`에 모두 출현한다. 계산대수기하의 공통 입문 후보이지만 GCT 문헌으로 승격하지 않았다.
- `MR1269324` (Weibel)은 `16`, `17`, `18`, `20`에도 출현한다. 분야 간 출현은 유지했으며 자동으로 하나의 역할로 병합하지 않았다.
- `MR1442260` (Stanley)은 `05`, `06`, `11`에 출현한다. 조합론적 표준서라는 역할만 공유하며 각 분야의 P 대 NP 역할을 대신하지 않는다.

### 표본 한계

- B002는 `-00/-01/-02`와 분야별 인용순 상위 100(단 `19`는 89)이라는 초기 표본이다. 따라서 결과 없음은 분야 전체·공개 문헌 전체·인증 DB 전체의 결과 없음이 아니다.
- 이 표본에는 초록이 없고 대다수가 단행본이다. 책의 제목·MSC·출판 맥락만으로 특정 정리, 후속 채택, 비판, 판본 관계를 확정할 수 없다.
- DOI resolver/landing 대조는 서지 경로만 확인했다. 원문을 대량 내려받거나 인증 DB·크리덴셜을 사용하지 않았고, 위에서 명시하지 않은 문헌을 판독 완료로 쓰지 않았다.

### 후속 우선순위

1. **직접 축:** `03`의 Krajíček, `06`의 Jukna, `08`의 Bodirsky, `12`의 Grigor'ev를 zbMATH Open record·공식 출판처·가능한 공개 원문에서 제목·초록·목차·판본으로 먼저 대조한다.
2. **대수/GCT 축:** `13`/`14`의 Cox–Little–O'Shea와 `15`의 Landsberg를 GCT의 실제 primary paper·survey와 분리해 연결한다. B002 밖의 공개 검색은 `geometric complexity theory`, `permanent determinant`, `arithmetic circuit lower bounds`로 시작한다.
3. **공개 누락 축:** ECCC, DROPS/LIPIcs, Theory of Computing, 공식 STOC·FOCS·CCC archive를 사용해 proceedings·technical report·preprint를 별도 판본으로 회수한다. B002 `68`이 인용순 상위 100 단행본 표본이라는 공백은 이미 [B002 공개 자료원 감사](B002-public-source-audit.md)에 기록되어 있다.
4. **먼 분야의 재검색:** 위 각 `다음 공개 검색`을 zbMATH Open에서 실행한 뒤에만, 실제 연결이 드러난 세부 MSC와 원문을 대상으로 확장한다. 검색 0건, API 실패, 미실행을 서로 바꾸지 않는다.

## 완료 상태

- **스캔 완료:** 23개 배정 분야, 2,289 B002 occurrence.
- **초기 후보화:** 완료. 직접 후보는 `03`, `06`, `08`, `12`; 방법·표현의 인접 후보는 나머지 명시 분야에 제한적으로 남겼다.
- **최종 핵심층 승인·covered:** 미실행.
- **공개 누락 검색:** 다음 검색식만 설계됨; 분야별 실행·원문 판독은 미실행.
