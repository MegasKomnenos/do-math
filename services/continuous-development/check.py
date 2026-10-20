"""Session-invoked structural checks. The dispatcher never imports this module."""

import argparse
import json
import ntpath
import re
import sys
from pathlib import Path


class Invalid(ValueError):
    pass


def need(condition, where, message):
    if not condition:
        raise Invalid(f"{where}: {message}")


def text(value, where):
    need(isinstance(value, str) and bool(value.strip()), where, "nonempty string required")
    return value


def choice(value, values, where):
    need(isinstance(value, str) and value in values.split(), where, f"expected {values}")


def ident(value, prefix, where):
    text(value, where)
    pattern = rf"{prefix}[1-9][0-9]*" if prefix else r"[a-z0-9]+(?:-[a-z0-9]+)*"
    need(re.fullmatch(pattern, value), where, f"expected ID matching {pattern}")
    return value


def obj(value, keys, where, optional=""):
    need(isinstance(value, dict), where, "object required")
    required = set(keys.split())
    need(required <= set(value) <= required | set(optional.split()), where,
         f"required keys: {keys or '(none)'}; optional keys: {optional or '(none)'}")
    return value


def rows(value, keys, where, optional=""):
    need(isinstance(value, list), where, "array required")
    for i, row in enumerate(value):
        obj(row, keys, f"{where}[{i}]", optional)
    return value


def strings(value, where):
    need(isinstance(value, list), where, "string array required")
    for i, item in enumerate(value):
        text(item, f"{where}[{i}]")
    need(len(set(value)) == len(value), where, "duplicate value")
    return value


def indexed(items, key, where):
    result = {}
    for row in items:
        value = text(row[key], f"{where}.{key}")
        need(value not in result, where, f"duplicate {key}: {value}")
        result[value] = row
    return result


def read(path):
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise Invalid(f"{path}: {exc}") from exc


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, path, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise Invalid(f"{path}: invalid JSON constant: {value}")

    try:
        return json.loads(read(path), object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as exc:
        raise Invalid(f"{path}: JSON line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def headings(path):
    """Read the contract's ATX headings, ignoring fenced examples."""
    lines, found, fence = [], [], None
    for raw in read(path).splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", raw)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            lines.append(raw)
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]))
            lines.append(raw)
            continue
        lines.append(raw)
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", raw)
        if match:
            found.append((len(match[1]), match[2], len(lines) - 1))
    result = []
    for i, (level, title, start) in enumerate(found):
        end = next((pos for lev, _, pos in found[i + 1:] if lev <= level), len(lines))
        result.append((level, title, "\n".join(lines[start + 1:end]).strip()))
    return result


def ids(path, prefix, level):
    result = set()
    for lev, title, body in headings(path):
        match = re.match(rf"^({prefix}[1-9][0-9]*)(?:\s+)(.+)$", title)
        if match:
            need(lev == level, path, f"{match[1]} must use {'#' * level}")
            need(match[1] not in result, path, f"duplicate ID: {match[1]}")
            need(body, path, f"{match[1]} has no content")
            result.add(match[1])
    return result


def relative(root, value, where, allow_dot=False):
    text(value, where)
    need("\\" not in value and not ntpath.splitdrive(value)[0], where, "use root-relative / paths")
    need(not value.startswith("/") and "#" not in value and ":" not in value, where, "relative path required")
    parts = value.rstrip("/").split("/")
    need((allow_dot and value == ".") or all(p not in ("", ".", "..") for p in parts), where, "invalid path component")
    need(not any(ord(c) < 32 for c in value), where, "control character in path")
    path = (root / value).resolve()
    need(path.is_relative_to(root), where, "path resolves outside its root")
    return path


