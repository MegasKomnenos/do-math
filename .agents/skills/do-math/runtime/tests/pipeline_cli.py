"""Scripted session outputs for testing the real orchestration and publication path."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from coordination import claim
from lean_broker import Paths, submit, wait
from runtime_support import read_json, write_json

session = Path.cwd()
inp = read_json(session / 'input.json')
role, task = inp['role'], inp['task']
output = session / 'output'
print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Scripted test activity.'}}), flush=True)

if role in ('attempt', 'explore', 'formalizer'):
    if role == 'attempt':
        claim(session, 'root')
    (output / 'report.md').write_text('For every natural number n, n + 0 = n by the defining equation of addition.', encoding='utf-8')
    if role == 'formalizer':
        (output / 'Proof.lean').write_text('theorem add_zero_example (n : Nat) : n + 0 = n := by rfl\n', encoding='utf-8')
elif role == 'peer':
    producer = Path(task['source'])
    source_role = task['source_role']
    (output / 'record.md').write_text('Natural numbers include zero. Right addition of zero reduces to its left argument by definition.', encoding='utf-8')
    data = {'title': 'Right addition of zero', 'description': 'A proof or observation about right addition of zero.',
            'exposition': 'record.md', 'claims': [{'id': 'c1', 'statement': 'For every natural number n, n + 0 = n.',
                                                'by': 'producer', 'evidence': 'record.md', 'dependencies': []}],
            'nodes': [], 'relations': [], 'solutions': [], 'glossary': []}
    if source_role != 'explore':
        lean = None
        if source_role == 'formalizer':
            shutil.copyfile(producer / 'output/Proof.lean', output / 'Proof.lean')
            lean = {'theorem': 'add_zero_example', 'sources': ['Proof.lean']}
        data['solutions'] = [{'id': 'solution', 'node': 'root', 'outcome': 'proved', 'claim': 'c1', 'formal_dependencies': [], 'lean': lean}]
    write_json(output / 'record.json', data)
elif role == 'review':
    (output / 'feedback.md').write_text('The precise argument was assessed.', encoding='utf-8')
    if task['kind'] == 'comprehensive':
        write_json(output / 'assessment.json', {'feedback': 'feedback.md', 'index_assessment': 'No new verdict.', 'findings': [], 'concerns': []})
    else:
        candidate = Path(task['candidate'])
        data = read_json(candidate / 'record.json')
        assessment = {'publish': True, 'reason': 'Useful retained mathematics.', 'index_assessment': 'Supported within its exact scope.',
                      'feedback': 'feedback.md', 'glossary_approved': True,
                      'claims': [{'claim': c['id'], 'status': 'supported', 'reason': 'Definitional equality.'} for c in data['claims']],
                      'nodes': [], 'relations': [], 'solutions': [], 'concerns': []}
        for solution in data['solutions']:
            verdict = {'proposal': solution['id'], 'level': 'informal', 'reason': 'Exact statement.'}
            if solution['lean']:
                source = candidate / 'Proof.lean'
                copied = session / 'work/Proof.lean'
                copied.write_bytes(source.read_bytes() + b'\n#print axioms add_zero_example\n')
                receipt = submit(Paths(inp['instance']), copied, 64, inp['session'])
                if wait(Paths(inp['instance']), receipt['job'], timeout=30) != 0:
                    raise RuntimeError('test compile failed')
                verdict.update(level='formal', formal_check={'job': receipt['job'], 'theorem': 'add_zero_example', 'axioms': [],
                               'alignment': 'matches', 'reason': 'Same proposition.',
                               'source_hashes': {'Proof.lean': hashlib.sha256(source.read_bytes()).hexdigest()},
                               'source_files': {'Proof.lean': 'work/Proof.lean'}})
            assessment['solutions'].append(verdict)
        write_json(output / 'assessment.json', assessment)
elif role == 'organizer':
    write_json(output / 'organization.json', {'batch': task['batch'], 'shared_context': task['batch'], 'modules': []})
