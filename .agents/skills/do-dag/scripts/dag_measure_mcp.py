"""실측기의 MCP 노출 — stdio JSON-RPC, 의존성 없는 순수 파이썬.

Claude는 `.mcp.json`, Codex는 `.agents/config.toml`에서 이 파일을 `dag-measure`
서버로 등재한다. MCP 도구는 서브에이전트에 상속되므로 오케가 파견한 모든 에이전트가
셸 재구현 없이 실측기를 부른다.

프로토콜: 한 줄 = JSON-RPC 메시지 하나(개행 구분). initialize · tools/list ·
tools/call · ping에 답하고 알림은 무시한다. 도구 실행은 dag_measure.main의 stdout을
그대로 담아 낸다 — CLI와 MCP가 같은 증거 블록을 내는 단일 경로다.
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dag_measure  # noqa: E402

_STR = {"type": "string"}
_BOOL = {"type": "boolean"}
_INT = {"type": "integer"}


def _schema(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required}


TOOLS = [
    {
        "name": "count",
        "description": "파일들×패턴의 파일별 계수와 히트 문맥. 계수 주장은 이 블록으로만 보고한다.",
        "inputSchema": _schema(
            {"pattern": _STR, "files": {**_STR, "description": "쉼표 구분+글롭"},
             "regex": _BOOL, "root": _STR},
            ["pattern", "files"],
        ),
    },
    {
        "name": "anchor",
        "description": "축자 문자열의 현재 행 번호와 유일/다중/부재 판정. 행 번호를 전사하지 않는다.",
        "inputSchema": _schema({"text": _STR, "file": _STR, "root": _STR}, ["text", "file"]),
    },
    {
        "name": "table",
        "description": "마크다운 표의 열 계수 검사. 이스케이프 파이프(\\|)를 열로 세지 않는다.",
        "inputSchema": _schema({"file": _STR, "root": _STR}, ["file"]),
    },
    {
        "name": "same",
        "description": "파일들의 내용 해시 군집 — 동문 사본의 갈림 검출. 기본은 개행·꼬리공백 정규화.",
        "inputSchema": _schema({"files": _STR, "raw": _BOOL, "root": _STR}, ["files"]),
    },
    {
        "name": "attrib",
        "description": "worktree 변경 목록과 귀속 목록의 대조 — 미귀속 편집·무변경 귀속을 낸다.",
        "inputSchema": _schema(
            {"worktree": _STR, "attributed": {**_STR, "description": "쉼표 구분 경로"},
             "allow_untracked": _BOOL},
            ["worktree", "attributed"],
        ),
    },
    {
        "name": "changes",
        "description": "HEAD 대비 현존 변경 파일과 삭제 경로를 분리한다. 삭제가 있으면 실패로 닫는다.",
        "inputSchema": _schema(
            {"worktree": _STR, "base": {**_STR, "description": "비교 기준(기본 HEAD)"}},
            ["worktree"],
        ),
    },
    {
        "name": "budget",
        "description": (
            "읽기 + 하네스 기저 + 도구 왕복 + 출력 유보의 합 대 모델 예산"
            "(【예산 · sonnet 200k · opus 250k · fable 250k · gpt-5.6-sol 250k · gpt-5.6-terra 250k · gpt-5.6-luna 250k】) 판정. "
            "저작 행은 자기 출력이 최대 항이므로 저작 예상 바이트를 writes로 준다. "
            "선행이 저작할 산출을 읽어야 하는데 아직 없으면 그 바이트를 pending으로 "
            "준다(저작 행의 writes = 그 소비자의 pending)."
        ),
        "inputSchema": _schema(
            {"files": _STR, "model": _STR,
             "writes": {**_INT, "description": "저작 예상 바이트(생략하면 실측 하한)"},
             "pending": {**_INT, "description": "측정 시점 미존재 정본의 바이트"},
             "root": _STR},
            ["files", "model"],
        ),
    },
]

_FLAGS = {"regex": "--regex", "raw": "--raw", "allow_untracked": "--allow-untracked"}


def _argv(name: str, args: dict) -> list[str]:
    out = [name]
    for key, value in args.items():
        if key in _FLAGS:
            if value:
                out.append(_FLAGS[key])
        elif value is not None:
            out += [f"--{key}", str(value)]
    return out


def call_tool(name: str, args: dict) -> tuple[str, bool]:
    """(블록 텍스트, isError). dag_measure.main을 그대로 태운다."""
    if name not in {t["name"] for t in TOOLS}:
        return f"미지 도구: {name}", True
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = dag_measure.main(_argv(name, args))
    except SystemExit as exc:  # argparse 오류
        return buf.getvalue() + f"\n인자 오류 (exit {exc.code})", True
    except Exception as exc:
        return buf.getvalue() + f"\n실행 실패: {type(exc).__name__}: {exc}", True
    return buf.getvalue().rstrip("\n"), rc != 0


def handle(msg: dict) -> dict | None:
    method = msg.get("method", "")
    msg_id = msg.get("id")
    if msg_id is None:
        return None  # 알림
    if method == "initialize":
        result = {
            "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "dag-measure", "version": "1.0.0"},
        }
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = msg.get("params", {})
        text, is_error = call_tool(params.get("name", ""), params.get("arguments", {}) or {})
        result = {"content": [{"type": "text", "text": text}], "isError": is_error}
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601, "message": f"미지 메서드: {method}"}}
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def main() -> int:
    stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        reply = handle(msg)
        if reply is not None:
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
