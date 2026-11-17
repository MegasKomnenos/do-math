# -*- coding: utf-8 -*-
"""기억/색인.md layer-1 절 끝에 M-0722 줄을 넣는다. 2026-11-17."""
import io
P = r"C:\math\기억\색인.md"
s = io.open(P, encoding="utf-8").read()
assert "M-0722" not in s
line = "- M-0722 [구조 압축 물결 4 — 횡단 단위 H1·H3와 뒤 단계 단위 U14·U15·U16을 병행해 끝내고, 디스크 가득 참과 지도 빌드 막힘을 넘긴 뒤, 9장을 지우고 10장을 남기기로 한 결정 작업자 K6의 결정을 받은 상태를 결정화한다] -- 경고: 디스크 여유는 파견 직후 한 번 본다(55 GB 임시 파일로 여섯 단위가 멈춤; 「완료」 반환 뒤 크기·git diff로 내려앉음 확인); 지도 그림의 틈은 ELK 뿌리 edgeNode·edgeEdge와 통과 선 수로 정해지고 build는 매번 재파생하므로 수리 중에는 빌드.py --정본으로; 히어독 파이썬 문자열의 제어문자 깨짐 — 커밋 전 전수 검사; 사용자 조건 「둘 다 보존」→「하나만 남기자」는 원문으로 적어 앞선 결정과의 관계를 밝힘; 결정 작업자의 결론은 수(진술·깊이·귀납·인증서·여유·배타 영역)로 선다\n"
i = s.find("\n## layer-2")
assert i > 0
s = s[:i].rstrip("\n") + "\n" + line + s[i:]
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
