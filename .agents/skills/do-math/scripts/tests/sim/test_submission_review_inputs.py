"""An identity review's own inputs on a Sim: an oversized retained history and the supplied source's aliases.

The start is ``support.review_sim.opened_sim``: a theorem imported by control
whose identity review the owner opened, its scope action queued. The legacy
tests reached a review opened by the synthetic task flow
(``purpose_fixtures.purpose_state``); no model call is made here.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math.review_cycle import record_turn
from support.engine_lifecycle import applied
from support.review_sim import opened_sim
from support.submission_calls import submission_model


def setUpModule():
    opened_sim()


class ReviewInputTests(unittest.TestCase):
    def test_review_stage_documents_reach_the_final_seat_input(self):
        self.maxDiff = None
        from do_math.context_store import prepare_role_input
        from support.engine_context import assert_review_documents, review_input_value
        from support.review_sim import dispute
        sim = opened_sim()
        engine = sim.engine
        cid = next(iter(engine.runtime['review_cycles']))
        dispute(sim, {'id': 'f1', 'statement': 'Exact quantifier objection', 'evidence': ['proposal']})
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        seen = []
        def proposal_copies(node, proposal):
            if isinstance(node, dict):
                return int(node == proposal) + sum(proposal_copies(v, proposal) for v in node.values())
            if isinstance(node, list):
                return sum(proposal_copies(v, proposal) for v in node)
            return 0
        for _ in range(12):
            action = deepcopy(next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review'))
            stage = action['stage']
            workspace = root / ('seat-' + str(len(seen)))
            context = engine._context(action, workspace)
            cycle = engine.runtime['review_cycles'][cid]
            value = context['role_review']
            assert_review_documents(self, value, owner='role_review', cycle=cycle, action=action)
            prepared = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='identity_review', profile=engine._execution_profile(action), snapshot=engine.head,
                workspace=workspace, activity_id=action['id'], clock=engine.ports.clock)
            final = review_input_value(self, prepared['context'], 'role_review', workspace,
                                       manifest=prepared['manifest'])
            assert_review_documents(self, final, owner='role_review', cycle=cycle, action=action)
            self.assertNotIn('proposal', prepared['context'], 'the complete proposal belongs to role_review once')
            self.assertEqual(final['proposal'], cycle['proposal'])
            self.assertEqual(proposal_copies(prepared['context'], cycle['proposal']), 1,
                             'the input-size contract supplies the complete current proposal exactly once')
            self.assertEqual(proposal_copies(final, cycle['proposal']), 1)
            from do_math.values import compact_json_bytes
            import hashlib
            for reference in final['source_refs']:
                original = cycle['turns'][reference['slot']][reference['index']]
                raw = (workspace / reference['local_path']).read_bytes()
                self.assertEqual(raw, compact_json_bytes(original))
                self.assertEqual(hashlib.sha256(raw).hexdigest(), reference['sha256'])
                self.assertEqual(len(raw), reference['bytes'])
                self.assertEqual(reference['proposal_digest'],
                    cycle['transcript_manifest'][reference['slot']][reference['index']]['proposal_digest'])
                self.assertIn({'role': original['role'], 'content': {'source_ref': reference}}, final['self_messages'])
            if stage == 'organize':
                assert_review_documents(self, final['pending_findings'], owner='pending_findings',
                                        cycle=cycle, action=action)
                for field in ('ref', 'stage', 'slot', 'id'):
                    changed = deepcopy(final['pending_findings'])
                    if field == 'ref':
                        del changed[0]['ref']
                    else:
                        changed[0]['ref'][field] = 'another-owner'
                    reason = (r'actual field.*pending_findings\[\]\.ref' if field == 'ref' else
                              "'" + field + "': 'another-owner'")
                    with self.subTest(fault=field), self.assertRaisesRegex(AssertionError, reason):
                        assert_review_documents(self, changed, owner='pending_findings', cycle=cycle, action=action)
            for field in ('proposal', 'identity_basis', 'policy_ref'):
                changed = deepcopy(final)
                del changed[field]
                reason = ('proposal' if field == 'proposal' else
                          r': role_review\.' + field + r' presence$')
                with self.subTest(stage=stage, missing=field), self.assertRaisesRegex(AssertionError, reason):
                    assert_review_documents(self, changed, owner='role_review', cycle=cycle, action=action)
            seen.append(stage)
            if stage == 'answer':
                break
            sim.step()
        self.assertEqual(set(seen), {'scope', 'initial', 'organize', 'judge', 'answer'})


    def test_large_own_review_history_does_not_request_mathematical_reconstruction(self):
        """The name says no reconstruction is requested; like the legacy test, this checks no model call and no resource disposition."""
        sim = opened_sim()
        engine = sim.engine
        self.assertEqual(engine.runtime["queue"][0]["role"], "identity_review")
        action = next(a for a in engine.runtime["queue"] if a["role"] == "identity_review")
        cid, kid = action["review_cycle_id"], action["target"]
        # The review input limit is its pinned profile's (context_store.prepare_role_input),
        # not the live config; the retained history alone exceeds it.
        limit = engine._execution_profile(action)["input"]["max_input_bytes"]
        engine.runtime["review_cycles"][cid] = record_turn(engine.runtime["review_cycles"][cid], action["slot"], [
            {"role": "assistant", "content": "Retained earlier reasoning. " * (limit // 28 + 1),
             "message_id": "retained-history"}])
        before = deepcopy(engine.instance["knowledge"][kid])
        engine._save()
        model = submission_model(sim)
        sim.step()
        self.assertEqual(model.calls, [])
        self.assertEqual(sim.instance["knowledge"][kid], before)
        self.assertFalse(any(row.get("event") == "review_resource_disposition"
                             for row in sim.runtime["review_cycles"][cid]["history"]))

    def test_fixed_question_resolver_accepts_the_supplied_source_aliases(self):
        # Review input reads the instance's supplied sources when it is prepared,
        # so the source may arrive after the cycle opened.
        sim = opened_sim()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        path = root / "paper.txt"
        path.write_text("The exact original source.", encoding="utf-8")
        applied(sim, "source", config={"path": str(path)})
        engine = sim.engine
        action = next(a for a in engine.runtime["queue"] if a["role"] == "identity_review")
        context = engine._context(action, root / "source-alias-input")
        source = context["sources"][0]
        cycle = engine.runtime["review_cycles"][action["review_cycle_id"]]
        for reference in (source["id"], "source:" + source["name"], source["local_path"], source["path"], source["name"]):
            with self.subTest(reference=reference):
                error = resolved = None
                try:
                    resolved = engine._research_source_spec(cycle, action, reference)
                except ValueError as rejected:
                    error = str(rejected)
                self.assertIsNone(error, "a supplied source alias was refused: " + str(error))
                self.assertEqual(resolved["sha256"], source["sha256"])


if __name__ == "__main__":
    unittest.main()
