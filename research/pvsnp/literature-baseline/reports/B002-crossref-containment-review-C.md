# B002 Crossref title-containment 검토 C

기준 시각: 2026-09-04 KST  
범위: `B002-crossref-title-review.jsonl`의 `classification=title_containment` 148행을 DOI 오름차순으로 정렬한 100–148번, **49 DOI**.

## 방법과 판정 경계

B 검토와 같은 기준을 적용했다. 각 행에서 B002 candidate의 저자/편집자·제목·연도·ISBN·DOI·publisher·`booktitle`과 B002 Crossref raw envelope의 title·author·ISBN·container·type·publisher를 대조했다. 각 DOI는 `https://doi.org/<DOI>`의 canonical official record 경로다. 이 slice는 49/49 `crossref_state=found`이므로, 결과 없음은 어떤 처분 근거도 아니다.

`same_work_title_variant`는 동일 DOI와 저자·ISBN/publisher·container가 맞고 title의 부제·권 표기만 다른 경우다. `same_work_reissue_or_edition`은 핵심 title·저자는 맞으나 ISBN·연도·imprint가 달라 실제 판본 대조가 필요한 경우다. `component_of_candidate_work`는 동일 DOI의 chapter/component와 수록 글 대응이다. `different_volume_or_part_identifier_conflict`와 `shared_set_or_generic_title`은 하나의 DOI를 여러 MR에 자동 병합하지 않기 위한 멤버별 처분이다.

## DOI별 처분

