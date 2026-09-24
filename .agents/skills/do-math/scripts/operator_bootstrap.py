"""Freeze and start a verified supervisor independently of its repair target."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import uuid


MANIFEST = "bootstrap-manifest.json"
FORMAT = 1
_REPARSE_POINT = 0x400


def _digest(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _ordinary_path(path: Path):
    for part in (path.absolute(), *path.absolute().parents):
        if not part.exists():
            continue
        info = part.lstat()
        if part.is_symlink() or getattr(info, "st_file_attributes", 0) & _REPARSE_POINT:
            raise ValueError("bootstrap path crosses a reparse point: " + str(part))


def _source_files(root: Path):
    files = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in {"__pycache__", ".git", ".lake"} for part in relative.parts):
            continue
        if relative.parts[:2] == ("scripts", "tests") or path.suffix == ".pyc" or relative.as_posix() == MANIFEST:
            continue
        _ordinary_path(path)
        if path.is_file():
            files[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def verify_snapshot(manifest_path: Path):
    _ordinary_path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {"format", "installation_root", "files", "snapshot_sha256"}:
        raise ValueError("invalid bootstrap manifest")
    if manifest["format"] != FORMAT or not isinstance(manifest["files"], dict):
        raise ValueError("unsupported bootstrap manifest")
    basis = {key: manifest[key] for key in ("format", "installation_root", "files")}
    if _digest(basis) != manifest["snapshot_sha256"]:
        raise ValueError("bootstrap manifest identity mismatch")
    root = manifest_path.parent.resolve(strict=True)
    if root.name != manifest["snapshot_sha256"]:
        raise ValueError("bootstrap directory identity mismatch")
    for name, digest in manifest["files"].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or relative.as_posix() != name or ".." in relative.parts or "\\" in name:
            raise ValueError("invalid bootstrap file path")
        target = root.joinpath(*relative.parts)
        _ordinary_path(target)
        if not target.resolve(strict=True).is_relative_to(root) or not target.is_file():
            raise ValueError("bootstrap file escaped its snapshot")
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("bootstrap file hash mismatch: " + name)
    if _source_files(root) != manifest["files"]:
        raise ValueError("bootstrap snapshot has unlisted or missing files")
    return manifest


def freeze(installation_root: Path, workspace: Path):
    """Publish a content-addressed runtime copy; no research state or tasks change."""
    _ordinary_path(installation_root)
    _ordinary_path(workspace)
    installation_root = installation_root.resolve(strict=True)
    workspace = workspace.resolve()
    if not (installation_root / "scripts/do_math/scheduled_operator.py").is_file():
        raise ValueError("installation has no supervisor")
    files = _source_files(installation_root)
    basis = {"format": FORMAT, "installation_root": str(installation_root), "files": files}
    identity = _digest(basis)
    parent = workspace / "operator/bootstrap"
    _ordinary_path(parent)
    parent.mkdir(parents=True, exist_ok=True)
    destination = parent / identity
    if destination.exists():
        verify_snapshot(destination / MANIFEST)
        return {"entrypoint": str(destination / "scripts/operator_bootstrap.py"),
                "manifest": str(destination / MANIFEST), "snapshot_sha256": identity}
    staging = parent / (".building-" + uuid.uuid4().hex)
    staging.mkdir()
    try:
        for name in files:
            source = installation_root.joinpath(*PurePosixPath(name).parts)
            target = staging.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if _source_files(staging) != files or _source_files(installation_root) != files:
            raise ValueError("installation changed while freezing supervisor")
        (staging / MANIFEST).write_text(json.dumps({**basis, "snapshot_sha256": identity},
                                                  ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        try:
            staging.rename(destination)
        except FileExistsError:
            verify_snapshot(destination / MANIFEST)
    finally:
        if staging.exists():
            # Only the fresh staging directory created above can be removed.
            _ordinary_path(staging)
            if staging.resolve().parent != parent.resolve() or not staging.name.startswith(".building-"):
                raise ValueError("invalid bootstrap staging cleanup target")
            shutil.rmtree(staging)
    verify_snapshot(destination / MANIFEST)
    return {"entrypoint": str(destination / "scripts/operator_bootstrap.py"),
            "manifest": str(destination / MANIFEST), "snapshot_sha256": identity}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--freeze" in args:
        parser = argparse.ArgumentParser(description="Freeze the installed supervisor without scheduling it")
        parser.add_argument("--freeze", action="store_true")
        parser.add_argument("--installation-root", type=Path, required=True)
        parser.add_argument("--workspace", type=Path, required=True)
        values = parser.parse_args(args)
        print(json.dumps(freeze(values.installation_root, values.workspace)))
        return 0
    snapshot_root = Path(__file__).resolve().parents[1]
    manifest_path = snapshot_root / MANIFEST
    frozen_location = snapshot_root.parent.name == "bootstrap" and snapshot_root.parent.parent.name == "operator"
    manifest = verify_snapshot(manifest_path) if frozen_location or manifest_path.exists() else None
    if args == ["--bootstrap-info"]:
        print(json.dumps({"mode": "frozen" if manifest else "live", "manifest": manifest}))
        return 0
    # This is a dedicated CLI entrypoint. Its package must come from the verified
    # snapshot beside it, independent of the working directory or live target.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from do_math import scheduled_operator
    if manifest:
        scheduled_operator.LIVE_INSTALLATION_ROOT = Path(manifest["installation_root"])
    return scheduled_operator.main(args)


if __name__ == "__main__":
    raise SystemExit(main())
