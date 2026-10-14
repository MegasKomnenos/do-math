from work import *
unit=REPO/'.claude/skills/do-math/scripts/tests/unit/test_review_research_owner_contract.py'
text=unit.read_text(encoding='utf-8')
start=text.index('    def test_review_stage_documents_reach_the_final_seat_input')
end=text.index('    def investigation',start)
method=text[start:end]
method=method.replace("        self.engine.instance['knowledge']['K1']['title'] = 'Fixture theorem'\n        from support.storage_records import INSTANCE_ID\n        self.engine.instance['id'] = INSTANCE_ID\n        self.engine.instance['goal_status'] = 'unresolved'\n        cid, _ = self.opened(scope=True)", "        from support.review_sim import dispute\n        sim = opened_sim()\n        engine = sim.engine\n        cid = next(iter(engine.runtime['review_cycles']))\n        dispute(sim, {'id': 'f1', 'statement': 'Exact quantifier objection', 'evidence': ['proposal']})\n        directory = tempfile.TemporaryDirectory()\n        self.addCleanup(directory.cleanup)\n        root = Path(directory.name)")
method=method.replace('self.engine','engine').replace("deepcopy(self.scene.pending())", "deepcopy(next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review'))").replace("self.root /", "root /")
a=method.index('            changes = None')
b=method.index('        self.assertEqual(set(seen)',a)
method=method[:a]+'            sim.step()\n'+method[b:]
text=text[:start]+text[end:]
text=text.replace("        self.engine.instance['knowledge']['K1']['title'] = 'Fixture theorem'\n        from support.storage_records import INSTANCE_ID\n        self.engine.instance['id'] = INSTANCE_ID\n        self.engine.instance['goal_status'] = 'unresolved'\n",'')
start=text.index("        workspace = self.root / 'final-fixed'")
end=text.index("        for field in ('question',",start)
text=text[:start]+"        workspace = self.root / 'frozen'\n        final = context['review_research']\n"+text[end:]
text=text.replace('        from do_math.context_store import prepare_role_input\n','').replace('from support.engine_context import assert_review_documents, review_input_value','from support.engine_context import assert_review_documents')
unit.write_text(text,encoding='utf-8',newline='')
sim=REPO/'.claude/skills/do-math/scripts/tests/sim/test_submission_review_inputs.py'
text=sim.read_text(encoding='utf-8').replace('class ReviewInputTests(unittest.TestCase):','class ReviewInputTests(unittest.TestCase):\n'+method)
sim.write_text(text,encoding='utf-8',newline='')
structure=REPO/'.claude/skills/do-math/scripts/tests/structure/test_doc_code.py'
text=structure.read_text(encoding='utf-8')
text=text.replace("tree = ast.parse((SCRIPTS / 'tests/unit/test_review_research_owner_contract.py').read_text(encoding='utf-8'))\n        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ResearchOwnerContractTests')\n        owners =",'owners =')
text=text.replace("'role_review': 'test_review_stage_documents_reach_the_final_seat_input'", "'role_review': ('sim/test_submission_review_inputs.py', 'ReviewInputTests', 'test_review_stage_documents_reach_the_final_seat_input')")
text=text.replace("'pending_findings': 'test_review_stage_documents_reach_the_final_seat_input'", "'pending_findings': ('sim/test_submission_review_inputs.py', 'ReviewInputTests', 'test_review_stage_documents_reach_the_final_seat_input')")
for owner in ('review_research','review_sources'):
    text=text.replace("'"+owner+"': 'test_fixed_question_context_keeps_original_bytes_after_unrelated_publication'", "'"+owner+"': ('unit/test_review_research_owner_contract.py', 'ResearchOwnerContractTests', 'test_fixed_question_context_keeps_original_bytes_after_unrelated_publication')")
text=text.replace('for owner, name in mapping.items():\n                methods =', "for owner, (path, class_name, name) in mapping.items():\n                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))\n                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)\n                methods =")
text=text.replace("changed['review_sources'] = 'missing'", "changed['review_sources'] = (*changed['review_sources'][:2], 'missing')").replace("changed['review_sources'] = 'test_research_schema_pins_question_and_digest'", "changed['review_sources'] = (*changed['review_sources'][:2], 'test_research_schema_pins_question_and_digest')")
structure.write_text(text,encoding='utf-8',newline='')
