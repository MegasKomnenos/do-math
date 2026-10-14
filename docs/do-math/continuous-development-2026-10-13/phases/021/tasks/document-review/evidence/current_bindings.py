from work import *
import re
owners={'role_review','pending_findings','review_research','review_sources'}
rows=[]
skill=REPO/'.claude/skills/do-math'
docs=[skill/name for name in ('SKILL.md','README.md','GLOSSARY.md')]+sorted((skill/'references').glob('*.md'))+sorted((skill/'계약').glob('*.md'))
for path in docs:
    heading=''
    for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if line.startswith('#'):heading=line
        if any(owner in line for owner in owners):
            rows.append({'path':path.relative_to(REPO).as_posix(),'line':i,'heading':heading,'text':line})
save('current-bindings.json',{'owners':sorted(owners),'documents':rows,
 'production':{'role_review':'review_cycle.context_for -> _prepare_review_context -> _context.role_review -> prepare_role_input',
               'pending_findings':'_add_findings -> cycle.findings/pending keys -> context_for.pending_findings -> role_review.pending_findings',
               'review_research':'fixed request -> _review_research_context -> _context -> prepare_role_input',
               'review_sources':'request.source_records -> _materialize_research_sources -> review_research.sources (sources line alias)'},
 'conditional_fields':'identity_basis/policy_ref are present in real engine cycles; pure cycle tests preserve their conditional absence.',
 'owners_distinct':'Fixed source ref/inline/artifact/snapshot is not general research_sources id/path/name or task results.',
 'boundary':'stage secrecy and immutable request/proposal/source contracts are unchanged; no new schema or runtime API'})
print(json.dumps(rows,ensure_ascii=False,indent=2))
