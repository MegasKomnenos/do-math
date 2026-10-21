"""Scoped graphify entry point. Only update writes state or invokes an LLM."""
import argparse
import ast
import builtins
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from semantic import MODEL, atomic_json, cached, digest, extract_document

REPO = Path(__file__).resolve().parents[4]
ROOT = REPO / ".claude" / "skills" / "do-math"
STATE = REPO / ".claude" / "graphify" / "do-math"
GRAPH = STATE / "graphify-out" / "graph.json"
PROMPT = REPO / ".claude" / "skills" / "graphify" / "references" / "semantic.md"
SKIP = {"__pycache__", ".git", ".venv", "graphify-out", ".pytest_cache"}


def inventory(root=ROOT):
    files = {}
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(directory) / d).is_symlink()
                         and (Path(directory) / d).resolve().is_relative_to(root.resolve()))
        for name in sorted(names):
            path = Path(directory) / name
            if path.suffix in {".pyc", ".pyo"} or path.is_symlink():
                continue
            if not path.resolve().is_relative_to(root.resolve()):
                continue
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    if not files:
        raise ValueError(f"empty corpus: {root}")
    return files


def hashes(files):
    return {name: digest(raw) for name, raw in files.items()}


def explicit_references(graph, files):
    """Connect literal internal file references; never infer contract compliance."""
    basenames = {}
    for name in files:
        basenames.setdefault(Path(name).name, []).append(name)
    pattern = re.compile(r"[\w./\\-]+")
    for source, raw in files.items():
        try:
            lines = raw.decode("utf-8-sig").splitlines()
        except UnicodeError:
            continue
        for number, line in enumerate(lines, 1):
            for match in pattern.finditer(line):
                token = match.group().replace("\\", "/")
                if not token.endswith((".py", ".md", ".json", ".ps1", ".txt")):
                    continue
                if "://" in line[max(0, match.start() - 8):match.start() + len(token)] or token.startswith("/"):
                    continue
                direct = (Path(source).parent / token).as_posix()
                target = direct if direct in files else token if token in files else None
                confidence = "EXTRACTED"
                # A unique basename is a useful candidate, but not a resolved runtime path.
                if target is None and "/" not in token and len(basenames.get(token, [])) == 1:
                    target = basenames[token][0]
                    confidence = "INFERRED"
                if target and target != source:
                    graph.add_edge("file::" + source, "file::" + target, relation="references",
                                   confidence=confidence, confidence_score=1.0 if confidence == "EXTRACTED" else 0.75,
                                   source_file=source, source_location=f"L{number}", quote=line.strip(),
                                   rationale="literal internal path" if confidence == "EXTRACTED" else "unique internal basename; verify current source")


def status(files, graph=GRAPH):
    current = hashes(files)
    previous = {}
    metadata = {}
    if graph.exists():
        data = json.loads(graph.read_text(encoding="utf-8"))
        metadata = data.get("graph", {}).get("scope", {})
        previous = metadata.get("files", {})
    instructions = PROMPT.read_text(encoding="utf-8")
    pending = [name for name, raw in files.items() if name.endswith(".md")
               and not cached(STATE, name, raw, files, digest(instructions.encode("utf-8")))]
    added = sorted(current.keys() - previous.keys())
    deleted = sorted(previous.keys() - current.keys())
    changed = sorted(k for k in current.keys() & previous.keys() if current[k] != previous[k])
    return {"state": "missing" if not graph.exists() else "stale" if added or deleted or changed else "current",
            "root": str(ROOT), "graph": str(graph), "built_at": metadata.get("built_at"),
            "files": len(files), "added": added, "changed": changed, "deleted": deleted,
            "semantic_pending": pending}


