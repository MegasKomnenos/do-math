"""Change only the bare function reference, preserving every other source byte."""
import difflib
import sys
from run_command import ROOT, EVIDENCE, write_json

scripts = ROOT / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(scripts), str(scripts / 'tests')]
from support import doc_code
from do_math import provider_final

doc = ROOT / '.claude/skills/do-math/references/CLI-실행-계약.md'
before = (EVIDENCE / 'cli-before.txt').read_bytes()
assert doc.read_bytes() == before
old, new = b'`provider_final.output_contract`', b'`provider_final.output_contract(...)`'
assert before.count(old) == 1
after = before.replace(old, new)
doc.write_bytes(after)
text = after.decode('utf-8')
schemas = doc_code.field_schemas()
functions = doc_code.function_reference_issues(text)
fields = doc_code.unowned_field_references(text, schemas)
assert functions == [] and fields == [], (functions, fields)
assert callable(provider_final.output_contract)
assert doc_code.function_reference_issues('`governance.missing_function(...)`') == [
    ('function reference', 'governance.missing_function(...)')]
assert doc_code.function_reference_issues('`planning.RECORD_FAMILIES(...)`') == [
    ('function reference', 'planning.RECORD_FAMILIES(...)')]
write_json(EVIDENCE / 'callable-probe.json', {
    'function_issues': functions, 'unowned_fields': fields, 'actual_callable': True,
    'source_bytes_preserved_except_notation': after.replace(new, old) == before,
    'nonexistent_rejected': True, 'noncallable_rejected': True,
    'before_bytes': len(before), 'after_bytes': len(after)})
(EVIDENCE / 'notation.diff').write_text(''.join(difflib.unified_diff(
    before.decode('utf-8').splitlines(keepends=True), text.splitlines(keepends=True),
    fromfile='CLI-실행-계약.before', tofile='CLI-실행-계약.after')), encoding='utf-8')
print('Existing callable and field checks pass; one notation replaced, all other bytes preserved.')
