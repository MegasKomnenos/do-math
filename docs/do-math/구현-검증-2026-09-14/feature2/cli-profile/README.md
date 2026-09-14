# 실제 CLI 파일 도구의 선택

`unelevated-relative-failure`는 CLI가 상대 경로를 PowerShell 설치 디렉터리에서 해석해 쓰기가 거부된 사례다. `unelevated-absolute-failure`는 정확한 절대 작업경로와 workdir를 주어도 workspace-write에서 쓰기가 거부된 사례다. 각 request와 stdout·stderr가 실제 설정·경로·오류를 보존한다.

[local-access-pass](local-access-pass/report.json)는 `danger-full-access`와 Windows Job에서 지정 작업 폴더의 실제 파일 쓰기·독립 읽기를 확인했다. 보고의 scratch 디렉터리 이름에 남은 unelevated 문자열은 실제 프로필 이름이 아니다. 실제 설정은 request.json과 보고의 profile 필드로 확인한다.

현재 실행기는 이 로컬 권한 구성을 사용한다. 별도 세션·작업경로·선별 입력과 실행기의 권한·판정 검사는 유지하며, 강한 호스트 접근 격리는 주장하지 않는다. Elevated 모드의 도우미 오류와 파일 쓰기 실패는 [별도 관찰 시험](../observation/elevated-failure/report.json)에 있다.
