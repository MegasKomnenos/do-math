---
name: ponytail-review
description: 과잉 설계만 겨냥한 코드 리뷰(ponytail-review). 지울 것(재발명된 stdlib, 불요 의존성, 추측성 추상화, 죽은 유연성)을 발견당 1행(위치·지울 것·대체물)으로 낸다. "과잉 설계 리뷰해줘", "뭘 지울 수 있어", "over-engineering 리뷰", "simplify review", /ponytail-review에서 호출한다. 정확성·보안 리뷰, 산문 첨삭(critique-text), 라운드 검증(verify-rounds)은 관할 밖이다.
---

# ponytail-review

diff를 불필요한 복잡성만 겨냥해 리뷰한다. 발견당 1행: 위치, 지울 것, 대체물. diff의 최선의 결말은 짧아지는 것이다.

## 원본 추적

- 원본: ponytail / ponytail / 4.9.0 / ponytail-review
- 원본 경로: `~/.claude/plugins/cache/ponytail/ponytail/4.9.0/skills/ponytail-review/`
- 원본 SKILL.md 해시: `e137a855bd87119a4517895a1000a59b0999e1b8`
- 원본 라이선스: MIT (Dietrich Gebert)
- 대조표: `.agents/skills/ponytail/references/원본_대조.md` (4종 통합)
- 재검토 트리거: 원본 플러그인 갱신(해시 불일치) 또는 로컬 규범 개정. adapt-skill 재호출로 수행한다

## 서식

`L<행>: <태그> <지울 것을 완결 문장으로>. <대체물>.` 여러 파일의 diff면 `<파일>:L<행>: ...`으로 쓴다.

태그:

- `delete:` 죽은 코드, 안 쓰는 유연성, 추측성 기능. 대체물: 없음.
- `stdlib:` 표준 라이브러리가 이미 제공하는 수제 구현. 함수 이름을 지목한다.
- `native:` 플랫폼이 이미 하는 일을 하는 의존성·코드. 기능 이름을 지목한다.
- `yagni:` 구현 하나뿐인 추상화, 아무도 안 쓰는 설정, 호출자 하나뿐인 층.
- `shrink:` 같은 로직, 더 적은 줄. 짧은 형태를 보인다.

## 예시

❌ "이 EmailValidator 클래스는 필요 이상으로 복잡할 수 있습니다. 이 단계에서 이 검증 규칙이 전부 필요한지 검토해 보셨나요?"

✅ `L12-38: stdlib: 27줄짜리 검증 클래스다. "@" 포함 검사 1줄이면 되고, 실질 검증은 확인 메일이 한다.`

✅ `L4: native: 포맷 호출 하나를 위해 moment.js를 들였다. Intl.DateTimeFormat이면 의존성 0이다.`

✅ `repo.py:L88: yagni: 구현이 하나뿐인 AbstractRepository다. 둘째 구현이 생길 때까지 인라인한다.`

✅ `L52-71: delete: 멱등한 로컬 호출을 감싼 재시도 래퍼다. 대체물 없음.`

✅ `L30-44: shrink: 수동 루프로 dict를 만든다. dict(zip(keys, values)) 1줄이면 된다.`

## 집계

유일하게 중요한 지표로 끝맺는다: `net: -<N>줄 감축 가능.`

지울 것이 없으면 `Lean already. Ship.`이라 적고 즉시 종료한다.

## 경계

- 관할은 과잉 설계와 복잡성뿐이다. 정확성 버그, 보안 구멍, 성능은 명시적으로 관할 밖이며 통상 리뷰로 보낸다.
- 스모크 테스트 하나, assert 자기검사 하나는 ponytail의 최소선이지 군살이 아니다. 삭제 대상으로 표시하지 않는다.
- 수정을 적용하지 않는다. 목록만 낸다.
- "stop ponytail-review" / "normal mode"로 이 스킬의 서식 제약을 해제한다.
