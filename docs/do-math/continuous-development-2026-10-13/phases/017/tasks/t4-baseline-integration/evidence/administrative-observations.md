# 검사 보조 코드와 실행 환경의 관측

첫 `python -u -B .../evidence/verify_task.py raw`의 실제 도구 종료 코드는 1이었다. 도구가 반환한 traceback은 다음과 같다. 이 명령은 공식 제품 시험이 아니라 보존된 원자료의 보조 재검산이다.

```text
Traceback (most recent call last):
  File "C:\math\docs\do-math\continuous-development-2026-10-13\phases\017\tasks\t4-baseline-integration\evidence\verify_task.py", line 258, in <module>
    if mode=='raw': raw_verify()
                    ^^^^^^^^^^^^
  File "C:\math\docs\do-math\continuous-development-2026-10-13\phases\017\tasks\t4-baseline-integration\evidence\verify_task.py", line 112, in raw_verify
    assert len(children) == 30
           ^^^^^^^^^^^^^^^^^^^
AssertionError
```

초기 집계는 argv에 `-c`가 들어간 모든 호출을 Python child로 분류했다. 보존된 companion-invocations.json에는 Python 30건과 Git 18건이 있고, Git commit의 `-c`도 초기 분류에 포함됐다. Python 실행 파일을 함께 확인하도록 보조 분류만 교정했다. 같은 원자료의 재검산은 verify-raw.command.json의 exit 0과 raw-verification.json에 있다. 기존 TestCase/WORKER/SNAPSHOT/기대값이나 원관측은 변경하지 않았다.

첫 정본 전체 실행 canonical-t4-full에는 작업자가 설정한 저장소 내부의 긴 TEMP/TMP가 전달됐다. boundary/result.json의 Git 계약 시험 네 failure는 Git 없는 임시 경로 또는 .git을 지운 경로가 상위 C:\math 저장소를 찾는 것과 연결되고, SHA-256 시험 두 error는 rev-list의 Filename too long 원오류다. 실제 시험은 저장소 밖 임시 디렉터리의 project_repository_root=None와 .git 제거 후 tracked-path 오류를 기대한다. 근거는 tests/support/port_contracts/git_backend.py의 두 메서드와 tests/boundary/test_port_git_backend.py의 remove_project다.

제품·fixture·기대값을 바꾸지 않고 후속 공식 전체 실행의 TEMP/TMP/TMPDIR만 저장소 밖의 짧은 작업 전용 dm017-* 경로로 지정한다. 첫 실행과 원로그·row·측정은 그대로 보존한다. 이후 실행은 별도 경로이며 첫 실행을 소급 성공으로 바꾸지 않는다. 같은 코드의 새 전체 실행은 이 구체적인 환경 원인의 대조이고 무조건 재시도가 아니다. 확정 판정은 후속 전체 결과와 각 실행 command.json의 실제 환경값에 따른다.

외부 TEMP의 canonical-t4-full-final은 294passed/1error/exit1이었다. Git6건은 모두 passed였고 설치 probe의 subprocess.run에서 WinError267이 났다. 공식 runner는 resource worker의 TEMP를 자기 output/worker/scratch로 다시 지정하므로 parent TEMP만 줄여도 resource fixture의 경로 길이는 별도다.

probe_path_observer.py는 현재 OperatorInstallationProbeTests의 실제 메서드를 정상 unittest lifecycle로 호출하며 subprocess.run을 관측용으로만 감싼다. 실제 프로그램·cwd·cwd.is_dir·문자 수와 반환/예외를 기록하고 cleanup 전에 동결 snapshot을 복사한다. fixture·프로그램·비교/기대값은 재작성하지 않았다. long은 실패 worker TEMP와 같은158자 prefix이고 실제 cwd262자/존재True/WinError267/exit1이다. short는 짧은출력 c4의 worker TEMP와 같은137자 prefix이고 실제 cwd241자/존재True/normalexit0·반려exit1/전체TestCaseexit0이다. 원관측은 probe-long-observation.json과 probe-short-observation.json 및 두 command/stdout/stderr에 있다. 현재 환경의 경로 대조이며 Windows 전체의 보편 상한이나 과거 WinError5 원인을 주장하지 않는다.

그 뒤 공식 전체 --output을 자기 evidence/c4와 m4로 지정한다. parent TEMP는 저장소 밖 짧은 전용 경로를 유지한다. 새 전체 실행은 같은 제품 판본을 전건 검증하며 두 실패 실행의 부분 성공을 합산하지 않는다. 원report/측정과 관측자료는 그대로 둔다.
