# GitHub 이슈 추적기

이 저장소는 GitHub Issues를 작업 추적기로 사용한다. 이 문서는 `wayfinder` 지도와 결정 티켓을 만드는 절차를 정한다.

## 저장소

- GitHub 저장소: `MegasKomnenos/math`
- 지도와 결정 티켓은 같은 저장소에 둔다.
- 지도와 결정 티켓의 관계에는 GitHub의 하위 이슈 기능을 사용한다.
- 결정 티켓 사이의 선행 관계에는 GitHub의 의존 관계 기능을 사용한다.

## 라벨

`wayfinder`는 다음 라벨만 사용한다:

- `wayfinder:map`
- `wayfinder:research`
- `wayfinder:prototype`
- `wayfinder:grilling`
- `wayfinder:task`

지도에는 `wayfinder:map`을 붙인다. 결정 티켓에는 티켓 종류와 같은 라벨 하나를 붙인다.

## 사용자 승인

새 이슈를 만들기 전에 다음 절차를 수행한다:

1. `write-for-reader`를 적용해 제목과 본문을 작성한다.
2. 제목, 본문, 라벨, 부모 지도와 선행 관계를 사용자에게 제안한다.
3. 사용자의 명시적 승인을 기다린다.
4. 사용자가 승인한 문면과 관계로 이슈를 만든다.

사용자의 승인을 받기 전에는 GitHub 이슈를 만들지 않는다. 사용자가 수정을 요구하면 수정한 전문을 다시 제안한다.

## 지도 만들기

지도 본문에는 다음 절을 순서대로 둔다:

```markdown
## Destination

<지도 종료 시점에 얻을 결과>

## Notes

<적용할 도메인, 스킬과 계속 지킬 결정>

## Decisions so far

## Not yet specified

<아직 질문을 정확히 쓸 수 없는 범위>

## Out of scope

<이번 지도에서 다루지 않는 범위>
```

열린 결정 티켓은 지도 본문에 나열하지 않는다. GitHub의 하위 이슈 목록이 열린 결정 티켓의 정본이다.

## 결정 티켓 만들기

결정 티켓 본문에는 다음 절만 둔다:

```markdown
## Question

<이 티켓이 답할 질문>
```

이슈를 먼저 만든다. 모든 이슈의 번호와 REST ID를 얻은 뒤 관계를 연결한다.

하위 이슈 관계는 다음 API로 연결한다:

```powershell
gh api -X POST "repos/MegasKomnenos/math/issues/<지도 번호>/sub_issues" -H "X-GitHub-Api-Version: 2026-03-10" -F "sub_issue_id=<결정 티켓 REST ID>"
```

선행 티켓이 후행 티켓을 막으면 다음 API를 호출한다:

```powershell
gh api -X POST "repos/MegasKomnenos/math/issues/<후행 티켓 번호>/dependencies/blocked_by" -H "X-GitHub-Api-Version: 2026-03-10" -F "issue_id=<선행 티켓 REST ID>"
```

`<결정 티켓 REST ID>`와 `<선행 티켓 REST ID>`에는 이슈 번호를 넣지 않는다. 다음 API가 반환하는 정수 `id`를 넣는다:

```powershell
gh api "repos/MegasKomnenos/math/issues/<이슈 번호>" --jq '.id'
```

## Frontier 찾기

Frontier는 다음 조건을 모두 충족하는 결정 티켓이다:

- 지도에 속한 열린 하위 이슈다.
- 담당자가 없다.
- 그 티켓을 막는 모든 결정 티켓이 닫혔다.

다음 API로 지도의 하위 이슈를 가져온다:

```powershell
gh api "repos/MegasKomnenos/math/issues/<지도 번호>/sub_issues" -H "X-GitHub-Api-Version: 2026-03-10" --paginate
```

다음 API로 결정 티켓을 막는 이슈를 가져온다:

```powershell
gh api "repos/MegasKomnenos/math/issues/<결정 티켓 번호>/dependencies/blocked_by" -H "X-GitHub-Api-Version: 2026-03-10" --paginate
```

GitHub 화면의 `Relationships` 영역에서도 같은 관계를 확인한다.

## 결정 티켓 수행하기

1. 결정 티켓을 수행하기 전에 담당자를 지정한다.
2. 티켓 종류에 맞는 스킬을 사용한다.
3. 답과 근거를 해결 댓글에 기록한다.
4. 결정 티켓을 닫는다.
5. 지도 `Decisions so far`에 티켓 제목, 링크와 한 줄 결론을 추가한다.

사용자가 읽는 문장에는 이슈 번호만 단독으로 쓰지 않는다. 이슈 제목에 링크를 걸고, 제목으로 지도와 결정 티켓을 지칭한다.
