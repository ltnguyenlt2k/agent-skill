"""Deterministic constraints; semantic classification belongs to the coding agent."""
from pathlib import Path
import hashlib
import re
import subprocess
import yaml
ROOT = Path(__file__).resolve().parents[1]
BUDGETS = {'trivial': 1, 'small': 2, 'medium': 3, 'complex': 5}
PHASES = ('routing', 'planning', 'implementation', 'review', 'verification')
CONDITIONS = {'always', 'ambiguous', 'plan_needed', 'regression_needed', 'review_needed',
 'review_feedback', 'worktree_needed', 'independent_workstreams', 'touches_react',
 'ui_audit', 'browser_needed', 'research_needed', 'security_sensitive'}


def read_yaml(path):
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError(f'{path}: expected a mapping')
    return data


def load(root=ROOT):
    return {name: read_yaml(root / 'registry' / f'{name}.yaml') for name in
            ('skills', 'workflows', 'domains', 'upstream-lock')}


def safe_path(root, path):
    if not isinstance(path, str) or Path(path).is_absolute():
        raise ValueError(f'invalid relative path: {path!r}')
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f'path escapes framework: {path}')
    return resolved


def selection_errors(ids, skills, complexity, allow_optional=False, check_budget=True):
    errors, owners = [], {}
    if complexity not in BUDGETS:
        return [f'unknown complexity: {complexity}']
    if len(ids) != len(set(ids)):
        errors.append('duplicate skill IDs')
    if check_budget and len(ids) > BUDGETS[complexity]:
        errors.append(f'{complexity} phase budget exceeded: {len(ids)} > {BUDGETS[complexity]}')
    for sid in ids:
        if sid not in skills:
            errors.append(f'unknown skill: {sid}')
            continue
        s = skills[sid]
        if not s['enabled'] and not allow_optional:
            errors.append(f'disabled skill selected: {sid}')
        owner = owners.setdefault(s['responsibility'], sid)
        if owner != sid:
            errors.append(f'duplicate responsibility: {owner}, {sid}')
        for other in s['conflicts']:
            if other in ids:
                errors.append(f'conflict: {sid}, {other}')
    return errors


def validate(root=ROOT, config=None, check_revisions=True):
    c = config or load(root)
    skills, workflows = c['skills']['skills'], c['workflows']['workflows']
    tasks = c['workflows']['task_workflows']
    domains, upstreams = c['domains']['domains'], c['upstream-lock']['upstreams']
    errors, owners = [], {}
    for task, wf in tasks.items():
        if wf not in workflows:
            errors.append(f'{task}: unknown workflow {wf}')
    for wf, info in workflows.items():
        if not safe_path(root, info['source']).is_file():
            errors.append(f'{wf}: missing workflow document')
        if not info.get('phases'):
            errors.append(f'{wf}: empty workflow')
    for domain, info in domains.items():
        if not safe_path(root, info['profile']).is_file():
            errors.append(f'{domain}: missing profile')
    required = {'responsibility','source','upstream','enabled','enabled_by_default','task_types',
                'domains','detect','conflicts','cost','load_phase','resources'}
    for sid, s in skills.items():
        missing = required - s.keys()
        if missing:
            errors.append(f'{sid}: missing fields {sorted(missing)}')
            continue
        if type(s['enabled']) is not bool or type(s['enabled_by_default']) is not bool:
            errors.append(f'{sid}: enabled flags must be boolean')
        if s['enabled_by_default'] and not s['enabled']:
            errors.append(f'{sid}: disabled owner enabled by default')
        if s['enabled']:
            previous = owners.setdefault(s['responsibility'], sid)
            if previous != sid:
                errors.append(f'duplicate enabled responsibility: {previous}, {sid}')
        source = safe_path(root, s['source'])
        if s['enabled'] and not source.is_file():
            errors.append(f'{sid}: missing skill entrypoint {s["source"]}')
        for resource in s['resources']:
            if s['enabled'] and not safe_path(root, resource).exists():
                errors.append(f'{sid}: missing resource {resource}')
        for conflict in s['conflicts']:
            if conflict not in skills:
                errors.append(f'{sid}: unknown conflict {conflict}')
            elif s['enabled'] and skills[conflict]['enabled']:
                errors.append(f'enabled conflict: {sid}, {conflict}')
        for task in s['task_types']:
            if task not in tasks:
                errors.append(f'{sid}: unknown task/workflow {task}')
        for domain in s['domains']:
            if domain not in domains:
                errors.append(f'{sid}: unknown domain {domain}')
        if s['cost'] not in {'low','medium','high'} or s['load_phase'] not in PHASES:
            errors.append(f'{sid}: invalid cost/phase')
        if s['detect'].get('when') not in CONDITIONS:
            errors.append(f'{sid}: invalid detect condition')
        up = s['upstream']
        if up != 'local':
            if up not in upstreams:
                errors.append(f'{sid}: missing upstream lock {up}')
            elif not source.is_relative_to(safe_path(root, upstreams[up]['path'])):
                errors.append(f'{sid}: source outside locked upstream')
    for name, up in upstreams.items():
        if not re.fullmatch(r'[0-9a-f]{40}', up.get('commit','')):
            errors.append(f'{name}: expected real 40-character SHA')
        if not up.get('repo','').startswith('https://github.com/'):
            errors.append(f'{name}: invalid repo URL')
        path = safe_path(root, up['path'])
        if up.get('strategy') == 'submodule':
            if check_revisions:
                try:
                    gitmodules = root / '.gitmodules'
                    module_path = subprocess.check_output(['git','config','-f',str(gitmodules),f'submodule.{up["path"]}.path'],text=True).strip()
                    module_url = subprocess.check_output(['git','config','-f',str(gitmodules),f'submodule.{up["path"]}.url'],text=True).strip()
                    if module_path != up['path'] or module_url != up['repo']:
                        errors.append(f'{name}: .gitmodules disagrees with lock')
                except subprocess.CalledProcessError:
                    errors.append(f'{name}: missing .gitmodules entry')
                try:
                    top = subprocess.check_output(['git','-C',str(path),'rev-parse','--show-toplevel'],text=True,stderr=subprocess.DEVNULL).strip()
                    actual = subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
                    if Path(top).resolve() != path.resolve() or actual != up['commit']:
                        errors.append(f'{name}: checkout does not match lock')
                    if subprocess.check_output(['git','-C',str(path),'status','--porcelain'],text=True):
                        errors.append(f'{name}: modified upstream checkout')
                except (subprocess.CalledProcessError,FileNotFoundError):
                    errors.append(f'{name}: submodule not initialized')
        elif up.get('strategy') == 'vendor':
            files = up.get('files',{})
            modes = up.get('modes',{})
            if set(modes) != set(files) or any(mode not in ('100644','100755') for mode in modes.values()):
                errors.append(f'{name}: invalid vendor Git mode manifest')
            if not files:
                errors.append(f'{name}: empty vendor manifest')
            if {str(f.relative_to(path)) for f in path.rglob('*') if f.is_file()} != set(files):
                errors.append(f'{name}: vendor file set changed')
            for relative, digest in files.items():
                f = safe_path(path,relative)
                if f.is_symlink() or not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != digest:
                    errors.append(f'{name}: vendor integrity mismatch: {relative}')
                # On Windows-mounted filesystems executable bits may be synthesized.
                if f.is_file() and modes.get(relative) == '100755' and not f.stat().st_mode & 0o111:
                    errors.append(f'{name}: missing executable mode: {relative}')
        else:
            errors.append(f'{name}: unsupported strategy')
    return errors


