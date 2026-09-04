# B002 Crossref title-containment 검토 B

기준 시각: 2026-09-04 KST  
범위: `B002-crossref-title-review.jsonl`의 `classification=title_containment` 148행을 DOI 오름차순으로 정렬한 51–99번, **49 DOI**.

## 방법과 판정 경계

각 행에서 B002 candidate의 원문 서지(저자/편집자, 제목, 연도, ISBN, DOI, publisher, `booktitle`), B002 Crossref raw envelope의 제목·저자·ISBN·container·type·publisher, DOI canonical resolver 경로를 대조했다. 표의 DOI는 `https://doi.org/<DOI>` 공식 record 경로다. `title_containment` 문자열만으로 처분하지 않았다.

이 slice의 `crossref_state`는 49/49 `found`다. 따라서 “Crossref 결과 없음”을 어느 행의 처분 근거로 쓰지 않았다.

처분은 다음 뜻으로 한정한다.

- `same_work_title_variant`: 동일 DOI와 저자·ISBN 또는 publisher/container가 맞고 Crossref가 부제·권 표기를 생략/축약한 경우.
- `same_work_reissue_or_edition`: 저자·핵심 제목은 맞지만 ISBN·연도·publisher imprint가 달라 전자 재발행/판본 관계를 실제로 대조해야 하는 경우.
- `different_volume_or_part_identifier_conflict`: 같은 DOI가 서로 다른 권/부분 후보에 걸렸고 ISBN이 한 쪽만 지지하는 경우.
- `component_of_candidate_work`: Crossref가 book chapter이고 candidate가 같은 DOI·저자·container의 수록 글인 경우.
- `wrong_identifier`: DOI의 Crossref title/type/container/ISBN이 candidate와 충돌하는 경우.

`same_work_*`는 수학 내용, 최신성, 판본 간 완전 동일성을 확정하지 않는다. `wrong_identifier`도 candidate가 틀렸다는 결론이 아니라 현재 DOI 연결이 그 candidate를 식별하지 못한다는 처분이다.

## DOI별 처분

