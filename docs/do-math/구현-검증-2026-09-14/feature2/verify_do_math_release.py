import hashlib,json,re,subprocess,sys,tempfile,zipfile
from pathlib import Path
root=Path(r'C:\math')
skill=root/'.claude/skills/do-math'
base=root/'docs/do-math/구현-검증-2026-09-14/feature2'
documents=[skill/'README.md',skill/'SKILL.md',skill/'GLOSSARY.md',skill/'references/CLI-실행-계약.md',
           *list((skill/'계약').glob('*.md')),root/'docs/do-math/구현-진행.md',root/'docs/do-math/기능-완료-대응.md',
           base/'README.md',base/'workflow/README.md',base/'semantic/README.md',base/'regression/README.md',base/'cli-profile/README.md']
missing=[]
for document in documents:
    for target in re.findall(r'\]\(([^)]+)\)',document.read_text(encoding='utf-8')):
        target=target.split('#',1)[0]
        if target and not target.startswith(('http:','https:','mailto:','/C:')) and not (document.parent/target).exists():
            missing.append([str(document.relative_to(root)),target])
archives=[]
for directory,manifest_name in ((base/'workflow','source-manifest.json'),(base/'regression/full','manifest.json'),(base/'regression/planning-final','manifest.json')):
    manifest=json.loads((directory/manifest_name).read_text(encoding='utf-8'))
    with zipfile.ZipFile(directory/'tested-skill.zip') as archive:
        assert set(archive.namelist())==set(manifest)
        assert all(hashlib.sha256(archive.read(name)).hexdigest()==digest for name,digest in manifest.items())
    archives.append({'path':str(directory.relative_to(base)),'files':len(manifest),'passed':True})
temporary=Path(tempfile.mkdtemp(prefix='do-math-bundle-restore-',dir=root/'.skill-workspace'))
subprocess.run(['git','-C',str(temporary),'init','-q'],check=True)
report=json.loads((base/'workflow/report.json').read_text(encoding='utf-8'))
ref='refs/heads/do-math/'+report['instance_id']
subprocess.run(['git','-C',str(temporary),'fetch',str(base/'workflow/research.bundle'),ref+':'+ref],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
sys.path.insert(0,str(skill/'scripts'))
from do_math.engine import ResearchEngine
restored=ResearchEngine(temporary,report['instance_id']).check()
result={'passed':not missing and restored['passed'],'missing_links':missing,'source_archives':archives,
        'restored_workflow_check':restored,'restoration_uses_actual_Git_and_current_checker':True,
        'no_models_or_Lean_started':True}
(base/'release-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
sys.exit(0 if result['passed'] else 1)
