"""Run a fresh, entirely real CLI/Lean research instance from a frozen skill."""
import argparse, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--skill-root',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--academic',action='store_true')
args=p.parse_args();skill=args.skill_root.resolve();dest=args.destination.resolve();dest.mkdir(parents=True,exist_ok=False)
entry=skill/'scripts/do_math.py';repo=dest/'repository';workspace=dest/'workspace'
manifest={path.relative_to(skill).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in skill.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc'}
(dest/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
goal='Prove that for every natural number n, n + 0 = n. Give a self-contained Lean proof using Lean core and a faithful concise explanation of its domain and quantification. Complete the reviewed task and the independent mathematical goal audits.'
(dest/'goal.txt').write_text(goal,encoding='utf-8')
config={'model':'gpt-5.6-sol','effort':'medium','work_calls':30,'operations_calls':20,'max_cycles':4,
        'reviewers':2,'goal_auditors':2,'review_rounds':3,'call_timeout_seconds':300,'run_timeout_seconds':2400,
        'lean_command':[r'C:\math\.skill-workspace\do-math-toolchains\lean-4.32.0\lean-4.32.0-windows\bin\lean.exe']}
(dest/'config.json').write_text(json.dumps(config),encoding='utf-8')
def command(name,*argv):
    print(name,flush=True)
    completed=subprocess.run([sys.executable,str(entry),*argv],cwd=r'C:\math',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (dest/(name+'-stdout.json')).write_bytes(completed.stdout);(dest/(name+'-stderr.txt')).write_bytes(completed.stderr)
    if completed.returncode:raise RuntimeError(name+' exit '+str(completed.returncode))
    return json.loads(completed.stdout.decode('utf-8'))
started=time.time()
initial=command('init','init','--create-repository','--repository',str(repo),'--workspace',str(workspace),'--goal-file',str(dest/'goal.txt'),'--config-file',str(dest/'config.json'))
instance=initial['instance_id'];common=['--repository',str(repo),'--instance',instance]
if args.academic:
    requirement={'kind':'academic_requirements','requirements':[{'id':'reproducibility-note','scope':'Write a brief reproducibility note for the solved theorem using its recorded Lean verification.',
        'assessor':'research_plan','criteria':['Create a readable note naming the verified theorem, the natural-number quantifier, and the exact Lean version recorded by the formal verifier.']}]}
    (dest/'academic-decision.json').write_text(json.dumps(requirement),encoding='utf-8')
    command('academic-decision','decision',*common,'--file',str(dest/'academic-decision.json'))
result=command('run','run',*common)
status=command('status','status',*common,'--json');check=command('check','check',*common)
command('export','export',*common,'--destination',str(dest/'export'),'--all')
subprocess.run(['git','-C',str(repo),'bundle','create',str(dest/'research.bundle'),'--all'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
passed=status['status']=='completed' and status['goal_status']=='mathematically_solved' and status['knowledge']['K']>=1 and check['passed']
if args.academic: passed=passed and status['academic_validation']['status']=='completed'
report={'passed':passed,'all_model_executions':'actual Codex CLI using existing login','formal':'actual Lean',
        'instance_id':instance,'status':status,'check':check,'elapsed_seconds':time.time()-started,'source_manifest':'source-manifest.json'}
(dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':passed,'instance_id':instance,'status':status['status'],'goal_status':status['goal_status'],'budget':status['budget'],'check':check},ensure_ascii=False),flush=True)
sys.exit(0 if passed else 1)
