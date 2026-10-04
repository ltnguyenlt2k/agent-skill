#!/usr/bin/env python3
"""Preview or explicitly apply one upstream at a specified immutable commit."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import yaml
from framework import ROOT, load, safe_path, validate


def git(repo,*args,capture=True):
    result=subprocess.run(['git','-C',str(repo),*args],check=True,text=True,
                          stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def vendor_files(source,up):
    files={}
    modes={}
    # Use the entire Git tree of the selected package, including hidden companion files.
    package=up['package']
    for line in git(source,'ls-tree','-r','HEAD','--',package).splitlines():
        meta,origin=line.split('\t')
        mode=meta.split()[0]
        if mode not in ('100644','100755'): raise ValueError('unsupported vendor entry mode: '+mode)
        relative=str(Path(origin).relative_to(package))
        modes[relative]=mode
        files[relative]=subprocess.check_output(['git','-C',str(source),'show',f'HEAD:{origin}'])
    extras=({'LICENSE.md':'UPSTREAM-LICENSE.md'} if package=='plugins/security-guidance'
            else {'THIRD_PARTY_NOTICES.md':'UPSTREAM-NOTICES.md'})
    for origin,target in extras.items():
        files[target]=subprocess.check_output(['git','-C',str(source),'show',f'HEAD:{origin}'])
        modes[target]='100644'
    if not files: raise ValueError('upstream package disappeared')
    return files,modes


def apply_files(target,files,modes):
    # Caller already checked target against its locked manifest; only this vendor tree changes.
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True)
    for relative,data in files.items():
        path=safe_path(target,relative)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o755 if modes[relative]=='100755' else 0o644)


def update(name,target_sha,apply=False,root=ROOT,show_diff=False):
    if not re.fullmatch(r'[0-9a-f]{40}',target_sha):
        raise ValueError('target must be a full immutable 40-character commit SHA')
    config=load(root)
    upstreams=config['upstream-lock']['upstreams']
    if name not in upstreams: raise ValueError(f'unknown upstream: {name}')
    up=upstreams[name]
    problems=validate(root,config)
    if problems: raise ValueError('repair current registry first: '+'; '.join(problems))
    path=safe_path(root,up['path'])
    old=up['commit']
    if old==target_sha:
        print(f'{name}: already pinned to {old}')
        return
    with tempfile.TemporaryDirectory(prefix='agent-skill-update-') as temp:
        if up['strategy']=='submodule':
            source=path
        else:
            source=Path(temp)/'source'
            source.mkdir()
            git(source,'init','--quiet')
            git(source,'remote','add','origin',up['repo'])
        git(source,'fetch','--no-tags','origin',old,target_sha,capture=False)
        git(source,'cat-file','-e',target_sha+'^{commit}')
        print(f'{name}\nOld: {old}\nNew: {target_sha}',flush=True)
        diffargs=['diff',old,target_sha]
        if up['strategy']=='vendor': diffargs+=['--',up['package']]
        git(source,*(diffargs[:1]+['--stat']+diffargs[1:]),capture=False)
        if show_diff: git(source,*diffargs,capture=False)
        if not apply:
            print('Preview only. Inspect the diff (--diff), then rerun with --apply to switch this pin.')
            return
        lock_path=root/'registry/upstream-lock.yaml'
        original_lock=lock_path.read_bytes()
        old_files={str(f.relative_to(path)):f.read_bytes() for f in path.rglob('*') if f.is_file()} if up['strategy']=='vendor' else None
        try:
            if up['strategy']=='submodule':
                git(source,'checkout','--detach',target_sha,capture=False)
                git(source,'submodule','update','--init','--recursive',capture=False)
            else:
                git(source,'checkout','--detach',target_sha,capture=False)
                files,modes=vendor_files(source,up)
                apply_files(path,files,modes)
                up['modes']=modes
                up['files']={p:hashlib.sha256(data).hexdigest() for p,data in sorted(files.items())}
            up['commit']=target_sha
            lock_path.write_text(yaml.safe_dump(config['upstream-lock'],sort_keys=False))
            problems=validate(root)
            if problems: raise ValueError('changed/missing skill paths or invalid registry: '+'; '.join(problems))
            for check in ('test-router.py','test-tooling.py'):
                subprocess.run([sys.executable,str(root/'scripts'/check)],check=True)
        except BaseException:
            lock_path.write_bytes(original_lock)
            if up['strategy']=='submodule':
                git(source,'checkout','--detach',old,capture=False)
                git(source,'submodule','update','--init','--recursive',capture=False)
            else: apply_files(path,old_files,yaml.safe_load(original_lock)['upstreams'][name]['modes'])
            print('Update failed; restored previous checkout/package and lock.',file=sys.stderr)
            raise
        print('Updated and verified. Review Git diff and commit the gitlink/vendor tree with the lock together.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('upstream')
    parser.add_argument('commit',help='full 40-character commit SHA; no implicit latest')
    parser.add_argument('--apply',action='store_true',help='explicitly switch checkout and lock after inspecting preview')
    parser.add_argument('--diff',action='store_true',help='show complete upstream diff')
    args=parser.parse_args()
    try: update(args.upstream,args.commit,args.apply,show_diff=args.diff)
    except (ValueError,OSError,subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        sys.exit(1)
