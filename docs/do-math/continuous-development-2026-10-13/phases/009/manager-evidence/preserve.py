"""Select exact evidence and preserve raw product bytes for the administrative commit."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
ROOT=Path(r'C:\math')
RUN=ROOT/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent
EV=RUN/'phases/009/tasks/document-callable/evidence'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value): p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
verification=json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
products=verification['product_commit_paths']
archive=OUT/'product-raw-bytes.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for path in products: z.writestr(path,(ROOT/path).read_bytes())
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(products)
    assert all(z.read(p)==(ROOT/p).read_bytes() for p in products)
evfiles=sorted(p for p in EV.rglob('*') if p.is_file() and
               not set(p.relative_to(EV).parts).intersection({'scratch','__pycache__','.git'}) and p.suffix!='.pyc')
total=sum(p.stat().st_size for p in evfiles)
assert total<40_000_000, total
common=[RUN/n for n in ('context.md','plan.md','seams.md')]
administrative=[OUT/n for n in ('verify.py','prepare_phase.py','prepare_common.py','preserve.py',
                                'verification.json','source-inspected.json','report-check.json',
                                'review.md','common-state.diff','product-raw-bytes.zip','preservation.json')]
paths=[ROOT/p for p in products]+common+administrative+evfiles+[
    RUN/'phases/009/tasks/document-callable/report.json',RUN/'phases/009/manager.json',
    RUN/'phases/010/phase.json',RUN/'phases/010/tasks/host-smoke/objective.md',
    RUN/'phases/010/tasks/reading-limits/objective.md',ROOT/'기억/layer1/M-0559.md',ROOT/'기억/색인.md']
relative=sorted({p.relative_to(ROOT).as_posix() for p in paths})
assert len(relative)==len(paths)
preservation={'product_paths':{p:sha(ROOT/p) for p in products},
              'raw_archive':{'path':archive.relative_to(RUN).as_posix(),'sha256':sha(archive),
                             'meaning':'Inspected raw bytes; Git clean blobs are validated independently. No automatic restoration.'},
              'task_evidence':{p.relative_to(RUN).as_posix():sha(p) for p in evfiles},
              'task_evidence_bytes':total,'exact_commit_paths':relative,
              'local_only':['Task scratch and service session logs','Git stage/commit receipts and commit-plan.json','Final handoff/administrative gate logs'],
              'excluded':['Timing caches','Unrelated pre-existing dirty/untracked files','Operator model settings and engine changes'],
              'limits':'Phase008 reports/evidence are already tracked; no historical files rewritten. Final overall gates remain incomplete.'}
write(OUT/'preservation.json',preservation)
write(OUT/'commit-plan.json',{'head':verification['head'],'paths':relative,
                            'sha256':{p:sha(ROOT/p) for p in relative if (ROOT/p).exists()}})
(OUT/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
print(json.dumps({'products':len(products),'evidence_files':len(evfiles),'evidence_bytes':total,
                  'commit_paths':len(relative)},ensure_ascii=False))

