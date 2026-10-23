# 300항목별 독립 검토 기록

대상: k4a876a6088f14bf090cb7da8b6e40a37/glossary.md. 최신 정본 k4dfeca2d4d014a23877e5aaa8f5cf457도 읽었으며 본문 차이는 없다. 표는 현행 번호순(1…338 중 살아 있는 300개)으로 정렬했다. 삭제된 번호는 누락이 아니다.

모든 행에서 일곱 칸을 읽었다. 근거 열은 실제 읽은 공개 원 정의(원 연구·동료의 glossary-proposals.md의 해당 이름 절)를 가리킨다. 현재 표기로 옮긴 이유는 review.md의 가족별 논증과 함께 읽는다. §1–11은 goal.md와 Parking.lean도 대조했다. 검토 메모는 기계 추출 결과가 아니라 항목별 수학 판단이다. 각 행의 현재 형식 대응 판정 근거 목록·대상 줄 번호는 entry-audit.json에 있다.

“새 결함 미발견”은 정의 보존·명시 영역·경계·정규화·인용 범위의 편집 검토 결과다. 원 연구의 모든 정리를 새로 증명하거나 모든 기존 Lean을 다시 공리 감사했다는 뜻이 아니다. 새 공리 감사는 새 두 파일과 필요한 21모듈에 대해 수행했다. 기존 미형식화는 오류로 세지 않았다. 외부 논문 전체를 이번에 다시 대조한 것은 아니며, 그 항목의 원 공개 연구·검토에서 실제 확인한 범위를 보존하는지 검사했다.

