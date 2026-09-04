# B001+B002 통합 후보·관계 색인 검사

검사일: 2026-09-04 KST

판정: **통과.** B001 20,429개 source-ID 후보와 B002 5,472개 MR 후보를 같은 MR 기본키에서만 합쳐 25,793개 안전 후보 참조를 만들었다. B001·B002의 관계 후보 2,756묶음도 하나의 member 형식으로 연결했다.

## 후보

| 항목 | 수 |
|---|---:|
| B001 후보 | 20,429 |
| B002 후보 | 5,472 |
| 같은 MR overlap | 108 |
| 안전한 기본키 합집합 | **25,793** |

겹친 MR 108건은 제목·creator·연도·DOI·ISBN 다섯 정규화 필드가 각각 108/108 일치했다. B002 record를 primary reference로 두되 B001 query·rank·원시 파일 provenance는 삭제하지 않는다. 같은 DOI만 가진 다른 source record는 통합 후보 수에서 빼지 않았다.

## 관계

| 관계 후보 | 묶음 |
|---|---:|
| `same_doi_candidate` | 1,906 |
| `same_bibliographic_fingerprint_candidate` | 496 |
| `edition_or_version_candidate` | 354 |
| **합계** | **2,756** |

모든 relation member는 통합 후보 25,793개 중 실제 ID를 가리키며 누락 참조는 0이다. DOI/fingerprint/edition 관계는 원 상태 `unverified_candidate`를 유지한다. 이 파일은 B002에서 이미 판정한 DOI 관계 결정이나 B001 direct-title 검토 결정을 덮어쓰지 않는다.

생성기 검사 4건이 통과했다. 같은 입력으로 두 번 재생성한 candidate·relation·manifest SHA-256은 모두 같았다. 정본 계수와 입력·출력 해시는 [`../manifests/B001-B002-unified.json`](../manifests/B001-B002-unified.json), 계약은 [`../catalog/B001-B002-unified-contract.md`](../catalog/B001-B002-unified-contract.md)에 있다.
