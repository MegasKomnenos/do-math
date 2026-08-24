# -*- coding: utf-8 -*-
"""런타임 스킬 사본 생성기.

정본 `.claude/skills/`와 타깃 런타임 디렉토리 `.agents/`의 `diff/`
디렉토리를 병합해 타깃의 `skills/` 트리를 생성한다. 타깃 skills 트리는
생성물이며 수기 편집하지 않는다. 절차 정본은 writing-skills
`references/멀티런타임_동기화.md`.

diff/ 디렉토리 구성:
- `_rules.json`  : 기계 변환 규칙(치환·frontmatter 이동·축자 사본 목록)
- `_manifest.json`: 오버레이별 정본 해시 기록(생성기가 관리, 수기 편집 금지)
- `<정본 상대경로>`: 오버레이 문서. 존재하면 그 경로의 생성물을 전문 대체한다.
  정본에 없는 경로의 오버레이는 타깃 전용 추가 문서로 그대로 포함된다.

_rules.json 스키마:
{
  "substitutions": [            // 순서 적용
    {"keep": "리터럴"},          // 이 리터럴을 이후 치환에서 보호
    {"from": "리터럴", "to": "리터럴"}
  ],
  "frontmatter_move": [         // SKILL.md 한정: frontmatter 키를 본문 줄로 이동
    {"key": "argument-hint", "label": "호출 인자"}
  ],
  "verbatim": ["fnmatch 패턴"]   // 변환 없이 정본 바이트 그대로 복사
}

사용:
  python .claude/skills/writing-skills/scripts/build_skill_mirrors.py            # 타깃 생성
  python .claude/skills/writing-skills/scripts/build_skill_mirrors.py --check    # 드리프트 검사(변경 없음)
  python .claude/skills/writing-skills/scripts/build_skill_mirrors.py --bless    # 오버레이 기준 해시 갱신
  python .claude/skills/writing-skills/scripts/build_skill_mirrors.py --target .agents

동작 주의: 빌드 모드는 오버레이 낡음 경고가 있어도 트리를 재생성하고 나서 exit 1을
반환한다(경고 = 미기록이 아니라 재검토 요구). check 모드는 어떤 파일도 쓰지 않는다.
"""
import argparse
import fnmatch
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE_REL = Path(".claude") / "skills"
DEFAULT_TARGETS = [".agents"]
SKIP_DIR_NAMES = {"__pycache__"}
SKIP_SUFFIXES = {".pyc"}
RESERVED = {"_rules.json", "_manifest.json"}


def iter_files(root: Path):
    """스킵 규칙을 적용해 root 아래 파일의 {posix 상대경로: 절대경로}를 돌려준다."""
    out = {}
    if not root.is_dir():
        return out
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in SKIP_DIR_NAMES for part in rel.parts):
            continue
        if p.suffix in SKIP_SUFFIXES:
            continue
        out[rel.as_posix()] = p
    return out


def load_rules(diff_dir: Path):
    rules_path = diff_dir / "_rules.json"
    if not rules_path.is_file():
        raise SystemExit(f"규칙 파일이 없다: {rules_path}")
    rules = json.loads(rules_path.read_text(encoding="utf-8-sig"))
    for entry in rules.get("substitutions", []):
        if not (set(entry) == {"keep"} or set(entry) == {"from", "to"}):
            raise SystemExit(f"_rules.json 치환 항목 형식 위반: {entry}")
    for entry in rules.get("frontmatter_move", []):
        if set(entry) != {"key", "label"}:
            raise SystemExit(f"_rules.json frontmatter_move 항목 형식 위반: {entry}")
    if not all(isinstance(p, str) for p in rules.get("verbatim", [])):
        raise SystemExit("_rules.json verbatim은 문자열 목록이어야 한다")
    return rules


def apply_substitutions(text: str, substitutions):
    """keep 리터럴을 플레이스홀더로 보호한 뒤 from→to를 순서대로 적용한다."""
    protected = []
    for entry in substitutions:
        if "keep" in entry:
            token = "\x00K{}\x00".format(len(protected))
            protected.append((token, entry["keep"]))
            text = text.replace(entry["keep"], token)
        else:
            text = text.replace(entry["from"], entry["to"])
    for token, literal in protected:
        text = text.replace(token, literal)
    return text


def move_frontmatter_keys(text: str, moves):
    """frontmatter의 이동 대상 키를 소거하고 닫는 --- 직후에 라벨 줄로 옮긴다."""
    nl = "\r\n" if text.startswith("---\r\n") else "\n"
    open_marker = "---" + nl
    close_marker = nl + "---" + nl
    if not moves or not text.startswith(open_marker):
        return text
    end = text.find(close_marker, len(open_marker))
    if end == -1:
        return text
    keys = [m["key"] for m in moves]
    labels = {m["key"]: m["label"] for m in moves}
    kept, moved = [], []
    for line in text[len(open_marker):end].split(nl):
        for key in keys:
            if line.startswith(key + ":"):
                moved.append((keys.index(key), labels[key] + ":" + line[len(key) + 1:]))
                break
        else:
            kept.append(line)
    if not moved:
        return text
    moved.sort()
    body = text[end + len(close_marker):]
    return (open_marker + nl.join(kept) + close_marker
            + nl.join(v for _, v in moved) + nl + body)