| 순번 | DOI · Crossref 공식 record | candidate link와 대조 근거 | 처분 |
|---:|---|---|---|
| 51 | `10.1007/978-3-642-61698-3`; *Algebra II*, book, Bourbaki, Springer | `MR1994218` *Algebra II, Chapters 4–7*; 저자·DOI 일치, candidate ISBN `3540007067`은 Crossref print ISBN `9783540007067`과 대응. | `same_work_title_variant` |
| 52 | `10.1007/978-3-658-43763-3`; *Understanding the Generality of Mathematical Statements*, book, Damrau, Springer | `MR4755317`; 저자·DOI와 두 ISBN(`9783658437626`, `9783658437633`) 일치. Crossref가 부제를 생략. | `same_work_title_variant` |
| 53 | `10.1007/978-3-662-02732-5_1`; *Methods and Structure of Commutative Harmonic Analysis*, book-chapter, Khavin | `MR1134136` incollection; DOI·저자·EMS *Commutative Harmonic Analysis I* container 일치. | `component_of_candidate_work` |
| 54 | `10.1007/978-3-662-03319-7`; *Theory of Orbits*, book, Boccaletti–Pucacco | `MR1391960` *Theory of Orbits, Vol. 1*; DOI·저자 일치, Crossref title은 권을 생략하고 eISBN pair를 제시. | `same_work_reissue_or_edition` |
| 55 | `10.1007/978-3-662-03444-6`; *Operator Algebras and Quantum Statistical Mechanics*, book, Bratteli–Robinson | `MR1441540` vol. 2; DOI·저자 일치, Crossref generic title/전자 ISBN과 candidate의 권 표기가 달라 판본 대조 필요. | `same_work_reissue_or_edition` |
| 56 | `10.1007/978-3-662-05389-8`; *Handbook of Stochastic Methods*, book, Gardiner | `MR2053476`; DOI·저자·candidate ISBN `3540208828`과 Crossref print ISBN `9783540208822` 대응, 부제만 차이. | `same_work_title_variant` |
| 57 | `10.1007/978-3-662-06292-0_2`; *Non-Associative Structures*, book-chapter, Kuz’min–Shestakov | `MR1360006` incollection; DOI·저자·*Algebra VI* container 일치. | `component_of_candidate_work` |
| 58 | `10.1007/978-3-662-65692-1`; *Spherical Functions of Mathematical Geosciences*, book, Freeden–Schreiner | `MR4516554`; DOI·저자·두 ISBN 일치, Crossref가 부제를 축약. | `same_work_title_variant` |
| 59 | `10.1007/978-3-662-71332-7`; *Special and General Relativity*, book, Boblest–Müller–Wunner | `MR5095869`; DOI·저자·두 ISBN 일치, Crossref가 긴 부제를 생략. | `same_work_title_variant` |
| 60 | `10.1007/978-3-7091-1625-8`; *Plasticity and Beyond*, book, Springer Vienna | `MR3137673`; DOI·두 ISBN 일치, candidate의 긴 부제가 Crossref 기본 title보다 상세. | `same_work_title_variant` |
| 61 | `10.1007/978-94-009-6259-0`; *Handbook of Philosophical Logic*, book, Springer Netherlands | `MR844595` *Vol. II*; Crossref title은 권을 생략하고 ISBN도 후보와 다르다. 같은 handbook/판본인지 권·ISBN으로 재대조 필요. | `same_work_reissue_or_edition` |
| 62 | `10.1007/978-94-010-0732-0`; *From Finite to Infinite Dimensional Dynamical Systems*, book, Springer Netherlands | `MR1881888` James C. Robinson, *Infinite-Dimensional Dynamical Systems* (Cambridge ISBN `0521632048`); Crossref의 title·ISBN·NATO container·publisher가 모두 충돌. | `wrong_identifier` |
| 63 | `10.1007/978-94-017-2881-2`; *Representation of Lie Groups and Special Functions*, book, Vilenkin–Klimyk | `MR1206906` vol. 3; 저자·DOI는 맞지만 Crossref generic title과 재발행 ISBN, candidate의 vol. 3/구 ISBN을 판본으로 대조해야 함. | `same_work_reissue_or_edition` |
| 64 | `10.1007/978-94-017-2883-6`; 같은 title, book, Vilenkin–Klimyk | `MR1220225` vol. 2; 저자·DOI는 맞고 권/ISBN 표기가 다르므로 판본 대조 필요. | `same_work_reissue_or_edition` |
| 65 | `10.1007/978-981-15-4174-2`; *Fundamentals of Astrophysical Fluid Dynamics*, book, Kato–Fukue | `MR4371036`; DOI·저자·두 ISBN 일치, candidate 부제만 추가. | `same_work_title_variant` |
| 66 | `10.1007/978-981-95-1884-5`; 같은 title, book, Kato–Fukue | `MR5028321`; DOI·저자·두 ISBN 일치, candidate 부제만 추가. | `same_work_title_variant` |
| 67 | `10.1007/b93802`; *Nonlinear Stability of Finite Volume Methods for Hyperbolic Conservation Laws*, book, Bouchut | `MR2128209`; DOI·저자와 print/eISBN 대응, candidate가 source·well-balanced subtitle을 확장. | `same_work_title_variant` |
| 68 | `10.1007/b98886`; *Applied Functional Data Analysis: Methods and Case Studies*, book, Springer | `MR1910407` Ramsay–Silverman; DOI·ISBN `9780387954141` 일치, Crossref가 부제를 보강. | `same_work_title_variant` |
| 69 | `10.1007/s00591-021-00310-x`; 독일어 AI 교육 article, Schönbrodt–Camminady–Frank | `MR4386009`; DOI·저자·journal 일치, candidate 긴 부제가 Crossref 기본 title을 확장. | `same_work_title_variant` |
| 70 | `10.1007/s11229-005-3715-x`; *INTRODUCTION*, journal-article, *Synthese* | `MR2197664` Nelsen, *An Introduction to Copulas*, Springer book; Crossref의 type·container·저자 부재가 candidate와 충돌. | `wrong_identifier` |
| 71 | `10.1016/S1874-575X(02)80015-7`; *Chapter 13 Rational billiards and flat structures*, book-chapter | `MR1928530` Masur–Tabachnikov incollection; DOI·저자·*Handbook of Dynamical Systems 1A* container 일치. | `component_of_candidate_work` |
| 72 | `10.1017/9781107337817`; *Non-Associative Normed Algebras*, monograph, Cabrera García–Rodríguez Palacios | `MR3791798` vol. 2; DOI·저자·candidate print ISBN `9781107043114`가 Crossref ISBN에 있음, Crossref가 권을 생략. | `same_work_title_variant` |
| 73 | `10.1017/9781108591034`; *Probability*, monograph, Durrett | `MR3930614`; DOI·저자·candidate ISBN `9781108473682`가 Crossref ISBN에 있음, Crossref가 부제를 생략. | `same_work_title_variant` |
| 74 | `10.1017/9781316678626`; *Factorization Algebras in Quantum Field Theory*, monograph, Costello–Gwilliam | `MR3586504` vol. 1; DOI·저자·candidate ISBN `9781107163102`가 Crossref ISBN에 있음. | `same_work_title_variant` |
| 75 | `10.1017/9781316779422`; *Random Graphs and Complex Networks*, monograph, van der Hofstad | `MR3617364` vol. 1; DOI·저자·candidate ISBN `9781107172876`가 Crossref ISBN에 있음. | `same_work_title_variant` |
| 76 | `10.1017/CBO9780511524486`; *Spinors and Space-Time*, monograph, Penrose–Rindler | `MR838301` vol. 2; DOI·저자·print ISBN 대응, Crossref가 권을 생략. | `same_work_title_variant` |
| 77 | `10.1017/CBO9780511526367.003`; *A Crash Course in Geometric Mechanics*, book-chapter | `MR2172978` incollection; DOI·5 저자·*Geometric Mechanics and Symmetry* container 일치. | `component_of_candidate_work` |
| 78 | `10.1017/CBO9780511530074`; *Padé Approximants Second Edition*, monograph, Baker–Graves-Morris | `MR1383091`; 저자·핵심 title은 맞으나 candidate 1996 ISBN과 Crossref eISBN만 있어 edition/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 79 | `10.1017/CBO9780511543241`; *Radial Basis Functions*, monograph, Buhmann | `MR1997878`; DOI·저자는 맞고 candidate subtitle/print ISBN과 Crossref eISBN이 달라 reissue 대조 필요. | `same_work_reissue_or_edition` |
| 80 | `10.1017/CBO9780511564048`; *Spinors and Space-Time*, monograph, Penrose–Rindler | `MR776784` vol. 1; DOI·저자·print ISBN 대응, Crossref가 권을 생략. | `same_work_title_variant` |
| 81 | `10.1017/CBO9780511608834`; *Epidemic Modelling*, monograph, Daley–Gani | `MR1688203`; DOI·저자·candidate ISBN `0521640792`가 Crossref print ISBN으로 대응, 부제 생략. | `same_work_title_variant` |
| 82 | `10.1017/CBO9780511609589`; *Enumerative Combinatorics*, monograph, Stanley–Fomin | `MR1676282` Stanley vol. 2; DOI·candidate print ISBN `0521560696`가 Crossref ISBN에 있고 Crossref가 권을 생략. | `same_work_title_variant` |
| 83 | `10.1017/CBO9780511614309`; *Elements of the Representation Theory of Associative Algebras*, monograph, Assem–Skowroński–Simson | `MR2197389` vol. 1; DOI·저자·candidate ISBN이 Crossref ISBN에 있고 권 생략. | `same_work_title_variant` |
| 84 | `10.1017/CBO9780511618123`; *String Theory*, monograph, Polchinski | `MR1648555` vol. I (ISBN `0521633036`)는 Crossref ISBN과 맞지 않음; `MR1648559` vol. II (ISBN `0521633044`)는 Crossref ISBN `9780521633048`과 대응. | `MR1648555`: `different_volume_or_part_identifier_conflict`; `MR1648559`: `same_work_title_variant` |
| 85 | `10.1017/CBO9780511618796`; *Learning Theory*, monograph, Cucker–Zhou | `MR2354721`; DOI·저자·candidate ISBN `9780521865593`가 Crossref ISBN에 있고 subtitle만 차이. | `same_work_title_variant` |
| 86 | `10.1017/CBO9780511623899`; *Methods of Algebraic Geometry*, monograph, Hodge–Pedoe | `MR1288307` vol. III; DOI·저자·핵심 title은 맞으나 candidate/Crossref ISBN이 달라 reissue 대조 필요. | `same_work_reissue_or_edition` |
| 87 | `10.1017/CBO9780511624216`; *Neural Network Learning*, monograph, Anthony–Bartlett | `MR1741038`; DOI·저자·핵심 title은 맞으나 candidate/Crossref ISBN 표기가 달라 reissue 대조 필요. | `same_work_reissue_or_edition` |
| 88 | `10.1017/CBO9780511756337`; *Electromagnetic Theory and Computation*, edited-book, Gross–Kotiuga | `MR2067778`; DOI·저자·candidate ISBN `0521801605`가 Crossref print ISBN으로 대응, subtitle 생략. | `same_work_title_variant` |
| 89 | `10.1017/CBO9780511779398`; *Probability*, monograph, Durrett | `MR2722836`; DOI·저자·candidate ISBN `9780521765398`가 Crossref ISBN에 있고 subtitle 생략. | `same_work_title_variant` |
| 90 | `10.1017/CBO9780511791246`; *Complex Variables*, monograph, Ablowitz–Fokas | `MR1989049`; DOI·저자·candidate ISBN `0521534291`가 Crossref print ISBN으로 대응, subtitle 생략. | `same_work_title_variant` |
| 91 | `10.1017/CBO9780511805967`; *Enumerative Combinatorics*, monograph, Stanley–Rota | `MR1442260` Stanley vol. 1; DOI·candidate ISBN `0521553091`가 Crossref ISBN에 있고 권 생략. | `same_work_title_variant` |
| 92 | `10.1017/CBO9780511840159`; *Theoretical Astrophysics*, monograph, Padmanabhan | `MR1841976` vol. II; DOI·candidate ISBN `0521562414`가 Crossref ISBN에 있고 권 생략. | `same_work_title_variant` |
| 93 | `10.1017/CBO9781107325777`; *Banach Algebras and the General Theory of *-Algebras*, monograph, Palmer | `MR1270014` vol. I; DOI·저자·candidate ISBN `0521366372`가 Crossref print ISBN으로 대응, 권 생략. | `same_work_title_variant` |
| 94 | `10.1017/CBO9781139062046`; *3264 and All That*, monograph, Eisenbud–Harris | `MR3617981`; DOI·저자·candidate ISBN이 Crossref ISBN에 있고 subtitle 생략. | `same_work_title_variant` |
| 95 | `10.1017/CBO9781139172059`; *Solitons*, monograph, Drazin–Johnson | `MR985322`; DOI·저자·candidate ISBN `052133389X`가 Crossref print ISBN으로 대응, subtitle 생략. | `same_work_title_variant` |
| 96 | `10.1017/CBO9781139193184`; *Conformal Fractals*, monograph, Przytycki–Urbański | `MR2656475`; DOI·저자·candidate ISBN `9780521438001`가 Crossref ISBN에 있고 subtitle 생략. | `same_work_title_variant` |
| 97 | `10.1017/CBO9781139644174`; *The Quantum Theory of Fields*, monograph, Weinberg | `MR1410064` vol. I (ISBN `0521550017`)는 Crossref ISBN과 맞지 않음; `MR1411911` vol. II (ISBN `0521550025`)는 Crossref ISBN `9780521550024`와 대응. | `MR1410064`: `different_volume_or_part_identifier_conflict`; `MR1411911`: `same_work_title_variant` |
| 98 | `10.1086/368660`; *Peurbach's Theoricae Novae Planetarum: A Translation with Commentary*, journal-article, Aiton | `MR1010779`; DOI·저자·journal 일치, Crossref가 commentary subtitle을 보강. | `same_work_title_variant` |
| 99 | `10.1090/amsip/002.2/02`; *Problems in low-dimensional topology (Introduction)*, book-chapter, AMS | `MR1470751` incollection; DOI·*Geometric Topology* container·candidate title 일치. | `component_of_candidate_work` |

