# B002 공개 bridge 검색 — MSC 00–33

조사 시각: 2026-09-04 21:42–21:46 KST. 이 보고서의 판정은 두 자리 MSC 제약을 넣어 재실행한 zbMATH Open API 결과만 쓴다. Endpoint: `GET https://api.zbmath.org/document/_search?search_string=<URL-encoded query>&page=0&results_per_page=3`. 모든 200행은 `execution_bool=true`를 확인했고, `total/returned`는 응답의 total과 실제 배열 길이다. 순위·인용 수는 핵심성 근거가 아니다. 검색 문법은 [zbMATH Help](https://zbmath.org/general-help/)와 [API](https://api.zbmath.org/)를 따른다.

`search_failed`는 유효한 0건이 아니다. `search_no_candidate_after_review`는 B002 중복, 분야 밖 잡음, 또는 metadata만으로 P 대 NP 역할을 확인하지 못한 상태다. `covered`와 최종 핵심층은 판정하지 않는다.

| MSC | 실제 scoped query | HTTP; total/returned | 처분 |
|---|---|---:|---|
| 00 | 좁힌 재실행 `cc:00 & ti:computation` | 200; 1,196/3 | **search_no_candidate_after_review:** [3982425](https://zbmath.org/3982425)/Zbl `0607.65041`, *Stiff computation*; [6032524](https://zbmath.org/6032524)/`1247.00010`, *Exploratory experimentation and computation*; [43351](https://zbmath.org/43351)/`0800.68012`, *The ecology of computation*. 세 제목 모두 B002 밖이나 P/NP 직접 역할은 metadata에서 확인되지 않았다. |
| 01 | `cc:01 & ti:"history of computational complexity"` | 200; 1/1 | **new_candidate_after_review:** `5604084`/Zbl `1169.68429`, Fortnow–Homer, *A short history of computational complexity* (2003, journal article, *BEATCS* 80, 95–133). [zbMATH](https://zbmath.org/5604084). |
| 03 | `cc:03 & ti:"proof complexity"` | 200; 114/3 | **new_candidate_after_review:** `7044161`/`1532.03002`, Jan Krajíček, *Proof complexity* (2019, book/book article, Cambridge). [zbMATH](https://zbmath.org/7044161), [DOI](https://doi.org/10.1017/9781108242066) (302). ECCC [TR23-199](https://eccc.weizmann.ac.il/report/2023/199/)도 200으로 대조했다. |
| 05 | `cc:05 & ti:"counting complexity"` | 200; 6/3 | **search_no_candidate_after_review:** 첫 record `7680491`, *Where Tutte and Holant meet: a view from counting complexity*의 P 대 NP 역할은 metadata에서 미확정이다. |
| 06 | `cc:06 & ti:"Boolean function complexity"` | 200; 3/3 | **search_no_candidate_after_review:** 첫 record `6842492`, *Composition limits and separating examples for some Boolean function complexity measures*는 원문/초록 대조 전 미확정이다. |
| 08 | `cc:08 & ti:"infinite-domain constraint satisfaction"` | 200; 8/3 | **search_no_candidate_after_review:** `7344230`, Bodirsky 저작은 B002 `MR4273453` 공개 대응이다. |
| 11 | `cc:11 & ti:"computational number theory"` | 200; 29/3 | **search_no_candidate_after_review:** `1391020`, *Advanced topics in computational number theory*의 P 대 NP·암호 역할은 미확정이다. |
| 12 | `cc:12 & ti:"algebraic complexity"` | 200; 5/3 | **search_no_candidate_after_review:** `3755869`, *Linear disjointness and algebraic complexity*의 핵심 역할은 원문 대조 전 미확정이다. |
| 13 | `cc:13 & ti:"computational commutative algebra"` | 200; 5/3 | **search_no_candidate_after_review:** `1515218`, Kreuzer–Robbiano 저작은 B002 `MR1790326` 대응이다. |
| 14 | `cc:14 & ti:"geometric complexity theory"` | 200; 16/3 | **new_candidate_after_review:** `6610118`/`1358.68108`, J. M. Landsberg, *An introduction to geometric complexity theory* (2016, journal article, *EMS Newsletter* 99, 10–18). [zbMATH](https://zbmath.org/6610118); [Theory of Computing GS010](https://www.theoryofcomputing.org/articles/gs010/)도 200. |
| 15 | `cc:15 & ti:"tensor rank"` (재시도) | 200; 67/3 | **search_no_candidate_after_review:** scoped 반환 3건의 상세 대조는 미실행; 무제약 Håstad record는 이 처분의 근거로 쓰지 않았다. |
| 16 | `cc:16 & ti:"polynomial identities"` | 200; 291/3 | **search_no_candidate_after_review:** query가 넓고 B002 밖 P 대 NP 기여는 미확정이다. |
| 17 | `cc:17 & ti:"Lie algebras" & ti:algorithms` | 200; 12/3 | **search_no_candidate_after_review:** `1418992`, de Graaf 저작은 B002 `MR1743970` 대응이다. |
| 18 | `cc:18 & ti:"category theory for computing"` | 200; 2/2 | **search_no_candidate_after_review:** `46995`, Barr–Wells 저작은 B002 `MR1094561` 대응이다. |
| 19 | `cc:19 & ti:"K-theory" & ti:complexity` | 200; 8/3 | **search_no_candidate_after_review:** `7908010`, controlled/operator K-theory record의 P 대 NP 역할은 미확정이다. |
| 20 | `cc:20 & ti:"computational group theory"` | 200; 34/3 | **search_no_candidate_after_review:** `2133330`, Holt–Eick–O'Brien 저작은 B002 `MR2129747` 대응이다. |
| 22 | 처음 `cc:22 & ti:"Lie groups" & ti:complexity`은 404; `cc:22 & ab:complexity`로 축소 | 200; 155/3 | **search_no_candidate_after_review:** 축소 query가 넓어 후보를 추가하지 않았다. |
| 26 | `cc:26 & ti:"complexity theory of real functions"` | 200; 1/1 | **search_no_candidate_after_review:** `52121`, Ker-I Ko 저작은 B002 `MR1137517` 대응이다. |
| 28 | `cc:28 & ti:"algorithmic randomness"` | 200; 1/1 | **search_no_candidate_after_review:** `7464645`, *Computable measure theory and algorithmic randomness*의 P 대 NP 역할은 미확정이다. |
| 30 | `cc:30 & ti:"algebraic complexity"` | 200; 1/1 | **search_no_candidate_after_review:** `4028758`, *Algebraic complexity of computing polynomial zeros*를 복소함수 분야 P 대 NP 후보로 판정하지 않았다. |
| 31 | `cc:31 & ti:"potential theory" & ti:complexity` | 200; 3/3 | **search_no_candidate_after_review:** `902833`, potential-theory complexity record의 P 대 NP 역할은 미확정이다. |
| 32 | 좁힌 재실행 `cc:32 & ti:complexity` | 200; 56/3 | **search_no_candidate_after_review:** [2115787](https://zbmath.org/2115787)/Zbl `1131.37052`, *Teichmüller geodesics of infinite complexity*; [6720179](https://zbmath.org/6720179)/`1375.32034`, *Symmetries in CR complexity theory*; [6499034](https://zbmath.org/6499034)/`1326.32006`, *CR complexity and hyperquadric maps*. 세 제목 모두 B002 밖이나 여기서 complexity는 P/NP 직접 역할로 확인되지 않았다. |
| 33 | `cc:33 & ti:"computation of special functions"` | 200; 10/3 | **search_no_candidate_after_review:** `3740651`, *The computation of special functions*의 P 대 NP 역할은 미확정이다. |

14의 판본 대조에는 `GET https://export.arxiv.org/api/query?id_list=0908.1932`도 HTTP 200으로 실행했다. `arXiv:0908.1932v2`, Ketan D. Mulmuley, *On P vs. NP, Geometric Complexity Theory, Explicit Proofs and the Complexity Barrier*, `cs.CC`를 반환했다. [arXiv record](https://arxiv.org/abs/0908.1932v2). 이는 preprint 식별일 뿐 peer-review·타당성 판정이 아니다.

- 실행 분야: **23/23**. 최종 fielded query 성공 23, 실패 0, 유효한 200의 0-result는 0.
- 새 후보 분야: **3** (`01`, `03`, `14`). `search_no_candidate_after_review`: 20.
- 최초 실패 시도는 `00` 두 번, `22`, `32`에 있었으나 모두 다른 유효한 fielded query로 좁혀 회복했다. 실패를 결과 없음으로 바꾸지 않았고, 재실행 결과만 최종 처분에 썼다.

다음 단계는 새 후보 3개와 미확정 반환 record를 초록·공식 원문/출판처 페이지에서 건별 대조하는 일이다. 이 보고서는 최종 핵심층이나 `covered`를 부여하지 않는다.