| 순번 | DOI · Crossref title/type | candidate link와 대조 근거 | 처분 |
|---:|---|---|---|
| 100 | `10.1090/chel/383.h`; *Algebras, Lattices, Varieties*, monograph | `MR3793673` vol. 1; DOI·3 저자·candidate ISBN `9781470442958`이 Crossref ISBN에 있고 권만 생략. | `same_work_title_variant` |
| 101 | `10.1090/coll/015`; *Linear Transformations in Hilbert Space and Their Applications to Analysis*, monograph | `MR1451877`; DOI·Stone·print ISBN 대응, Crossref가 applications subtitle을 보강. | `same_work_title_variant` |
| 102 | `10.1090/coll/048`; *Geometric Nonlinear Functional Analysis*, monograph | `MR1727673` vol. 1; DOI·2 저자·ISBN 대응, 권 생략. | `same_work_title_variant` |
| 103 | `10.1090/coll054.1`; *Orthogonal Polynomials on the Unit Circle*, monograph | `MR2105088` part 1; DOI·Simon·ISBN 대응, part 생략. | `same_work_title_variant` |
| 104 | `10.1090/gsm/061`; *Cartan for Beginners*, monograph | `MR2003610`; DOI·2 저자·candidate ISBN 대응, moving-frames subtitle 생략. | `same_work_title_variant` |
| 105 | `10.1090/gsm/100`; *Algebra*, monograph | `MR2472787`; DOI·Isaacs·candidate ISBN 대응, graduate-course subtitle 생략. | `same_work_title_variant` |
| 106 | `10.1090/gsm/165`; *Advanced Modern Algebra*, monograph | `MR3443588` part 1; DOI·Rotman·candidate ISBN 대응, part 생략. | `same_work_title_variant` |
| 107 | `10.1090/memo/0788`; *ℛ-boundedness, Fourier multipliers and problems of elliptic and parabolic type*, journal-article | `MR2006641`; DOI·3 저자·Memoirs container 일치, TeX 표기만 다름. | `same_work_title_variant` |
| 108 | `10.1090/mmono/104`; *Wulff Construction: A Global Shape from Local Interaction*, monograph | `MR1181197`; DOI·3 저자·AMS translation series 일치, candidate title 축약. | `same_work_title_variant` |
| 109 | `10.1090/mmono/105`; *Mathematical Scattering Theory: General Theory*, monograph | `MR1180965`; DOI·Yafaev·핵심 title은 맞지만 candidate/Crossref ISBN가 달라 e-reissue/edition 대조 필요. | `same_work_reissue_or_edition` |
| 110 | `10.1090/mmono/110`; *Introduction to Complex Analysis Part II. Functions of Several Variables*, monograph | `MR1192135` part II; DOI·Shabat은 맞고 ISBN·상세 title이 달라 판본 대조 필요. | `same_work_reissue_or_edition` |
| 111 | `10.1090/surv/040.3`; *The Classification of the Finite Simple Groups, Number 3*, monograph | `MR1490581` number 3/part I/chapter A; DOI·3 저자·ISBN 대응, Crossref가 part/chapter 생략. | `same_work_title_variant` |
| 112 | `10.1093/acprof:oso/9780199585205.001.0001`; *Quantum Gravity*, monograph | `MR3025613`; DOI·Kiefer·ISBN `9780199585205` 일치, Crossref가 Third Edition을 보강. | `same_work_title_variant` |
| 113 | `10.1109/mcs.2008.931718`; *Hybrid dynamical systems*, journal-article | `MR2499435`; DOI·3 저자·IEEE journal 일치, candidate subtitle 생략. | `same_work_title_variant` |
| 114 | `10.1111/j.1749-6632.1985.tb14533.x`; *Problems and Results in Combinatorial Geometry*, journal-article | `MR809186` Erdős incollection; DOI·저자·conference/journal publication context가 같은 article을 가리키며 title 표기만 다름. | `same_work_title_variant` |
| 115 | `10.1137/1.9780898717938`; *Finite Difference Schemes and Partial Differential Equations, Second Edition*, monograph | `MR2124284`; DOI·Strikwerda·print ISBN 대응, Crossref가 edition을 보강. | `same_work_title_variant` |
| 116 | `10.1137/1.9780898719505`; *A Multigrid Tutorial, Second Edition*, monograph | `MR1774296`; DOI·3 저자·print ISBN 대응, Crossref가 edition을 보강. | `same_work_title_variant` |
| 117 | `10.1137/1.9781611971170`; *Introduction to Matrix Analysis, Second Edition*, monograph | `MR1455129`; DOI·Bellman·print ISBN 대응, Crossref가 edition을 보강. | `same_work_title_variant` |
| 118 | `10.1137/1.9781611975925`; *The Cahn–Hilliard Equation: Recent Advances and Applications*, book | `MR4001523`; DOI·Miranville·candidate ISBN `9781611975918`가 Crossref ISBN에 있고 subtitle 보강. | `same_work_title_variant` |
| 119 | `10.1137/s0036144597327347`; *The Global Positioning System and the Implicit Function Theorem*, article | `MR1642768`; DOI·3 저자·SIAM Review 일치, capitalization만 차이. | `same_work_title_variant` |
| 120 | `10.1142/0712-vol1`; *Mechanics of Continuous Media*, monograph | `MR1470716` vol. 1,2; DOI·Sedov·World Scientific은 맞으나 candidate의 복수 권과 Crossref `vol1`/ISBN가 달라 판본 범위 대조 필요. | `same_work_reissue_or_edition` |
| 121 | `10.1142/1284`; *Topics in Polynomials*, monograph | `MR1298187`; DOI·3 저자·ISBN 대응, extremal-problems subtitle 생략. | `same_work_title_variant` |
| 122 | `10.1142/9789812774200`; *Associative Functions: Triangular Norms and Copulas*, monograph | `MR2222258`; DOI·3 저자·World Scientific 일치, candidate title 축약. | `same_work_title_variant` |
| 123 | `10.1142/p802`; *Geometric Mechanics*, book | `MR2894526` part II의 ISBN `9781848167780`은 Crossref ISBN(`9781848167773`, `9781848167797`)과 맞지 않고 Crossref title에 part가 없음. | `different_volume_or_part_identifier_conflict` |
| 124 | `10.1142/p926`; *Fractional Calculus and Waves in Linear Viscoelasticity*, monograph | `MR4485803`; DOI·Mainardi·candidate ISBN이 Crossref print ISBN에 있고 subtitle 생략. | `same_work_title_variant` |
| 125 | `10.1201/9781420003451.axb`; *Dniester Notebook*, book-chapter | `MR2203726` incollection; DOI·*Non-Associative Algebra and Its Applications* container·candidate ISBN 일치. | `component_of_candidate_work` |
| 126 | `10.1201/9781420035315`; *Handbook of Discrete and Computational Geometry, Second Edition*, book | `MR2082993`; DOI·CRC handbook title은 맞으나 candidate 2004 print ISBN과 Crossref eISBN가 달라 edition/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 127 | `10.1201/9781420049954`; *CRC Handbook of Combinatorial Designs*, book | `MR1392993`; DOI·CRC publisher·print ISBN 대응, initial article/`The` 차이. | `same_work_title_variant` |
| 128 | `10.1201/9781420056945`; *Geometry, Topology and Physics, Second Edition*, book | `MR2001829`; DOI·Nakahara·candidate ISBN `0750306068`이 Crossref print ISBN으로 대응, edition 보강. | `same_work_title_variant` |
| 129 | `10.1201/9781420066531`; *Transforms and Applications Handbook, Third Edition*, book | `MR2640541`; DOI·candidate ISBN `9781420066524`가 Crossref ISBN에 있고 title의 관사/edition만 차이. | `same_work_title_variant` |
| 130 | `10.1201/b15885`; *An Introduction to Intersection Homology Theory, Second Edition*, monograph | `MR2207421`; DOI·2 저자·print ISBN 대응, Crossref가 edition을 보강. | `same_work_title_variant` |
| 131 | `10.1214/ss/1009212519`; *Bayesian model averaging: a tutorial (with comments …)*, article | `MR1765176`; DOI·4 저자·*Statistical Science* 일치, Crossref가 comments/rejoinder를 보강. | `same_work_title_variant` |
| 132 | `10.1515/9781400830329`; *Google's PageRank and Beyond*, edited-book | `MR2262054`; DOI·2 저자·PUP은 맞으나 candidate print ISBN과 Crossref eISBN가 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 133 | `10.1515/9781400830558`; *Higher Topos Theory (AM-170)*, edited-book | `MR2522659`; DOI·Lurie·PUP은 맞으나 print/eISBN이 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 134 | `10.1515/9781400835416`; *Log-Gases and Random Matrices (LMS-34)*, edited-book | `MR2641363`; DOI·Forrester·PUP은 맞으나 print/eISBN이 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 135 | `10.1515/9781400846528`; *Spaces of PL Manifolds and Categories of Simple Maps (AM-186)*, edited-book | `MR3202834`; DOI·3 저자·PUP은 맞으나 candidate print ISBN과 Crossref eISBN가 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 136 | `10.1515/9781400866618`; *Action-minimizing Methods in Hamiltonian Dynamics*, edited-book | `MR3330134`; DOI·Sorrentino·PUP은 맞으나 print/eISBN이 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 137 | `10.1515/9781400881598`; *Functional Integration and Partial Differential Equations (AM-109)*, edited-book | `MR833742`; DOI·Freidlin·PUP은 맞으나 print/eISBN이 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 138 | `10.1515/9781400882496`; *The Admissible Dual of GL(N) via Compact Open Subgroups (AM-129)*, edited-book | `MR1204652`; DOI·Bushnell–Kutzko·PUP은 맞으나 print/eISBN이 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 139 | `10.1515/9781400882526`; *Introduction to Toric Varieties (AM-131)*, edited-book | `MR1234037`; DOI·Fulton·PUP은 맞으나 print/eISBN이 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 140 | `10.1515/9781400883936`; *Cohomological Induction and Unitary Representations (PMS-45)*, edited-book | `MR1330919`; DOI·2 저자·PUP은 맞으나 print/eISBN이 달라 host/reissue 대조 필요. | `same_work_reissue_or_edition` |
| 141 | `10.1515/9783110203059`; *Simple Lie Algebras over Fields of Positive Characteristic*, edited-book | `MR2573283` vol. II; DOI·Strade·candidate ISBN `9783110197013`가 Crossref ISBN에 있고 권 생략. | `same_work_title_variant` |
| 142 | `10.1515/9783110218114`; *Approximations and Endomorphism Algebras of Modules*, edited-book | `MR2985554` vol. 1 및 `MR2985654` vol. 2가 같은 DOI·동일 ISBN을 공유하고 Crossref는 권을 식별하지 않음. | 두 MR 모두 `shared_set_or_generic_title` |
| 143 | `10.1515/9783110497397`; *Multiphysics Phase-Field Fracture*, edited-book | `MR4304073`; DOI·Wick·candidate ISBN이 Crossref ISBN에 있고 subtitle 생략. | `same_work_title_variant` |
| 144 | `10.1515/9783110801194`; *Systems*, edited-book, De Gruyter | `MR1828371` Halter-Koch, *Ideal systems*, Marcel Dekker; title·ISBN·publisher·저자 신호가 충돌. | `wrong_identifier` |
| 145 | `10.1515/9783111337487-002`; *Nonstandard Sobolev scales … X-ray transform …*, book-chapter | `MR4815452` incollection; DOI·Monard·container·candidate ISBN 일치. | `component_of_candidate_work` |
| 146 | `10.1515/dmvm-2025-0078`; 독일어 KI 교육 article | `MR4995776`; DOI·4 저자·journal 일치, candidate 부제가 survey 결과를 보강. | `same_work_title_variant` |
| 147 | `10.2991/978-94-91216-37-4`; *Continued Fractions*, book | `MR2433845` vol. 1; DOI·2 저자는 맞으나 candidate ISBN과 Crossref eISBN/series가 달라 reissue 대조 필요. | `same_work_reissue_or_edition` |
| 148 | `10.37236/1194`; *An On-Line Version of the Encyclopedia of Integer Sequences*, article | `MR1715316`은 이 원 논문에 대한 “Comments on …” article이다. DOI는 원 논문 record를 가리키므로 title containment만으로 동일 work가 아님. | `related_but_distinct_work` |