## 집계와 후속 의무

| 상호배타적 DOI 행 패턴 | DOI 행 수 | candidate link 수 | 멤버별 처분 |
|---|---:|---:|---|
| `same_work_title_variant`만 | 31 | 31 | variant 31 |
| `same_work_reissue_or_edition` | 9 | 9 | reissue/edition 9 |
| `component_of_candidate_work` | 5 | 5 | component 5 |
| `wrong_identifier` | 2 | 2 | wrong identifier 2 |
| 혼합: variant + `different_volume_or_part_identifier_conflict` | 2 | 4 | variant 2, volume/part conflict 2 |
| `shared_set_or_generic_title`, `related_but_distinct_work`, `unresolved` | 0 | 0 | 각 0 |
| **합계** | **49** | **51** | variant **33**, reissue **9**, component **5**, conflict **2**, wrong **2** |

`MR1648555`/`MR1648559`와 `MR1410064`/`MR1411911`은 같은 Crossref DOI를 공유하지만 멤버별 ISBN 대조 결과가 갈린다. 따라서 DOI 하나를 근거로 두 MR을 병합하지 않는다. `MR1881888`과 `MR2197664`의 `wrong_identifier`도 candidate record를 수정·삭제하라는 지시가 아니며, 후속 단계에서 MathSciNet 원 서지와 publisher edition을 다시 대조해야 한다.

### 완전성 검산

source slice의 DOI 집합은 정렬된 51–99번 49행으로 고정했다. 위 표의 DOI 집합도 49개이며, 두 집합의 대칭차는 0이어야 한다. 후보 연결은 51개(84·97번이 각각 두 MR)를 모두 표에 포함했다. 이 보고서는 후보/관계 JSONL을 수정하지 않는다.
