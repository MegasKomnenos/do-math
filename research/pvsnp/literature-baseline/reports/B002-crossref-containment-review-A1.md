# B002 Crossref title-containment 검토 A1

대상은 DOI 오름차순 source slice 1–10이다. 후보 BibTeX의 저자·ISBN·연도·권/판과 Crossref raw의 author·ISBN·container·year/type를 실제 비교했다. DOI URL은 Crossref가 반환한 공식 record URL이다. PDF·인증·크리덴셜은 사용하지 않았다.

| DOI · MR | 대조 필드 | 처분 |
|---|---|---|
| `10.1002/0471722065` · MR1788152 | Kotz–Balakrishnan–Johnson, 2000, 2판; candidate ISBN `0-471-18387-3`와 Crossref ISBN `9780471183877`의 13자리 대응, Crossref는 Wiley series와 같은 저자를 기록. candidate `Vol. 1`은 포괄 title의 권 | `component_of_candidate_work` |
| `10.1002/9780470277980` · MR2382998 | Cooke, candidate 2008/ISBN `9780470259528`; Crossref Cooke, 2007, ISBN `9780470259528/9780470277980`, subtitle *Its Nature, Origins, and Uses* | `same_work_title_variant` |
| `10.1007/0-306-48332-7` · MR1865755 | candidate *Encyclopedia of Optimization* I–VI, 2001, ISBN `0-7923-6932-7`; Crossref 2001 Springer reference-book, ISBN `9780792369325/9780306483325` | `same_work_title_variant` |
| `10.1007/3-540-12732-1` · MR725167 | Kraus 1983, ISBN `3-540-12732-1`, LNP vol. 190; Crossref 1983 Springer LNP와 ISBN/포괄 subtitle 일치 | `same_work_title_variant` |
| `10.1007/978-0-387-21822-9` · MR2026891 | Ewens 2004, 2판, I, candidate print ISBN `0-387-20191-2`; Crossref Ewens 2004, Interdisciplinary Applied Mathematics, ISBN `9780387218229` | `component_of_candidate_work` |
| `10.1007/978-0-387-49835-5` · MR2371524 | Daley–Vere-Jones 2008, 2판, II, candidate ISBN `978-0-387-21337-8`; Crossref 같은 저자·연도·Probability and Its Applications 및 ISBN `9780387213378/9780387498355` | `component_of_candidate_work` |
| `10.1007/978-0-8176-4727-8` · MR2500203 | Romanovski–Shafer 2009, candidate ISBN `978-0-8176-4726-1`; Crossref 같은 두 저자·연도·ISBN `9780817647261/9780817647278`; subtitle만 생략 | `same_work_title_variant` |
| `10.1007/978-0-85729-021-2` · MR2723325 | Einsiedler–Ward 2011, candidate ISBN `978-0-85729-020-5`; Crossref 같은 저자·연도·ISBN `9780857290205/9780857290212`; *with a view towards number theory*가 생략 | `same_work_title_variant` |
| `10.1007/978-1-4020-5141-8` · MR2356157 | Hazewinkel–Gubareni–Kirichenko 2007, *Vol. 2*, ISBN `978-1-4020-5140-1`; Crossref 2007 Springer Mathematics and Its Applications, ISBN `9781402051401` | `component_of_candidate_work` |
| `10.1007/978-1-4020-8743-1` · MR3134868 | Oñate 2013 *… linear statics, Vol. 2*, candidate ISBN `978-1-4020-8742-4/8743-1`; Crossref 같은 저자·연도·series·두 ISBN | `component_of_candidate_work` |

## 검산

처분 합계: `same_work_title_variant=5`, `component_of_candidate_work=5`, 나머지=0, 합계=10. source slice DOI 집합과 보고 DOI 집합의 대칭차는 0이며 candidate link 수는 10이다. 권 표기가 있는 다섯 행은 ISBN·저자·연도가 일치해도 Crossref 포괄 record와 후보 권을 같은 단일 제목으로 병합하지 않고 component로 기록했다.
