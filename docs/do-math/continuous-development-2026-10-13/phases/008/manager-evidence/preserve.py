"""Preserve bounded task evidence and raw pending product bytes before handoff."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
TASK = RUN / 'phases/008/tasks/document-recovery'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    report = json.loads((TASK / 'report.json').read_text(encoding='utf-8-sig'))
    final = json.loads((TASK / 'evidence/source-final.json').read_text(encoding='utf-8-sig'))
    changed = sorted(row['path'] for row in report['changes'])
    archive = OUT / 'pending-product-bytes.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for rel in changed:
            assert sha(ROOT / rel) == final[rel]
            z.writestr(rel, (ROOT / rel).read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert sorted(z.namelist()) == changed
        assert all(hashlib.sha256(z.read(rel)).hexdigest() == final[rel] for rel in changed)
    evidence = sorted(p for p in (TASK / 'evidence').rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts and 'scratch' not in p.parts)
    local_only = {'commit.json', 'commit-paths.nul', 'commit-message.txt', 'stage.json', 'commit-plan.json',
                  'finalize.json'}
    manager = sorted(p for p in OUT.iterdir() if p.is_file() and p.name not in local_only)
    paths = set(evidence + manager + [TASK / 'report.json', RUN / 'context.md', RUN / 'plan.md', RUN / 'seams.md',
                RUN / 'phases/009/phase.json', RUN / 'phases/009/tasks/document-callable/objective.md',
                ROOT / '기억/layer1/M-0558.md', ROOT / '기억/색인.md'])
    paths.add(OUT / 'preservation.json')
    paths.add(RUN / 'phases/008/manager.json')
    preservation = {'pending_product': {'archive': archive.relative_to(RUN).as_posix(),
                        'sha256': sha(archive), 'files': {p: final[p] for p in changed},
                        'meaning': 'Inspection-time raw bytes only; products await009 regression and are not staged as product files.'},
                    'task_evidence': {p.relative_to(RUN).as_posix(): sha(p) for p in evidence},
                    'task_report_sha256': sha(TASK / 'report.json'),
                    'tracked_paths': sorted(p.relative_to(ROOT).as_posix() for p in paths),
                    'local_only': sorted(local_only) + ['phases/008/logs/', 'runtime/'],
                    'common_doc_review': 'common-documents.diff was reviewed; G1~G8 and unrelated C content remain unchanged. C10 removes the obsolete recovery_source retention claim because008 removed its last consumer.'}
    (OUT / 'preservation.json').write_text(json.dumps(preservation, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'commit-plan.json').write_text(json.dumps({'paths': preservation['tracked_paths']}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'pending_product_files': len(changed), 'archive_bytes': archive.stat().st_size,
                      'evidence_files': len(evidence), 'commit_paths': len(paths)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
