import sys
from task_driver import E, PY, REPO, baseline_check, execute, snapshot, write

steps = [
    ('verify-final-mirror-plan',[PY,'-u','-B',E/'verify_task.py','mirror-plan']),
    ('final-mirror-build',[PY,'-u','-B',REPO/'.claude/skills/writing-skills/scripts/build_skill_mirrors.py']),
    ('mirror-check',[PY,'-u','-B',REPO/'.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check']),
    ('skill',[PY,'-u','-B',REPO/'.claude/skills/do-math/scripts/probe_cli.py','--skill-only']),
]
for label, argv in steps:
    code = execute(label,argv,external_temp=True)
    if code: sys.exit(code)
write(E/'source-final.json',snapshot())
baseline_check('final')
sys.exit(execute('final-verify',[PY,'-u','-B',E/'final_verify.py'],external_temp=True))