def resolve_internal_imports(graph, unresolved, files):
    """Resolve unique local module imports missed by the upstream extractor."""
    modules = {}
    for name in files:
        if not name.endswith(".py"):
            continue
        stem = Path(name).stem
        modules.setdefault(stem, set()).add(name)
        modules.setdefault(name[:-3].replace("/", "_"), set()).add(name)
        if stem == "__init__":
            modules.setdefault(Path(name).parent.name, set()).add(name)
    remaining = []
    for edge in unresolved:
        if edge.get("relation") not in {"imports", "imports_from"} or edge["source"] not in graph:
            remaining.append(edge)
            continue
        target = edge["target"]
        candidates = modules.get(target, set())
        if len(candidates) != 1:
            remaining.append(edge)
            continue
        name = next(iter(candidates))
        attrs = {k: v for k, v in edge.items() if k not in {"source", "target"}}
        attrs.update(confidence="INFERRED", confidence_score=0.75,
                     rationale="unique local Python module name; verify import search path")
        graph.add_edge(edge["source"], "file::" + name, **attrs)
    return remaining


def separate_out_of_scope_imports(unresolved, files):
    """Keep imports without a matching corpus module separate from missing internal links."""
    stems = {Path(name).stem for name in files if name.endswith(".py")}
    directories = {part for name in files for part in Path(name).parts[:-1]}
    external, remaining = [], []
    for edge in unresolved:
        target = edge["target"]
        if (edge.get("relation") in {"imports", "imports_from"}
                and not target.startswith("scripts_") and target not in stems
                and target not in directories):
            external.append(edge)
        else:
            remaining.append(edge)
    return remaining, external


def resolve_symbol_references(graph, unresolved, files):
    """Follow explicit Python import bindings to internal symbols or external scope."""
    modules = {}
    internal_directories = {part.lower() for name in files for part in Path(name).parts[:-1]}
    builtin_names = {name.lower() for name in dir(builtins)}
    for name in files:
        if name.endswith(".py"):
            modules.setdefault(Path(name).stem.lower(), set()).add(name)
            modules.setdefault(name[:-3].replace("/", ".").lower(), set()).add(name)
    symbols = {}
    for nid, data in graph.nodes(data=True):
        if data.get("_callable"):
            label = data.get("label", "").strip(".()")
            symbols.setdefault((data.get("source_file"), label), set()).add(nid)
    bindings = {}
    external_members = {}
    local_external_names = {}
    for name, raw in files.items():
        if not name.endswith(".py"):
            continue
        try:
            tree = ast.parse(raw.decode("utf-8-sig"), filename=name)
        except (SyntaxError, UnicodeError):
            continue
        local = {}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module.lower()
                candidates = modules.get(module, set()) or modules.get(module.rsplit(".", 1)[-1], set())
                for item in node.names:
                    local[(item.asname or item.name).lower()] = (candidates, item.name, module in internal_directories)
            elif isinstance(node, ast.Import):
                for item in node.names:
                    alias = item.asname or item.name.split(".")[0]
                    module = item.name.lower()
                    candidates = modules.get(module, set()) or modules.get(module.rsplit(".", 1)[-1], set())
                    local[alias.lower()] = (candidates, None, module in internal_directories)
        bindings[name] = local
        def external_attributes(nodes, location):
            return {(location, node.attr.lower()) for root in nodes if root is not None for node in ast.walk(root)
                    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                    and (binding := local.get(node.value.id.lower()))
                    and not binding[0] and not binding[2]}

        members = {(node.lineno, node.attr.lower()) for node in ast.walk(tree)
                   if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                   and (binding := local.get(node.value.id.lower()))
                   and not binding[0] and not binding[2]}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                annotations = [arg.annotation for arg in (*node.args.posonlyargs, *node.args.args,
                                                         *node.args.kwonlyargs)]
                if node.args.vararg:
                    annotations.append(node.args.vararg.annotation)
                if node.args.kwarg:
                    annotations.append(node.args.kwarg.annotation)
                members.update(external_attributes([*annotations, node.returns, *node.decorator_list], node.lineno))
            elif isinstance(node, ast.ClassDef):
                members.update(external_attributes(node.decorator_list, node.lineno))
        external_members[name] = members

        scoped = []
        for scope in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
            pending = list(scope.body)
            while pending:
                node = pending.pop()
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                pending.extend(ast.iter_child_nodes(node))
                if not isinstance(node, ast.ImportFrom) or not node.module:
                    continue
                module = node.module.lower()
                candidates = modules.get(module, set()) or modules.get(module.rsplit(".", 1)[-1], set())
                if not candidates and module not in internal_directories:
                    scoped.extend((scope.lineno, scope.end_lineno, node.lineno, (item.asname or item.name).lower())
                                  for item in node.names)
        local_external_names[name] = scoped
    remaining, external = [], []
    for edge in unresolved:
        if edge.get("relation") not in {"calls", "references", "inherits", "imports_from"}:
            remaining.append(edge)
            continue
        name = edge.get("source_file", "")
        prefix = name[:-3].replace("/", "_").lower() + "_py_"
        target = edge["target"].lower()
        alias = target[len(prefix):] if target.startswith(prefix) else target
        binding = bindings.get(name, {}).get(alias)
        if binding:
            candidates, original, internal_namespace = binding
            matches = set().union(*(symbols.get((candidate, original), set()) for candidate in candidates)) if original else set()
            if len(matches) == 1 and edge["source"] in graph:
                attrs = {k: v for k, v in edge.items() if k not in {"source", "target"}}
                attrs.update(confidence="INFERRED", confidence_score=0.75,
                             rationale="explicit Python import alias to unique internal symbol")
                graph.add_edge(edge["source"], next(iter(matches)), **attrs)
                continue
            if not candidates and not internal_namespace:
                external.append(edge)
                continue
        elif alias in builtin_names:
            external.append(edge)
            continue
        elif edge.get("source_location", "").startswith("L") and (
                int(edge["source_location"][1:]), alias) in external_members.get(name, set()):
            external.append(edge)
            continue
        elif edge.get("source_location", "").startswith("L") and any(
                start <= int(edge["source_location"][1:]) <= end and imported <= int(edge["source_location"][1:])
                and alias == imported_alias for start, end, imported, imported_alias in local_external_names.get(name, [])):
            external.append(edge)
            continue
        remaining.append(edge)
    return remaining, external


