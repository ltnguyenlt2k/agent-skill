# Agent Skill

A reusable AI engineering orchestration and skill layer for Codex, Claude Code and
compatible coding agents. Describe the task naturally; the agent inspects your project
and loads the smallest relevant workflow and skills.

```text
request → intent → repository evidence → domain → complexity
        → workflow → minimum skills → execution → verification
```

## Install in a project

Requires Git, Bash, Python 3.10+ and PyYAML. If PyYAML is unavailable, install the
framework requirements in a virtual environment; no global or heavy dependencies
are installed automatically.

```bash
git submodule add https://github.com/ltnguyenlt2k/agent-skill.git .agent-skill
git submodule update --init --recursive
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r .agent-skill/requirements.txt
.agent-skill/scripts/install-project.sh
.agent-skill/scripts/doctor.sh
```

The installer adds a managed section to project-root `AGENTS.md` and `CLAUDE.md`.
Existing project rules are preserved; repeated installation is idempotent. The kit
must be mounted at `.agent-skill/`. Run from any directory, or pass `--project /path/to/project`.
Commit both the submodule and adapters in the host project. Project-specific
constraints override generic framework guidance.

Then ask normally:

- “Fix this crash.”
- “Research the best architecture for this feature.”
- “Redesign this page.”
- “Add this camera module.”
- “Create a six-month roadmap.”

No skill names are required. The host agent interprets intent semantically; the
framework is an instruction/metadata layer, not a daemon or an NLP classifier.
An agent must read the root adapter for routing to take effect.

## Routing and context cost

Metadata first, bodies later. Each responsibility has one active owner. Current
repository code/configuration establishes API/version/architecture facts; project-root
rules and project constraints take priority over generic domain/workflow advice.
Explicit user instructions and host safety policies remain authoritative.

Optional phases run only when needed: no ceremonial planning, unnecessary research,
or unnecessary parallel agents. A completed phase releases its skill context before
the next phase loads. The active primary skill budget per phase is 1 for trivial,
2 for small, 3 for medium and 5 for complex work. Sequential tasks may use more
skills in total without keeping their bodies active simultaneously.

| Responsibility | Owner | Activation |
| --- | --- | --- |
| Engineering workflow/debugging/TDD/planning/verification | Superpowers | Needed task phase |
| Design intelligence | UI UX Pro Max | Interface design |
| React implementation quality | Vercel React Best Practices | Affected React/Next code |
| Final web UX/accessibility audit | Vercel Web Design Guidelines | Relevant web UI audit |
| Browser/E2E verification | Agent Browser | Useful web browser check |
| Technical research | Matt Pocock research only | Requested research/material unknowns |
| Security review | Anthropic security-guidance | Affected security boundaries |
| Long-term roadmap | Local roadmap | Roadmap request, no code implementation |
| Alternative design intelligence | Anthropic frontend-design | Disabled; explicit owner switch only |

Having React installed does not activate React guidance for an nginx timeout.
A Qt camera freeze routes to debugging with desktop/C++/vision evidence, not web
skills. Research plus roadmap stays a planning task. Domain custom skill folders
are intentionally empty in V1 until a recurring gap is demonstrated.

This repository is not a giant prompt dumped into every request, a collection where
every skill is active, a replacement for project architecture, or permission to
ignore current code/version constraints.

## Repository layout

```text
AGENTS.md / CLAUDE.md          small routing adapters
registry/                     skills, workflows, domains, upstream lock
router/                       entrypoint, classification, conflict/context policies
profiles/                     concise relevant domain constraints
workflows/                    task-specific phase guidance
upstream/                     five complete pinned Git submodules
conditional/security-guidance/ complete vendored security plugin + upstream terms
optional/anthropic-frontend-design/ complete disabled package + license/notices
custom/roadmap/                local long-term planning skill
custom/{cpp,qt6,embedded,ros2,machine-vision}/  reserved, empty in V1
adapters/{claude,codex}/       adapter notes
templates/                    project-root adapters
scripts/                      bootstrap/install/update/validate/doctor/resolve/tests
tests/                        recorded routing cases and expected-route notes
```

