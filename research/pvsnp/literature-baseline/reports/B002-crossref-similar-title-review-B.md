# B002 Crossref similar-title 상세 검토 B

대상은 지정된 16 DOI–MR 행이다. 후보 BibTeX title·저자·연도와 현행 Crossref raw의 returned DOI, title, type, publisher, ISBN/container/year를 대조했다. Crossref `url`은 공식 DOI record 경로로 사용했다. PDF·인증·크리덴셜은 사용하지 않았다.

| MR | DOI | 후보 ↔ Crossref의 판정 근거 | 처분 |
|---|---|---|---|
| MR3364185 | `10.1007/978-3-319-16092-4` | Tkachuk 2015 *A Cp-theory problem book*; 같은 저작의 2011·2014 record와 DOI/연도만 다름 | `same_work_reissue_or_edition` |
| MR814495 | `10.1007/978-3-662-02427-0` | Hackbusch 1985 *Multigrid methods and applications* ↔ *Multi-Grid …*; 저자·연도·출판처 일치 | `same_work_title_variant` |
| MR2815182 | `10.1007/978-94-007-0840-2` | Mundici 2011 Łukasiewicz/MV-algebras ↔ Crossref의 Unicode 표기 | `same_work_title_variant` |
| MR1461937 | `10.1007/bf00376449` | Franchella 1997 König infinity lemma; Crossref의 문자 encoding만 다름 | `same_work_title_variant` |
| MR1608967 | `10.1007/bf02634165` | Zabrodin 1997 Hirota difference equations ↔ curly apostrophe 표기 | `same_work_title_variant` |
| MR932459 | `10.1007/bfb0007371` | Francis 1987 H-infinity control ↔ H∞ 표기 | `same_work_title_variant` |
| MR836132 | `10.1007/bfb0075405` | Bruner–May–McClure–Steinberger 1986 H-infinity ring spectra ↔ H∞ 표기 | `same_work_title_variant` |
| MR1794807 | `10.1007/s003650010026` | Petrushev의 후보는 “research problems 2001-1”, Crossref는 “Research Problems 2000-3”; 저자·주제는 같지만 문제 번호가 다름 | `related_but_distinct_work` |
| MR2196098 | `10.1007/s10659-005-4738-8` | Ciarlet 2005 differential geometry/elasticity; applications 단복수 차이만 존재 | `same_work_title_variant` |
| MR740342 | `10.1016/0370-1573(84)90106-6` | Makhan'kov–Fedyanin 1984 quasi-one-dimensional condensed-matter theory; Crossref의 non-linear/hyphen 표기 차이 | `same_work_title_variant` |
| MR2035095 | `10.1016/s1570-7954(03)80060-8` | Kuku 2003 K0/K1/K2 functors; Crossref의 subscript 표기 차이 | `same_work_title_variant` |
| MR4354541 | `10.1017/9781108936880` | Riehl–Verity 2022 infinity-category theory; ∞ TeX/Unicode 표기 차이 | `same_work_title_variant` |
| MR800853 | `10.1017/cbo9780511661914` | Schofield 1985 skew fields 저작; candidate singular/record plural 표기 차이 | `same_work_title_variant` |
| MR2356959 | `10.1017/cbo9780511721373` | Peszat–Zabczyk 2007 Lévy noise; accent 표기 차이 | `same_work_title_variant` |
| MR1482800 | `10.1017/cbo9780511896064` | Borel 1997 automorphic forms on SL2(R); TeX/괄호 표기 차이 | `same_work_title_variant` |
| MR2538715 | `10.1017/is008008012jkt087` | Hazrat–Vavilov 2009 Bak's K-theory work; Crossref 공백 누락(`theK`) | `same_work_title_variant` |

## 검산

처분 합계: `same_work_title_variant=14`, `same_work_reissue_or_edition=1`, `related_but_distinct_work=1`, 나머지=0, 합계=16. 입력 16 DOI–MR 집합과 위 16행의 대칭차는 0이다. 특히 MR1794807은 유사 제목·저자만으로 같은 research-problem 번호를 병합하지 않았다.