def add_inherited_method_calls(graph, files):
    """Connect explicit self and zero-argument super calls through known bases."""
    classes = {}
    methods = {}
    calls = []
    locations = {}
    for nid, data in graph.nodes(data=True):
        locations.setdefault((data.get("source_file"), data.get("source_location")), []).append((nid, data))
    for name, raw in files.items():
        if not name.endswith(".py"):
            continue
        try:
            tree = ast.parse(raw.decode("utf-8-sig"), filename=name)
        except (SyntaxError, UnicodeError):
            continue
        for cls in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
            class_id = next((nid for nid, data in locations.get((name, f"L{cls.lineno}"), [])
                             if data.get("_callable_class")), None)
            if not class_id:
                continue
            classes[class_id] = cls
            for method in cls.body:
                if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                method_id = next((nid for nid, data in locations.get((name, f"L{method.lineno}"), [])
                                  if data.get("label") == f".{method.name}()"), None)
                if not method_id:
                    continue
                methods[class_id, method.name] = method_id
                pending = list(method.body)
                while pending:
                    node = pending.pop()
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                        continue
                    pending.extend(ast.iter_child_nodes(node))
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                        continue
                    receiver = node.func.value
                    if isinstance(receiver, ast.Name) and receiver.id == "self":
                        calls.append((class_id, method_id, node.func.attr, node.lineno, name, "self"))
                    elif (isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name)
                          and receiver.func.id == "super" and not receiver.args and not receiver.keywords):
                        calls.append((class_id, method_id, node.func.attr, node.lineno, name, "super"))

    def bases(class_id):
        linked = [target for _, target, data in graph.out_edges(class_id, data=True)
                  if data.get("relation") == "inherits" and target in classes]
        by_name = {graph.nodes[base]["label"]: base for base in linked}
        return [by_name[name] for node in classes[class_id].bases
                if (name := getattr(node, "id", None) or getattr(node, "attr", None)) in by_name]

    @lru_cache(maxsize=None)
    def mro(class_id, seen=frozenset()):
        if class_id in seen:
            return [class_id]
        parents = bases(class_id)
        sequences = [mro(parent, seen | {class_id})[:] for parent in parents] + [parents[:]]
        order = [class_id]
        while any(sequences):
            candidate = next((head[0] for head in sequences if head
                              and not any(head[0] in tail[1:] for tail in sequences)), None)
            if candidate is None:
                break  # Ambiguous or incomplete hierarchy; retain only proven prefix.
            order.append(candidate)
            for sequence in sequences:
                if sequence and sequence[0] == candidate:
                    sequence.pop(0)
        return order

    def inherited(class_id, method_name):
        return next((methods[base, method_name] for base in mro(class_id)[1:]
                     if (base, method_name) in methods), None)

    for cls, source, method_name, line, name, receiver in calls:
        if receiver == "self" and (cls, method_name) in methods:
            continue
        target = inherited(cls, method_name)
        if target and not any(v == target and d.get("relation") == "calls" and d.get("source_location") == f"L{line}"
                              for _, v, d in graph.out_edges(source, data=True)):
            graph.add_edge(source, target, relation="calls", context="inherited_self_call" if receiver == "self" else "super_call",
                           confidence="INFERRED", confidence_score=0.75, source_file=name,
                           source_location=f"L{line}", rationale=f"{receiver} call resolved through declared base classes")


