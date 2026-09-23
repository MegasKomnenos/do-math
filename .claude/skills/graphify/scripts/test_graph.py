import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import graph
import semantic


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
                 "model": "gpt-6-sol", "transport": "codex exec",
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
            for name in ("module", "function", "caller"):
                g.add_node(name, label=name, source_file=name + ".py")
            g.add_edge("module", "function", relation="contains")
            g.add_edge("caller", "function", relation="calls")
            target.write_text(json.dumps(json_graph.node_link_data(g, edges="links")))
            with redirect_stdout(io.StringIO()) as output:
                graph.read_graph("affected", ["module"], graph_path=target)
            result = json.loads(output.getvalue())
            self.assertIn("caller", {n["id"] for n in result["nodes"]})
            self.assertEqual(result["edges"][0]["target"], "function")


if __name__ == "__main__":
    unittest.main()
