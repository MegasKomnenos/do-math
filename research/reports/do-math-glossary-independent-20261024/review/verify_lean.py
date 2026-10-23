"""Recompile the published Lean sources in a separate writable directory.

python verify_lean.py --settings INSTANCE/settings.json --work NEW_WORK_DIR
Reads the existing Lean toolchain; writes only under --work.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--settings',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    source=Path(__file__).resolve().parent/'lean'
    work=args.work.resolve();work.mkdir(parents=True,exist_ok=True)
    build=work/'build';build.mkdir(exist_ok=True)
    logs=work/'logs';logs.mkdir(exist_ok=True)
    settings=json.loads(args.settings.read_text(encoding='utf-8-sig'))['lean']
    env=os.environ.copy();env.update(settings.get('env',{}));env['LEAN_PATH']=str(build)
    order=[];seen=set()
    def visit(name):
        if name in seen:return
        seen.add(name)
        for line in (source/(name+'.lean')).read_text(encoding='utf-8').splitlines():
            if line.startswith('import '):
                for mod in line.split()[1:]:
                    if (source/(mod+'.lean')).exists():visit(mod)
        order.append(name)
    visit('SeriesRepair')
    audit={}
    for name in order:
        path=source/(name+'.lean')
        argv=settings['command']+['-R',str(source),'-o',str(build/(name+'.olean')),str(path)]
        result=subprocess.run(argv,cwd=settings['cwd'],env=env,capture_output=True,encoding='utf-8',errors='replace')
        output=result.stdout+result.stderr
        (logs/(name+'.log')).write_text(output,encoding='utf-8')
        audit[name]={'argv':argv,'cwd':settings['cwd'],'exit_code':result.returncode,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        (work/'execution.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
        print(name,result.returncode,flush=True)
        if result.returncode:raise SystemExit(result.returncode)
    expected=set()
    for name in ('GlossaryRepair','SeriesRepair'):
        text=(source/(name+'.lean')).read_text(encoding='utf-8')
        expected.update('GlossaryRepair.'+x for x in re.findall(r'^#print axioms (\w+)',text,re.M))
    axioms={}
    for name in ('GlossaryRepair','SeriesRepair'):
        for decl,values in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",(logs/(name+'.log')).read_text(encoding='utf-8')):
            axioms[decl]=[x.strip() for x in values.split(',') if x.strip()]
    assert set(axioms)==expected,(set(axioms),expected)
    assert all(set(v)<={'propext','Classical.choice','Quot.sound'} for v in axioms.values()),axioms
    (work/'axioms.json').write_text(json.dumps(axioms,indent=2),encoding='utf-8')
    print('All published repair declarations audited; no additional axioms.')

if __name__=='__main__':main()
