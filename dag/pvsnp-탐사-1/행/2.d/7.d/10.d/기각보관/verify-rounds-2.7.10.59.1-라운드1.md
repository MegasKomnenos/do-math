---
유형: 기각보관
출처: verify-rounds-2.7.10.59.1
라운드: 1
항목: 1
---

# 기각 보관

## R1-01

제목: R1-1 — L02~L06 작업자·직후 검증런의 마커 명령에 하위 명령이 없다

### 위치
`.sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/4.md` 14행, `5.md` 14행, `6.md` 14행, `7.md` 14행, `8.md` 14행, `9.md` 14행, `10.md` 14행, `11.md` 14행, `12.md` 14행, `13.md` 14행이 하위 명령 없는 `dag_marker.py`를 `명령`에 둔다. 사본의 각 행은 원본의 같은 행이다.

### 기준
`C:\math\기억\layer3\L-0001.md` 「검증 계약」 절은 다음을 정한다.

```
검증 계약에는 대상, 실패 조건, 측정값, 실행 형상, 증거 위치를 적는다. “확인한다”는 지시만으로는 무엇이 실패인지 판정할 수 없다.
```

`C:\math\.sdd\dag\pvsnp-탐사-1\행\2.d\7.d\10.d\59-보고.md` 「검산」 절 107~110행은 하위 명령 없는 명령이 실패하고 `status`가 실행됨을 기록한다.

```
- 마커 명령: `python C:\math\.claude\skills\do-dag\scripts\dag_marker.py`
- 결과: 하위 명령이 없어서 exit 1과 사용법을 반환했다. 마커 명령은 이 전개의 검산 명령이 아니다.
- 상태 명령: `python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status`
- 결과: exit 0. 활성 국면 `pvsnp-탐사-1`과 상태 정본 `C:\math\.sdd\dag\pvsnp-탐사-1\파견표.md`를 확인했다.
```

### 영향
L02~L06 작업자와 직후 검증런은 `명령`의 둘째 명령을 실행할 때 exit 1을 받는다. 파견문은 그 실패가 완료 판단에 미치는 영향을 정하지 않는다. 따라서 정상 작업도 명령 실패와 함께 끝나며, 완료 기준과 상태 완료 기준의 재현 가능한 검산 기록을 남길 수 없다.

### 조각 1 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/4.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 2 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/5.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 3 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/6.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 4 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/7.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 5 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/8.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 6 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/9.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 7 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/10.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 8 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/11.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 9 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/12.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 조각 10 — .sdd/dag/pvsnp-탐사-1/행/2.d/7.d/10.d/13.md 14~14행
원래:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py
```
대체:
```
  python C:\math\.claude\skills\do-dag\scripts\dag_marker.py status
```

### 보관 심사

최종 판정: 기각
- 심사 1: 승인 · 수리한다
- 심사 2: 기각 · 관문 1이 성립하지 않는다. 심사 대상이 기준으로 인용한 `C:\math\기억\layer3\L-0001.md`는 지정된 기준 원문 목록에 없다. 그 인용의 실재를 기준 원문에서 직접 대조할 수 없다.
- 심사 3: 승인 · 수리한다
