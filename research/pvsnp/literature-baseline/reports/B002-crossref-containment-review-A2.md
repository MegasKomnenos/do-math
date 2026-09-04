# B002 Crossref title-containment 검토 A2

대상은 DOI 오름차순 source slice 11–20이다. 후보 BibTeX의 저자·ISBN·연도·권/부분과 Crossref raw의 author·ISBN·container·year/type를 대조했다. PDF·인증·크리덴셜은 사용하지 않았다.

| DOI · MR | 대조 필드 | 처분 |
|---|---|---|
| `10.1007/978-1-4419-6351-2` · MR2682846 | Schlick 2010, candidate ISBN `978-1-4419-6350-5`, vol.21; Crossref 같은 저자·연도·Interdisciplinary Applied Mathematics·ISBN `9781441963505/3512`, subtitle 생략 | `same_work_title_variant` |
| `10.1007/978-1-4419-7049-7` · MR2744149 | Taylor 2011 PDE III, candidate ISBN `…7048-0`, vol.117; Crossref 같은 저자·연도·Applied Mathematical Sciences·ISBN `9781441970480/0497`, nonlinear subtitle 생략 | `same_work_title_variant` |
| `10.1007/978-1-4612-0985-0` · MR1033497 | Zeidler 1990 *… II/A*, ISBN `0-387-96802-4`; Crossref 같은 저자·연도이고 공식 Springer record가 이 DOI를 II/A에 배정 | `same_work_title_variant` |
| `10.1007/978-1-4612-0985-0` · MR1033498 | Zeidler 1990 *… II/B*, ISBN `0-387-97167-X`; 공식 Springer record는 II/B에 별도 DOI `10.1007/978-1-4612-0981-2`를 배정 | `different_volume_or_part_identifier_conflict` |
| `10.1007/978-1-4612-1088-7` · MR781125 | Berndt 1985 *Ramanujan’s Notebooks Part I*, ISBN `0-387-96110-0`; Crossref 같은 저자·연도·두 13자리 ISBN의 포괄 title | `component_of_candidate_work` |
| `10.1007/978-1-4612-1100-6` · MR807945 | Dubrovin–Fomenko–Novikov 1985 *Modern Geometry Part II*, vol.104; Crossref 같은 저자·연도·GTM·ISBN | `component_of_candidate_work` |
| `10.1007/978-1-4612-1624-7` · MR1486573 | Berndt 1998 *Ramanujan’s Notebooks Part V*, ISBN `0-387-94941-0`; Crossref 같은 저자·연도·ISBN의 포괄 title | `component_of_candidate_work` |
| `10.1007/978-1-4612-4420-2` · MR1080172 | van der Waerden 1991 *Algebra Vol. I*, ISBN `0-387-97424-5`; Crossref 같은 저자·연도·ISBN의 포괄 title | `component_of_candidate_work` |
| `10.1007/978-1-4612-4474-5` · MR1076994 | Dubrovin–Fomenko–Novikov 1990 *Modern Geometry Part III*, vol.124; Crossref 같은 저자·연도·GTM·ISBN | `component_of_candidate_work` |
| `10.1007/978-1-4612-4552-0` · MR1033992 | McKenzie–Valeriote 1989, candidate ISBN `0-8176-3439-8`, Progress in Mathematics 79; Crossref 같은 저자·연도·series·ISBN, 관사만 생략 | `same_work_title_variant` |
| `10.1007/978-1-4612-4566-7` · MR932255 | Zeidler 1988 *… IV*, ISBN `0-387-96499-1`; Crossref 같은 저자·연도·ISBN의 포괄 title | `component_of_candidate_work` |

처분 합계: `same_work_title_variant=4`, `component_of_candidate_work=6`, `different_volume_or_part_identifier_conflict=1`, 합계=11 candidate links. source slice DOI 집합과 보고 DOI 집합 대칭차는 0이며 source DOI 수는 10이다.
