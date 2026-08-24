---
name: ponytail-audit
description: 저장소 전체의 과잉 설계 감사(ponytail-audit). ponytail-review와 같되 diff가 아니라 코드베이스 전체를 훑어, 지우거나 단순화하거나 stdlib·플랫폼 기능으로 바꿀 것을 큰 것부터 순위로 낸다. "코드베이스 감사해줘", "과잉 설계 찾아줘", "find bloat", /ponytail-audit에서 호출한다. 1회성 보고이고 수정은 적용하지 않는다.
---

# ponytail-audit

ponytail-review의 저장소 전체판이다. diff 대신 전체 트리를 훑고, 감축이 큰 발견부터 순위로 낸다.

## 원본 추적

- 원본: ponytail / ponytail / 4.9.0 / ponytail-audit
- 원본 경로: `~/.claude/plugins/cache/ponytail/ponytail/4.9.0/skills/ponytail-audit/`
- 원본 SKILL.md 해시: `5582d10335daff5b5947f9b77927fbc97f2047f3`
- 원본 라이선스: MIT (Dietrich Gebert)
- 대조표: `.agents/skills/ponytail/references/원본_대조.md` (4종 통합)
- 재검토 트리거: 원본 플러그인 갱신(해시 불일치) 또는 로컬 규범 개정. adapt-skill 재호출로 수행한다

## 스캔 범위

정본 코드 표면만 훑는다. 제외한다: `.agents/`(build_skill_mirrors.py 생성 미러이며 여기서의 중복은 설계다), `기억/`·`dag/`(산문·아카이브), `.git/`과 빌드 산출물.

## 태그

ponytail-review와 같은 어휘를 축자로 쓴다.

- `delete:` 죽은 코드, 안 쓰는 유연성, 추측성 기능. 대체물: 없음.
- `stdlib:` 표준 라이브러리가 이미 제공하는 수제 구현. 함수 이름을 지목한다.
- `native:` 플랫폼이 이미 하는 일을 하는 의존성·코드. 기능 이름을 지목한다.
- `yagni:` 구현 하나뿐인 추상화, 아무도 안 쓰는 설정, 호출자 하나뿐인 층.
- `shrink:` 같은 로직, 더 적은 줄. 짧은 형태를 보인다.

## 사냥감

stdlib·플랫폼이 이미 제공하는 의존성, 구현 하나뿐인 인터페이스, 제품 하나뿐인 팩토리, 위임만 하는 래퍼, 하나만 내보내는 파일, 죽은 플래그·설정, 수제 stdlib.

## 출력

발견당 1행, 순위순: `<태그> <지울 것을 완결 문장으로>. <대체물>. [경로]`

끝맺음: `net: -<N>줄, -<M>개 의존성 감축 가능.` 지울 것이 없으면 `Lean already. Ship.`이라 적고 즉시 종료한다.

## 경계

- 관할은 과잉 설계와 복잡성뿐이다. 정확성 버그, 보안 구멍, 성능은 통상 리뷰로 보낸다.
- 목록만 내고 아무것도 적용하지 않는다. 1회성이다.
- "stop ponytail-audit" / "normal mode"로 이 스킬의 서식 제약을 해제한다.