def transform(rel: str, raw: bytes, rules) -> bytes:
    for pattern in rules.get("verbatim", []):
        if fnmatch.fnmatch(rel, pattern):
            return raw
    try:
        text = raw.decode("utf-8-sig")  # BOM은 소거(잔존 시 frontmatter 인식이 조용히 깨진다)
    except UnicodeDecodeError:
        return raw  # 바이너리는 그대로
    if "\x00" in text:
        raise SystemExit(f"원문에 NUL 문자 포함(플레이스홀더 오염 위험): {rel}")
    text = apply_substitutions(text, rules.get("substitutions", []))
    if rel.endswith("SKILL.md"):
        text = move_frontmatter_keys(text, rules.get("frontmatter_move", []))
    return text.encode("utf-8")


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def build_target(target: str, check: bool, bless: bool) -> tuple[bool, list[str]]:
    """타깃 하나를 생성(또는 검사)한다. (정상 여부, 메시지 목록)을 돌려준다."""
    msgs = []
    ok = True
    tdir = ROOT / target
    diff_dir = tdir / "diff"
    out_root = tdir / "skills"
    rules = load_rules(diff_dir)
    manifest_path = diff_dir / "_manifest.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if manifest_path.is_file() else {"overlays": {}}
    )
    base_files = iter_files(ROOT / BASE_REL)
    overlay_files = {
        rel: p for rel, p in iter_files(diff_dir).items() if rel not in RESERVED
    }

    # 산출 트리 계산
    outputs = {}
    for rel, p in base_files.items():
        outputs[rel] = transform(rel, p.read_bytes(), rules)
    for rel, p in overlay_files.items():
        outputs[rel] = p.read_bytes()  # 오버레이는 축자 우선(정본에 없으면 추가 문서)

    # 오버레이 기준 해시 점검(정본이 움직였는데 오버레이가 그대로인 침묵 낡음 방지)
    new_manifest = {"overlays": {}}
    for rel in sorted(overlay_files):
        if rel not in base_files:
            msgs.append(f"[{target}] 추가 문서 오버레이(정본에 없음): {rel}")
            continue
        cur = sha1(base_files[rel].read_bytes())
        rec = manifest.get("overlays", {}).get(rel)
        if rec is None:
            if check:
                ok = False
                msgs.append(f"[{target}] 오버레이 미등록(빌드 실행으로 기준 해시를 기록해야 낡음 감지가 작동): {rel}")
            else:
                new_manifest["overlays"][rel] = cur
                msgs.append(f"[{target}] 오버레이 신규 등록: {rel}")
        elif rec != cur and not bless:
            new_manifest["overlays"][rel] = rec
            ok = False
            msgs.append(
                f"[{target}] 오버레이 낡음 의심: {rel} — 정본이 변경되었는데 기준 해시가 그대로다. "
                f"오버레이를 재검토·개정한 뒤 --bless로 기준을 갱신하라."
            )
        else:
            new_manifest["overlays"][rel] = cur

    # 기존 트리와 대조
    existing = iter_files(out_root)
    created = [r for r in outputs if r not in existing]
    updated = [r for r in outputs if r in existing and existing[r].read_bytes() != outputs[r]]
    deleted = [r for r in existing if r not in outputs]

    if check:
        for r in created:
            ok = False
            msgs.append(f"[{target}] 드리프트(생성 필요): skills/{r}")
        for r in updated:
            ok = False
            msgs.append(f"[{target}] 드리프트(내용 불일치): skills/{r}")
        for r in deleted:
            ok = False
            msgs.append(f"[{target}] 드리프트(잔존 파일): skills/{r}")
        if not (created or updated or deleted):
            msgs.append(f"[{target}] 드리프트 없음 ({len(outputs)}파일)")
        return ok, msgs

    for r in created + updated:
        dest = out_root / r
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(outputs[r])
    for r in deleted:
        (out_root / r).unlink()
    # 빈 디렉토리 정리
    for d in sorted((x for x in out_root.rglob("*") if x.is_dir()), reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass
    manifest_path.write_text(
        json.dumps(new_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    msgs.append(
        f"[{target}] 생성 {len(created)} · 갱신 {len(updated)} · 삭제 {len(deleted)} "
        f"(총 {len(outputs)}파일)"
    )
    return ok, msgs


def main(argv=None):
    ap = argparse.ArgumentParser(description="런타임 스킬 사본 생성기")
    ap.add_argument("--check", action="store_true", help="변경 없이 드리프트·낡음만 검사")
    ap.add_argument("--bless", action="store_true", help="오버레이 기준 해시를 현 정본으로 갱신")
    ap.add_argument("--target", action="append", choices=DEFAULT_TARGETS,
                    help="특정 타깃만(기본: 전 타깃)")
    args = ap.parse_args(argv)
    if args.check and args.bless:
        ap.error("--check와 --bless는 함께 쓸 수 없다(bless는 빌드 모드에서 manifest를 갱신한다)")
    all_ok = True
    for target in (args.target or DEFAULT_TARGETS):
        ok, msgs = build_target(target, check=args.check, bless=args.bless)
        all_ok = all_ok and ok
        for m in msgs:
            print(m)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
