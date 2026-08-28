---
행: z
유형: 싱크
---

# 국면 종결 싱크 — pvsnp-탐사-1

- 목표: 국면 pvsnp-탐사-1을 단계 원장대로 결산하고 닫는다.
- 완료 기준: `C:\math\.sdd\dag\pvsnp-탐사-1\행\z-결산.md`가 실재하고 frontmatter `상태:`가 단계 원장의 종결 상태를 갖는다. 증거 형태: 결산 파일 실물.
- 작업 디렉토리: C:\math (저장소 루트)
- 명령: python C:\math\.claude\skills\do-dag\scripts\dag_check.py --table C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
- 스킬 루트: C:\math\.claude\skills\do-dag
- 모델_프리셋: codex-full
- 검증런_모델_프리셋: codex-full
- 계약: C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\계약\싱크.md
- 불변식: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md
- 겨냥: C:\math\.sdd\dag\pvsnp-탐사-1\행\z-결산.md
- 정본: 국면명 pvsnp-탐사-1 · 이음새 원장 C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md
- 읽기 목록: C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md, C:\math\.sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md, C:\math\.claude\skills\do-dag\계약\공통.md, C:\math\.claude\skills\do-dag\계약\싱크.md, C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md
- 모델 배정 근거: Claude opus low — 배정표 codex-full(싱크 gpt-5.6-terra low)에서 이탈한다. 이 행은 격리 없이 메인 체크아웃(저장소 루트)에서 커밋·push·마커 종결을 수행하고, 불변식 6항 (3)이 저장소에 닿는 격리 없는 행의 Codex 배정을 막는다(사용자확정 결정 C:\math\.sdd\dag\pvsnp-탐사-1\결정\사용자확정-codexfull전환.md)
- 예산:
  [실측기 budget]
  명령: python dag_measure.py budget --files C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식.md,C:/math/.sdd/dag/pvsnp-탐사-1/행/0.d/불변식-2.md,.claude/skills/do-dag/계약/공통.md,.claude/skills/do-dag/계약/싱크.md --model opus --writes 8000 --pending 20000
  시각: 2026-08-25T15:11:50Z
  대상해시: sha1:92c8cd32b8fd
  .claude\skills\do-dag\계약\공통.md: ~4,077tok
  .claude\skills\do-dag\계약\싱크.md: ~10,040tok
  .sdd\dag\pvsnp-탐사-1\행\0.d\불변식-2.md: ~916tok
  .sdd\dag\pvsnp-탐사-1\행\0.d\불변식.md: ~1,395tok
  미존재 정본: ~10,526tok (20,000바이트 — 측정 시점 미존재)
  읽기 합계: ~26,954tok (문자계열 단가 견적)
  하네스 기저: ~28,000tok (시스템 프롬프트·툴 스키마·스킬 목록 — 실측 상수)
  도구 왕복: ~10,000tok (셸·검색 결과, 편집 회신 — 실측 상수)
  출력 유보: ~35,000tok (하한 — 저작 예상 8,000바이트는 하한 미달)
  소요 견적: ~99,954tok
  판정: opus 250,000 대비 예산 안
  [/실측기]
- 산출: C:\math\.sdd\dag\pvsnp-탐사-1\행\z-결산.md
- 반환: 공통 최종 반환 계약을 따른다. 완료 첫 줄은 `DONE`. 싱크의 상세 결과는 결산 frontmatter `상태:`가 진다. 추가 필드 없음.

## 임무

1. 첫 행동으로 `불변식:` 슬롯의 파일 전건을 읽는다.
2. 절차·단계 원장의 정본은 `C:\math\.claude\skills\do-dag\계약\싱크.md`다. 국면 종결 싱크의 단계를 그 원장대로 수행한다. 국면명은 pvsnp-탐사-1, 이음새 원장은 `C:\math\.sdd\dag\pvsnp-탐사-1\이음새.md`다.
