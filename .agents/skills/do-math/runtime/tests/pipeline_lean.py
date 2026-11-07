"""Small compiler stand-in for orchestration tests; not mathematical evidence."""
from pathlib import Path
import re
import sys

if '--version' in sys.argv:
    print('Lean (pipeline test stand-in)')
    raise SystemExit(0)
source = Path(sys.argv[-1]).read_text(encoding='utf-8')
for theorem in re.findall(r'#print axioms\s+(\S+)', source):
    print(f"'{theorem}' does not depend on any axioms")
