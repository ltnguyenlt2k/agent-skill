#!/usr/bin/env python3
"""Append managed adapters without overwriting project rules."""
import argparse
from pathlib import Path
import sys
from framework import ROOT
START='<!-- agent-skill:begin -->'
END='<!-- agent-skill:end -->'


def render(existing, template):
    block=f'{START}\n{template.strip()}\n{END}'
    if START in existing or END in existing:
        if existing.count(START)!=1 or existing.count(END)!=1 or existing.index(START)>existing.index(END):
            raise ValueError('malformed managed adapter block; repair it before installing')
        first,last=existing.index(START),existing.index(END)+len(END)
        return existing[:first]+block+existing[last:]
    return existing.rstrip()+ ('\n\n' if existing.strip() else '') + block+'\n'


def install(project, framework=ROOT):
    project,framework=Path(project).resolve(),Path(framework).resolve()
    if (project/'.agent-skill').resolve()!=framework:
        raise ValueError('framework must be mounted at PROJECT/.agent-skill; add the Git submodule first')
    updates=[]
    for name in ('AGENTS.md','CLAUDE.md'):
        target=project/name
        if target.is_symlink():
            raise ValueError(f'refusing symlink adapter: {target}')
        existing=target.read_text() if target.exists() else ''
        result=render(existing,(framework/'templates'/('project-'+name)).read_text())
        if result!=existing: updates.append((target,result))
    # Validate both before any write, preserving unrelated existing instructions.
    for target,result in updates:
        target.write_text(result)
    return [str(target) for target,_ in updates]

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=ROOT.parent)
    args=parser.parse_args()
    try:
        changed=install(args.project)
        print('Adapters updated: '+', '.join(changed) if changed else 'Adapters already current.')
    except (ValueError,OSError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        sys.exit(1)