def build_graph(files, semantics):
    import networkx as nx
    from graphify.extract import extract
    # A fresh snapshot prevents mixed revisions and limits graphify's source scans to this corpus.
    with tempfile.TemporaryDirectory(prefix="do-math-graphify-ast-") as temporary:
        snapshot = Path(temporary)
        for name, raw in files.items():
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        selected = [snapshot / name for name in files if Path(name).suffix in {".py", ".md"}]
        extraction = extract(selected, root=snapshot, cache_root=snapshot, parallel=False)
        if extraction.get("failed_sources") or extraction.get("_failed_sources"):
            raise ValueError("AST extraction failed: " + str(extraction.get("failed_sources", extraction.get("_failed_sources"))))
        nodes = extraction["nodes"]
        for item in nodes + extraction["edges"]:
            source = item.get("source_file", "")
            if Path(source).is_absolute():
                item["source_file"] = Path(source).relative_to(snapshot).as_posix()
            else:
                item["source_file"] = source.replace("\\", "/")
    graph = nx.MultiDiGraph()
    for name in files:
        graph.add_node("file::" + name, label=name, file_type="document" if name.endswith(".md") else "code",
                       node_kind="file", source_file=name, source_location="L1")
    for node in nodes:
        if node.get("source_file") not in files:
            continue
        attributes = dict(node)
        nid = attributes.pop("id")
        graph.add_node(nid, **attributes)
        graph.add_edge("file::" + node["source_file"], nid, relation="contains", confidence="EXTRACTED",
                       source_file=node["source_file"], source_location=node.get("source_location", "L1"))
    unresolved = []
    for edge in extraction["edges"]:
        if edge.get("source_file") not in files:
            continue
        if edge["source"] not in graph or edge["target"] not in graph:
            unresolved.append(edge)
            continue
        attrs = {k: v for k, v in edge.items() if k not in {"source", "target"}}
        graph.add_edge(edge["source"], edge["target"], **attrs)
    unresolved = resolve_internal_imports(graph, unresolved, files)
    unresolved, external_symbols = resolve_symbol_references(graph, unresolved, files)
    add_inherited_method_calls(graph, files)
    unresolved, external = separate_out_of_scope_imports(unresolved, files)
    for document in semantics:
        name = document["source_file"]
        prefix = "semantic::" + name + "::"
        for node in document["nodes"]:
            graph.add_node(prefix + node["key"], label=node["label"], file_type="concept", node_kind="contract",
                           source_file=name, source_location=f"L{node['line']}", description=node["summary"],
                           summary=node["summary"], quote=node["quote"])
            graph.add_edge("file::" + name, prefix + node["key"], relation="defines", confidence="EXTRACTED",
                           source_file=name, source_location=f"L{node['line']}")
        for edge in document["edges"]:
            target = "file::" + edge["target_file"] if edge.get("target_file") else prefix + edge["target"]
            graph.add_edge(prefix + edge["source"], target, relation=edge["relation"], confidence=edge["confidence"],
                           confidence_score={"EXTRACTED": 1.0, "INFERRED": 0.75, "AMBIGUOUS": 0.2}[edge["confidence"]],
                           source_file=name, source_location=f"L{edge['line']}", quote=edge["quote"],
                           rationale=edge.get("rationale"))
    explicit_references(graph, files)
    graph.graph["unresolved_references"] = unresolved
    graph.graph["out_of_scope_imports"] = external
    graph.graph["out_of_scope_symbols"] = external_symbols
    return graph


