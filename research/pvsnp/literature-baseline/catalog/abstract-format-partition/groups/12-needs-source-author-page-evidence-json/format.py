"""Recognize and re-extract this group from the pinned local sources."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from partition import group_main
FORMAT = {'family': 'author-page-evidence-json', 'outcome': 'needs-source'}
if __name__ == '__main__':
    group_main(Path(__file__).parent, FORMAT)
