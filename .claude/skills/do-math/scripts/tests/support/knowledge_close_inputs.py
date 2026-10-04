"""LeanDouble의 명시 원천 등록으로 만든 합성 출력. 실제 Lean 녹화가 아니다."""
from io import BytesIO
from pathlib import Path
import tempfile

from do_math.lean_evidence import check_file
from support.lean import LeanDouble

SOURCE = 'theorem knowledge_close : True := True.intro'
NAME = 'knowledge_close'


def compiler_output():
    lean = LeanDouble().allow(SOURCE, [NAME], signatures={NAME: NAME + ' : True'},
        dependencies={NAME: {'True': {'type': 'Prop', 'value': None}}},
               declaration_evidence={NAME: {'type': 'True', 'value': None}}, axioms={NAME: []})
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'proposal.lean'
        path.write_bytes(check_file(SOURCE.encode(), [NAME], extract_evidence=True))
        stdout, stderr = BytesIO(), BytesIO()
        with lean.spawn(['synthetic-lean', str(path)], stdout=stdout, stderr=stderr) as process:
            code = process.wait()
        if code != 0 or stderr.getvalue():
            raise AssertionError('명시 등록한 합성 Lean 입력 생성 실패')
        return stdout.getvalue().decode('utf-8')


def parse_base(stdout):
    return {'stdout': stdout, 'stderr': '', 'dependency_closure': {}, 'declaration_evidence': {}}
