# B002 Crossref similar-title 상세 검토 A

대상은 지정된 16 DOI–MR 행이다. 후보 BibTeX title·저자·연도와 현행 Crossref raw의 returned DOI, title, type, publisher, ISBN/container/year를 대조했다. DOI resolver는 해당 Crossref `url`을 공식 record 경로로 사용했다. PDF·인증·크리덴셜은 사용하지 않았다.

| MR | DOI | 후보 ↔ Crossref의 판정 근거 | 처분 |
|---|---|---|---|
| MR1891212 | `10.1002/9780470317006` | Kendall–Barden–Carne–Le, 1999 *Shape and shape theory* ↔ Wiley 1999 ISBN `9780470317006/9780471968238`, *Shape & Shape Theory*; `&` 표기 차이 | `same_work_title_variant` |
| MR1680267 | `10.1002/9780470317044` | Rolski et al., 1999 제목 ↔ Wiley 1999 ISBN `9780470317044/9780471959250`, *Insurance & Finance* | `same_work_title_variant` |
| MR719544 | `10.1007/0-387-32792-4` | Seneta 1981 *Nonnegative matrices and Markov chains* ↔ *Non-negative …*; hyphen만 다름 | `same_work_title_variant` |
| MR1402474 | `10.1007/3-540-76074-1` | van der Schaft 1996 `L2-gain` 저작; Crossref도 같은 저자·제목 | `same_work_title_variant` |
| MR2676219 | `10.1007/978-0-387-74315-8` | Featherstone 2008 *Rigid body dynamics algorithms* ↔ Crossref *Robot Dynamics Algorithms*; 같은 저자이나 표제·판 관계를 raw만으로 확정 못함 | `unresolved` |
| MR3112896 | `10.1007/978-0-8176-4652-3` | Saichev–Woyczyński, 2013 Volume 2 ↔ Crossref *… Volume 2* | `same_work_title_variant` |
| MR1353236 | `10.1007/978-0-8176-4757-5` | Başar–Bernhard, 1995 H-infinity/minimax 저작 ↔ Crossref H∞ 표기 | `same_work_title_variant` |
| MR2664620 | `10.1007/978-1-4419-1524-5_2` | Bergner 2010 chapter *A survey of (∞,1)-categories*; DOI suffix `_2`와 Crossref chapter title 일치 | `component_of_candidate_work` |
| MR3024898 | `10.1007/978-1-4419-7442-6` | Tkachuk 2011 *A Cp-theory problem book* ↔ Crossref *A Cp-Theory Problem Book* | `same_work_title_variant` |
| MR1844565 | `10.1007/978-1-4471-0507-7` | van der Schaft 2000 같은 `L2-gain` 저작; 1996 MR1402474와 별 DOI/연도라 판본·재발행 | `same_work_reissue_or_edition` |
| MR1201152 | `10.1007/978-1-4612-0327-8` | Dal Maso 1993 Γ-convergence ↔ Crossref Γ 표기 | `same_work_title_variant` |
| MR1162533 | `10.1007/978-1-4612-0383-4` | Adams–Barbasch–Vogan 1992 Langlands classification ↔ Crossref가 관사 생략 | `same_work_title_variant` |
| MR1151617 | `10.1007/978-1-4613-9200-2` | Howe–Tan 1992 *Nonabelian harmonic analysis* ↔ *Non-Abelian …* | `same_work_title_variant` |
| MR4866895 | `10.1007/978-3-031-69706-7_11` | Krityakierne–Thanatipanonda 2024 chapter; suffix `_11`, Crossref chapter title와 후보의 C-finite/C2-finite 표기 대응 | `component_of_candidate_work` |
| MR1388037 | `10.1007/978-3-0348-7762-6` | Amrein–Boutet de Monvel–Georgescu 1996 C0-groups/N-body 제목 ↔ Crossref C0/`N-Body` 표기 | `same_work_title_variant` |
| MR3243753 | `10.1007/978-3-319-04747-8` | Tkachuk 2014 *A Cp-theory problem book*; 2011 MR3024898과 같은 저작의 다른 DOI·연도 | `same_work_reissue_or_edition` |

## 검산

처분 합계: `same_work_title_variant=11`, `same_work_reissue_or_edition=2`, `component_of_candidate_work=2`, `unresolved=1`, 나머지=0, 합계=16. 입력 16 DOI–MR 집합과 위 16행의 대칭차는 0이다. `unresolved` 한 건은 출판처 판/ISBN·저자 record를 더 확인하기 전까지 자동 병합하지 않는다.