class Check:
    def __init__(self, repo, records):
        self.repo = Path(repo).resolve()
        self.records = Path(records).resolve()
        need(self.repo.is_dir(), self.repo, "project directory missing")
        need(self.records.is_dir(), self.records, "records directory missing")
        need(not self.repo.is_relative_to(self.records), self.records, "records must not contain the project root")

    def phase_dir(self, phase):
        ident(phase, "", "phase")
        return relative(self.records, f"phases/{phase}", "phase")

    def ref(self, value, where, directory=False):
        text(value, where)
        scope, sep, rest = value.partition(":")
        need(sep and scope in ("repo", "run"), where, "reference must start with repo: or run:")
        name, fragment, anchor = rest.partition("#")
        root = self.repo if scope == "repo" else self.records
        path = relative(root, name, where, allow_dot=directory)
        need(path.is_dir() if directory else path.is_file(), where, f"missing {'directory' if directory else 'file'}: {path}")
        if fragment:
            need(not directory and re.fullmatch(r"[CSAG][1-9][0-9]*", anchor), where, "invalid heading reference")
            level = 2 if anchor[0] in "CS" else 3
            need(anchor in ids(path, anchor[0], level), where, f"missing heading: {anchor}")
        return path

    def refs(self, value, where, required=False):
        strings(value, where)
        need(not required or value, where, "at least one reference required")
        for reference in value:
            self.ref(reference, where)

    def common(self):
        settings_path = self.records / "settings.json"
        if settings_path.exists():
            settings = obj(load(settings_path), "manager", settings_path)
            selection = obj(settings["manager"], "", f"{settings_path}: manager", "model effort")
            for key, value in selection.items():
                text(value, f"{settings_path}: manager.{key}")
        context = self.records / "context.md"
        need(ids(context, "C", 2), context, "at least one C item required")
        need(ids(context, "G", 3), context, "at least one G criterion required")
        for name in ("plan.md", "seams.md"):
            text(read(self.records / name), self.records / name)
        return ids(self.records / "seams.md", "S", 2)

    def objective(self, directory, task):
        path = directory / "tasks" / task / "objective.md"
        sections = [(title, body) for level, title, body in headings(path) if level == 2]
        expected = ["목적과 역할", "완료 조건", "판단과 경계", "검증 방법"]
        need([title for title, _ in sections] == expected, path, f"required sections in order: {expected}")
        for title, body in sections:
            need(body, path, f"empty section: {title}")
        acceptance = ids(path, "A", 3)
        need(acceptance, path, "at least one A criterion required")
        active = None
        for level, title, _ in headings(path):
            if level == 2:
                active = title
            if re.match(r"A[1-9][0-9]*\s", title):
                need(active == "완료 조건", path, "A criteria belong in 완료 조건")
        return acceptance

    def spec(self, phase):
        directory = self.phase_dir(phase)
        path = directory / "phase.json"
        spec = obj(load(path), "kind purpose tasks", path)
        choice(spec["kind"], "work review", f"{path}: kind")
        text(spec["purpose"], f"{path}: purpose")
        tasks = rows(spec["tasks"], "id inputs writes provides uses", f"{path}: tasks", "model effort")
        need(tasks, path, "phase requires at least one task")
        indexed(tasks, "id", path)
        for task in tasks:
            ident(task["id"], "", path)
            for key in ("model", "effort"):
                if key in task:
                    text(task[key], f"{path}: {task['id']}.{key}")
            for name in ("inputs", "writes", "provides", "uses"):
                strings(task[name], f"{path}: {task['id']}.{name}")
            for seam in task["provides"] + task["uses"]:
                ident(seam, "S", path)
            need(spec["kind"] != "review" or not task["writes"], path, "review tasks cannot write project files")
            self.objective(directory, task["id"])
        return spec

    def scope(self, value, where):
        path = relative(self.repo, value, where)
        need(not any(c in value for c in "*?[]"), where, "glob write scopes are not supported")
        is_dir = value.endswith("/")
        need(not path.is_dir() or is_dir, where, "directory write scope must end in /")
        need(not path.is_file() or not is_dir, where, "file write scope cannot end in /")
        return path, is_dir

    @staticmethod
    def includes(scope, path):
        root, is_dir = scope
        return path == root or (is_dir and path.is_relative_to(root))

    def phase(self, phase):
        seams = self.common()
        directory, spec = self.phase_dir(phase), self.spec(phase)
        need((directory / "logs").is_dir(), directory, "logs directory missing")
        scopes, providers = [], set()
        for task in spec["tasks"]:
            where = f"{directory / 'phase.json'}: {task['id']}"
            self.refs(task["inputs"], f"{where}.inputs")
            need(set(task["provides"] + task["uses"]) <= seams, where, "unknown seam ID")
            need(not providers.intersection(task["provides"]), where, "multiple providers for a seam in one phase")
            providers.update(task["provides"])
            need((directory / "tasks" / task["id"] / "evidence").is_dir(), where, "evidence directory missing")
            for value in task["writes"]:
                scope = self.scope(value, where)
                for reserved in (self.records, Path(__file__).resolve().parent):
                    need(not scope[0].is_relative_to(reserved) and not self.includes(scope, reserved), where, "write scope overlaps records or engine")
                for owner, previous in scopes:
                    need(not self.includes(previous, scope[0]) and not self.includes(scope, previous[0]), where, f"write scope overlaps {owner}: {value}")
                scopes.append((task["id"], scope))
        return spec

    def report(self, phase, task_id):
        directory, spec = self.phase_dir(phase), self.spec(phase)
        tasks = {task["id"]: task for task in spec["tasks"]}
        need(task_id in tasks, directory, f"unknown task: {task_id}")
        task = tasks[task_id]
        path = directory / "tasks" / task_id / "report.json"
        data = obj(load(path), "status narrative acceptance changes seams findings checks", path)
        choice(data["status"], "complete partial blocked", f"{path}: status")
        text(data["narrative"], f"{path}: narrative")
        acceptance = rows(data["acceptance"], "id result detail evidence", f"{path}: acceptance")
        need(set(indexed(acceptance, "id", path)) == self.objective(directory, task_id), path, "acceptance must cover exactly the assigned A IDs")
        for row in acceptance:
            choice(row["result"], "pass fail not_run", path)
            text(row["detail"], path)
            self.refs(row["evidence"], path, required=row["result"] == "pass")
        passed = all(row["result"] == "pass" for row in acceptance)
        need((data["status"] == "complete") == passed, path, "complete must match all A criteria passing")
        changes = rows(data["changes"], "path detail", f"{path}: changes")
        indexed(changes, "path", path)
        scopes = [self.scope(value, path) for value in task["writes"]]
        for row in changes:
            changed = relative(self.repo, row["path"], path)
            need(not row["path"].endswith("/") and not changed.is_dir(), path, "changes must name files")
            need(any(self.includes(scope, changed) for scope in scopes), path, f"change outside writes: {row['path']}")
            text(row["detail"], path)
        seams = rows(data["seams"], "id result detail evidence", f"{path}: seams")
        need(set(indexed(seams, "id", path)) == set(task["provides"] + task["uses"]), path, "seams must cover exactly provides and uses")
        for row in seams:
            choice(row["result"], "conforms deviation not_checked", path)
            text(row["detail"], path)
            self.refs(row["evidence"], path, required=row["result"] == "conforms")
        findings = rows(data["findings"], "id kind detail evidence affects next_action", f"{path}: findings")
        indexed(findings, "id", path)
        for row in findings:
            ident(row["id"], "F", path)
            choice(row["kind"], "fact decision assumption issue question", path)
            text(row["detail"], path)
            text(row["next_action"], path)
            self.refs(row["evidence"], path)
            self.refs(row["affects"], path)
        checks = rows(data["checks"], "command cwd result exit_code evidence detail", f"{path}: checks")
        for row in checks:
            text(row["command"], path)
            text(row["detail"], path)
            self.ref(row["cwd"], path, directory=True)
            choice(row["result"], "pass fail not_run", path)
            need(row["exit_code"] is None if row["result"] == "not_run" else type(row["exit_code"]) is int, path, "executed checks need integer exit_code; not_run needs null")
            self.refs(row["evidence"], path, required=row["result"] != "not_run")
        return data

    def handoff(self, phase, candidate="manager.pending.json"):
        self.common()
        directory, spec = self.phase_dir(phase), self.spec(phase)
        path = relative(directory, candidate, directory)
        data = obj(load(path), "next decision reports dispositions context_updates plan_update seam_updates completion", path)
        text(data["decision"], path)
        text(data["plan_update"], path)
        next_phase = data["next"]
        next_dir = None
        if next_phase is not None:
            ident(next_phase, "", path)
            need(next_phase != phase, path, "next must be a new phase")
            next_dir = self.phase_dir(next_phase)
            self.phase(next_phase)
            need(not (next_dir / "manager.json").exists() and not (next_dir / "manager.pending.json").exists(), path, "next phase already has a manager result")
            need(not any(next_dir.glob("tasks/*/report.json")), path, "next phase already has reports")
            need(not any(p.is_file() and p.name != ".gitkeep" for p in (next_dir / "logs").iterdir()), path, "next phase already has session logs")
            need(data["completion"] is None, path, "continuation requires completion: null")
        reports = rows(data["reports"], "task state detail evidence", f"{path}: reports")
        need(set(indexed(reports, "task", path)) == {t["id"] for t in spec["tasks"]}, path, "reports must cover exactly all assigned tasks")
        findings, completed = set(), set()
        for row in reports:
            choice(row["state"], "read missing invalid", path)
            text(row["detail"], path)
            self.refs(row["evidence"], path, required=True)
            report_path = directory / "tasks" / row["task"] / "report.json"
            if row["state"] == "missing":
                need(not report_path.exists(), path, f"report exists: {row['task']}")
            elif row["state"] == "invalid":
                need(report_path.is_file(), path, "invalid report must exist")
                try:
                    self.report(phase, row["task"])
                except Invalid:
                    pass
                else:
                    raise Invalid(f"{path}: report is valid: {row['task']}")
            else:
                report = self.report(phase, row["task"])
                if report["status"] == "complete":
                    completed.add(row["task"])
                findings.update(f"{phase}/{row['task']}/{f['id']}" for f in report["findings"])
            if row["state"] != "read":
                need(next_dir is not None, path, "missing/invalid reports require another phase")
                targets = {f"run:phases/{next_phase}/tasks/{t['id']}/objective.md" for t in self.spec(next_phase)["tasks"]}
                need(targets.intersection(row["evidence"]), path, "missing/invalid report needs a next-task objective reference")
        dispositions = rows(data["dispositions"], "item action destination reason evidence", f"{path}: dispositions")
        need(set(indexed(dispositions, "item", path)) == findings, path, "dispositions must cover exactly all findings from read reports")
        for row in dispositions:
            choice(row["action"], "carry resolve reject", path)
            text(row["reason"], path)
            self.refs(row["destination"], path, required=row["action"] == "carry")
            self.refs(row["evidence"], path, required=True)
            if row["action"] == "carry":
                need(next_dir is not None, path, "cannot finish with carried findings")
                allowed = {self.records / "context.md", self.records / "plan.md"}
                allowed.update(next_dir.glob("tasks/*/objective.md"))
                need(any(self.ref(ref, path) in allowed for ref in row["destination"]), path, "carry destination must be current context/plan or a next objective")
        updates = rows(data["context_updates"], "item action destination reason evidence", f"{path}: context_updates")
        indexed(updates, "item", path)
        current_ids = ids(self.records / "context.md", "C", 2)
        for row in updates:
            ident(row["item"], "C", path)
            choice(row["action"], "add amend replace retire", path)
            text(row["reason"], path)
            self.refs(row["destination"], path, required=row["action"] != "retire")
            self.refs(row["evidence"], path, required=True)
            if row["action"] in ("add", "amend"):
                need(row["item"] in current_ids, path, "updated C item missing from context")
        updates = rows(data["seam_updates"], "id detail evidence", f"{path}: seam_updates")
        indexed(updates, "id", path)
        for row in updates:
            ident(row["id"], "S", path)
            text(row["detail"], path)
            self.refs(row["evidence"], path, required=True)
        if next_phase is None:
            need(spec["kind"] == "review", path, "only a review phase can finish the project")
            need(completed == {t["id"] for t in spec["tasks"]}, path, "all review tasks must be complete")
            completion = obj(data["completion"], "criteria review_reports remaining", f"{path}: completion")
            criteria = rows(completion["criteria"], "criterion result evidence", path)
            expected = {f"run:context.md#{item}" for item in ids(self.records / "context.md", "G", 3)}
            need(set(indexed(criteria, "criterion", path)) == expected, path, "completion must cover exactly all G criteria")
            for row in criteria:
                choice(row["result"], "satisfied", path)
                self.refs(row["evidence"], path, required=True)
            self.refs(completion["review_reports"], path, required=True)
            expected = {f"run:phases/{phase}/tasks/{t['id']}/report.json" for t in spec["tasks"]}
            need(set(completion["review_reports"]) == expected, path, "completion must include every review report")
            strings(completion["remaining"], path)
        return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    for name in ("phase", "report", "handoff"):
        command = commands.add_parser(name)
        for arg in ("repo", "records", "phase"):
            command.add_argument(arg)
        if name == "report":
            command.add_argument("task")
        if name == "handoff":
            command.add_argument("candidate", nargs="?", default="manager.pending.json")
    args = parser.parse_args(argv)
    try:
        checker = Check(args.repo, args.records)
        extra = [args.task] if args.mode == "report" else [args.candidate] if args.mode == "handoff" else []
        getattr(checker, args.mode)(args.phase, *extra)
    except Invalid as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"PASS {args.mode} {args.phase}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
