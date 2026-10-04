#!/usr/bin/env python3
import argparse
import sys
import yaml
from framework import read_yaml, resolve
parser = argparse.ArgumentParser(description='Resolve semantic decision YAML; no keyword classifier.')
parser.add_argument('decision',help='YAML: tasks, domains, complexity, conditions; optional design_owner')
args = parser.parse_args()
try:
    print(yaml.safe_dump(resolve(read_yaml(args.decision)),sort_keys=False),end='')
except (ValueError,KeyError,TypeError,OSError) as exc:
    print(f'ERROR: {exc}',file=sys.stderr)
    sys.exit(1)