| 번호 | 대상 이름 | 원 정의 근거 | 검토한 수학·영역·경계 | 결과 |
|---|---|---|---|---|
| 1 | 자연수 | goal.md 및 대상의 출처 칸 | 0 포함 관례와 양수 원 문제를 구별. | 정의 대조; 새 결함 미발견 |
| 2 | 자리집합 | goal.md 및 대상의 출처 칸 | [0]=∅; Fin 값에 1을 더함. | 정의 대조; 새 결함 미발견 |
| 3 | 선호 목록 | goal.md 및 대상의 출처 칸 | 빈 함수 하나; 도착 순서 보존. | 정의 대조; 새 결함 미발견 |
| 4 | 주차 과정 | goal.md 및 대상의 출처 칸 | 최소 빈자리와 실패 전파가 결정적. | 정의 대조; 새 결함 미발견 |
| 5 | 주차 함수 | goal.md 및 대상의 출처 칸 | 성공 목록 부분집합이며 순열 궤도 아님. | 정의 대조; 새 결함 미발견 |
| 6 | 실제 주차 자리 | goal.md 및 대상의 출처 칸 | 성공 조건으로 i번째 자리 존재. | 정의 대조; 새 결함 미발견 |
| 7 | 변위 | goal.md 및 대상의 출처 칸 | s≥a로 Nat 차와 정수 차 일치. | 정의 대조; 새 결함 미발견 |
| 8 | 최대 변위 | goal.md 및 대상의 출처 칸 | n≥1의 달성 최대; 빈 크기 미지정. | 정의 대조; 새 결함 미발견 |
| 9 | 누적 개수 | goal.md 및 대상의 출처 칸 | A₀,ℓ=1과 Aₙ,−1=0; 표의 유효 사각형 보존. | 정의 대조; 새 결함 미발견 |
| 10 | 정확 개수 | goal.md 및 대상의 출처 칸 | b는 양수 크기만; 차분의 자연수 잘림은 포함으로 해소. | 정의 대조; 새 결함 미발견 |
| 11 | 단봉성 | goal.md 및 대상의 출처 칸 | 평탄 봉우리 허용; 실수 구현 누락 F3. | 수정/보완 F3 |
| 12 | 선호 접두부 · β | k746a9db449ff45fd9b973172e4b40861/glossary-proposals.md | k≤N; N=k=0의 빈 접두부. | 정의 대조; 새 결함 미발견 |
| 13 | 직전 빈자리 · p_S(s) | k746a9db449ff45fd9b973172e4b40861/glossary-proposals.md | 0을 포함한 max; 내부 prev는 원 직전 빈자리 값. | 정의 대조; 새 결함 미발견 |
| 14 | 전이 간격 · g_S(s) | k746a9db449ff45fd9b973172e4b40861/glossary-proposals.md | s−p≥1; 내부 gap의 한 칸 변환 확인. | 정의 대조; 새 결함 미발견 |
| 15 | 전이 가중치 · w_ℓ(S,s) | k746a9db449ff45fd9b973172e4b40861/glossary-proposals.md | 선호가 p+1,…,s에 놓이므로 min(g,ℓ+1). | 정의 대조; 새 결함 미발견 |
| 16 | 제한 점유 접두부 개수 · D_ℓ(S) | k746a9db449ff45fd9b973172e4b40861/glossary-proposals.md | 판 [18] 고정; §153의 제한형이라 편집상 중복 후보 F5. | 수정/보완 F5-선택 |
| 17 | 정확 점유 접두부 개수 · H(S,m) | k746a9db449ff45fd9b973172e4b40861/glossary-proposals.md | 빈 초기화는 M₀ 정의와 구분됨. | 정의 대조; 새 결함 미발견 |
| 18 | 첫 실패 개수 · F_n,k | k746a9db449ff45fd9b973172e4b40861/glossary-proposals.md | 첫 실패 뒤 선호도 모두 세는 전체 목록 사건. | 정의 대조; 새 결함 미발견 |
| 19 | 점유 자리집합 | k342ab0d73a284696bcb1050ba1ce7e00/glossary-proposals.md | 점유집합은 순서 없는 상태이며 선호 목록과 다름. | 정의 대조; 새 결함 미발견 |
| 20 | 후보 자리집합 | k342ab0d73a284696bcb1050ba1ce7e00/glossary-proposals.md | 빈 후보와 min 선택의 두 경우. | 정의 대조; 새 결함 미발견 |
| 21 | 빈 목록까지 확장한 보조 최대 변위 | k342ab0d73a284696bcb1050ba1ce7e00/glossary-proposals.md | 빈 sup=0 확장; 양수에서 §8과 같음. | 정의 대조; 새 결함 미발견 |
| 22 | 봉우리 위치 조건 | k342ab0d73a284696bcb1050ba1ce7e00/glossary-proposals.md | c<n 및 마지막 비교 k<n−1 정확. | 정의 대조; 새 결함 미발견 |
| 23 | 주차 결과 순열 · π | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | 자리→차 번호인 역순열. | 정의 대조; 새 결함 미발견 |
| 24 | 선호 선택 폭 · hⱼ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | 왼쪽 큰 번호 장벽; h≥1. | 정의 대조; 새 결함 미발견 |
| 25 | 전체 개수 · Tₙ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | T₀=1; Cayley는 n≥1, rooted 식은 s≥0. | 정의 대조; 새 결함 미발견 |
| 26 | 프라임 주차 함수 · PPFₙ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | n=1의 프라임 조건은 공허함. | 정의 대조; 새 결함 미발견 |
| 27 | 프라임 누적 개수 · pᵖʳₙ,ℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | p₀=0과 PF₀=1을 혼동하지 않음. | 정의 대조; 새 결함 미발견 |
| 28 | 프라임 정확 개수 · qₙ,ℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | 프라임 수준 개수의 망원차; b와 다름. | 정의 대조; 새 결함 미발견 |
| 29 | 누적 지수 생성함수 · ℱℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | EGF의 n=0 항 1; 해석적 사용 조건부. | 정의 대조; 새 결함 미발견 |
| 30 | 프라임 누적 지수 생성함수 · 𝒞ℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | 상수항 0; 전해석성은 인용한 비형식 판정 범위. | 정의 대조; 새 결함 미발견 |
| 31 | 포화 보정 다항식 · Vℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | ℓ=0 합은 빈 합 0. | 정의 대조; 새 결함 미발견 |
| 32 | 보정 원시함수 · Wℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | 상수항 0인 V의 원시함수. | 정의 대조; 새 결함 미발견 |
| 33 | 프라임 정확 지수 생성함수 · ℋℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | ℓ≥1 제한으로 두 C의 영역 적합. | 정의 대조; 새 결함 미발견 |
| 34 | 양의 단순극 위치 · ρℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | 양의 C=1 근; 원 순열 분해의 비형식 보증 유지. | 정의 대조; 새 결함 미발견 |
| 35 | 점근 계수 · κℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | ρ>0,C′>0이 분모 보장. | 정의 대조; 새 결함 미발견 |
| 36 | 인접 차분 · Δⱼ,ℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | 정수 중앙차; n=0 경계와 양수 Lean 제한 구별. | 수정/보완 F3 |
| 37 | 누적 증분 · eⱼ,ᵣ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | r≥1에서 e₀,r=0; b₀를 만들지 않음. | 정의 대조; 새 결함 미발견 |
| 38 | 마지막 차량 가중치 · ωₖ,ℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | min 가중치는 n=0 자식에도 적합. | 정의 대조; 새 결함 미발견 |
| 39 | 포화 손실 · Kₙ,ℓ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | 두 T 인수 비음수; 포화 가정은 별도. | 정의 대조; 새 결함 미발견 |
| 40 | 정규화 전체 계수 · fⱼ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | T/j!의 보통 계수 척도. | 정의 대조; 새 결함 미발견 |
| 41 | 단위 허용 거리 정규화 계수 · uₙ | k12c717105e4f436ebbc4a311ae64134a/glossary-proposals.md | Aₙ,₁/n!, 차량 선호와 다른 u. | 정의 대조; 새 결함 미발견 |
| 42 | 선착 조건 | k2809252f588641b39bcaf13513db3951/glossary-proposals.md | 단사·초기점유 배제·선착 증인이 모두 필요. | 정의 대조; 새 결함 미발견 |
| 43 | 변위 제한 실행 기록 | k2809252f588641b39bcaf13513db3951/glossary-proposals.md | n=0 빈 함수 쌍 하나; M̄ 제한과 동치. | 정의 대조; 새 결함 미발견 |
| 44 | 왼쪽 차량 번호 집합 | k2809252f588641b39bcaf13513db3951/glossary-proposals.md | 마지막 차량 제외; |I|=마지막 자리−1. | 정의 대조; 새 결함 미발견 |
| 45 | 도착 번호 표준화 | k2809252f588641b39bcaf13513db3951/glossary-proposals.md | 증가 열거로 원 도착 순서 유지. | 정의 대조; 새 결함 미발견 |
| 46 | 제한 기록 분해 자료 | k2809252f588641b39bcaf13513db3951/glossary-proposals.md | 변위 선택 수 min(|I|,ℓ)+1; 빈 자식 포함. | 정의 대조; 새 결함 미발견 |
| 47 | 원 제한 분해 자료 | k2809252f588641b39bcaf13513db3951/glossary-proposals.md | 기록쌍과 원 PF의 자료형 차이 보존. | 정의 대조; 새 결함 미발견 |
| 48 | 마지막 차량 분해 대응 | k2809252f588641b39bcaf13513db3951/glossary-proposals.md | 오른쪽에서 |I|+1을 빼고 양쪽 번호 표준화. | 정의 대조; 새 결함 미발견 |
| 49 | 원형 주차 확률모형 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | n+1칸에 n대; 유일 빈자리 회전 해석. | 정의 대조; 새 결함 미발견 |
| 50 | 정확 변위 차량 수 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | Y는 정확 차량 수; 두 변수 급수와 기호 구별. | 정의 대조; 새 결함 미발견 |
| 51 | 고변위 차량 수 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | ≥ℓ 표시이며 Z₀=n. | 정의 대조; 새 결함 미발견 |
| 52 | 변위 표시 개수 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | 다중 차량을 중복 표시; n=0 경계만 0. | 정의 대조; 새 결함 미발견 |
| 53 | 동반 표시 개수 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | Y=0 또는 Z≥1이라 잘린 차 곱과 정수 곱 같음. | 정의 대조; 새 결함 미발견 |
| 54 | 표시 개수 간격 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | 정수 R 차; 닫힌 공식의 비형식 범위 보존. | 정의 대조; 새 결함 미발견 |
| 55 | 전체 지수 생성함수 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | 전체 T의 EGF; 제한 F와 구별. | 정의 대조; 새 결함 미발견 |
| 56 | 전체 생성함수 보조 급수 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | xΨ로 상수항 0. | 정의 대조; 새 결함 미발견 |
| 57 | 표시 간격 지수 생성함수 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | n≥1 시작; J₀=0과 적합. | 정의 대조; 새 결함 미발견 |
| 58 | 포화 결손 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | A≤T라 결손 비음수; 차는 정수. | 정의 대조; 새 결함 미발견 |
| 59 | 고변위 표시 다항식 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | z=0에서도 z⁰=1; 빈 다항식 값 1. | 정의 대조; 새 결함 미발견 |
| 60 | 이항 표시 모멘트 | k21248694f4c24bad89564e3143deba52/glossary-proposals.md | p=0 빈 모멘트 1; G(1+y) 계수 관계. | 정의 대조; 새 결함 미발견 |
| 61 | ℓ-구간 주차 함수 집합 | kdd440866190648ffb7237cbd5b1d4c7c/glossary-proposals.md | 빈 목록에 M̄를 사용해 영역 오류 회피. | 정의 대조; 새 결함 미발견 |
| 62 | 최대 변위 수준 집합 | kdd440866190648ffb7237cbd5b1d4c7c/glossary-proposals.md | 양수 크기의 수준 집합; 개수가 b. | 정의 대조; 새 결함 미발견 |
| 63 | 절단 길이 | kdd440866190648ffb7237cbd5b1d4c7c/glossary-proposals.md | 원 t는 pg+1이므로 min(ℓ+1,h). | 정의 대조; 새 결함 미발견 |
| 64 | 총 변위 | kdd440866190648ffb7237cbd5b1d4c7c/glossary-proposals.md | 총 변위는 합; 최대값으로 옮기지 않음. | 정의 대조; 새 결함 미발견 |
| 65 | 비감소 주차 함수 집합 | kdd440866190648ffb7237cbd5b1d4c7c/glossary-proposals.md | 비감소 목록만 제한; 일반 PF와 구별. | 정의 대조; 새 결함 미발견 |
| 66 | Fubini 수 | kdd440866190648ffb7237cbd5b1d4c7c/glossary-proposals.md | 블록 순서 유지; Fub와 A₁ 연결은 정리. | 정의 대조; 새 결함 미발견 |
| 67 | 원형 선형 탐사의 최대 변위 | kdd440866190648ffb7237cbd5b1d4c7c/glossary-proposals.md | v≥1 최대와 v<m 성공 범위; mod 대표 명시. | 정의 대조; 새 결함 미발견 |
| 68 | 단위 허용 거리의 블록 구조 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.4 | 안정 정렬과 원 발생 번호가 원 §4.4와 일치. | 정의 대조; 새 결함 미발견 |
| 69 | 블록 셋째 이후 위치 집합 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.4 | 셋째 이후의 원 차량 번호 집합. | 정의 대조; 새 결함 미발견 |
| 70 | 뒤따르는 블록 둘째 위치 집합 | kdd440866190648ffb7237cbd5b1d4c7c/exposition.md §4.4 | 이전 블록 마지막 번호보다 뒤인 둘째 번호. | 정의 대조; 새 결함 미발견 |
| 71 | 선형 결손 상계 | k5bedcf491ebd45f1a1dcb7fb84fad705/glossary-proposals.md | 삼각 재귀; E≤L 및 일치 띠를 분리. | 정의 대조; 새 결함 미발견 |
| 72 | 수송 자식 가중치 | k5bedcf491ebd45f1a1dcb7fb84fad705/glossary-proposals.md | j<n이라 자식 Tₙ₋₁₋ⱼ가 정의됨. | 정의 대조; 새 결함 미발견 |
| 73 | 인접 수송 경계합 | k5bedcf491ebd45f1a1dcb7fb84fad705/glossary-proposals.md | n≤2ℓ+1이 두 K의 포화 가정 보장. | 정의 대조; 새 결함 미발견 |
| 74 | 말단 항 유지 수송 상계 | k5bedcf491ebd45f1a1dcb7fb84fad705/glossary-proposals.md | 버린 자식 차가 비양수라는 추가 조건을 유지. | 정의 대조; 새 결함 미발견 |
| 75 | 고정 끝 거리 표시 간격 극한 | k5bedcf491ebd45f1a1dcb7fb84fad705/glossary-proposals.md | r=1도 계승0!=1; 극한 성질은 별도. | 정의 대조; 새 결함 미발견 |
| 76 | 포화 초과 가중 급수 | k5bedcf491ebd45f1a1dcb7fb84fad705/glossary-proposals.md | ℓ=0도 형식 꼬리 정의 가능; EGF 원천과 계승 구분. | 정의 대조; 새 결함 미발견 |
| 77 | 앞선 큰 값 위치 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | §24와 pg=j−h; 다른 출력 함수라 유지 가능. | 정의 대조; 새 결함 미발견 |
| 78 | 뿌리 있는 숲 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | 모든 부모 경로가 0에 도달; 일반 숲과 감소 숲 구분. | 정의 대조; 새 결함 미발견 |
| 79 | 부분나무 크기 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | 자기 자신 1과 진자손 개수; 순환 없음 필요. | 정의 대조; 새 결함 미발견 |
| 80 | 감소 숲 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | 부모>자식 또는0이 반복 종료 보장. | 정의 대조; 새 결함 미발견 |
| 81 | 큰 자손 수 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | 라벨 큰 진자손만 세며 일반 숲에서 정의. | 정의 대조; 새 결함 미발견 |
| 82 | 최대 큰 자손 수 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | n≥1 필수; 원 M 분포 주장은 정의 아님. | 정의 대조; 새 결함 미발견 |
| 83 | 최대 변위 끝 거리 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | n−1−M≥0; 결손 E와 다른 입력. | 정의 대조; 새 결함 미발견 |
| 85 | 사슬 재귀 가중합 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | H′<H 삼각 재귀; B 기저의 수리 유한합 확인. | 정의 대조; 새 결함 미발견 |
| 86 | 최댓값 면적 | k10f126a516ee4c4caf6cf7cc38d28a09/glossary-proposals.md | 브라운 연속 경로의 적분; 예외 경로0 허용. | 정의 대조; 새 결함 미발견 |
| 87 | 원형 최대 변위 재척도화 | k24d813562f8a4abfad309a53255354c9/glossary-proposals.md | m−d_max 전체를 m^(2/3)로 나눔; confined 조건은 분포 조건. | 정의 대조; 새 결함 미발견 |
| 88 | 최댓값 면적 라플라스 변환 | k24d813562f8a4abfad309a53255354c9/glossary-proposals.md | s≥0에서 피적분함수≤1. | 정의 대조; 새 결함 미발견 |
| 89 | 최대 변위 재척도화 극한분포 | k24d813562f8a4abfad309a53255354c9/glossary-proposals.md | 독립 지수변수와 면적의 비; 법칙과 실현 변수 구분. | 정의 대조; 새 결함 미발견 |
| 90 | 허용 거리 비교 인자 | k83ac8ca8d9c44903b97b8979ac04bdd3/glossary-proposals.md | 분모 2ℓ+2>0; 거리비 정리와 정의 구분. | 정의 대조; 새 결함 미발견 |
| 91 | 제한 순열 가중치 | k83ac8ca8d9c44903b97b8979ac04bdd3/glossary-proposals.md | n=0 빈 곱1; q≥1. | 정의 대조; 새 결함 미발견 |
| 92 | 큰 선택 폭 위치 수 | k83ac8ca8d9c44903b97b8979ac04bdd3/glossary-proposals.md | >q인 폭 수; 차량 고변위 수와 다름. | 정의 대조; 새 결함 미발견 |
| 93 | 문턱 선택 폭 위치 수 | k83ac8ca8d9c44903b97b8979ac04bdd3/glossary-proposals.md | =q인 폭 수; ≥와 >의 차. | 정의 대조; 새 결함 미발견 |
| 96 | 큰 크기 사슬 집합 · \(\mathfrak C_{n,a}\) | ka8fb76538efa4aa28114eaab004058ff/glossary-proposals.md | 엄격 감소 크기열; n≤a이면 공집합. | 정의 대조; 새 결함 미발견 |
| 97 | 사슬 계수 · \(\mathfrak c_{n,a}\) | ka8fb76538efa4aa28114eaab004058ff/glossary-proposals.md | 모든 T 인수≥0; 마지막 B와 원 기저의 유한합 일치. | 정의 대조; 새 결함 미발견 |
| 98 | 성분 수송 계수 · \(\mathfrak I(n,s)\) | ka8fb76538efa4aa28114eaab004058ff/glossary-proposals.md | s≥n일 때0; ϑ와 이항 윗첨자 다름. | 정의 대조; 새 결함 미발견 |
| 99 | 사슬 응답 다항식 · \(\mathfrak K_z(n,s)\) | ka8fb76538efa4aa28114eaab004058ff/glossary-proposals.md | n≤s 경계0과 자연수 매개변수 연결 범위 확인. | 정의 대조; 새 결함 미발견 |
| 100 | 사슬 경계 손실 다항식 · \(\mathfrak D_{n,k}(z)\) | ka8fb76538efa4aa28114eaab004058ff/glossary-proposals.md | Tₖ 곱; UpperRatio 잘린 영역을 동일시하지 않음. | 정의 대조; 새 결함 미발견 |
| 103 | 사슬 곡률 비율 · \(\mathfrak R_{n,k}\) | ka8fb76538efa4aa28114eaab004058ff/glossary-proposals.md | k+2≤n에서 양수 손실 분모; 사슬 전개 형식 한계 유지. | 정의 대조; 새 결함 미발견 |
| 104 | 사슬 이동 손실 · \(\mathfrak H_{n,k}\) | ka8fb76538efa4aa28114eaab004058ff/glossary-proposals.md | 양수성은 응답 단조성과 추가 손실; n≥k+3. | 정의 대조; 새 결함 미발견 |
| 105 | 말단 크기 곡률 다항식 · \(\mathfrak N_{n,s}(u)\) | ka8fb76538efa4aa28114eaab004058ff/glossary-proposals.md | u≥0 양수성과 다항식의 전체 정의를 구별. | 정의 대조; 새 결함 미발견 |
| 106 | 선형 결손 오차 | k9001cda0e9704d678342f834dec9e9d6/glossary-proposals.md | L−E 정수 차; 전칭 부호와 별개. | 정의 대조; 새 결함 미발견 |
| 107 | 선형 원천 | k9001cda0e9704d678342f834dec9e9d6/glossary-proposals.md | n=0 원천0; (k−ℓ)₊ 유지. | 정의 대조; 새 결함 미발견 |
| 108 | 선형 전이 연산자 | k9001cda0e9704d678342f834dec9e9d6/glossary-proposals.md | g의 정의역 전체 ℕ; n=0 출력0. | 정의 대조; 새 결함 미발견 |
| 109 | 선형 전개 층 | k9001cda0e9704d678342f834dec9e9d6/glossary-proposals.md | r차 전이 반복; n차 재귀와 구별. | 정의 대조; 새 결함 미발견 |
| 110 | 제한 이항 폭 모멘트 | k9001cda0e9704d678342f834dec9e9d6/glossary-proposals.md | 이항 모멘트 p=0 포함; 계승 모멘트에는 p! 인자. | 정의 대조; 새 결함 미발견 |
| 116 | 순열별 제한 곡률 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | 세 min 곱의 정수 차; 빈 순열에서0. | 정의 대조; 새 결함 미발견 |
| 118 | 제한 표시 지수 급수 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | q^a 미분 인자 복원; n=0 계수도 검사. | 정의 대조; 새 결함 미발견 |
| 119 | 감쇠 제한 지수 급수 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | 감쇠 평가는 F(q−1,q); 상수항1. | 정의 대조; 새 결함 미발견 |
| 120 | 감쇠 문턱 지수 급수 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | q∂Y 인자 필수; 빈 계수0. | 정의 대조; 새 결함 미발견 |
| 121 | 전체 계수 절단 다항식 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | §162의 q≥2 제한형; 중복 정리 제안 F5. | 수정/보완 F5-선택 |
| 122 | 제한 표시 전달 계수 쌍 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | q=2일 때 V₀=0으로 정의 가능. | 정의 대조; 새 결함 미발견 |
| 123 | 감쇠 표시 분자 급수 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | q² 두 미분 차; 조건부 증가와 전칭 부호 구별. | 정의 대조; 새 결함 미발견 |
| 124 | 감쇠 표시 원천 급수 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | 모든 급수의 q≥2 영역 맞음; 전달식 Lean 미완료 유지. | 정의 대조; 새 결함 미발견 |
| 125 | 제한 표시 응답 커널 | k772e2708b66f4a2e8e9322e151db43ab/glossary-proposals.md | 선형 ODE의 상수항0이 형식해를 유일하게 함. | 정의 대조; 새 결함 미발견 |
| 126 | 역급수 계수 | k52423a2c3ac04a04a4e61cb863a834a7/glossary-proposals.md | m=1의0⁰=1; 분모 m!>0. | 정의 대조; 새 결함 미발견 |
| 127 | 사슬 응답 지수급수 | k52423a2c3ac04a04a4e61cb863a834a7/glossary-proposals.md | n>s인 응답만 합하며 다항식 계수환 명시. | 정의 대조; 새 결함 미발견 |
| 128 | 동차 응답 다항식 | k52423a2c3ac04a04a4e61cb863a834a7/glossary-proposals.md | 두 역급수 상수항1이라 가역. | 정의 대조; 새 결함 미발견 |
| 129 | 말단 경계 요구 비 | k52423a2c3ac04a04a4e61cb863a834a7/glossary-proposals.md | n=k+d+1,d≥2로 두 양수 응답 분모 보장. | 정의 대조; 새 결함 미발견 |
| 130 | 이항 절단 비 하계 | k52423a2c3ac04a04a4e61cb863a834a7/glossary-proposals.md | min(p,k)까지 이항합; 분모(k+1)^j>0. | 정의 대조; 새 결함 미발견 |
| 131 | 응답 1차 차분 | k52423a2c3ac04a04a4e61cb863a834a7/glossary-proposals.md | u 변수 다항식의 한 차분; Δ와 다른 객체. | 정의 대조; 새 결함 미발견 |
| 132 | 원 성분 계수 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | q≥1로 Aᵢ,q−1 유효; q=0 보조 확장 제외. | 정의 대조; 새 결함 미발견 |
| 133 | 전체 성분 계수 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | 모든 i≥0의 (i+1)Tᵢ; Cayley 연결 확인. | 정의 대조; 새 결함 미발견 |
| 134 | 원 성분 절단 기저 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | k=0 포함; n≤2k+1에서만 J와 같음. | 정의 대조; 새 결함 미발견 |
| 135 | 소성분 조립 개수 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | k=0일 때 J₀(n>0)=0; F(0,k)는 k≥2에서만. | 정의 대조; 새 결함 미발견 |
| 136 | 원 성분 사슬 다항식 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | n≤k의 빈 합으로 Tₙ; 전역 다항식과 제한 사슬 구별. | 정의 대조; 새 결함 미발견 |
| 137 | 원 성분 곡률 다항식 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | 세 다항식 평가의 정수 계수 차분. | 수정/보완 F4 |
| 138 | 절단 계수 일치 관계 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | i<N의 엄격 절단; i≤N 아님. | 정의 대조; 새 결함 미발견 |
| 139 | 일반 지수 정규화 연산 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | EGF 계승 정규화; ℚ 입력. | 정의 대조; 새 결함 미발견 |
| 140 | 적분 성분 원천 연산 | kdc2eaac490144ba1be92ba8a428a2228/glossary-proposals.md | c(h−1)/h!이므로 도함수 egf(c). | 정의 대조; 새 결함 미발견 |
| 141 | 보조 Abel 다항식 | k0ee8ae2f5ad94097af2c3778062ded44/glossary-proposals.md | r=0 값1; 다음 지수 r의 Abel 다항식. | 정의 대조; 새 결함 미발견 |
| 142 | 실수 허용 거리 누적 함수 | kafb8753e508c467d89d38921889dab4a/glossary-proposals.md | 빈 순열 값1과 양수 n의 x=0 값0 구별. | 정의 대조; 새 결함 미발견 |
| 143 | 연속 최대 변위 | kafb8753e508c467d89d38921889dab4a/glossary-proposals.md | v∈[0,1)라 floor 최대=M; 확률은 T로 나눔. | 정의 대조; 새 결함 미발견 |
| 144 | 원형 호 | kafb8753e508c467d89d38921889dab4a/glossary-proposals.md | 빈자리 e마다 역방향 점유호가 분할을 이룸. | 정의 대조; 새 결함 미발견 |
| 145 | 톱니 상승량 | kafb8753e508c467d89d38921889dab4a/glossary-proposals.md | 단위 구간 볼록성과 점프의 1/k 인자 확인. | 정의 대조; 새 결함 미발견 |
| 146 | 마지막 최대 변위 차량 | kafb8753e508c467d89d38921889dab4a/glossary-proposals.md | 최대 달성 차량 중 가장 큰 번호; Fin 값+1. | 정의 대조; 새 결함 미발견 |
| 147 | 도착 시각별 정확 개수 | kafb8753e508c467d89d38921889dab4a/glossary-proposals.md | τ별 사건은 서로소·전부; 합이 b. | 정의 대조; 새 결함 미발견 |
| 148 | 정규화 사슬 응답 | k178f470ddcb549fe86572026bed89f80/glossary-proposals.md | j=0,c>0 분모; §99의 정규화 제한. | 정의 대조; 새 결함 미발견 |
| 149 | 말단 혼합 보정 | k178f470ddcb549fe86572026bed89f80/glossary-proposals.md | 두 곡률의 양수 영역 k+3≤n≤2k+1 필요. | 정의 대조; 새 결함 미발견 |
| 150 | 일반 삼각 해 연산 | k178f470ddcb549fe86572026bed89f80/glossary-proposals.md | 모든 자식 j<n으로 존재·유일. | 정의 대조; 새 결함 미발견 |
| 151 | 일반 삼각 해의 매개변수 차분 | k178f470ddcb549fe86572026bed89f80/glossary-proposals.md | 전방 차분의 z+1과 r 단계 정의 일치. | 정의 대조; 새 결함 미발견 |
| 152 | 혼합 문턱 개수 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | 앞≤ℓ·뒤<ℓ; n=0,ℓ=0 경계1 보존. | 정의 대조; 새 결함 미발견 |
| 153 | 앞부분 개수 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | 판 매개변수 전역화; Dℓ는 n=18 제한형 F5. | 수정/보완 F5-선택 |
| 154 | 뒷부분 개수 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | 엄격 문턱; 완료 상태 [n]의 빈 접미부1. | 정의 대조; 새 결함 미발견 |
| 155 | 도착 원천 개수 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | 크기 h+1 마지막 차를 대입; b₀ 아님. | 정의 대조; 새 결함 미발견 |
| 156 | 도착 전달 커널 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | ℓ+min(m+1,ℓ) 인자와 mixed 첨자 j≤m. | 정의 대조; 새 결함 미발견 |
| 157 | 혼합 문턱 이변수 급수 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | h!r! EGF 정규화, 문턱 ℓ≥1. | 정의 대조; 새 결함 미발견 |
| 158 | 도착 표시 이변수 급수 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | 크기 h+r+1, 표시 차 h+1의 지수급수. | 정의 대조; 새 결함 미발견 |
| 159 | 도착 인접 차 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | 원 Δ와 다른 도착별 정수 차. | 정의 대조; 새 결함 미발견 |
| 160 | 도착 부호 전달 하계 | k3402f089d15b489eb2cbad3ffa444bb7/glossary-proposals.md | r−1−b<r로 재귀 종료; 음수 초기값 보존. | 정의 대조; 새 결함 미발견 |
| 161 | 역방향 차분 원천 | k39ce4750627e4a0e9735832b2fb49076/glossary-proposals.md | j=k+1 별도 가지; 거듭제곱 밑0 문제 회피. | 정의 대조; 새 결함 미발견 |
| 162 | 문턱 1까지 확장한 전체 계수 절단 다항식 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | q=1 추가값1; §121과 중복 검토 F5. | 수정/보완 F5-선택 |
| 163 | 두 차량 국소 계수 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | 두 간격은 실제 적용에서≥1; 국소 식과 일반 원 연결 구별. | 정의 대조; 새 결함 미발견 |
| 164 | 도착 초기 음수 급수 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | 비음수 급수가 음의 원천으로 쓰임; 이름이 부호 아님. | 정의 대조; 새 결함 미발견 |
| 165 | 도착 초기 양수 급수 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | 포화와 문턱 단조성으로 각 인자 계수 비음수. | 정의 대조; 새 결함 미발견 |
| 166 | 도착 부호 전달 지수급수 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | Z¹의 EGF이며 새 개수 정의 아님. | 정의 대조; 새 결함 미발견 |
| 167 | 부호 분리 전달 급수 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | y차수 귀납으로 유일; X−Y는 Ẑ 관계. | 정의 대조; 새 결함 미발견 |
| 168 | 도착 대각 적분 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | beta 적분으로 분모 n!; h+r=n−1. | 정의 대조; 새 결함 미발견 |
| 169 | 계승비 커널 보정 급수 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | m−ℓ−1>0 및 m−p≥0. | 정의 대조; 새 결함 미발견 |
| 170 | 양수 전달 하한 급수 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | ℱℓ₋₁는 ℓ=1에도 F₀로 유효. | 정의 대조; 새 결함 미발견 |
| 171 | 음수 전달 상한 모멘트 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | 무한 d족도 차수 귀납이 유일; 최소차수 ℓ+d+1. | 정의 대조; 새 결함 미발견 |
| 172 | 부호 전달 포락선 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | 포락선의 차; 원 Δ 재정의 아님. | 정의 대조; 새 결함 미발견 |
| 173 | 끝점·현 포락선 | k9a8431776364465195c7ae81c0c031ec/glossary-proposals.md | R 분자 상수항0; q=1에는 P⁺ 사용. | 정의 대조; 새 결함 미발견 |
| 174 | 혼합 역분모 자료 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | W 상수항0,F 상수항1로 지수·역급수 가능. | 정의 대조; 새 결함 미발견 |
| 175 | 도착 원천 지수급수 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | S의 마지막 차 크기 h+1; Fq(Fq−P⁺q)와 적합. | 정의 대조; 새 결함 미발견 |
| 176 | 도착 전달 커널 지수급수 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | m<q−1의 포화 보정이 Vq−1. | 정의 대조; 새 결함 미발견 |
| 177 | 원 공통 동차 전달자 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | u는 x만의 급수; y 초기값 명시. | 정의 대조; 새 결함 미발견 |
| 178 | 원 공통 강제 전달자 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | 강제항은 x,y 급수; 동차 전달자와 다름. | 정의 대조; 새 결함 미발견 |
| 179 | 정확 버린 원천 급수 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | 원 커널 차에서 mixed 하나 제거; 비음수 잔여. | 정의 대조; 새 결함 미발견 |
| 180 | 최소 원천 분리 원시함수 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | 모든 역분모 상수항1; k∈{0,1,2}. | 정의 대조; 새 결함 미발견 |
| 181 | 삼각 적분 차 연산 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | 정해진 상수항0 적분 두 항의 차. | 정의 대조; 새 결함 미발견 |
| 182 | 대각 커널 부호 보정 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | 대각 적분의 영역 적합; 부호 있는 원천 유지. | 정의 대조; 새 결함 미발견 |
| 183 | 공통 분모 곡률 분자 | k1e30f22632294be9991c2e6b0dba5d04/glossary-proposals.md | 세 F의 상수항1; 분모 곱 가역. | 정의 대조; 새 결함 미발견 |
| 184 | 조건별 한 차량 선호 개수 | k3c8d00ecefb9486697fd5692a47dad49/glossary-proposals.md | s 점유 시0; 빈자리에서는 원 선호 섬유 개수. | 정의 대조; 새 결함 미발견 |
| 185 | 순서 있는 두 자리 선호쌍 개수 | k3c8d00ecefb9486697fd5692a47dad49/glossary-proposals.md | 첫 자리 점유를 갱신한 뒤 두 번째 가중치 곱. | 정의 대조; 새 결함 미발견 |
| 186 | 조건별 한 단계 합산 연산 | k3c8d00ecefb9486697fd5692a47dad49/glossary-proposals.md | 점유 자리는 weight=0이라 합에 넣어도 무방. | 정의 대조; 새 결함 미발견 |
| 187 | 조건 목록을 만족하는 부분 실행 | k3c8d00ecefb9486697fd5692a47dad49/glossary-proposals.md | 길이 k 조건 목록; 빈 경우 공허 성공. | 정의 대조; 새 결함 미발견 |
| 188 | 조건 목록의 완료 개수 | k3c8d00ecefb9486697fd5692a47dad49/glossary-proposals.md | 빈 조건 완료 개수1; step 재귀는 원 개수와 별도 동일성. | 정의 대조; 새 결함 미발견 |
| 189 | 도착 성분 부분합 | k3c8d00ecefb9486697fd5692a47dad49/glossary-proposals.md | j=0 합0; ℓ≥1에서 mixed−A와 연결. | 정의 대조; 새 결함 미발견 |
| 190 | 정수 Green 가중치 | k3c8d00ecefb9486697fd5692a47dad49/glossary-proposals.md | 0≤r,s≤D일 때만 비음수 Green 곱. | 정의 대조; 새 결함 미발견 |
| 191 | 도착 숲 · G_α | kb555148741aa4c0687e60906bd144e43/glossary-proposals.md | 오른쪽 가장 가까운 큰 차량이 부모; 종료·개별 전단사 구별. | 정의 대조; 새 결함 미발견 |
| 192 | 골격 · Sk_x(G) | kb555148741aa4c0687e60906bd144e43/glossary-proposals.md | 실수 x≥0 골격; 자연수 구현 제한 별도. | 정의 대조; 새 결함 미발견 |
| 193 | Cayley 분할 핵 · Spl(t,s) | kb555148741aa4c0687e60906bd144e43/glossary-proposals.md | 엄격 과반 성분만; 동률로 연장하지 않음. | 정의 대조; 새 결함 미발견 |
| 195 | 골격 곡률 이득 · Γ⁺ₙ,ℓ | kb555148741aa4c0687e60906bd144e43/glossary-proposals.md | 고정 q F의 세 U 평가; 원 Γ⁺와 연결. | 정의 대조; 새 결함 미발견 |
| 196 | 꽉 찬 상자 손실 · Γ⁻ₙ,ℓ | kb555148741aa4c0687e60906bd144e43/glossary-proposals.md | F(q−1,q)−F(q−1,q−1); 양수성 n≥ℓ+1. | 정의 대조; 새 결함 미발견 |
| 197 | 상반부 형상 함수 · Φ₁(u) | kb555148741aa4c0687e60906bd144e43/glossary-proposals.md | 형상 식은 정의이나 극한 성질은 추측으로 유지. | 정의 대조; 새 결함 미발견 |
| 198 | 일반 가중 재귀 평가기 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | 자연수와 NNReal 구분은 맞지만 새 미검토 구현 누락 F3. | 수정/보완 F3 |
| 199 | 비교 가능한 표시 합 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | T−L 동일성에 c=x 조건이 빠짐 F1. | 수정/보완 F1 |
| 200 | 맨 위 뿌리 표시 합 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | 뿌리를 반드시 표시; s≤x이면 빈 합0. | 정의 대조; 새 결함 미발견 |
| 201 | 비교 불가능 표시 보정 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | 숲 합과 경계 대수식의 형식 식별을 구분해야 함 F2. | 수정/보완 F2 |
| 202 | 전체 급수 원시함수 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | Ψ의 상수항0 원시함수; 계승(s!) 유지. | 정의 대조; 새 결함 미발견 |
| 203 | 지수 원천 계수 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | 원천 계수의 부호와 원 Δ 부호를 구별. | 정의 대조; 새 결함 미발견 |
| 204 | 반복 원시함수 커널 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | 각 반복 적분 상수항0, 지수 계수 정수. | 정의 대조; 새 결함 미발견 |
| 205 | 원천 지수 층 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | I의 최소차수로 각 n에서 r합이 유한. | 정의 대조; 새 결함 미발견 |
| 206 | 짝지은 4차 하계 분자 | k526e621123a64cee8d48c8b3c7c79a04/glossary-proposals.md | 모멘트의 >,≥ 및 2 계수 보존; 하계 범위 제한. | 정의 대조; 새 결함 미발견 |
| 207 | 조건별 변위 제한 실행 기록 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | 실행 기록의 조건별 부분집합; 원 번호와 Fin 차이. | 정의 대조; 새 결함 미발견 |
| 208 | 조건별 제한 분해 자료 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | 자식 조건을 증가 열거에 당겨와 도착 번호 유지. | 정의 대조; 새 결함 미발견 |
| 209 | 조건별 마지막 차량 조립 대응 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | 조립 방향 Ξ→Tr; 제한의 보존 필요. | 정의 대조; 새 결함 미발견 |
| 210 | 문턱 앞 선택 수 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | 원 i≤j는 내부 i.val<j. | 정의 대조; 새 결함 미발견 |
| 211 | 혼합 분해 유효 첨자집합 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | r=a+c 재매개화; 유한 직사각형. | 정의 대조; 새 결함 미발견 |
| 212 | 이항 이변수 합성 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | 두 이항계수의 배열 합성; 차량 순서 변경 아님. | 정의 대조; 새 결함 미발견 |
| 213 | 배열 이동·차 연산 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | 배열 이동은 미분 EGF 대응; 값 차는 ℤ. | 정의 대조; 새 결함 미발견 |
| 214 | 도착 커널 증가량 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | m,j 영역 유지; kernelGain의 부호 근거 있음. | 정의 대조; 새 결함 미발견 |
| 215 | 도착 전달 잔여 | ke2436447b98547689b08023d2935b621/glossary-proposals.md | J−Z¹ 잔여; 전칭 Δ 부호는 결론 아님. | 정의 대조; 새 결함 미발견 |
| 216 | 대칭 폭 원천 | kcee4fdfe71574e5ab1b3a1c16c325818/glossary-proposals.md | q≤r≤2q에서만 양수 원천 분해. | 정의 대조; 새 결함 미발견 |
| 217 | 대칭 폭 원천의 전체 항 | kcee4fdfe71574e5ab1b3a1c16c325818/glossary-proposals.md | 분모 r+1은 계승 정규화와 양립. | 정의 대조; 새 결함 미발견 |
| 218 | 대칭 폭 원천의 가운데 항 | kcee4fdfe71574e5ab1b3a1c16c325818/glossary-proposals.md | r=2q의 안쪽 합은 실제 빈 합. | 정의 대조; 새 결함 미발견 |
| 219 | 폭 원천 전이 응답 | kcee4fdfe71574e5ab1b3a1c16c325818/glossary-proposals.md | 일반 j,S 정의와 j=0 정수 원천 형식 보증 구별. | 정의 대조; 새 결함 미발견 |
| 220 | 폭 원천 4차 이득 함수 | kcee4fdfe71574e5ab1b3a1c16c325818/glossary-proposals.md | j=1,…,4 응답 선형결합; 원 부호 자체 아님. | 정의 대조; 새 결함 미발견 |
| 221 | 대칭 폭 원천의 끝띠 하계 | kcee4fdfe71574e5ab1b3a1c16c325818/glossary-proposals.md | 양 끝띠의 합집합이라 중복 한 번만 셈. | 정의 대조; 새 결함 미발견 |
| 222 | 끝띠 폭 비교값 | kcee4fdfe71574e5ab1b3a1c16c325818/glossary-proposals.md | 분기 보정 Binc 포함; m 충분히 클 때만 4차 하계 동일. | 수정/보완 F4 |
| 223 | 폭 전이의 매개변수 계수 | k4ae9589f84b84e11861e1ef456c2e3b5/glossary-proposals.md | 계승 포함 적분 계수; n<r+a+1 소멸. | 정의 대조; 새 결함 미발견 |
| 224 | 정확 손실 정규화 폭 비교비 | k4ae9589f84b84e11861e1ef456c2e3b5/glossary-proposals.md | q−1 응답 분모 양수; 대각 q 단조성 실패 지위 유지. | 정의 대조; 새 결함 미발견 |
| 225 | 골격 크기 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | 실수 문턱 정의와 자연수 q 구현 제한 구별. | 정의 대조; 새 결함 미발견 |
| 226 | 문턱 꼭짓점 수 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | 같은 크기 부분나무 서로소로 qe≤n. | 정의 대조; 새 결함 미발견 |
| 227 | 골격 잎 수 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | 골격 잎=큰 자식 없는 큰 꼭짓점; 빈 골격 동치. | 정의 대조; 새 결함 미발견 |
| 228 | 조건부 도착 숲 법칙 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | 분모 양수; 정수 y에서 원 A로 정규화. | 정의 대조; 새 결함 미발견 |
| 229 | Gibbs 성분 가중 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | 성분 크기 s의 s! 정규화; A₀=1 사용. | 정의 대조; 새 결함 미발견 |
| 230 | 골격 잎 수별 차분 기여 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | 같은 숲의 세 가중치를 한 λ 부류에서 뺌. | 정의 대조; 새 결함 미발견 |
| 231 | 정규화 이득 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | q²Γ⁺/A; 양수 분모로 부호 보존. | 정의 대조; 새 결함 미발견 |
| 232 | 정규화 손실 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | q²Γ⁻/A; 단조성은 항등식만으로 안 나옴. | 정의 대조; 새 결함 미발견 |
| 233 | 부분나무 크기 묶음별 정확 개수 | ka1c3633303ca4d7fb91d8a309579022b/glossary-proposals.md | 숲 크기 중복집합으로 원 PF를 분류. | 정의 대조; 새 결함 미발견 |
| 234 | 단항 원천 응답 매개변수 다항식 | k41df00b303bc4da78d9d610e8bcf85ae/glossary-proposals.md | X 계수 추출 κ; 재귀의 두 T 인자 역할 구별. | 정의 대조; 새 결함 미발견 |
| 235 | 절단 전 대칭 폭 원천 | k41df00b303bc4da78d9d610e8bcf85ae/glossary-proposals.md | q=0 포함 형식 정의; 원천 양수성의 제한과 구별. | 정의 대조; 새 결함 미발견 |
| 236 | 가중 폭 원천 유한 합 | k41df00b303bc4da78d9d610e8bcf85ae/glossary-proposals.md | r≤n−2,a≤n−r−1의 두 유한 합 끝점. | 정의 대조; 새 결함 미발견 |
| 237 | 유한 순서 라벨 감소 숲 | k1b4bb39af602435783a027a919ef8943/glossary-proposals.md | Option 가상 뿌리와 원 0 표현이 동치. | 정의 대조; 새 결함 미발견 |
| 238 | 부모 함수 조상 관계 | k1b4bb39af602435783a027a919ef8943/glossary-proposals.md | 반사 폐포여서 자기 자신 포함. | 정의 대조; 새 결함 미발견 |
| 239 | 자손 닫힘 성질 | k1b4bb39af602435783a027a919ef8943/glossary-proposals.md | 부모 폐쇄 아닌 자손 폐쇄; 제한 크기 보존 조건. | 정의 대조; 새 결함 미발견 |
| 240 | 유한 순서 라벨 감소 숲 가중합 | k1b4bb39af602435783a027a919ef8943/glossary-proposals.md | 자연수 w의 실제 숲 합; NNReal Eq와 계수환 구별. | 정의 대조; 새 결함 미발견 |
| 241 | 최대 라벨 분해 자료 | k1b4bb39af602435783a027a919ef8943/glossary-proposals.md | 최대 라벨 자손 집합과 그 여집합의 양방향 분해. | 정의 대조; 새 결함 미발견 |
| 243 | 적중 축약 경로 인자 | k2874758a73b749c0b8af17fcc1be6660/glossary-proposals.md | 균등 일반 숲·독립 균등 부착점; d=0 빈 곱1. | 정의 대조; 새 결함 미발견 |
| 244 | 균등 부착점 평균 깊이 | k2874758a73b749c0b8af17fcc1be6660/glossary-proposals.md | 경로에서 가상 뿌리 제외; d=0 깊이0. | 정의 대조; 새 결함 미발견 |
| 245 | 균등 숲 문턱 표시 수 | k2874758a73b749c0b8af17fcc1be6660/glossary-proposals.md | 일반 숲 위 문턱 표시 수; 감소 숲 합과 다른 가중치. | 정의 대조; 새 결함 미발견 |
| 246 | 균등 숲 순서쌍 표시 수 | k2874758a73b749c0b8af17fcc1be6660/glossary-proposals.md | 순서쌍이라 a(a−1); 사슬 해석에는 x>n/2 필요. | 정의 대조; 새 결함 미발견 |
| 247 | Cayley 보조 계수 | k2874758a73b749c0b8af17fcc1be6660/glossary-proposals.md | 양의 정수 j만; 음수 보조0은 본 영역 아님. | 정의 대조; 새 결함 미발견 |
| 248 | 골격 크기별 정규화 이득 값 | k2874758a73b749c0b8af17fcc1be6660/glossary-proposals.md | 정규화 q²; Eζ 관계의 2x>n 제한 유지. | 정의 대조; 새 결함 미발견 |
| 249 | 자손 집합 | k0c2f8df2c56e4828bbf691cacca83b2a/glossary-proposals.md | 자기 자신 포함 자손 집합; 크기가 t_v. | 정의 대조; 새 결함 미발견 |
| 250 | 골격 잎 집합 | k0c2f8df2c56e4828bbf691cacca83b2a/glossary-proposals.md | 자연수 문턱 골격 잎; 일반 실수 λ 정의와 제한 관계. | 정의 대조; 새 결함 미발견 |
| 251 | 한 숲의 차분 기여 | k0c2f8df2c56e4828bbf691cacca83b2a/glossary-proposals.md | 세 곱의 차는 정수; n=0 구현0을 b₀와 동일시 안 함. | 정의 대조; 새 결함 미발견 |
| 252 | 소부분나무 가중 결합 계수 | k0c2f8df2c56e4828bbf691cacca83b2a/glossary-proposals.md | 작은 t만 곱한 계수; q^(a+e) 복원 필요. | 정의 대조; 새 결함 미발견 |
| 253 | 골격·적중 성분 다항식 | k0c2f8df2c56e4828bbf691cacca83b2a/glossary-proposals.md | 비음수 계수의 F; 원 A 평가와 부호 문제 구별. | 정의 대조; 새 결함 미발견 |
| 255 | 거듭제곱 중앙차 | k0c2f8df2c56e4828bbf691cacca83b2a/glossary-proposals.md | a=0,1의 계승 인자0; 음의 지수 표기는 유리수 해석. | 정의 대조; 새 결함 미발견 |
| 256 | 골격·연속 적중 동시 표시 다항식 | kb29a863507944e8d9442e6cd0a3f1d8f/glossary-proposals.md | e_(q+1) 추가 정보; m<2q 영역 유지. | 정의 대조; 새 결함 미발견 |
| 257 | 현재 골격의 전진 곡률 | kb29a863507944e8d9442e6cd0a3f1d8f/glossary-proposals.md | 현재 q를 고정한 U 전진 차분; 다음 Γ와 다름. | 정의 대조; 새 결함 미발견 |
| 258 | 다음 정확 적중 보정 | kb29a863507944e8d9442e6cd0a3f1d8f/glossary-proposals.md | F(q+2,q)와 Aₙ,q+1 차; 다음 문턱을 섞지 않음. | 정의 대조; 새 결함 미발견 |
| 259 | 합친 수송 행렬식 | kb29a863507944e8d9442e6cd0a3f1d8f/glossary-proposals.md | hM≥0은 명시 가정; 무조건 U 아님. | 정의 대조; 새 결함 미발견 |
| 260 | 소부분나무 기초 가중치 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | 빈 곱1; q를 넘는 크기는 이 기초 곱에서 제외. | 정의 대조; 새 결함 미발견 |
| 261 | 표시 2차 이득 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | U 두 번 미분; a(a−1)의 계승 인자. | 정의 대조; 새 결함 미발견 |
| 262 | 표시 정확 손실 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | Y=0에서 적중1,2만 남음; 1/2는 짝수 계수로 정수. | 정의 대조; 새 결함 미발견 |
| 263 | 표시 2차 하계 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | 원 부등식은 2Δ≥2L; 비음수 L은 미증명. | 정의 대조; 새 결함 미발견 |
| 264 | 표시 원천 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | 자식 s−1≤m−1로 L 정의역 안; F(0,q) 대체 적합. | 정의 대조; 새 결함 미발견 |
| 265 | 원 차분 전달 원천 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | s−1≥q와 q≥2로 모든 A 인수 유효. | 정의 대조; 새 결함 미발견 |
| 266 | 원 차분 전달 핵 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | 자식 n<r은 보조0; n=r에서1. | 정의 대조; 새 결함 미발견 |
| 267 | 비절단 문턱 표시합 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | 표시 꼭짓점 인자만 제거; 절단 없는 나머지 곱. | 정의 대조; 새 결함 미발견 |
| 268 | 대칭 홀수 잔여 | k7a6fb5f6105e475dab570454a8d5ef85/glossary-proposals.md | 홀수 이항항의 첫 미분 제거라 잔여 비음수. | 정의 대조; 새 결함 미발견 |
| 269 | 연속 블록 표시 다항식 | k716f5d11dad24f78a224774000d9f0b0/glossary-proposals.md | 빈 구간1; z=1에서 정규화 응답. | 정의 대조; 새 결함 미발견 |
| 270 | 첫 칸 복원 표시 다항식 | k716f5d11dad24f78a224774000d9f0b0/glossary-proposals.md | 삭제 뒤 한 칸 수 표시; 전체 분할 z표시와 다름. | 정의 대조; 새 결함 미발견 |
| 271 | 블록 층 말단 행렬식 | k716f5d11dad24f78a224774000d9f0b0/glossary-proposals.md | 계승 배율 필요; 말단 괄호와 전체 행렬식 구별. | 정의 대조; 새 결함 미발견 |
| 272 | 큰 연결 성분 수 | k9a3297b965b24ea7a87eb1a666b8cd1a/glossary-proposals.md | 뿌리의 t>q는 큰 연결 성분 개수. | 정의 대조; 새 결함 미발견 |
| 273 | 큰 연결 성분 수별 성분 다항식 | k9a3297b965b24ea7a87eb1a666b8cd1a/glossary-proposals.md | j=0 iff 큰 부분나무0; m<3(q+1)에서 세 부류. | 정의 대조; 새 결함 미발견 |
| 274 | 성분 세 평가 차 연산 | k9a3297b965b24ea7a87eb1a666b8cd1a/glossary-proposals.md | 일반 다항식 선형 평가 차; 1에 적용하면0. | 정의 대조; 새 결함 미발견 |
| 275 | 두 큰 성분 보존 원천 | k9a3297b965b24ea7a87eb1a666b8cd1a/glossary-proposals.md | m≤2q+3; 두 큰 성분 보존항과 원천 부호 구별. | 정의 대조; 새 결함 미발견 |
| 276 | 문턱 지수 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | n=0 빈 합0; Λ₀=∞는 양수 크기만. | 정의 대조; 새 결함 미발견 |
| 277 | 복제 문턱 함수 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | ∏t/T 숲 법칙의 확률; W와 T 인자 구별. | 정의 대조; 새 결함 미발견 |
| 278 | 복제 최대 변위 분포 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | ℓ=0 별도 차분; 합1이며 r=1에 b/T. | 정의 대조; 새 결함 미발견 |
| 279 | 연속 문턱 창 개수 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | A연속 창 차; 확률은 다시 T로 나눔. | 정의 대조; 새 결함 미발견 |
| 280 | 로그–로그 오목성 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | 끝거리 로그 좌표의 기울기 방향 확인; 단봉 함의 옳음. | 정의 대조; 새 결함 미발견 |
| 281 | 최댓값 면적 밀도 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | 면적 밀도 U표현은 원 제안과 같음; 외부 논문 새 대조 안 함. | 정의 대조; 새 결함 미발견 |
| 282 | 극한 최대 변위 밀도 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | Laplace 도함수와 (3/2)y^(1/2) 인자. | 정의 대조; 새 결함 미발견 |
| 283 | 로그 시계 핵 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | exp 변수치환으로 적분 Γ(1/3), log곡률 −e^u. | 정의 대조; 새 결함 미발견 |
| 284 | 연속 약단봉성 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | 열린 구간 내부 최대점 존재를 요구하는 정의. | 정의 대조; 새 결함 미발견 |
| 285 | 연속 엄격 단봉성 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | 엄격 단봉 정의에 이계도함수 조건은 없음. | 정의 대조; 새 결함 미발견 |
| 286 | 극한분포 보조변수 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | ν의 한 실현 변수; 법칙 자체와 중복 객체 아님. | 정의 대조; 새 결함 미발견 |
| 287 | 기울인 면적 함수 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | x^c 기울임, 확률밀도 정규화 아님. | 정의 대조; 새 결함 미발견 |
| 299 | 브라운 최댓값과정 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | t=0에도 sup0=0; 경로 [0,∞) 필요. | 정의 대조; 새 결함 미발견 |
| 300 | 최댓값 면적과정 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | 적분 위끝 t; t=1에서 Z. | 정의 대조; 새 결함 미발견 |
| 301 | 척도 격자간격 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | (n+1) 척도 사용; n으로 조용히 대체 안 함. | 정의 대조; 새 결함 미발견 |
| 302 | 끝거리 좌표 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | n+1−ℓ 전체에 δ 곱; 실제 자리와 다른 좌표. | 정의 대조; 새 결함 미발견 |
| 303 | 최대 변위 점확률 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | 원 점확률 b/T; 양수 T. | 정의 대조; 새 결함 미발견 |
| 304 | 밀도 근사 잔차 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | 잔차의 작음은 정의에 포함하지 않음. | 정의 대조; 새 결함 미발견 |
| 310 | 극한 밀도 최대점 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | 다른 좌표의 최대점에서 단조 변수변환; 비형식 수용 범위. | 정의 대조; 새 결함 미발견 |
| 311 | 역면적 시계 | k79ddad1bf51547cd86cce1308aac35c1/glossary-proposals.md | 거의 확실한 면적의 엄격 증가·발산으로 도달시간 유일. | 정의 대조; 새 결함 미발견 |
| 312 | 가장 큰 성분 크기 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | 모든 t의 max는 뿌리 성분 max; 새 구현 누락 F3. | 수정/보완 F3 |
| 313 | 숲 조건부 복제 누적함수 | kb0b4ce4e999f41b3821a41a4d3bbe87f/glossary-proposals.md | 0의 누적값0, y≥n에서1; 숲 고정 법칙. | 정의 대조; 새 결함 미발견 |
| 314 | 숲 조건부 복제 행 | kb0b4ce4e999f41b3821a41a4d3bbe87f/glossary-proposals.md | 숲별 누적차; 혼합에는 ∏t/T 가중 필요. | 정의 대조; 새 결함 미발견 |
| 315 | 시계 조건부 최대 변위 분포 | kb0b4ce4e999f41b3821a41a4d3bbe87f/glossary-proposals.md | Λℓ+1≤τ<Λℓ 반열린 구간이 분할. | 정의 대조; 새 결함 미발견 |
| 316 | 거듭제곱 면적 시계 변수 | k897ef751296e4645b92f7c47695977cd/glossary-proposals.md | α=3/2에 ν 변수; 독립성 유지. | 정의 대조; 새 결함 미발견 |
| 317 | 거듭제곱 면적 시계 밀도 | k897ef751296e4645b92f7c47695977cd/glossary-proposals.md | 변수변환의 Jacobian αy^(α−1); α>0 전체. | 정의 대조; 새 결함 미발견 |
| 323 | 경로 역면적 시계 밀도 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | 경로 조건부 밀도; 모든 연속 경로의 정규화 주장 아님. | 정의 대조; 새 결함 미발견 |
| 324 | 시계 고정 극한 밀도 | k2d51fc12f1254808a99f42f03fe5224b/glossary-proposals.md | τ고정 Jacobian으로 τ^(−2/3) 인자 확인. | 정의 대조; 새 결함 미발견 |
| 325 | 복제 비정규화 누적합 | k46d25e2fa94842ba880225ee0a0666b9/glossary-proposals.md | (0,0) 미지정 보존; 새 실제 숲 구현 누락 F3. | 수정/보완 F3 |
| 326 | 복제 뿌리 인수 | k46d25e2fa94842ba880225ee0a0666b9/glossary-proposals.md | s=0 별도0; 음수 거듭제곱 밑0 회피. | 수정/보완 F3 |
| 327 | 복제 인접 차 | k46d25e2fa94842ba880225ee0a0666b9/glossary-proposals.md | ℓ=0은 b₁−b₀; Δₙ,₀를 만들지 않음. | 수정/보완 F3 |
| 328 | 복제 마지막 차 볼록화 | k46d25e2fa94842ba880225ee0a0666b9/glossary-proposals.md | c,b,d>0; r 모든 실수의 지수합. | 정의 대조; 새 결함 미발견 |
| 329 | 복제 마지막 차 영점 | k46d25e2fa94842ba880225ee0a0666b9/glossary-proposals.md | 유일 양의 영점; ρ>1은 별도 수용 결과. | 정의 대조; 새 결함 미발견 |
| 331 | 복제 차의 이중 누적 핵 | k46d25e2fa94842ba880225ee0a0666b9/glossary-proposals.md | 각 숲의 log밑=−Λ; ℓ=0 마지막 경첩항 제거. | 정의 대조; 새 결함 미발견 |
| 334 | 갱신 정규화 전체 계수 | k4b37ac60c05b499ab584ccb775bc7267/glossary-proposals.md | j=0 값1; T/(j+1)! 척도. | 정의 대조; 새 결함 미발견 |
| 335 | 끝거리 누적확률 | k4b37ac60c05b499ab584ccb775bc7267/glossary-proposals.md | N≥3,m≤floor(N/2)에서 문턱≥0. | 정의 대조; 새 결함 미발견 |
| 336 | 갱신 교대층 | k4b37ac60c05b499ab584ccb775bc7267/glossary-proposals.md | R_i≤m라 분모 양수; β 인수 모두 양수. | 정의 대조; 새 결함 미발견 |
| 337 | 균질 갱신층 | k4b37ac60c05b499ab584ccb775bc7267/glossary-proposals.md | k=0 모든 정수 m에1; k≥1의 음수 m만0. | 정의 대조; 새 결함 미발견 |
| 338 | 갱신층 계수 | k4b37ac60c05b499ab584ccb775bc7267/glossary-proposals.md | k=0 빈 곱1; 양수 계수와 극한 주장 분리. | 정의 대조; 새 결함 미발견 |