## 집계와 검산

| 상호배타적 DOI 행 패턴 | DOI 행 수 | candidate link 수 | 멤버별 처분 |
|---|---:|---:|---|
| `same_work_title_variant` | 29 | 29 | variant 29 |
| `same_work_reissue_or_edition` | 14 | 14 | reissue/edition 14 |
| `component_of_candidate_work` | 2 | 2 | component 2 |
| `different_volume_or_part_identifier_conflict` | 1 | 1 | conflict 1 |
| `shared_set_or_generic_title` | 1 | 2 | shared/generic 2 |
| `wrong_identifier` | 1 | 1 | wrong identifier 1 |
| `related_but_distinct_work` | 1 | 1 | related/distinct 1 |
| `unresolved` | 0 | 0 | 0 |
| **합계** | **49** | **50** | variant **29**, reissue **14**, component **2**, conflict **1**, shared **2**, wrong **1**, related **1** |

100–148 source DOI 집합과 위 표 DOI 집합은 각 49개여야 하며 대칭차는 0이어야 한다. candidate link는 50개인데, 142번 DOI가 Vol. 1·Vol. 2 두 MR을 공유하기 때문이다. 그 두 MR은 DOI 하나를 근거로 병합하지 않으며, 123번의 Part II conflict·144번 wrong identifier·148번 comment/article 관계도 원 candidate/관계 JSONL을 수정하는 근거가 아니다.
