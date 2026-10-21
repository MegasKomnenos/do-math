import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import graph
import semantic


class EvidenceRecoveryTests(unittest.TestCase):
    def setUp(self):
        # Reproduce the wrapped Korean sentence and invented punctuation from real failures.
        self.raw = ("동일 ID/내용은\n재전달되고 내용 변경은 반려된다.\n"
                    "| 같은 정의를 사용한다 |\n동일 ID/내용은\n").encode("utf-8")
        self.files = {"contract.md": self.raw}
        self.response = {"nodes": [
            {"key": "delivery", "label": "Delivery", "summary": "Repeated delivery preserves content",
             "line": 2, "quote": "동일 ID/내용은"},
            {"key": "definition", "label": "Definition", "summary": "Shared definition",
             "line": 3, "quote": "같은 정의를 사용한다."}],
            "edges": [{"source": "delivery", "target": "definition", "relation": "requires",
                       "confidence": "INFERRED", "rationale": "Example relation",
                       "line": 2, "quote": "동일 ID/내용은 재전달되고 내용 변경은 반려된다."}]}
        self.corrections = {"corrections": [
            {"kind": "nodes", "index": 0, "line": 1, "quote": "동일 ID/내용은"},
            {"kind": "nodes", "index": 1, "line": 3, "quote": "같은 정의를 사용한다"},
            {"kind": "edges", "index": 0, "line": 2, "quote": "재전달되고 내용 변경은 반려된다."}]}

    def runner(self, outputs):
        outputs = iter(outputs)

        def run(command, **kwargs):
            # Exercise actual invocation/log parsing while replacing only the CLI process.
            response = next(outputs)
            Path(command[command.index("-o") + 1]).write_text(json.dumps(response), encoding="utf-8")
            kwargs["stdout"].write(b'{"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":5}}\n')
            self.assertLessEqual(kwargs["timeout"], 30)
            return SimpleNamespace(returncode=0)
        return run

    def extract(self, state):
        return semantic.extract_document(state, "contract.md", self.raw, self.files, "instructions", 30)

    def test_repairs_all_evidence_without_changing_meaning_or_accepting_approximate_quotes(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(semantic.shutil, "which", return_value="codex"), \
                patch.object(semantic.subprocess, "run", side_effect=self.runner([self.response, self.corrections])) as run:
            state = Path(directory)
            result = self.extract(state)
            self.assertEqual(run.call_count, 2)
            semantic.validate(result, "contract.md", self.raw, self.files)
            self.assertEqual(result["usage"], {"input_tokens": 20, "output_tokens": 10})
            self.assertEqual(len(result["repair_runs"]), 1)
            self.assertEqual(result, semantic.cached(state, "contract.md", self.raw, self.files,
                                                     semantic.digest(b"instructions")))
            for kind in ("nodes", "edges"):
                for before, after in zip(self.response[kind], result[kind]):
                    self.assertEqual({k: v for k, v in before.items() if k not in {"line", "quote"}},
                                     {k: v for k, v in after.items() if k not in {"line", "quote"}})

    def test_repeated_invalid_repairs_preserve_graph_and_cache_and_release_lock(self):
        wrong = copy.deepcopy(self.corrections)
        wrong["corrections"][0]["line"] = 2
        last = {"corrections": [wrong["corrections"][0]]}
        with tempfile.TemporaryDirectory() as directory, patch.object(semantic.shutil, "which", return_value="codex"), \
                patch.object(semantic.subprocess, "run", side_effect=self.runner([self.response, wrong, last])) as run:
            state = Path(directory)
            target = state / "graph.json"
            target.write_bytes(b"old graph")
            cache = semantic.cache_path(state, "contract.md")
            cache.parent.mkdir()
            cache.write_bytes(b"old cache")
            with patch.object(graph, "STATE", state), patch.object(graph, "GRAPH", target):
                with self.assertRaisesRegex(RuntimeError, "Graph preserved.*|Fix extraction failures"):
                    graph.update(self.files, 1, 30)
            self.assertEqual(run.call_count, 3)
            self.assertEqual(target.read_bytes(), b"old graph")
            self.assertEqual(cache.read_bytes(), b"old cache")
            self.assertFalse((state / "update.lock").exists())

    def test_non_evidence_error_is_not_repaired(self):
        wrong = copy.deepcopy(self.response)
        wrong["edges"][0].update(target=None, target_file="../outside.py")
        with tempfile.TemporaryDirectory() as directory, patch.object(semantic.shutil, "which", return_value="codex"), \
                patch.object(semantic.subprocess, "run", side_effect=self.runner([wrong])) as run:
            with self.assertRaisesRegex(ValueError, "out-of-scope.*see"):
                self.extract(Path(directory))
            self.assertEqual(run.call_count, 1)

    def test_reuses_only_identical_completed_failed_extraction(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(semantic.shutil, "which", return_value="codex"):
            state = Path(directory)
            with patch.object(semantic.subprocess, "run", side_effect=self.runner([self.response, {"corrections": []}])):
                with self.assertRaisesRegex(ValueError, "missing evidence corrections"):
                    self.extract(state)
            origin = next((state / "runs").iterdir())
            # Legacy failures recorded only this error string.
            semantic.atomic_json(origin / "validation-error.json", {"error": "invalid evidence: contract.md:2"})
            prompt = (origin / "input.txt").read_text(encoding="utf-8")
            self.assertIsNone(semantic.failed_response(state, "contract.md", self.raw + b"changed", prompt))
            self.assertIsNone(semantic.failed_response(state, "contract.md", self.raw, prompt + "changed"))
            with patch.object(semantic.subprocess, "run", side_effect=self.runner([self.corrections])) as run:
                result = self.extract(state)
            self.assertEqual(run.call_count, 1)
            self.assertEqual(result["extraction_run_id"], origin.name)
            self.assertEqual(result["usage"], {"input_tokens": 20, "output_tokens": 10})
            (origin / "events.jsonl").write_text('{"type":"turn.failed"}\n', encoding="utf-8")
            self.assertIsNone(semantic.failed_response(state, "contract.md", self.raw, prompt))

    def test_corrections_cannot_drop_add_or_change_other_fields(self):
        issues = [{"kind": "nodes", "index": 0}]
        valid = self.corrections["corrections"][0]
        for entries in ([], [valid, valid], [dict(valid, index=1)], [dict(valid, summary="changed")]):
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                semantic.apply_corrections(self.response, issues, {"corrections": entries})


class ScopeTests(unittest.TestCase):
    def test_inventory_excludes_generated_and_external_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "scope"
            root.mkdir()
            (root / "contract.md").write_text("contract", encoding="utf-8")
            (root / "graphify-out").mkdir()
            (root / "graphify-out" / "graph.json").write_text("{}")
            outside = Path(directory) / "external.md"
            outside.write_text("outside")
            try:
                (root / "outside.md").symlink_to(outside)
            except OSError:
                pass
            self.assertEqual(set(graph.inventory(root)), {"contract.md"})

    def test_status_detects_add_modify_delete_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            target = state / "graph.json"
            old = {"a.py": b"old", "deleted.py": b"old"}
            target.write_text(json.dumps({"graph": {"scope": {"files": graph.hashes(old)}}}))
            before = target.read_bytes()
            with patch.object(graph, "STATE", state):
                result = graph.status({"a.py": b"new", "new.py": b"new"}, target)
            self.assertEqual(result["state"], "stale")
            self.assertEqual(result["changed"], ["a.py"])
            self.assertEqual(result["added"], ["new.py"])
            self.assertEqual(result["deleted"], ["deleted.py"])
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(list(state.iterdir()), [target])

    def test_semantic_rejects_wrong_evidence_external_targets_and_model(self):
        raw = b"# Contract\nRequires worker.\n"
        valid = {"source_file": "contract.md", "sha256": semantic.digest(raw),
                 "model": "gpt-6.1-sol", "transport": "codex exec",
                 "nodes": [{"key": "worker", "label": "Worker", "summary": "Worker required", "line": 2, "quote": "Requires worker."}],
                 "edges": [{"source": "worker", "target_file": "worker.py", "relation": "requires", "confidence": "EXTRACTED", "line": 2, "quote": "Requires worker."}]}
        files = {"contract.md": raw, "worker.py": b""}
        semantic.validate(valid, "contract.md", raw, files)
        for alter in (lambda x: x["nodes"][0].update(line=1),
                      lambda x: x["edges"][0].update(target_file="../external.py"),
                      lambda x: x.update(model="other"),
                      lambda x: x.update(sha256="incorrect")):
            wrong = copy.deepcopy(valid)
            alter(wrong)
            with self.assertRaises(ValueError):
                semantic.validate(wrong, "contract.md", raw, files)

    def test_failed_update_preserves_old_graph_and_releases_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            target = state / "graph.json"
            target.write_bytes(b"old graph")
            with patch.object(graph, "STATE", state), patch.object(graph, "GRAPH", target), \
                    patch.object(graph, "extract_document", side_effect=RuntimeError("intentional failure")):
                with self.assertRaisesRegex(RuntimeError, "Graph preserved"):
                    graph.update({"contract.md": b"# Contract"}, 1, 10)
            self.assertEqual(target.read_bytes(), b"old graph")
            self.assertFalse((state / "update.lock").exists())

    def test_structural_graph_has_internal_call_and_document_links(self):
        files = {"a.py": b"from b import worker\ndef caller():\n    return worker()\n",
                 "b.py": b"def worker():\n    return 1\n",
                 "contract.md": b"# Contract\nSee [other](other.md).\nImplementation: `a.py`.\n",
                 "other.md": b"# Other\n"}
        result = graph.build_graph(files, [])
        self.assertEqual({d["source_file"] for _, d in result.nodes(data=True)}, set(files))
        self.assertTrue(any(d.get("relation") == "calls" and result.nodes[u]["source_file"] == "a.py"
                            and result.nodes[v]["source_file"] == "b.py" for u, v, d in result.edges(data=True)))
        self.assertTrue(any(d.get("relation") == "references" and result.nodes[u]["source_file"] == "contract.md"
                            and result.nodes[v]["source_file"] == "other.md" for u, v, d in result.edges(data=True)))
        self.assertTrue(result.has_edge("file::contract.md", "file::a.py"))
        self.assertTrue(any(d.get("quote") == "Implementation: `a.py`." for d in result["file::contract.md"]["file::a.py"].values()))

    def test_local_imports_and_inherited_mixin_calls(self):
        files = {
            "pkg/mixin.py": b"class WorkMixin:\n    def work(self): pass\n",
            "pkg/host.py": b"from .mixin import WorkMixin\nclass Host(WorkMixin):\n    def run(self):\n        self.work()\n",
            "pkg/support.py": b"def helper(): pass\n",
            "tests/fixture.py": b"from pkg.host import Host\n",
            "tests/consumer.py": b"from fixture import helper\nfrom pkg import support\nimport json\n",
        }
        result = graph.build_graph(files, [])
        self.assertTrue(any(u == "pkg_host_host_run" and v == "pkg_mixin_workmixin_work"
                            and d.get("relation") == "calls" and d.get("source_location") == "L4"
                            for u, v, d in result.edges(data=True)))
        self.assertTrue(any(v == "file::tests/fixture.py" and d.get("relation") == "imports_from"
                            for _, v, d in result.edges(data=True)))
        self.assertTrue(any(e["target"] == "pkg" for e in result.graph["unresolved_references"]))
        self.assertFalse(any(e["target"] == "pkg" for e in result.graph["out_of_scope_imports"]))
        self.assertTrue(any(e["target"] == "json" for e in result.graph["out_of_scope_imports"]))
        self.assertFalse(any(e["target"] == "fixture" for e in result.graph["unresolved_references"]))
        import networkx as nx
        bare = nx.MultiDiGraph()
        bare.add_node("caller")
        leftover = graph.resolve_internal_imports(bare, [{"source": "caller", "target": "pkg_support",
                                                        "relation": "imports_from"}], files)
        self.assertEqual(leftover, [])
        self.assertTrue(bare.has_edge("caller", "file::pkg/support.py"))

    def test_super_call_and_import_alias_resolve_without_external_symbol_edges(self):
        files = {
            "base.py": b"class BaseMixin:\n    def step(self): return 1\n",
            "host.py": b"from base import BaseMixin\nclass Host(BaseMixin):\n    def step(self):\n        return super().step()\n",
            "helper.py": b"def target(arg):\n    def wrapper(fn): return fn\n    return wrapper\n",
            "test.py": b"from helper import target as category\nfrom pathlib import Path\nimport argparse\n@category('x')\ndef check(path: Path, parser: argparse.ArgumentParser): pass\n",
            "local.py": b"import os\ndef check(\n    path: os.PathLike[str],\n):\n    from argparse import Namespace\n    return Namespace()\n",
        }
        result = graph.build_graph(files, [])
        self.assertTrue(any(u == "host_host_step" and v == "base_basemixin_step"
                            and d.get("context") == "super_call" and d.get("source_location") == "L4"
                            for u, v, d in result.edges(data=True)))
        self.assertTrue(any(v == "helper_target" and d.get("relation") == "references"
                            and d.get("source_file") == "test.py" for _, v, d in result.edges(data=True)))
        self.assertTrue(any(e["target"] == "path" or e["target"].endswith("_py_path")
                            for e in result.graph["out_of_scope_symbols"]))
        self.assertTrue(any(e["target"] == "argumentparser" or e["target"].endswith("_py_argumentparser")
                            for e in result.graph["out_of_scope_symbols"]))
        self.assertTrue(any(e["target"] == "pathlike" or e["target"].endswith("_py_pathlike")
                            for e in result.graph["out_of_scope_symbols"]))
        remaining, external = graph.resolve_symbol_references(result, [
            {"source": "local_check", "target": "namespace", "relation": "calls",
             "source_file": "local.py", "source_location": "L6"}], files)
        self.assertEqual(remaining, [])
        self.assertEqual(len(external), 1)
        self.assertFalse(any(e["target"].endswith("_py_category") for e in result.graph["unresolved_references"]))

    def test_all_queries_are_read_only_and_preserve_multiple_relations(self):
        import networkx as nx
        from networkx.readwrite import json_graph
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "graph.json"
            g = nx.MultiDiGraph()
            for name in ("caller", "callee"):
                g.add_node(name, label=name, source_file=name + ".py", source_location="L1")
            g.add_edge("caller", "callee", relation="calls", confidence="EXTRACTED")
            g.add_edge("caller", "callee", relation="references", confidence="EXTRACTED")
            target.write_text(json.dumps(json_graph.node_link_data(g, edges="links")))
            before = target.read_bytes()
            with patch.object(graph.subprocess, "run", side_effect=AssertionError("query launched a process")):
                for command, terms in (("query", ["callee"]), ("path", ["caller", "callee"]), ("explain", ["caller"]), ("affected", ["callee"])):
                    with redirect_stdout(io.StringIO()) as output:
                        graph.read_graph(command, terms, graph_path=target)
                    if command != "query":
                        self.assertEqual(json.loads(output.getvalue())["total_edges"], 2)
                    else:
                        self.assertIn("NODE caller", output.getvalue())
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(list(Path(directory).iterdir()), [target])

    def test_file_impact_includes_callers_of_its_symbols(self):
        import networkx as nx
        from networkx.readwrite import json_graph
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "graph.json"
            g = nx.MultiDiGraph()
            for name in ("module", "function", "caller", "unrelated"):
                g.add_node(name, label=name, source_file=name + ".py")
            g.add_edge("module", "function", relation="contains")
            g.add_edge("caller", "unrelated", relation="uses")
            g.add_edge("caller", "function", relation="calls")
            target.write_text(json.dumps(json_graph.node_link_data(g, edges="links")))
            with redirect_stdout(io.StringIO()) as output:
                graph.read_graph("affected", ["module"], graph_path=target)
            result = json.loads(output.getvalue())
            self.assertIn("caller", {n["id"] for n in result["nodes"]})
            self.assertIn("function", {n["id"] for n in result["nodes"]})
            self.assertEqual(result["edges"][0]["target"], "function")
            self.assertEqual(result["edges"][0]["relation"], "calls")

    def test_exact_query_filters_relation_and_keeps_all_visible_endpoints(self):
        import networkx as nx
        from networkx.readwrite import json_graph
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "graph.json"
            g = nx.MultiDiGraph()
            for name in ("caller", "callee", "unrelated"):
                g.add_node(name, label=name, source_file=name + ".py")
            g.add_edge("caller", "callee", relation="calls")
            g.add_edge("caller", "unrelated", relation="references")
            target.write_text(json.dumps(json_graph.node_link_data(g, edges="links")))
            with redirect_stdout(io.StringIO()) as output:
                graph.read_graph("query", ["caller"], graph_path=target, exact=True, relations=["calls"])
            result = json.loads(output.getvalue())
            self.assertEqual({node["id"] for node in result["nodes"]}, {"caller", "callee"})
            self.assertEqual([(edge["source"], edge["target"]) for edge in result["edges"]],
                             [("caller", "callee")])
            with self.assertRaisesRegex(ValueError, "Exact node ID"):
                graph.read_graph("query", ["call"], graph_path=target, exact=True)


if __name__ == "__main__":
    unittest.main()
