# B002 공개 누락 검색: MSC 34–65 (재실행)

조회일: 2026-09-04 KST  
상태: **23개 분야 재실행 완료; `covered`·최종 핵심층 승인 아님.**

## 정정 경계

이 판본은 앞선 `cc:*<분야>` 및 bare keyword 질의를 근거에서 제거한다. 그 질의의 HTTP 404는 `execution_bool=false`, `total=null`이므로 0건이나 후보 부재를 뜻하지 않는다. 이 보고서에는 `cc:<두 자리 분야>`와 명시적 `ti:` 또는 `ab:` 필드를 쓴 재실행만 남긴다.

양성 대조로 zbMATH Open document API에서 다음 세 질의를 실행했다. 모두 HTTP 200, `execution_bool=true`, `returned=3`이었다.

| 양성 대조 query | total |
|---|---:|
| `cc:52 & ti:computational` | 168 |
| `cc:52 & ab:computational` | 1,064 |
| `cc:52 & (ti:computational | ti:algorithm*)` | 981 |

기본 endpoint는 [zbMATH Open document search API](https://api.zbmath.org/v1/document/_search)다. 모든 재실행은 `results_per_page=3`을 붙였고, 조회창은 2026-09-04 21:38–21:46 KST다. endpoint 전체는 `https://api.zbmath.org/v1/document/_search?search_string=<아래 query의 URL 인코딩>&results_per_page=3`이다. PDF·인증 DB·크리덴셜은 사용하지 않았다.

후보는 (1) 실제 API 반환에 식별자·제목·유형이 있고, (2) B002 후보 JSONL의 정규화 제목과 다시 대조해 같은 제목의 B002 레코드가 없고, (3) 제목 또는 공개 원 레코드의 범위가 그 분야의 계산·계산가능성·복잡도 경계를 실제로 가리킬 때만 남겼다. 순위·인용 수는 판정에 쓰지 않았다.

## 1. 23개 분야의 fielded zbMATH 실행

| MSC | 최종 fielded query | HTTP / execution_bool | total / returned | 검토 처분 |
|---|---|---|---:|---|
| 34 | `cc:34 & ti:computability` | 200 / true | 15 / 3 | 초기 경계 후보 |
| 35 | `cc:35 & ti:complexity` | 200 / true | 190 / 3 | 초기 경계 후보 |
| 37 | `cc:37 & ti:computability` | 200 / true | 47 / 3 | 초기 경계 후보 |
| 39 | `cc:39 & ti:complexity` | 200 / true | 40 / 3 | 초기 경계 후보 |
| 40 | `cc:40 & ti:complexity` | 200 / true | 11 / 3 | `search_no_candidate_after_review` |
| 41 | `cc:41 & ti:complexity` | 200 / true | 124 / 3 | arXiv 보조 후보 유지 |
| 42 | `cc:42 & ti:"Fourier spectrum" & ti:Boolean` | 200 / true | 3 / 3 | 초기 경계 후보 |
| 43 | `cc:43 & ti:complexity` | 200 / true | 10 / 3 | `search_no_candidate_after_review` |
| 44 | `cc:44 & ti:complexity` | 200 / true | 11 / 3 | 초기 경계 후보 |
| 45 | `cc:45 & ti:complexity` | 200 / true | 64 / 3 | 초기 경계 후보 |
| 46 | `cc:46 & ti:complexity` | 200 / true | 111 / 3 | 초기 경계 후보 |
| 47 | `cc:47 & ti:complexity` | 200 / true | 110 / 3 | 초기 경계 후보 |
| 49 | `cc:49 & ti:complexity` | 200 / true | 171 / 3 | 초기 경계 후보 |
| 51 | `cc:51 & ti:complexity` | 200 / true | 43 / 3 | 초기 경계 후보 |
| 52 | `cc:52 & ti:"extension complexity"` | 200 / true | 14 / 3 | 초기 직접 접점 후보 |
| 53 | `cc:53 & ti:"geometric complexity"` | 200 / true | 4 / 3 | `search_no_candidate_after_review` |
| 54 | `cc:54 & ti:computability` | 200 / true | 26 / 3 | 초기 경계 후보 |
| 55 | `cc:55 & ti:computational` | 200 / true | 59 / 3 | arXiv 보조 후보 유지 |
| 57 | `cc:57 & ti:computational` | 200 / true | 62 / 3 | 초기 경계 후보 |
| 58 | `cc:58 & ti:computational` | 200 / true | 44 / 3 | `search_no_candidate_after_review` |
| 60 | `cc:60 & (ti:pseudorandom* | ti:derandom*)` | 200 / true | 61 / 3 | 초기 직접 접점 후보 |
| 62 | `cc:62 & ti:"statistical-computational"` | 200 / true | 6 / 3 | 초기 경계 후보 |
| 65 | `cc:65 & ti:"information-based complexity"` | 200 / true | 16 / 3 | 초기 경계 후보 |

34·35·37·39에는 먼저 `cc:<분야> & (ti:computational | ti:algorithm*)`도 실행했다. total은 각각 2,055·4,751·1,481·193으로 넓었으므로 위 표의 더 좁은 `ti:computability`/`ti:complexity`로 다시 질의했다. 42·62·65도 첫 fielded 질의가 각각 11,113·5,648·1,467건으로 넓어서, 위 표의 title phrase 질의로 3·6·16건까지 좁혔다. 이 단계에서는 반환 3건의 순위로 부재를 결론내리지 않는다.

`search_no_candidate_after_review`는 위 query가 성공했고 실제 반환 세 건을 제목·유형·B002 중복에 대해 검토했으나, 이 초기 단계의 계산/P vs NP 경계 후보 조건을 충족한 것이 없었다는 뜻이다. 분야 전체의 부재가 아니다.

## 2. B002 밖 초기 후보

각 줄의 B002 대조 결과는 제목 일치 0건이다. 역할은 초기 판독·공개 판본 대조의 우선순위일 뿐, 원문 판독·수학적 타당성 검증·최종 핵심층 채택이 아니다.

| MSC | 실제 공개 레코드 | 유형·역할과 선정 근거 |
|---|---|---|
| 34 | Zbl `1137.68025`, *Computability with polynomial differential equations* (2008), DOI [10.1016/j.aam.2007.02.003](https://doi.org/10.1016/j.aam.2007.02.003) | journal article. 다항 미분방정식과 computability를 제목으로 직접 결합한 ODE-계산가능성 경계 후보. |
| 35 | Zbl `1458.53095`, *Complexity of parabolic systems* (2020), DOI [10.1007/s10240-020-00117-x](https://doi.org/10.1007/s10240-020-00117-x) | journal article. PDE의 “complexity”가 P vs NP 복잡도와 같은 뜻인지는 원문 판독 전 미확정인 경계 후보. |
| 37 | Zbl `0821.68053`, *Computability with low-dimensional dynamical systems* (1994), DOI [10.1016/0304-3975(94)90229-1](https://doi.org/10.1016/0304-3975(94)90229-1) | journal article. 동역학계와 계산가능성의 직접 접점 후보. |
| 39 | Zbl `1014.37003`, *Maximal pattern complexity for discrete systems* (2002), DOI [10.1017/S0143385702000585](https://doi.org/10.1017/S0143385702000585) | journal article. discrete system의 complexity 개념을 다루는 차분/동역학 경계 후보; P vs NP 직접성은 미확정. |
| 41 | arXiv `1806.06290`, *Average-Case Lower Bounds and Satisfiability Algorithms for Small Threshold Circuits* (2018), [원 레코드](https://arxiv.org/abs/1806.06290) | preprint, primary `cs.CC`. threshold circuit의 평균 경우 하계와 SAT 알고리즘을 함께 명시하므로 회로복잡도 장벽 후보. |
| 42 | Zbl `1212.42017`, *On the Fourier spectrum of symmetric Boolean functions* (2009), DOI [10.1007/s00493-009-2310-z](https://doi.org/10.1007/s00493-009-2310-z); arXiv `1407.3500`도 [재검증](https://arxiv.org/abs/1407.3500)됨 | journal article / preprint. Boolean 함수 Fourier spectrum·sparsity의 계산복잡도 교량 후보. 두 레코드는 별도 작업 후보이며 관계는 미확정. |
| 44 | Zbl `1005.82035`, *On the computational complexity of determining polyatomic structures by X-rays* (2000), DOI [10.1016/S0304-3975(97)00298-3](https://doi.org/10.1016/S0304-3975(97)00298-3) | journal article. 변환·역문제 맥락에서 계산복잡도를 명시하는 경계 후보. |
| 45 | Zbl `0920.65090`, *Monte Carlo complexity of global solution of integral equations* (1998), DOI [10.1006/jcom.1998.0471](https://doi.org/10.1006/jcom.1998.0471) | journal article. 적분방정식 해법의 Monte Carlo complexity 후보. |
| 46 | Zbl `1164.68006`, *Complexity measures of sign matrices* (2007), DOI [10.1007/s00493-007-2160-5](https://doi.org/10.1007/s00493-007-2160-5) | journal article. sign matrix complexity의 함수해석/이산 복잡도 교량 후보. |
| 47 | Zbl `0746.65049`, *Degeneration and complexity of bilinear maps: Some asymptotic spectra* (1991), DOI [10.1515/crll.1991.413.127](https://doi.org/10.1515/crll.1991.413.127) | journal article. bilinear map의 complexity를 명시하므로 연산자/대수 복잡도 경계 후보. |
| 49 | Zbl `0576.90083`, *Informational complexity of mathematical programming* (1983) | journal article. 수학적 계획법의 정보복잡도 후보; P vs NP 직접 결론은 미확정. |
| 51 | Zbl `0593.68035`, *Computational complexity of art gallery problems* (1986), DOI [10.1109/TIT.1986.1057165](https://doi.org/10.1109/TIT.1986.1057165) | journal article. 기하 문제의 계산복잡도 후보. |
| 52 | Zbl `1328.68081`, *A generalization of extension complexity that captures P* (2015), DOI [10.1016/j.ipl.2015.02.005](https://doi.org/10.1016/j.ipl.2015.02.005); arXiv `1402.5950`도 [재검증](https://arxiv.org/abs/1402.5950)됨 | journal article / preprint. extension complexity와 P의 관계를 제목으로 명시하는 직접 접점 후보. 두 판본의 동일 작업 여부·관계는 후속 판본 대조가 필요하다. |
| 54 | Zbl `1071.03027`, *Computability on subsets of metric spaces* (2003), DOI [10.1016/S0304-3975(02)00693-X](https://doi.org/10.1016/S0304-3975(02)00693-X) | journal article. 일반위상/분석의 계산가능성 경계 후보. |
| 55 | arXiv `1210.1429`, *Computing Homology and Persistent Homology Using Iterated Morse Decomposition* (2012), [원 레코드](https://arxiv.org/abs/1210.1429) | preprint, primary `math.AT`. 계산/지속 호몰로지의 재진입 후보이며 P vs NP 직접성은 미확정. |
| 57 | Zbl `1065.68667`, *The computational complexity of knot and link problems* (1999), DOI [10.1145/301970.301971](https://doi.org/10.1145/301970.301971) | journal article. 매니폴드·매듭 문제의 계산복잡도 후보. |
| 60 | Zbl `0816.60070`, *Derandomized graph products* (1995), DOI [10.1007/BF01277956](https://doi.org/10.1007/BF01277956) | journal article. 확률·derandomization의 직접 접점 후보. |
| 62 | Zbl `1539.62179`, *Statistical-computational trade-offs in tensor PCA and related problems via communication complexity* (2024), DOI [10.1214/23-AOS2331](https://doi.org/10.1214/23-AOS2331); arXiv `2005.08099`도 [재검증](https://arxiv.org/abs/2005.08099)됨 | journal article / preprint. statistical-computational trade-off·communication complexity의 통계 경계 후보. 두 레코드는 별도 작업 후보이며 관계는 미확정. |
| 65 | Zbl `0758.65044`, *Information-based complexity of linear operator equations* (1992), DOI [10.1016/0885-064X(92)90013-2](https://doi.org/10.1016/0885-064X(92)90013-2) | journal article. 수치 연산자방정식의 information-based complexity 후보. |

arXiv 보조 후보는 2026-09-04 21:46 KST에 공식 Atom API `id_list=1806.06290,1407.3500,1208.0526,1402.5950,1210.1429,2005.08099,1606.01424&max_results=10`으로 재검증했다. HTTP 200, `total=7`, `returned=7`이었고, 위 표의 41·42·52·55·62 레코드 제목과 primary category를 다시 확인했다. 49의 `1208.0526`과 65의 `1606.01424`도 응답에는 있었지만, 정확한 zbMATH 후보가 있으므로 중복 표에는 싣지 않았다.

## 3. 현재 처분과 한계

| 처분 | 분야 수 | 분야 |
|---|---:|---|
| B002 밖 초기/경계 후보 발견 | 19 | 34, 35, 37, 39, 41, 42, 44, 45, 46, 47, 49, 51, 52, 54, 55, 57, 60, 62, 65 |
| `search_no_candidate_after_review` | 4 | 40, 43, 53, 58 |
| 재실행 API 실패 | 0 | — |

**관찰:** 재실행한 23개 zbMATH 질의는 전부 HTTP 200과 `execution_bool=true`였다. 42·62·65의 넓은 첫 질의는 각각 더 좁은 title phrase 질의로 재실행해 3·6·16건으로 줄였다.

**추론:** B002의 `-00/-01/-02` 상위 100 표본은 표준서 중심이어서, 이번 재실행은 논문형 계산·계산가능성·복잡도 경계 후보를 다수 드러냈다. 이는 `covered` 판정이나 후보의 P vs NP 직접 관련성 확정이 아니다. 특히 35·39·44·49의 “complexity”는 동명이의 가능성이 있으므로 원문·초록·venue를 다시 읽어 의미를 판정해야 한다.

**다음 단계:** 후보마다 공식 출판 판본/정정·후속 판본과 초록 또는 원문을 대조하고, 직접 후보는 전후방 인용과 원 성과·장벽·비판을 별도 기록한다. 이 파일만으로 어느 분야도 `covered`로 바꾸지 않는다.
