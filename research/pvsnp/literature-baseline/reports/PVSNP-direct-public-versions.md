# P vs NP 직접 9개 work의 공개 판본 대조

범위는 [`PVSNP-direct-foundations.md`](PVSNP-direct-foundations.md)의 9 work다. 출판 record와 공개 landing/metadata만 확인했으며 PDF를 내려받거나 원문을 완독하지 않았다. 공개 mirror가 있다는 사실만으로 출판본 동일성을 확정하지 않는다.

| work | 공식 출판 record | 공개 경로·유형 | 대조 범위와 처분 |
|---|---|---|---|
| CMI / Cook description | [CMI P vs NP](https://www.claymath.org/millennium/p-vs-np/) | [CMI problem-description PDF landing](https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf), 공식 공개 PDF, 12쪽 | Cook 명의·문제 표제·CMI 공식 문제 설명을 확인. 이는 원 논문 판본이 아니라 2000 problem description이다. `official_public_version_confirmed`. |
| Cook 1971 | [ACM STOC record](https://dl.acm.org/doi/10.1145/800157.805047), *The complexity of theorem-proving procedures*, Cook, 1971, pp.151–158 | [CMU landing/PDF link](https://www.cs.cmu.edu/~15455/resources/Cook1971-complx-thm-proof.pdf), 공개 course mirror | 표제·저자와 1971 work의 공개 경로는 확인했지만 ACM proceedings의 쪽수·typesetting·판권 페이지를 mirror와 대조하지 않았다. `public_version_not_confirmed`. |
| Levin 1973 | [MathNet record](https://www.mathnet.ru/eng/ppi914), Russian *Универсальные задачи перебора*, *PPI* 9(3), 1973, pp.115–116; 영어판 pp.265–266 | MathNet의 원문·영어 번역 공개 링크, 기관 repository/official record | MathNet이 저자 Levin, 접수일 1972-06-07, 러시아 원문·영어판의 별 쪽수를 명시한다. 번역은 별 판본이며 문장·용어 동등성은 미판독. `official_public_version_confirmed` (서지·판본 분리). |
| Karp 1972 | [Springer chapter/book record](https://link.springer.com/book/10.1007/978-1-4684-2001-2), *Reducibility among Combinatorial Problems*, pp.85–103, DOI `10.1007/978-1-4684-2001-2_9` | 공식 publisher landing만 | 저자·chapter title·쪽수는 공식 metadata로 확인. 합법 공개 저자/기관/repository full-version landing은 이번 경로에서 확인 못함. `public_version_not_confirmed`. |
| Ladner 1975 | [ACM JACM record](https://dl.acm.org/doi/10.1145/321864.321877), 22(1), 155–171 | 공식 publisher landing만 | title·저자·journal·권·쪽수·DOI를 확인. 공개 판본은 확인 못함. `public_version_not_confirmed`. |
| Baker–Gill–Solovay 1975 | [SIAM record](https://epubs.siam.org/doi/abs/10.1137/0204037), *SIAM J. Comput.* 4(4), 431–442 | 공식 abstract/landing만 | 저자·title·journal·권·쪽수·DOI를 확인. 공개 저자/기관 판본은 확인 못함. `public_version_not_confirmed`. |
| Razborov–Rudich 1997 | [Elsevier record](https://linkinghub.elsevier.com/retrieve/pii/S002200009791494X), *JCSS* 55(1), 24–35 | [Rudich public-paper landing](https://www.cs.cmu.edu/~rudich/papers/index.htm), 공개 PostScript 링크 | 저자 공개 목록이 *Natural Proofs* 공개 판본을 연결하는 것은 확인. Elsevier 출판판의 페이지·layout·version/date와 public PostScript의 동일성은 미대조. `public_version_not_confirmed`. |
| Aaronson–Wigderson 2008/2009 | [ACM TOCT record](https://dl.acm.org/doi/10.1145/1490270.1490272), 1(1), Article 2, 2:1–2:54 | [IAS author PDF landing](https://www.math.ias.edu/~avi/PUBLICATIONS/MYPAPERS/SCOTT/alg.pdf), [ECCC TR08-005 landing](https://eccc.weizmann.ac.il/eccc-reports/2008/TR08-005/Paper.pdf) | 공개 IAS/ECCC 판본의 title·두 저자와 2008 report 경로, ACM의 2009 journal metadata를 확인. STOC 731–740, ECCC, journal 54쪽은 자동 동일 판본이 아니라 preprint/proceedings/journal 관계다. `official_public_version_confirmed` (관계는 부분 확인). |
| Arora–Barak 2009 | [Cambridge book record](https://www.cambridge.org/core/books/computational-complexity/), *Computational Complexity: A Modern Approach*, 2009 | [저자/Princeton companion](https://theory.cs.princeton.edu/complexity/), 공개 Internet draft landing | companion은 저자 draft와 보조자료를 제공하고, 출판 2009 책은 B002 `MR2500087`의 저자·연도·ISBN·DOI와 일치한다. draft의 장/쪽/정리 좌표를 출판본에 전사하지 않았다. `official_public_version_confirmed` (별 draft 판본). |

## 집계와 한계

- 9/9 work를 처분했다.
- 공식 공개 판본 또는 공식 저자/기관 공개판의 판본 지위를 확인: 4 (`CMI`, `Levin`, `Aaronson–Wigderson`, `Arora–Barak`).
- 공개 경로는 있으나 출판본과의 동일성 미확정: 2 (`Cook`, `Razborov–Rudich`).
- 공식 출판 record만 확인, 공개 판본 미확정: 3 (`Karp`, `Ladner`, `Baker–Gill–Solovay`).

공개 PDF가 있는 경우에도 이 보고서는 landing/header/metadata까지만 확인했다. 정의·정리·가정·쪽수의 원문 판독과 출판판–공개판 line-by-line 대조는 후속 작업이다.