def update(files, workers, timeout):
    STATE.mkdir(parents=True, exist_ok=True)
    lock = STATE / "update.lock"
    try:
        handle = lock.open("x")
    except FileExistsError:
        raise RuntimeError(f"update already running or interrupted; inspect {lock} before removing it")
    try:
        with handle:
            handle.write(str(os.getpid()))
        instructions = PROMPT.read_text(encoding="utf-8")
        prompt_hash = digest(instructions.encode("utf-8"))
        documents, pending = [], []
        for name, raw in files.items():
            if not name.endswith(".md"):
                continue
            result = cached(STATE, name, raw, files, prompt_hash)
            if result:
                documents.append(result)
            else:
                pending.append((name, raw))
        print(f"Semantic: {len(documents)} cached, {len(pending)} pending; codex exec {MODEL}", flush=True)
        failures = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            jobs = {pool.submit(extract_document, STATE, name, raw, files, instructions, timeout): name
                    for name, raw in pending}
            for job in as_completed(jobs):
                try:
                    result = job.result()
                    documents.append(result)
                    print(f"Semantic OK: {jobs[job]} ({len(result['nodes'])} nodes)", flush=True)
                except Exception as error:
                    failures.append(f"{jobs[job]}: {error}")
                    print(f"Semantic FAILED: {failures[-1]}", flush=True)
        if failures:
            raise RuntimeError("Graph preserved. Fix extraction failures and explicitly rerun update:\n" + "\n".join(failures))
        graph = build_graph(files, documents)
        if hashes(inventory()) != hashes(files):
            raise RuntimeError("corpus changed during update; graph preserved; rerun update explicitly")
        from graphify.cluster import cluster
        from graphify.export import to_json, to_html
        from importlib.metadata import version
        communities = cluster(graph)
        labels = {}
        for cid, members in communities.items():
            frequent = Counter(graph.nodes[n]["source_file"] for n in members).most_common(2)
            labels[cid] = " / ".join(Path(name).name for name, _ in frequent)
        graph.graph["scope"] = {"root": ".claude/skills/do-math", "files": hashes(files),
                                "built_at": datetime.now(timezone.utc).isoformat(),
                                "semantic_model": MODEL, "semantic_transport": "codex exec",
                                "graphify_version": version("graphifyy"),
                                "prompt_hash": prompt_hash,
                                "usage": {d["source_file"]: d.get("usage") for d in documents}}
        GRAPH.parent.mkdir(parents=True, exist_ok=True)
        staging = GRAPH.with_suffix(".pending.json")
        try:
            if not to_json(graph, communities, str(staging), force=True, community_labels=labels):
                raise RuntimeError("graph export refused")
            if hashes(inventory()) != hashes(files):
                raise RuntimeError("corpus changed before publication; graph preserved; rerun update explicitly")
            os.replace(staging, GRAPH)
        finally:
            staging.unlink(missing_ok=True)
        report = ["# do-math graph", "", f"Built: {graph.graph['scope']['built_at']}", "",
                  f"{len(files)} files · {graph.number_of_nodes()} nodes · {graph.number_of_edges()} edges", "",
                  f"Scope: .claude/skills/do-math only. Semantic extraction: codex exec {MODEL}.",
                  "This is a navigation map, not a correctness or contract-compliance verdict.",
                  "Python/Markdown structural extraction; other files have inventory nodes only.",
                  f"Unresolved structural references: {len(graph.graph['unresolved_references'])} (stored in graph metadata).",
                  f"Out-of-scope imports: {len(graph.graph['out_of_scope_imports'])} (stored separately in graph metadata).",
                  f"Out-of-scope symbols: {len(graph.graph['out_of_scope_symbols'])} (stored separately in graph metadata).",
                  "Token usage per document: graph.scope.usage; null means unavailable, not zero.", "", "## Communities", ""]
        for cid, members in communities.items():
            report.append(f"- {cid}: {labels[cid]} ({len(members)} nodes)")
        (GRAPH.parent / "GRAPH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        print(f"Graph updated: {GRAPH} ({graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges)", flush=True)
        # Large graphs render relationships at community level; the tree keeps symbol navigation.
        if not to_html(graph, communities, str(GRAPH.parent / "graph.html"),
                       community_labels=labels, node_limit=5000):
            print("HTML relationship view skipped: fewer than two communities; use tree.html and graph.json")
        subprocess.run([sys.executable, "-m", "graphify", "tree", "--graph", str(GRAPH),
                        "--output", str(GRAPH.parent / "tree.html"),
                        "--max-children", "1000", "--label", "do-math"], check=True)
    finally:
        lock.unlink(missing_ok=True)


def read_graph(command, terms, budget=2500, dfs=False, graph_path=GRAPH, exact=False, relations=None):
    """Use graphify's pure query functions, bypassing CLI query logs/stamps."""
    import networkx as nx
    from networkx.readwrite import json_graph
    from graphify.serve import _find_node, _query_graph_text
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    graph = json_graph.node_link_graph(data, edges="links")
    def resolve(term, strict=False):
        if term in graph:
            return term
        if "file::" + term in graph:
            return "file::" + term
        if strict:
            raise ValueError(f"Exact node ID or file path required: {term}")
        matches = _find_node(graph, term)
        if len(matches) != 1:
            candidates = [{"id": n, "label": graph.nodes[n]["label"],
                           "source_file": graph.nodes[n]["source_file"]} for n in matches[:12]]
            raise ValueError(f"Use exact node ID or file path; matches for {term}: " + json.dumps(candidates, ensure_ascii=False))
        return matches[0]

    relations = set(relations or [])
    if command == "query" and not exact:
        # Preserve actual direction while exploring incoming and outgoing context.
        traversal = nx.MultiGraph()
        traversal.add_nodes_from(graph.nodes(data=True))
        for u, v, attrs in graph.edges(data=True):
            if not relations or attrs.get("relation") in relations:
                traversal.add_edge(u, v, **{**attrs, "_src": u, "_tgt": v})
        print(_query_graph_text(traversal, terms[0], mode="dfs" if dfs else "bfs",
                                depth=2, token_budget=budget, graph_path=str(graph_path)))
        return 0

    seed = resolve(terms[0], strict=command == "query")
    if command == "query":
        edges = [(u, v, d) for u, v, d in list(graph.out_edges(seed, data=True)) + list(graph.in_edges(seed, data=True))
                 if not relations or d.get("relation") in relations]
        selected = [seed] + [n for u, v, _ in edges for n in (u, v) if n != seed]
    elif command == "path":
        target = resolve(terms[1])
        try:
            selected = nx.shortest_path(graph, seed, target)
        except nx.NetworkXNoPath:
            print("No directed path found. This does not establish absence of a dependency.")
            return 0
        edges = [(u, v, d) for u, v in zip(selected, selected[1:]) for d in graph[u][v].values()]
    elif command == "affected":
        from graphify.affected import DEFAULT_AFFECTED_RELATIONS, affected_nodes
        members = {seed} | {v for _, v, d in graph.out_edges(seed, data=True)
                            if d.get("relation") in {"contains", "method", "defines"}}
        hits = affected_nodes(graph, seed, depth=2)
        for member in members - {seed}:
            if graph.nodes[member].get("node_kind") == "contract":
                hits.extend(affected_nodes(graph, member, depth=2))
        selected = [seed] + sorted(members - {seed}) + list(dict.fromkeys(hit.node_id for hit in hits if hit.node_id not in members))
        selected_set = set(selected)
        edges = [(u, v, d) for u, v, d in graph.edges(data=True) if u in selected_set and v in selected_set | members
                 and d.get("relation") in DEFAULT_AFFECTED_RELATIONS]
        edges.sort(key=lambda edge: (edge[1] not in members,
                                     edge[2].get("relation") not in {"calls", "indirect_call"},
                                     edge[2].get("source_file", ""), edge[2].get("source_location", "")))
    else:
        edges = list(graph.out_edges(seed, data=True)) + list(graph.in_edges(seed, data=True))
        selected = [seed] + [n for u, v, _ in edges for n in (u, v) if n != seed]
    selected = list(dict.fromkeys(selected))
    if command == "affected":
        visible = [seed]
        for u, v, _ in edges:
            missing = [n for n in (u, v) if n not in visible]
            if len(visible) + len(missing) <= 40:
                visible.extend(missing)
        visible.extend(n for n in selected if n not in visible and len(visible) < 40)
    else:
        visible = selected[:40]
    visible_set = set(visible)
    visible_edges = [(u, v, d) for u, v, d in edges if u in visible_set and v in visible_set][:80]
    result = {"nodes": [{"id": n, **graph.nodes[n]} for n in visible],
              "edges": [{"source": u, "target": v, **d} for u, v, d in visible_edges],
              "total_nodes": len(selected), "total_edges": len(edges),
              "truncated": len(selected) > 40 or len(visible_edges) < len(edges)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="read-only content-hash freshness check")
    build = sub.add_parser("update", help=f"explicit rebuild; changed Markdown uses codex exec {MODEL}")
    build.add_argument("--workers", type=int, default=8)
    build.add_argument("--timeout", type=int, default=900)
    for name in ("query", "path", "explain", "affected"):
        command = sub.add_parser(name)
        command.add_argument("terms", nargs=2 if name == "path" else 1)
        if name == "query":
            command.add_argument("--budget", type=int, default=2500)
            command.add_argument("--dfs", action="store_true")
            command.add_argument("--exact", action="store_true", help="show one exact node and its direct relations")
            command.add_argument("--relation", action="append", help="limit query to this relation; repeatable")
    args = parser.parse_args()
    files = inventory()
    if args.command == "update":
        if args.workers < 1 or args.timeout < 1:
            parser.error("workers and timeout must be positive")
        update(files, args.workers, args.timeout)
        return 0
    current = status(files)
    if args.command == "status":
        print(json.dumps(current, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(current, ensure_ascii=False), file=sys.stderr, flush=True)
    if current["state"] == "missing":
        print("No graph. Run update explicitly to build it.", file=sys.stderr)
        return 2
    return read_graph(args.command, args.terms, getattr(args, "budget", 2500), getattr(args, "dfs", False),
                      exact=getattr(args, "exact", False), relations=getattr(args, "relation", None))


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