## Develop and verify

```bash
git clone --recurse-submodules https://github.com/ltnguyenlt2k/agent-skill.git
cd agent-skill
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
./scripts/bootstrap.sh
```

Bootstrap initializes exact gitlink revisions, checks resolved entrypoints against
the registry and lock, then runs validation and tests. It does not invent pins or
replace mismatched lock data: a mismatch fails so dependency drift is reviewable.
No upstream script or API-backed security hook is executed during bootstrap.

Individual checks:

```bash
python3 scripts/validate-registry.py
python3 scripts/test-router.py
python3 scripts/test-tooling.py
./scripts/doctor.sh
```

`test-router.py` checks recorded semantic decisions against deterministic resolution:
required/excluded owners, domain/task filters, optional flags, phase budgets,
conflicts, missing resources and vendor integrity. It does not prove that every host
model correctly interprets arbitrary natural language. `test-tooling.py` uses offline
Git fixtures to verify adapter preservation and updater preview/apply/rollback.
Browser and hardware checks remain task-specific; report unavailable checks honestly.

An agent may record its classification as YAML and resolve it mechanically:

```yaml
tasks: [bugfix]
domains: [desktop, cpp, computer-vision]
complexity: medium
conditions:
  regression_needed: true
```

```bash
python3 scripts/resolve-route.py /path/to/decision.yaml
```

The result separates owners by phase. For an explicit alternative design request,
use `design_owner: anthropic-frontend-design` with task `design`: the default owner
is removed without globally enabling both owners.

## Deliberate upstream updates

All seven dependencies have actual immutable revisions in
[`registry/upstream-lock.yaml`](registry/upstream-lock.yaml). Five are complete
submodules. The two Anthropic packages are controlled vendor copies with file hashes,
Git modes, upstream license/terms and attribution; their full repository is not stored.

Choose one upstream and an explicit full commit SHA:

```bash
./scripts/update-upstream.sh superpowers <40-character-commit-sha> --diff
# Inspect the diff before applying:
./scripts/update-upstream.sh superpowers <40-character-commit-sha> --apply
```

The first command fetches and previews old/new revisions without switching pins.
`--apply` switches that one checkout/package and lock, validates sources and runs
both test suites. Failure restores the old checkout/package and lock. Review the
framework diff and commit the changed gitlink/vendor tree with its lock together.
There is no implicit “always latest” update. Bootstrap uses no `--remote`.

Upstream layout changes require a deliberate registry adaptation; missing skill
paths cause failure and rollback rather than an unrelated substitution.

## Package compatibility and trust

UI UX Pro Max's current source entrypoint is
`upstream/ui-ux-pro-max/.claude/skills/ui-ux-pro-max/SKILL.md`, with its scripts, data
and references intact. Resolve plugin-variable examples relative to that actual
package directory. Matt Pocock research is under `skills/engineering/research/`;
its other responsibilities are not exposed. Its delegation instruction is subject
to router/host policy: research can run in the current agent when parallel work
is unavailable or unjustified.

Anthropic security-guidance is currently a plugin, not a `SKILL.md`. Its README is
the registered entrypoint and relevant rule/prompt files remain available under
`hooks/`. Loading review guidance does not install or execute the plugin. API-backed
hooks require separate runtime setup and authorization. The package carries
Anthropic's upstream commercial terms; the local MIT license does not relicense it.
Anthropic frontend-design retains its own package license and is disabled by default.

Treat upstream instructions and scripts as dependencies. Inspect updates, preserve
licenses, never copy project secrets into this kit and never let an upstream override
routing conflicts/context policy. Available guidance does not imply installed browser
binaries, provider API access, or permission for external actions.

See [`docs/implementation-report.md`](docs/implementation-report.md) for pinned
revisions, acceptance evidence and intentional specification interpretations.
