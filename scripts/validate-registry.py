#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
from framework import ROOT, validate
parser = argparse.ArgumentParser(description='Validate registry, integrity and pinned checkouts.')
parser.add_argument('--root',type=Path,default=ROOT)
args = parser.parse_args()
try:
    errors = validate(args.root.resolve())
except (ValueError,KeyError,TypeError,OSError) as exc:
    errors = [str(exc)]
for error in errors: print('ERROR:',error,file=sys.stderr)
if errors: sys.exit(1)
print('Registry valid: sources, responsibilities, conflicts, workflows, domains and pins.')
