"""작업자 공개 도구를 같은 프로세스에서 실행하고 원 출력 바이트를 보존한다."""
from contextlib import chdir, redirect_stdout
from io import BytesIO, TextIOWrapper


def invoke_tool(function, workspace, arguments, *, ports, environment):
    buffer = BytesIO()
    output = TextIOWrapper(buffer, encoding='utf-8', write_through=True)
    with chdir(workspace), redirect_stdout(output):
        code = function(arguments, ports=ports, environment=environment)
    raw = buffer.getvalue()
    output.detach()
    return code, raw
