# B001+B002 통합 후보 참조 계약

## 안전한 동일성

B001과 B002의 후보를 합칠 때 같은 MathSciNet MR 기본키만 동일 후보로 취급한다. 두 catalog에서 같은 MR인 108건은 정규화 제목·creator·연도·DOI·ISBN도 모두 일치한다. 통합 record는 B002를 primary로 가리키고 B001의 검색 provenance는 B001 후보 record에 그대로 남긴다.

다른 자료원의 DOI·정규화 제목·저자·연도 일치는 관계 신호다. B002 공개 감사에서 wrong DOI, chapter DOI, set DOI와 다른 권 DOI를 실제 확인했으므로, 이 신호로 source record나 판본을 합쳐 없애지 않는다.

## 구조

- `B001-B002-candidates.jsonl`은 원 후보를 복제하지 않는 참조 index다. `global_candidate_id`, primary catalog record, 모든 catalog record 참조와 primary 정규화 요약을 둔다.
- `B001-B002-relations.jsonl`은 B001 교차-source 관계와 B002 관계 후보를 같은 member 참조 형식으로 합친다. 원 relation ID·type·status·signal을 보존한다.
- 원 서지·content flag·분야/검색 rank provenance는 각각 `B001-candidates.jsonl`, `B002-candidates.jsonl`에서 읽는다.

통합은 문헌 선별이나 판본 관계 승인이 아니다. 관계 상태가 `unverified_candidate`이면 공식 출판 record와 실제 내용을 검토하기 전에는 병합·삭제하지 않는다.
