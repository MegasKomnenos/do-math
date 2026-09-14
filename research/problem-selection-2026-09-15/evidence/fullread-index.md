# 전문 독해 목록과 최종 대조

이번 보완에서는 **논문 11편과 발표자료 1개, 총 234쪽**을 본문·각주·참고문헌 또는 마지막 슬라이드까지 읽었다. 주 에이전트가 S1·S2를 직접 읽었고, 나머지는 표에 적힌 병행 독해 담당이 전문을 읽었다. 주 에이전트는 반환된 정리·적용 조건·발견을 취합하고, 중요한 쟁점은 원문과 재대조했다. 모든 원문을 주 에이전트 혼자 완독했다는 뜻은 아니다.

전문 독해와 모든 정리의 독립 인증은 다르다. 이 기록은 실제 읽은 판본·구간, 선정 문제에 직접 사용할 증명의 대조, 확인한 오류와 적용 한계를 남긴다. 기계 검사는 파일 해시·쪽수·보고된 페이지 범위의 완전성을 확인하며, 그것만으로 독해나 수학적 정확성을 증명하지 않는다.

## 읽은 원문

| ID | 원문·판본 | 쪽수 | 독해 담당 | 상세 기록 |
|---|---|---:|---|---|
| S1 | [Statistics on ℓ-interval parking functions](https://jeremymartinmath.github.io/papers/StatisticsLIPF.pdf), 저자 공개본 | 25 | 주 에이전트 | [핵심](fullread-core.md) |
| S2 | [Interval and ℓ-interval Rational Parking Functions](https://dmtcs.episciences.org/14279/pdf), 저널 PDF·표지 arXiv v5 | 29 | 주 에이전트 | [핵심](fullread-core.md) |
| S3 | [Parking functions and Łukasiewicz paths](https://www.dmlett.com/archive/v14/DML24_v14_pp77-84.pdf), 저널 PDF | 8 | fullread_background | [관련 결과](fullread-background.md) |
| S4 | [Celano, Permutation Patterns 2025 발표](https://sites.cs.st-andrews.ac.uk/pp25/program/slides/celano.pdf) | 36 | fullread_background | [관련 결과](fullread-background.md) |
| S5 | [A Note on the Log-Concavity of Parking Functions](https://arxiv.org/pdf/2412.19783v1), v1 | 4 | fullread_background | [관련 결과](fullread-background.md) |
| S6 | [Inversions in parking functions](https://arxiv.org/pdf/2508.11587v1), v1 | 30 | fullread_followups | [후속 원문](fullread-followups.md) |
| S7 | [Counting ℓ-interval Fubini rankings through their parking outcome](https://arxiv.org/pdf/2603.00693v1), v1 | 21 | fullread_followups | [후속 원문](fullread-followups.md) |
| S8 | [Luck and magic for Pitman–Stanley polytopes and parking functions](https://arxiv.org/pdf/2603.19194v2), v2 | 33 | fullread_followups | [후속 원문](fullread-followups.md) |
| S9 | [Parking functions, Smirnov words, and noncrossing Chow polynomials](https://arxiv.org/pdf/2609.05131v1), v1 | 18 | fullread_followups | [후속 원문](fullread-followups.md) |
| D1 | [Huh, h-Vectors of matroids and logarithmic concavity](https://arxiv.org/pdf/1201.2915v2), v2 | 9 | fullread_background | [관련 결과](fullread-background.md) |
| D2 | [Bradt 외, Unit interval parking functions and the r-Fubini numbers](https://arxiv.org/pdf/2401.06937v1), v1 | 11 | candidate_research | [직접 기초](fullread-foundations.md) |
| D3 | [Konheim–Weiss, An Occupancy Discipline and Applications](https://sites.math.rutgers.edu/~zeilberg/akherim/KronheimWeiss1966.pdf), 기관 공개 스캔 | 10 | candidate_research | [직접 기초](fullread-foundations.md) |

D3의 쪽수는 서지 표지 1쪽을 포함한다. Bradt의 출판본 15쪽은 별도로 확보해 핵심 정리의 2쪽을 대조했으며 위 완독 수량에 중복으로 넣지 않았다. 각 논문이 다시 인용하는 책·논문 전부를 재귀적으로 읽은 것은 아니다. 선정 문제의 발판과 적용 경계를 확인하는 직접 원문을 위 목록으로 명시했다.

## 파일과 출처의 보존

[기계 판독 목록](fullread-index.json)에 원문 URL·로컬 PDF·전문 텍스트·해시·전체 독해 구간이 있다. 원문과 추출물은 `originals/` 아래에 로컬 보존하며 Git에서 제외한다. 기계 추출에서 수식이 깨진 곳은 담당 기록의 PDF 렌더 대조로 보완했다. 특히 D3의 기계 텍스트는 검색용이며 수식은 렌더와 아래 독해 기록을 함께 읽는다.

최초 S1~S4는 scholarly MCP로 확보했다. 추가 원문은 MCP의 arXiv 요청 제한·timeout 및 브라우저 오류를 확인한 뒤 공식 arXiv 또는 기관 공개 PDF로 보완한 경우가 있다. Bradt 출판본의 MCP 확보와 부분 대조도 별도로 기록했다. 실제로 성공한 경로와 오류는 각 담당 JSON에 남겼으며, 보조 경로로 받은 PDF를 MCP 성공으로 표시하지 않는다.

## 검토 결과와 반영

선정 문제의 양화와 최대 변위·누적 개수·정확 개수의 구별은 유지한다. 읽은 논문이 제공하는 정리 사슬에서 원 문제의 해결은 확인하지 못했다. 문제의 난도는 여전히 근거에 따른 추정이며 해결 보장이 아니다.

시작 자료에는 다음을 반영했다.

1. 점화식에 필요한 모든 ℓ≥0의 누적 개수와 빈 목록을 명시하고, 좌우 분해에서 빈자리와 평행이동의 역할을 설명했다.
2. 단위 구간 블록 정리의 직접 원천 Bradt와, 무제한 순열별 곱의 직접 원천 Konheim–Weiss를 연결했다.
3. S1의 제한 2→1 자리 보존 대응, 인접 역전 제거의 단조성, S7의 Fubini 하위족에서 증가 구간별 분해를 발판으로 추가했다.
4. S1·S2의 다섯 인쇄 주장에 대한 구체적 반례, S3의 가정 생략, S4의 잘못된 예와 상한, 후속 논문의 표기·범위 결함을 기록했다. 이를 선정 추측의 반증과 구별했다.
5. 순열 불변성을 요구하는 대상이 집합인지 통계인지 구별해 S6 평균화 정리의 적용 설명을 교정했다. ‘간접 연결을 찾지 못함’을 ‘어떤 연결도 불가능함’으로 쓰지 않았다.
6. 다른 컴퓨터에서 원문만 다시 받아도 재현 검사에 필요한 원 회수 기록을 사용할 수 있도록, 최초 네 MCP manifest의 정확한 바이트를 함께 보존했다.

[원문 주장 반례 재현](source-findings.json), [공개 수치·출처 검사](reference-validation.json), [독립된 빈 작업공간에서의 재현](portability-validation.json)을 구별한다. 이 검토는 연구 준비를 개선한 것이며, 선정 문제의 풀이를 시작하거나 새로운 n의 단봉성을 시험한 작업이 아니다.
