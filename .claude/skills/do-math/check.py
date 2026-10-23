"""Check do-math session structure and published references; see protocol.md."""

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from glossary import check_glossary


CATEGORIES = ("plan", "research", "explore", "peer", "review")


class Invalid(ValueError):
    """An expected, actionable protocol error."""


def need(condition, where, message):
    if not condition:
        raise Invalid(f"{where}: {message}")


def obj(value, where):
    need(isinstance(value, dict), where, "expected an object")
    return value


def text(value, where):
    need(isinstance(value, str) and bool(value.strip()), where, "expected nonempty text")
    return value


def items(value, where):
    need(isinstance(value, list), where, "expected an array (use [] when empty)")
    return value


def choice(value, choices, where):
    need(value in choices, where, "expected one of " + ", ".join(choices))


def identifier(value, where):
    text(value, where)
    need(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", value), where,
         "expected an identifier containing letters, digits, _ or -")
    return value


def read_json(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise Invalid(f"{path}: {exc}") from exc
    return obj(data, str(path))


def local_file(root, value, where):
    """Resolve a portable file reference within its publication root."""
    text(value, where)
    parts = PurePosixPath(value)
    need(not parts.is_absolute() and ".." not in parts.parts
         and "\\" not in value and ":" not in value and "\0" not in value, where,
         "expected a relative /-separated file path without .. components, backslashes, : or NUL")
    path = root.joinpath(*parts.parts).resolve()
    need(path.is_relative_to(root.resolve()), where, "file escapes its record")
    need(path.is_file(), where, f"file does not exist: {path}")
    return path


class Checker:
    def __init__(self, session):
        self.session = Path(session).resolve()
        self.output = self.session / "output"
        self.knowledge = None

    def record(self, value, where):
        identifier(value, where)
        path = self.knowledge / value / "output.json"
        need(path.is_file(), where, f"record does not exist: {path}")
        return read_json(path)

    def references(self, value, where):
        for index, ref in enumerate(items(value, where)):
            loc = f"{where}[{index}]"
            obj(ref, loc)
            record = self.record(ref.get("record"), loc + ".record")
            if "file" in ref:
                local_file(self.knowledge / ref["record"], ref["file"], loc + ".file")
            if "result" in ref:
                result_id = identifier(ref["result"], loc + ".result")
                need(record.get("category") in ('research', 'peer') or
                     (record.get('category') == 'review' and record.get('target', {}).get('kind') == 'bundle'),
                     loc, 'result reference needs research, peer or a bundle review')
                need(result_id in self.result_ids(record, loc), loc + ".result",
                     "result does not exist in referenced record")

    def supersedes(self, value, where):
        for index, record_id in enumerate(items(value, where)):
            self.record(record_id, f"{where}[{index}]")

    def target(self, value, where, kinds=('research', 'goal', 'bundle')):
        obj(value, where)
        choice(value.get("kind"), kinds, where + ".kind")
        if value["kind"] == "goal":
            need("record" not in value, where, "a goal target has no record")
            return None
        if value['kind'] == 'bundle':
            work = self.record(value.get('work'), where + '.work')
            peer = self.record(value.get('peer'), where + '.peer')
            need(work.get('category') in ('research', 'explore'), where, 'work must be research or explore')
            need(peer.get('category') == 'peer', where, 'peer must be a peer record')
            need(peer.get('target') == {'kind': work['category'], 'record': value['work']},
                 where, 'peer must target this exact work')
            return {value['work']: work, value['peer']: peer}
        record = self.record(value.get("record"), where + ".record")
        need(record.get("category") == value['kind'], where, 'target category must match kind')
        return record

    @staticmethod
    def result_ids(record, where):
        result_ids = []
        for index, result in enumerate(items(record.get("results"), where + ".results")):
            loc = f"{where}.results[{index}]"
            obj(result, loc)
            result_ids.append(identifier(result.get("id"), loc + ".id"))
        need(len(set(result_ids)) == len(result_ids), where + ".results", "duplicate result id")
        return result_ids

    def request(self, request, where):
        obj(request, where)
        text(request.get("instructions"), where + ".instructions")
        self.references(request.get("references"), where + ".references")
        for key in ("model", "effort"):
            if key in request:
                text(request[key], where + "." + key)
        if "model" in request:
            provider, separator, name = request["model"].partition("/")
            need(provider in ("codex", "claude") and separator and name.strip(),
                 where + ".model", "expected codex/<model> or claude/<model>")
        if "model" in request or "effort" in request:
            text(request.get("selection_reason"), where + ".selection_reason")

    def check_input(self):
        data = read_json(self.session / "input.json")
        category = data.get("category")
        choice(category, CATEGORIES, "input.json.category")
        instance = Path(text(data.get("instance"), "input.json.instance"))
        need(instance.is_absolute() and instance.is_dir(), "input.json.instance",
             "expected an existing absolute instance directory")
        self.knowledge = instance / "knowledge"
        need(self.knowledge.is_dir(), "input.json.instance", "knowledge/ directory is missing")
        context = obj(data.get("context"), "input.json.context")
        common = items(context.get("common"), "input.json.context.common")
        need(bool(common), "input.json.context.common", "expected at least one common-context file")
        for index, value in enumerate(common + [context.get("category")]):
            loc = (f"input.json.context.common[{index}]" if index < len(common)
                   else "input.json.context.category")
            path = Path(text(value, loc))
            need(path.is_absolute() and path.is_file(), loc, "expected an existing absolute file")
        task = obj(data.get("task"), "input.json.task")
        text(task.get("instructions"), "input.json.task.instructions")
        self.references(task.get("references"), "input.json.task.references")
        if category == "research":
            self.supersedes(task.get("supersedes"), "input.json.task.supersedes")
        elif category == "review":
            self.target(task.get("target"), "input.json.task.target")
        elif category == 'peer':
            self.target(task.get('target'), 'input.json.task.target', ('research', 'explore'))
        elif category == "plan":
            if task.get("previous_plan") is not None:
                record = self.record(task["previous_plan"], "input.json.task.previous_plan")
                need(record.get("category") == "plan", "input.json.task.previous_plan", "expected a plan record")
            for index, event in enumerate(items(task.get("events"), "input.json.task.events")):
                loc = f"input.json.task.events[{index}]"
                obj(event, loc)
                choice(event.get("kind"), ("start", "review_finished", "peer_finished", "exploration_finished",
                                           "session_failed", "user_input"), loc + ".kind")
                if event["kind"] in ("review_finished", "peer_finished", "exploration_finished"):
                    expected = {"review_finished": "review", 'peer_finished': 'peer', "exploration_finished": "explore"}[event["kind"]]
                    record = self.record(event.get("record"), loc + ".record")
                    need(record.get("category") == expected, loc, f"expected a record of category {expected}")
                elif event["kind"] == "session_failed":
                    identifier(event.get("session"), loc + ".session")
                    text(event.get("reason"), loc + ".reason")
                elif event["kind"] == "user_input":
                    text(event.get("text"), loc + ".text")
        return data

    def plan(self, data):
        text(data.get("reason"), "output.json.reason")
        for index, request in enumerate(items(data.get("research"), "output.json.research")):
            loc = f"output.json.research[{index}]"
            self.request(request, loc)
            self.supersedes(request.get("supersedes"), loc + ".supersedes")
        for index, request in enumerate(items(data.get("explorations"), "output.json.explorations")):
            self.request(request, f"output.json.explorations[{index}]")
        for index, request in enumerate(items(data.get('peers', []), 'output.json.peers')):
            loc = f'output.json.peers[{index}]'
            self.request(request, loc)
            self.target(request.get('target'), loc + '.target', ('research', 'explore'))
        for index, request in enumerate(items(data.get("reviews"), "output.json.reviews")):
            loc = f"output.json.reviews[{index}]"
            self.request(request, loc)
            target = obj(request.get("target"), loc + ".target")
            self.target(target, loc + '.target', ('research', 'bundle'))
        need("goal_review" in data, "output.json.goal_review", "required (use null if not requested)")
        if data["goal_review"] is not None:
            self.request(data["goal_review"], "output.json.goal_review")
        need("wait" in data, "output.json.wait", "required (use null if not waiting)")
        if data["wait"] is not None:
            waiting = obj(data["wait"], "output.json.wait")
            text(waiting.get("needed"), "output.json.wait.needed")
            text(waiting.get("reason"), "output.json.wait.reason")

    def authored_results(self, data):
        self.result_ids(data, "output.json")
        for index, result in enumerate(data["results"]):
            loc = f"output.json.results[{index}]"
            local_file(self.output, result.get("exposition"), loc + ".exposition")
            text(result.get("verification"), loc + ".verification")
            need("lean" in result, loc + ".lean", "required (use null if no Lean result)")
            if result["lean"] is not None:
                lean = obj(result["lean"], loc + ".lean")
                sources = items(lean.get("sources"), loc + ".lean.sources")
                need(bool(sources), loc + ".lean.sources", "expected at least one source file")
                for n, source in enumerate(sources):
                    local_file(self.output, source, f"{loc}.lean.sources[{n}]")
                text(lean.get("version"), loc + ".lean.version")
    def research(self, data):
        self.authored_results(data)
        for index, attempt in enumerate(items(data.get("failed_attempts"), "output.json.failed_attempts")):
            loc = f"output.json.failed_attempts[{index}]"
            obj(attempt, loc)
            text(attempt.get("description"), loc + ".description")
            text(attempt.get("verification"), loc + ".verification")
        for index, question in enumerate(items(data.get("open_questions"), "output.json.open_questions")):
            text(question, f"output.json.open_questions[{index}]")

    def explore(self, data):
        local_file(self.output, data.get("exposition"), "output.json.exposition")
        for index, question in enumerate(items(data.get("questions"), "output.json.questions")):
            text(question, f"output.json.questions[{index}]")

    def peer(self, data, task):
        self.target(data.get('target'), 'output.json.target', ('research', 'explore'))
        need(data['target'] == task['target'], 'output.json.target', 'must match input target')
        need('goal' not in data and 'overview_assessment' not in data,
             'output.json', 'peer responses do not issue review verdicts')
        self.explore(data)
        self.authored_results(data)
        need(not data['supersedes'], 'output.json.supersedes', 'peer responses do not replace other records')

    @staticmethod
    def judgment(value, choices, where):
        obj(value, where)
        choice(value.get("verdict"), choices, where + ".verdict")
        text(value.get("reason"), where + ".reason")

    def review(self, data, task):
        target = self.target(data.get("target"), "output.json.target")
        need(data['target'] == task['target'], 'output.json.target', 'must match input.json.task.target')
        if data['target']['kind'] == 'bundle':
            self.bundle_review(data, target)
            return
        if target is None:
            self.judgment(data.get("goal"), ("achieved", "not_achieved", "undetermined"), "output.json.goal")
            return
        self.judgment(data.get("overview_assessment"),
                      ("supported", "not_supported", "undetermined"), "output.json.overview_assessment")
        reviewed_ids = []
        for index, result in enumerate(items(data.get("results"), "output.json.results")):
            loc = f"output.json.results[{index}]"
            obj(result, loc)
            reviewed_ids.append(identifier(result.get("result"), loc + ".result"))
            self.judgment(result.get("assessment"), ("supported", "not_supported", "undetermined"), loc + ".assessment")
            self.judgment(result.get("lean"), ("accepted", "rejected", "not_checked", "not_applicable"), loc + ".lean")
            self.judgment(result.get("alignment"), ("matches", "differs", "not_checked", "not_applicable"), loc + ".alignment")
            self.judgment(result.get("terminology"), ("conforms", "deviates"), loc + ".terminology")
        need(sorted(reviewed_ids) == sorted(self.result_ids(target, "target record")),
             "output.json.results", "must judge each target result exactly once")
        text(data.get("summary"), "output.json.summary")

    def bundle_review(self, data, bundle):
        local_file(self.output, data.get('exposition'), 'output.json.exposition')
        self.result_ids(data, 'output.json')
        for old in data['supersedes']:
            previous = self.record(old, 'output.json.supersedes')
            need(previous.get('category') == 'review' and previous.get('target') == data['target'],
                 'output.json.supersedes', 'only reviews of this exact bundle may be replaced')
        required = {(rid, result) for rid, record in bundle.items() if record['category'] != 'explore'
                    for result in self.result_ids(record, rid)}
        seen = []
        for i, row in enumerate(data['results']):
            loc = f'output.json.results[{i}]'
            source = obj(row.get('source'), loc + '.source')
            rid = source.get('record')
            need(isinstance(rid, str) and rid in bundle, loc + '.source', 'source must belong to this work/peer bundle')
            if 'result' in source:
                result = identifier(source['result'], loc + '.source.result')
                need((rid, result) in required, loc + '.source.result', 'unknown authored result')
                seen.append((rid, result))
            else:
                local_file(self.knowledge / rid, source.get('file'), loc + '.source.file')
                text(source.get('statement'), loc + '.source.statement')
            for key, choices in (
                ('assessment', ('supported', 'not_supported', 'undetermined')),
                ('lean', ('accepted', 'rejected', 'not_checked', 'not_applicable')),
                ('alignment', ('matches', 'differs', 'not_checked', 'not_applicable')),
                ('terminology', ('conforms', 'deviates'))):
                self.judgment(row.get(key), choices, loc + '.' + key)
        need(sorted(seen) == sorted(required), 'output.json.results',
             'must judge every authored work/peer result exactly once')
        overviews = []
        for i, row in enumerate(items(data.get('overview_assessments'), 'output.json.overview_assessments')):
            loc = f'output.json.overview_assessments[{i}]'
            obj(row, loc)
            overviews.append(row.get('record'))
            self.judgment(row.get('assessment'), ('supported', 'not_supported', 'undetermined'), loc + '.assessment')
        need(all(isinstance(rid, str) for rid in overviews) and sorted(overviews) == sorted(bundle),
             'output.json.overview_assessments', 'must assess both overviews exactly once')
        text(data.get('summary'), 'output.json.summary')

    def run(self):
        data = self.check_input()
        output = read_json(self.output / "output.json")
        need(output.get("category") == data["category"], "output.json.category", "must match input.json.category")
        overview = obj(output.get("overview"), "output.json.overview")
        title = text(overview.get("title"), "output.json.overview.title")
        need('\n' not in title and '\r' not in title, "output.json.overview.title", "expected a single-line title")
        text(overview.get("summary"), "output.json.overview.summary")
        self.references(output.get("references"), "output.json.references")
        self.supersedes(output.get("supersedes"), "output.json.supersedes")
        # The entire output directory is copied. Links would preserve dependencies
        # on the author's working directory or another mutable location.
        for path in (self.output, *self.output.rglob("*")):
            need(not path.is_symlink() and not path.is_junction(), str(path),
                 "publish a regular file/directory, not a filesystem link")
        if data["category"] == "plan":
            self.plan(output)
            problems = check_glossary(self.output)
            need(not problems, 'glossary', '; '.join(problems))
        elif data["category"] == "research":
            self.research(output)
        elif data["category"] == "explore":
            self.explore(output)
        elif data['category'] == 'peer':
            self.peer(output, data['task'])
        else:
            self.review(output, data["task"])


def check_session(session):
    """Return [] on success, or [first actionable error]; never write files.

    session is a str or Path naming a session directory. Expected JSON, file,
    encoding and protocol failures are diagnostics. Programming errors propagate.
    """
    try:
        Checker(session).run()
    except (Invalid, OSError, UnicodeError) as exc:
        return [str(exc)]
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", type=Path, help="session directory containing input.json and output/")
    args = parser.parse_args(argv)
    errors = check_session(args.session)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
