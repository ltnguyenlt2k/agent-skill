#!/usr/bin/env python3
"""Offline behavior checks for adapter preservation and updater rollback."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from framework import ROOT


def module(filename,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/filename)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

installer=module('install-project.py','installer')
updater=module('update-upstream.py','updater')

class ToolingTests(unittest.TestCase):
    def test_install_preserves_constraints_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp); kit=project/'.agent-skill'
            (kit/'templates').mkdir(parents=True)
            for name in ('AGENTS.md','CLAUDE.md'):
                (kit/'templates'/('project-'+name)).write_text('Read .agent-skill/router/ROUTER.md')
                (project/name).write_text('Project rule: preserve Qt6.\n')
            self.assertEqual(len(installer.install(project,kit)),2)
            result=(project/'AGENTS.md').read_text()
            self.assertIn('Project rule: preserve Qt6.',result)
            self.assertIn('.agent-skill/router/ROUTER.md',result)
            self.assertEqual(installer.install(project,kit),[])

    def test_install_malformed_block_no_partial_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp); kit=project/'.agent-skill'
            (kit/'templates').mkdir(parents=True)
            for name in ('AGENTS.md','CLAUDE.md'):
                (kit/'templates'/('project-'+name)).write_text('adapter')
            (project/'CLAUDE.md').write_text(installer.START)
            with self.assertRaises(ValueError): installer.install(project,kit)
            self.assertFalse((project/'AGENTS.md').exists())

    def test_install_wrong_mount_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp); kit=project/'.agent-skill'; kit.mkdir()
            with self.assertRaises(ValueError): installer.install(project,project/'wrong')
            (project/'AGENTS.md').symlink_to(project/'outside')
            with self.assertRaisesRegex(ValueError,'symlink'): installer.install(project,kit)

    def test_unknown_upstream_and_mutable_ref_rejected(self):
        for name,sha in [('superpowers','main'),('unknown','1'*40)]:
            with self.subTest(name=name),self.assertRaises(ValueError): updater.update(name,sha)

    def fixture(self,root):
        source=root/'source';source.mkdir()
        def git(*args):
            return subprocess.check_output(['git','-C',str(source),*args],text=True,stderr=subprocess.DEVNULL).strip()
        git('init','--quiet')
        git('config','user.name','Tooling Test')
        git('config','user.email','test@example.invalid')
        pkg=source/'plugins/security-guidance';pkg.mkdir(parents=True)
        (source/'LICENSE.md').write_text('fixture license')
        (pkg/'README.md').write_text('old')
        (pkg/'run.sh').write_text('#!/bin/sh\nexit 0\n');(pkg/'run.sh').chmod(0o755)
        git('add','.');git('commit','-qm','old');old=git('rev-parse','HEAD')
        (pkg/'README.md').write_text('new')
        git('add','.');git('commit','-qm','new');new=git('rev-parse','HEAD')
        kit=root/'kit';kit.mkdir()
        path=kit/'conditional/security-guidance';path.mkdir(parents=True)
        (path/'README.md').write_text('old')
        (path/'run.sh').write_text('#!/bin/sh\nexit 0\n');(path/'run.sh').chmod(0o755)
        (path/'UPSTREAM-LICENSE.md').write_text('fixture license')
        up={'repo':str(source),'commit':old,'path':'conditional/security-guidance','strategy':'vendor',
            'package':'plugins/security-guidance','files':{str(f.relative_to(path)):hashlib.sha256(f.read_bytes()).hexdigest() for f in path.iterdir()},
            'modes':{'README.md':'100644','run.sh':'100755','UPSTREAM-LICENSE.md':'100644'}}
        (kit/'registry').mkdir()
        lock={'upstreams':{'security-guidance':up}}
        (kit/'registry/upstream-lock.yaml').write_text(yaml.safe_dump(lock))
        return kit,path,{'upstream-lock':lock},new

    def test_vendor_preview_apply_and_rollback_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit,path,config,new=self.fixture(Path(tmp))
            original=(kit/'registry/upstream-lock.yaml').read_bytes()
            # Fixtures use a local git remote. Validation is tested separately in test-router.
            with patch.object(updater,'load',return_value=config),patch.object(updater,'validate',return_value=[]),contextlib.redirect_stdout(io.StringIO()):
                updater.update('security-guidance',new,root=kit)
                self.assertEqual((path/'README.md').read_text(),'old')
                self.assertEqual((kit/'registry/upstream-lock.yaml').read_bytes(),original)
                real_run=subprocess.run
                with patch.object(updater.subprocess,'run',wraps=real_run) as run:
                    # Let real Git calls run; fail the post-update test command.
                    def fail_check(args,**kwargs):
                        if str(args[0]).endswith('python3') or 'test-router.py' in str(args):
                            raise subprocess.CalledProcessError(1,args)
                        return real_run(args,**kwargs)
                    run.side_effect=fail_check
                    with self.assertRaises(subprocess.CalledProcessError):
                        updater.update('security-guidance',new,apply=True,root=kit)
                self.assertEqual((path/'README.md').read_text(),'old')
                self.assertEqual((kit/'registry/upstream-lock.yaml').read_bytes(),original)
                self.assertTrue((path/'run.sh').stat().st_mode & 0o111)
            # Apply succeeds when fixture checks exist.
            (kit/'scripts').mkdir()
            for name in ('test-router.py','test-tooling.py'):
                (kit/'scripts'/name).write_text('pass\n')
            config['upstream-lock']=yaml.safe_load(original)
            with patch.object(updater,'load',return_value=config),patch.object(updater,'validate',return_value=[]),contextlib.redirect_stdout(io.StringIO()):
                updater.update('security-guidance',new,apply=True,root=kit)
            self.assertEqual((path/'README.md').read_text(),'new')
            self.assertEqual(yaml.safe_load((kit/'registry/upstream-lock.yaml').read_text())['upstreams']['security-guidance']['commit'],new)
            self.assertTrue((path/'run.sh').stat().st_mode & 0o111)

    def test_submodule_update_rolls_back_failed_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            kit,_,_,new=self.fixture(base)
            source=base/'source'
            old=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD~1'],text=True).strip()
            target=kit/'upstream/demo';target.parent.mkdir()
            subprocess.run(['git','clone','--quiet',str(source),str(target)],check=True)
            subprocess.run(['git','-C',str(target),'checkout','--quiet','--detach',old],check=True)
            config={'upstream-lock':{'upstreams':{'demo':{'repo':str(source),'commit':old,'path':'upstream/demo','strategy':'submodule'}}}}
            lock=kit/'registry/upstream-lock.yaml';lock.write_text(yaml.safe_dump(config['upstream-lock']))
            original=lock.read_bytes()
            (kit/'scripts').mkdir()
            (kit/'scripts/test-router.py').write_text('raise SystemExit(1)\n')
            (kit/'scripts/test-tooling.py').write_text('pass\n')
            with patch.object(updater,'load',return_value=config),patch.object(updater,'validate',return_value=[]),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(subprocess.CalledProcessError):
                    updater.update('demo',new,apply=True,root=kit)
                self.assertEqual(subprocess.check_output(['git','-C',str(target),'rev-parse','HEAD'],text=True).strip(),old)
                self.assertEqual(lock.read_bytes(),original)
                config['upstream-lock']=yaml.safe_load(original)
                (kit/'scripts/test-router.py').write_text('pass\n')
                updater.update('demo',new,apply=True,root=kit)
            self.assertEqual(subprocess.check_output(['git','-C',str(target),'rev-parse','HEAD'],text=True).strip(),new)
            self.assertEqual(yaml.safe_load(lock.read_text())['upstreams']['demo']['commit'],new)

if __name__=='__main__': unittest.main(verbosity=2)
