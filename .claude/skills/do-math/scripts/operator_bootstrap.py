"""Freeze and start a verified supervisor independently of its repair target."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import uuid


MANIFEST = "bootstrap-manifest.json"
# Settled fingerprints of verified files; a cache beside the manifest, not identity.
MARKS = "bootstrap-fingerprints.json"
FORMAT = 1


def _source_paths(root: Path, file_io):
    # The installation file set is file_io's; the snapshot's own markers are not sources.
    # The root is proved once; each file only below it.
    file_io.no_reparse(root)
    paths = {name: path for name, path in file_io.installation_files(root).items() if name not in {MANIFEST, MARKS}}
    for path in paths.values():
        file_io.no_reparse(path, below=root)
    return paths


def _source_files(root: Path, file_io):
    return {name: file_io.sha256_file(path) for name, path in _source_paths(root, file_io).items()}


def _file_io():
    # The fingerprint primitives ship in this snapshot's own package.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from do_math import file_io
    return file_io


def _json_digest(value):
    # Loaded from the same snapshot package as _file_io(), which put it on sys.path.
    from do_math.values import json_digest
    return json_digest(value)


def _marks(root: Path):
    try:
        value = json.loads((root / MARKS).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def verify_snapshot(manifest_path: Path):
    """Verify the frozen copy; hash only files whose settled fingerprint changed.

    The first verification hashes every file and records settled fingerprints
    beside the manifest. Later starts compare fingerprints (accidental-change
    threat model, design D1) and hash a file again only when it differs.
    """
    file_io = _file_io()
    # Proves the snapshot root and its ancestors; files are checked below the root.
    file_io.no_reparse(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {"format", "installation_root", "files", "snapshot_sha256"}:
        raise ValueError("invalid bootstrap manifest")
    if manifest["format"] != FORMAT or not isinstance(manifest["files"], dict):
        raise ValueError("unsupported bootstrap manifest")
    basis = {key: manifest[key] for key in ("format", "installation_root", "files")}
    if _json_digest(basis) != manifest["snapshot_sha256"]:
        raise ValueError("bootstrap manifest identity mismatch")
    root = manifest_path.parent.resolve(strict=True)
    if root.name != manifest["snapshot_sha256"]:
        raise ValueError("bootstrap directory identity mismatch")
    recorded, settled = _marks(root), {}
    for name, digest in manifest["files"].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or relative.as_posix() != name or ".." in relative.parts or "\\" in name:
            raise ValueError("invalid bootstrap file path")
        target = root.joinpath(*relative.parts)
        file_io.no_reparse(target, below=root)
        if not target.resolve(strict=True).is_relative_to(root) or not target.is_file():
            raise ValueError("bootstrap file escaped its snapshot")
        mark = file_io.file_fingerprint(target)
        stored = file_io.fingerprint_json(mark)
        if recorded.get(name) != stored or not file_io.fingerprint_settled(mark):
            if file_io.sha256_file(target) != digest:
                raise ValueError("bootstrap file hash mismatch: " + name)
        if file_io.fingerprint_settled(mark):
            settled[name] = stored
    if set(_source_paths(root, file_io)) != set(manifest["files"]):
        raise ValueError("bootstrap snapshot has unlisted or missing files")
    if settled != recorded:
        file_io.write_bytes_atomic(root / MARKS, json.dumps(settled, sort_keys=True).encode("utf-8"))
    return manifest


def freeze(installation_root: Path, workspace: Path):
    """Publish a content-addressed runtime copy; no research state or tasks change."""
    file_io = _file_io()
    file_io.no_reparse(installation_root)
    file_io.no_reparse(workspace)
    installation_root = installation_root.resolve(strict=True)
    workspace = workspace.resolve()
    if not (installation_root / "scripts/do_math/scheduled_operator.py").is_file():
        raise ValueError("installation has no supervisor")
    files = _source_files(installation_root, file_io)
    basis = {"format": FORMAT, "installation_root": str(installation_root), "files": files}
    identity = _json_digest(basis)
    parent = workspace / "operator/bootstrap"
    file_io.no_reparse(parent)
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
        if _source_files(staging, file_io) != files or _source_files(installation_root, file_io) != files:
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
            file_io.no_reparse(staging)
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
    installation_root = Path(manifest["installation_root"]) if manifest else snapshot_root
    return scheduled_operator.main(args, installation_root=installation_root)


if __name__ == "__main__":
    raise SystemExit(main())