def resolve(decision, config=None):
    c = config or load()
    skills = c['skills']['skills']
    tasks, domains = decision.get('tasks',[]), decision.get('domains',[])
    complexity, flags = decision.get('complexity','small'), decision.get('conditions',{})
    if not tasks or set(tasks) - set(c['workflows']['task_workflows']):
        raise ValueError('tasks must be nonempty known task types')
    if set(domains) - set(c['domains']['domains']):
        raise ValueError('unknown domains')
    if complexity not in BUDGETS:
        raise ValueError('unknown complexity')
    if set(flags) - (CONDITIONS - {'always'}) or any(type(v) is not bool for v in flags.values()):
        raise ValueError('conditions must be known boolean decisions')
    flags = dict(flags)
    if 'research' in tasks: flags['research_needed'] = True
    if 'security_review' in tasks: flags['security_sensitive'] = True
    override = decision.get('design_owner')
    if override not in (None,'ui-ux-pro-max','anthropic-frontend-design'):
        raise ValueError('unknown design owner')
    if override == 'anthropic-frontend-design' and 'design' not in tasks:
        raise ValueError('design owner switch requires design intent')
    phases = {phase: [] for phase in PHASES}
    for sid,s in skills.items():
        if (not s['enabled'] or not s['enabled_by_default']) and not override == sid == 'anthropic-frontend-design': continue
        if override == 'anthropic-frontend-design' and sid == 'ui-ux-pro-max': continue
        if s['task_types'] and not set(tasks).intersection(s['task_types']): continue
        if s['domains'] and not set(domains).intersection(s['domains']): continue
        when = s['detect']['when']
        if when != 'always' and not flags.get(when,False): continue
        phases[s['load_phase']].append(sid)
    for phase,ids in phases.items():
        errors = selection_errors(ids,skills,complexity,allow_optional=override == 'anthropic-frontend-design')
        if errors: raise ValueError(f'{phase}: ' + '; '.join(errors))
    union = [sid for ids in phases.values() for sid in ids]
    errors = selection_errors(union,skills,complexity,allow_optional=override == 'anthropic-frontend-design',check_budget=False)
    if errors: raise ValueError('; '.join(errors))
    return {'tasks':tasks,'domains':domains,'complexity':complexity,
            'workflows':list(dict.fromkeys(c['workflows']['task_workflows'][t] for t in tasks)),
            'phases':{phase:ids for phase,ids in phases.items() if ids},'skills':union}
