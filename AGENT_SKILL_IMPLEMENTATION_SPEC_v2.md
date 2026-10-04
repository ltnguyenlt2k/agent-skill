# Agent Skill — Implementation Specification

> **Repository:** `agent-skill`
>
> **Canonical GitHub repository:** `https://github.com/ltnguyenlt2k/agent-skill`
>
> **Clone URL:** `https://github.com/ltnguyenlt2k/agent-skill.git`
>
> **Purpose:** Give this file to an AI coding agent (Claude Code, Codex CLI, or compatible agent). The agent must create a reusable Git repository that can be added to future projects as a Git submodule. The framework must automatically infer the user's intent, project domain, complexity, workflow, and minimum non-overlapping skill set from natural-language requests and repository evidence.

## 0. Primary objective

Build and populate the existing repository `ltnguyenlt2k/agent-skill` with these properties:

1. The user only describes the task naturally: e.g. “fix this timeout”, “research this architecture”, “redesign this UI”, “add Basler support”, “make a 6-month roadmap”.
2. The user does **not** need to name a skill or workflow.
3. The agent first classifies task + domain + complexity using the request and repository evidence.
4. It selects the **minimum** relevant workflow/skills.
5. It never loads two skills with the same responsibility.
6. It progressively loads context. Large upstream packages may exist on disk, but must not all enter context.
7. Current repository evidence and project-specific rules override generic skill advice.
8. Verification is required before claiming completion.
9. Upstream skill packages must be preserved accurately; do not flatten a package to only `SKILL.md` if it depends on scripts, references, rules, assets, metadata, tests, or companion files.
10. Upstreams must be pinned to known commits/tags and updateable deliberately.

---

# 1. Core design principles

## 1.1 One responsibility → one active owner

Never activate two skills that own the same responsibility.

Examples:

- Debugging owner: Superpowers `systematic-debugging`
- TDD owner: Superpowers `test-driven-development`
- Planning owner: Superpowers `writing-plans`
- Execution owner: Superpowers `executing-plans`
- Completion verification owner: Superpowers `verification-before-completion`
- Design intelligence owner: UI UX Pro Max
- React implementation/performance owner: Vercel `react-best-practices`
- Web UX/accessibility final audit owner: Vercel `web-design-guidelines`
- Browser interaction/E2E owner: Vercel `agent-browser`
- Technical research owner: Matt Pocock `research`
- Security review owner: Anthropic `security-guidance`
- Long-term product/engineering roadmap owner: local `roadmap` skill

If two candidate skills overlap, registry conflict rules must prevent simultaneous activation.

## 1.2 Progressive disclosure

Never preload all skill bodies.

Routing sequence:

```text
USER REQUEST
    ↓
read tiny router + registry
    ↓
inspect repository evidence
    ↓
TASK classification
    +
DOMAIN classification
    +
COMPLEXITY classification
    ↓
workflow resolution
    ↓
skill resolution
    ↓
load minimum required skill bodies/resources
    ↓
execute
    ↓
test/review/verify as required
```

## 1.3 Evidence hierarchy

When guidance conflicts, use this priority:

```text
Current repository code/configuration
        >
Project-root AGENTS.md / CLAUDE.md
        >
Project-specific profile/constraints
        >
Domain skill
        >
General workflow skill
        >
Generic model knowledge
```

Official/current documentation should be consulted when API/version correctness is material.

## 1.4 Context budget

Default policy:

```yaml
trivial:
  max_primary_skills: 1

small:
  max_primary_skills: 2

medium:
  max_primary_skills: 3

complex:
  max_primary_skills: 5
```

Loading an additional skill requires a unique responsibility that is not already covered.

---

# 2. Approved upstream sources

Use the following upstream repositories. Verify the repository exists before cloning. Preserve relevant package structure and licenses.

## 2.1 Superpowers — workflow engine

Official/source repository:

`https://github.com/obra/superpowers.git`

Purpose:

- brainstorming
- writing plans
- executing plans
- systematic debugging
- test-driven development
- requesting/receiving code review
- verification before completion
- worktrees when useful
- subagents/parallel execution only for genuinely complex independent work

**Policy:** Superpowers is the sole owner of general engineering workflow responsibilities. Do not add alternative TDD/debug/implementation/review frameworks to the active stack.

Keep the upstream repository/package intact under:

```text
upstream/superpowers/
```

Expose only selected skills through the local registry.

## 2.2 UI UX Pro Max — primary design intelligence

Source:

`https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git`

Purpose:

- design-system intelligence
- product/style selection
- typography
- palette
- UX rules
- components/layout guidance
- stack-aware design guidance
- searchable design knowledge

Store:

```text
upstream/ui-ux-pro-max/
```

**Policy:** This is the primary active design owner.

Anthropic `frontend-design` must **not** be active by default because its responsibility overlaps substantially with UI UX Pro Max.

## 2.3 Vercel Agent Skills

Source:

`https://github.com/vercel-labs/agent-skills.git`

Relevant packages:

- `react-best-practices`
- `web-design-guidelines`

Keep the upstream repository/package structure intact:

```text
upstream/vercel-agent-skills/
```

Activation:

- `react-best-practices`: only when React/Next.js is detected or the task directly modifies React.
- `web-design-guidelines`: primarily final UI/UX/accessibility audit, not the primary design generator.

## 2.4 Agent Browser

Source:

`https://github.com/vercel-labs/agent-browser.git`

Store:

```text
upstream/agent-browser/
```

Purpose:

- browser interaction
- localhost verification
- visual/browser inspection
- navigation/form interaction
- E2E verification where applicable

Do not activate for non-browser tasks.

## 2.5 Matt Pocock Skills — research only

Source:

`https://github.com/mattpocock/skills.git`

Store upstream:

```text
upstream/matt-pocock-skills/
```

Expose **only the research responsibility** in the active registry.

Do not expose overlapping TDD/debug/implement/code-review skills if present because Superpowers owns those responsibilities.

## 2.6 Anthropic Security Guidance

Source repository:

`https://github.com/anthropics/claude-code.git`

Relevant package:

`plugins/security-guidance`

Prefer sparse checkout or a controlled sync script if practical; do not unnecessarily make the working tree enormous.

Store relevant package under:

```text
conditional/security-guidance/
```

Activation examples:

- authentication
- authorization
- credentials/secrets
- uploads
- network-facing APIs
- user-controlled queries
- filesystem/path handling
- cryptography
- security review

Do not activate for harmless styling, renames, documentation edits, etc.

## 2.7 Anthropic Frontend Design — optional, disabled

Source repository:

`https://github.com/anthropics/skills.git`

Relevant package:

`skills/frontend-design`

Store, if included:

```text
optional/anthropic-frontend-design/
```

Registry:

```yaml
enabled_by_default: false
conflicts:
  - ui-ux-pro-max
```

Only activate when the user explicitly requests the Anthropic frontend-design approach or the framework intentionally switches design owner. Never load it together with UI UX Pro Max.

---

# 3. Repository structure to create

Create:

```text
agent-skill/
│
├── README.md
├── VERSION
├── LICENSE
├── AGENTS.md
├── CLAUDE.md
├── .gitignore
├── .gitmodules
│
├── registry/
│   ├── skills.yaml
│   ├── workflows.yaml
│   ├── domains.yaml
│   └── upstream-lock.yaml
│
├── router/
│   ├── ROUTER.md
│   ├── task-classification.md
│   ├── domain-detection.md
│   ├── complexity.md
│   ├── conflict-resolution.md
│   └── context-policy.md
│
├── profiles/
│   ├── web.md
│   ├── frontend.md
│   ├── backend.md
│   ├── desktop.md
│   ├── cpp.md
│   ├── embedded.md
│   ├── ros2.md
│   ├── computer-vision.md
│   ├── devops.md
│   └── security.md
│
├── workflows/
│   ├── simple-task.md
│   ├── research.md
│   ├── feature.md
│   ├── bugfix.md
│   ├── ui-design.md
│   ├── refactor.md
│   ├── roadmap.md
│   ├── review.md
│   └── security-review.md
│
├── upstream/
│   ├── superpowers/
│   ├── ui-ux-pro-max/
│   ├── vercel-agent-skills/
│   ├── agent-browser/
│   └── matt-pocock-skills/
│
├── conditional/
│   └── security-guidance/
│
├── optional/
│   └── anthropic-frontend-design/
│
├── custom/
│   ├── roadmap/
│   │   └── SKILL.md
│   ├── cpp/
│   ├── qt6/
│   ├── embedded/
│   ├── ros2/
│   └── machine-vision/
│
├── adapters/
│   ├── claude/
│   └── codex/
│
├── templates/
│   ├── project-AGENTS.md
│   └── project-CLAUDE.md
│
├── scripts/
│   ├── bootstrap.sh
│   ├── install-project.sh
│   ├── update-upstream.sh
│   ├── validate-registry.py
│   ├── doctor.sh
│   └── test-router.py
│
└── tests/
    ├── routing-cases.yaml
    └── expected/
```

Empty custom domain folders are intentional in V1. Do **not** invent large generic C++/Qt/ROS2/vision skills merely to fill them. Add domain skills later only when there is a demonstrated recurring gap.

---

# 4. Git strategy

Prefer upstream repositories/packages as pinned Git submodules when practical.

Example:

```bash
git submodule add https://github.com/obra/superpowers.git upstream/superpowers
git submodule add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git upstream/ui-ux-pro-max
git submodule add https://github.com/vercel-labs/agent-skills.git upstream/vercel-agent-skills
git submodule add https://github.com/vercel-labs/agent-browser.git upstream/agent-browser
git submodule add https://github.com/mattpocock/skills.git upstream/matt-pocock-skills
```

For very large upstreams where only one package is needed, a controlled sparse/vendor sync is acceptable, but:

- preserve all files required by the skill;
- preserve upstream license/attribution;
- record repository URL and commit SHA;
- never silently update to latest;
- document the chosen strategy.

Create:

```text
registry/upstream-lock.yaml
```

Example:

```yaml
upstreams:
  superpowers:
    repo: https://github.com/obra/superpowers.git
    commit: "<PINNED_SHA>"
    path: upstream/superpowers

  ui-ux-pro-max:
    repo: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git
    commit: "<PINNED_SHA>"
    path: upstream/ui-ux-pro-max

  vercel-agent-skills:
    repo: https://github.com/vercel-labs/agent-skills.git
    commit: "<PINNED_SHA>"
    path: upstream/vercel-agent-skills

  agent-browser:
    repo: https://github.com/vercel-labs/agent-browser.git
    commit: "<PINNED_SHA>"
    path: upstream/agent-browser

  matt-pocock-skills:
    repo: https://github.com/mattpocock/skills.git
    commit: "<PINNED_SHA>"
    path: upstream/matt-pocock-skills
```

Resolve and write real SHAs during implementation.

---

# 5. Router behavior

`router/ROUTER.md` must be concise and act as the main decision protocol.

The agent must:

1. Parse the natural-language request.
2. Inspect minimal repository evidence.
3. Classify task.
4. Detect one or more domains.
5. Estimate complexity.
6. Select a workflow.
7. Query `registry/skills.yaml`.
8. Eliminate conflicts/duplicate responsibilities.
9. Load the minimum skill resources.
10. Execute.
11. Verify before completion.

The router must explicitly state:

```text
Never ask the user to select a skill when the task can be inferred.
Never load every available skill.
Never activate two owners for the same responsibility.
Do not perform research for trivial/local tasks.
Do not brainstorm trivial changes.
Do not create a plan merely for ceremony.
Do not use parallel agents unless workstreams are genuinely independent.
Do not trust a generic skill over current project evidence.
```

---

# 6. Task classification

Support at minimum:

```yaml
task_types:
  trivial:
  research:
  roadmap:
  feature:
  bugfix:
  design:
  refactor:
  review:
  test:
  security_review:
```

Classification must be semantic, not keyword-only.

Examples:

### Trivial

- rename a symbol
- typo
- small config change
- tiny copy adjustment

Workflow:

```text
inspect → change → verify
```

### Research

- compare technologies
- investigate architecture
- find official/current APIs
- evaluate SDK/framework
- technical analysis

Workflow:

```text
research → evidence → synthesis
```

Only add planning/roadmap if requested or clearly needed.

### Feature

For a non-trivial feature:

```text
inspect → brainstorm only if decisions are ambiguous → plan → implement → test → review if warranted → verify
```

### Bugfix

```text
reproduce/inspect
→ systematic-debugging
→ identify root cause
→ regression test when appropriate
→ fix
→ verify
```

### Design

```text
inspect product/project
→ UI UX Pro Max
→ implementation
→ framework-specific implementation skill if detected
→ browser verification if web
→ web-design-guidelines final audit if web
→ verify
```

### Roadmap

```text
research if knowledge is missing
→ roadmap
→ milestones/dependencies/risks/deliverables
```

Roadmap must not silently turn into implementation.

---

# 7. Domain detection

Use repository evidence, not just user wording.

## Web / React / Next.js

Evidence examples:

```text
package.json
react dependency
next dependency
next.config.*
src/app/
pages/
vite.config.*
```

## C++

```text
CMakeLists.txt
*.cpp
*.hpp
*.h
conanfile.*
vcpkg.json
```

## Qt desktop

```text
find_package(Qt5...)
find_package(Qt6...)
QApplication
QMainWindow
*.ui
qml/
```

## ROS2

```text
package.xml
ament_cmake
ament_python
rclcpp
rclpy
launch/
ros2 workspace structure
```

## Embedded / STM32

```text
*.ioc
STM32Cube*
HAL_*
CMSIS
FreeRTOS
linker scripts
startup_*.s
platformio.ini
```

## Computer vision / machine vision

```text
OpenCV
cv2
cv::
Pylon/Basler
camera SDKs
YOLO
ONNX Runtime
TensorRT
image-processing pipeline
```

Multiple domains may be detected, but this does not mean all domain profiles should be loaded. Load only those relevant to the current task.

---

# 8. Skill registry

Create `registry/skills.yaml`.

It must contain metadata, not full skill bodies.

Recommended schema:

```yaml
skills:
  <id>:
    responsibility: <unique responsibility>
    source: <path>
    upstream: <name>
    enabled: true
    task_types: []
    domains: []
    detect: {}
    conflicts: []
    cost: low|medium|high
    load_phase: routing|planning|implementation|review|verification
```

Populate at minimum:

```yaml
skills:

  brainstorming:
    responsibility: requirements-and-design-clarification
    source: upstream/superpowers
    enabled: true
    task_types: [feature]
    cost: medium
    load_phase: planning

  writing-plans:
    responsibility: implementation-planning
    source: upstream/superpowers
    enabled: true
    task_types: [feature, refactor]
    cost: medium
    load_phase: planning

  executing-plans:
    responsibility: planned-implementation
    source: upstream/superpowers
    enabled: true
    task_types: [feature, refactor]
    cost: medium
    load_phase: implementation

  systematic-debugging:
    responsibility: root-cause-debugging
    source: upstream/superpowers
    enabled: true
    task_types: [bugfix]
    cost: low
    load_phase: implementation

  test-driven-development:
    responsibility: tdd
    source: upstream/superpowers
    enabled: true
    task_types: [feature, bugfix]
    cost: medium
    load_phase: implementation

  verification-before-completion:
    responsibility: completion-verification
    source: upstream/superpowers
    enabled: true
    task_types: [feature, bugfix, refactor, design]
    cost: low
    load_phase: verification

  ui-ux-pro-max:
    responsibility: design-intelligence
    source: upstream/ui-ux-pro-max
    enabled: true
    task_types: [design]
    domains: [web, frontend, desktop]
    conflicts: [anthropic-frontend-design]
    cost: medium
    load_phase: planning

  react-best-practices:
    responsibility: react-implementation-quality
    source: upstream/vercel-agent-skills
    enabled: true
    domains: [react, nextjs]
    cost: medium
    load_phase: implementation

  web-design-guidelines:
    responsibility: web-ux-accessibility-audit
    source: upstream/vercel-agent-skills
    enabled: true
    task_types: [design, review]
    domains: [web]
    cost: medium
    load_phase: review

  agent-browser:
    responsibility: browser-e2e-verification
    source: upstream/agent-browser
    enabled: true
    domains: [web]
    cost: medium
    load_phase: verification

  research:
    responsibility: technical-research
    source: upstream/matt-pocock-skills
    enabled: true
    task_types: [research]
    cost: medium
    load_phase: planning

  security-guidance:
    responsibility: security-review
    source: conditional/security-guidance
    enabled: true
    task_types: [security_review]
    cost: medium
    load_phase: review

  roadmap:
    responsibility: long-term-roadmapping
    source: custom/roadmap
    enabled: true
    task_types: [roadmap]
    cost: low
    load_phase: planning

  anthropic-frontend-design:
    responsibility: design-intelligence
    source: optional/anthropic-frontend-design
    enabled: false
    task_types: [design]
    conflicts: [ui-ux-pro-max]
    cost: medium
    load_phase: planning
```

During implementation, resolve the exact paths of upstream skills from the cloned repositories and update `source` fields accordingly.

---

# 9. Workflow registry

Create `registry/workflows.yaml`.

Example:

```yaml
workflows:

  trivial:
    phases:
      - inspect
      - implement
      - verify

  research:
    phases:
      - research
      - synthesize

  bugfix:
    phases:
      - inspect
      - debug
      - test
      - implement
      - verify

  feature:
    phases:
      - inspect
      - clarify_if_needed
      - plan_if_needed
      - implement
      - test
      - review_if_needed
      - verify

  ui_design:
    phases:
      - inspect
      - design
      - implement
      - browser_verify_if_web
      - ux_audit_if_web
      - verify

  roadmap:
    phases:
      - research_if_needed
      - roadmap
```

Do not force every optional phase to run.

---

# 10. Profiles

Profiles are small domain routing documents, not giant tutorials.

Each should generally stay concise.

Example `profiles/desktop.md`:

```text
Detect desktop framework from repository evidence.

If Qt:
- detect Qt version
- respect current widget/QML architecture
- do not convert desktop UI to web
- keep UI thread responsive
- inspect threading/event-loop constraints when debugging freezes

If machine vision dependencies exist:
- load machine-vision context only for tasks touching acquisition/processing/visualization
```

Example `profiles/ros2.md`:

```text
Detect ROS2 distro/project structure where possible.
Respect existing packages, nodes, topics, services/actions, launch files and QoS.
Do not redesign ROS graph unless the task requires it.
For a local bug, inspect the affected package first rather than loading broad robotics context.
```

Do not write speculative domain rules that are not broadly reliable.

---

# 11. Custom roadmap skill

Create:

```text
custom/roadmap/SKILL.md
```

Its responsibility is exclusively long-term planning.

It should produce, as applicable:

- objective
- assumptions
- current state
- phases
- milestones
- dependencies
- risks
- validation gates
- deliverables
- Now / Next / Later
- estimated sequencing

It must not implement code.

It may request/use research first when important information is missing.

---

# 12. Root adapters

## `AGENTS.md`

Keep it small. It should route Codex to the framework.

Required core content:

```text
AI Engineering Framework: this repository's `.agent-skill/` submodule (or current repository root when developing the framework itself).

For non-trivial tasks:
1. Read the router entrypoint.
2. Classify task intent.
3. Inspect minimal repository evidence to determine domain.
4. Determine complexity.
5. Resolve the minimum workflow.
6. Resolve the minimum non-overlapping skill set.
7. Load skill bodies/resources only after resolution.
8. Prefer current project evidence over generic guidance.
9. Verify before claiming completion.

Never load all available skills.
Never load two skills with the same responsibility.
Do not ask the user to choose a skill when intent can be inferred.
```

## `CLAUDE.md`

Provide equivalent behavior for Claude Code.

Do not duplicate hundreds of lines from router/registry into these files.

---

# 13. Project templates

Create `templates/project-AGENTS.md` and `templates/project-CLAUDE.md`.

They should assume the kit is mounted at:

```text
.agent-skill/
```

A future project should need only:

```bash
git submodule add https://github.com/ltnguyenlt2k/agent-skill.git .agent-skill
git submodule update --init --recursive
```

Then copy/generate root adapters.

`install-project.sh` should automate this adapter setup where possible.

The project root may add its own constraints below the framework reference. Project-specific constraints override generic framework guidance.

---

# 14. Update policy

`scripts/update-upstream.sh` must:

1. fetch upstream changes;
2. show old/new commit;
3. never silently switch behavior;
4. allow update of one upstream at a time;
5. update `upstream-lock.yaml`;
6. run registry validation;
7. run router tests;
8. warn about changed/missing skill paths.

No uncontrolled “always latest” behavior.

---

# 15. Registry validation

Implement `scripts/validate-registry.py`.

Validate at least:

- every enabled skill source exists;
- duplicate `responsibility` values are rejected unless one owner is disabled/optional;
- conflict references exist;
- workflow names are valid;
- domain references are valid;
- upstream lock entries exist;
- no active pair has mutual/declared conflict;
- optional disabled skills do not become active accidentally.

Exit non-zero on invalid configuration.

---

# 16. Router tests

Create `tests/routing-cases.yaml` with realistic cases.

At minimum:

```yaml
cases:

  - request: "Fix the websocket timeout through the reverse proxy."
    expected_task: bugfix
    expected_include:
      - systematic-debugging
      - verification-before-completion
    expected_exclude:
      - ui-ux-pro-max
      - react-best-practices
      - research
      - roadmap

  - request: "Redesign this React product page so it feels premium and has a distinct identity."
    repo_evidence:
      - package.json: react,next
    expected_task: design
    expected_include:
      - ui-ux-pro-max
      - react-best-practices
      - agent-browser
      - web-design-guidelines
    expected_exclude:
      - anthropic-frontend-design
      - systematic-debugging

  - request: "Research quadruped robot architecture and create a six-month DIY roadmap."
    expected_tasks:
      - research
      - roadmap
    expected_include:
      - research
      - roadmap
    expected_exclude:
      - ui-ux-pro-max
      - test-driven-development
      - agent-browser

  - request: "Basler acquisition freezes the Qt UI after a few minutes."
    repo_evidence:
      - CMakeLists.txt: Qt6,OpenCV,Pylon
    expected_task: bugfix
    expected_domains:
      - desktop
      - cpp
      - computer-vision
    expected_include:
      - systematic-debugging
      - verification-before-completion
    expected_exclude:
      - react-best-practices
      - web-design-guidelines
      - roadmap

  - request: "Rename VehicleConfig to CarConfig."
    expected_task: trivial
    expected_max_primary_skills: 1
    expected_exclude:
      - research
      - ui-ux-pro-max
      - brainstorming
```

`test-router.py` should validate deterministic registry/routing constraints where possible. Semantic classification may remain agent-driven, but deterministic conflict/budget checks must be tested.

---

# 17. README requirements

README must explain:

## What this repository is

A reusable AI engineering orchestration/skill layer for Claude Code, Codex, and compatible coding agents.

## What it is not

- not a giant prompt dumped into every request;
- not a collection where every skill is active;
- not a replacement for project architecture;
- not permission for agents to ignore current code/version constraints.

## Typical usage

```bash
git submodule add https://github.com/ltnguyenlt2k/agent-skill.git .agent-skill
git submodule update --init --recursive
```

Then install/copy adapters.

User interaction remains natural:

```text
"Fix this crash."
"Research the best architecture for this feature."
"Redesign this page."
"Add this camera module."
"Create a six-month roadmap."
```

No skill names required.

## Explain automatic routing

```text
request
→ intent
→ repository evidence
→ domain
→ complexity
→ workflow
→ minimum skills
→ execution
→ verification
```

## Explain credit/context efficiency

- metadata first;
- bodies later;
- one owner per responsibility;
- context budget;
- no ceremonial planning;
- no unnecessary research;
- no unnecessary multi-agent execution.

---

# 18. Installation/bootstrapping behavior

Create `scripts/bootstrap.sh` for developing the kit itself.

It should:

- verify `git`, Python, and required basic tools;
- initialize/update recursive submodules;
- resolve actual upstream skill paths;
- populate/check lock metadata;
- run validation;
- run router tests;
- print a concise status report.

Do not install heavy global dependencies without explicit need.

---

# 19. Security and trust

Treat upstream skills as executable/instruction-bearing dependencies.

Therefore:

- pin commits;
- inspect upstream diffs before updates;
- preserve licenses;
- do not execute arbitrary upstream scripts during bootstrap unless necessary and documented;
- do not allow an upstream skill to override router conflict/context policy;
- project secrets must never be copied into this kit.

---

# 20. Acceptance criteria

The implementation is complete only when all of the following are true:

- [ ] Repository structure exists.
- [ ] Required upstreams are cloned/submoduled or intentionally sparse-vendored.
- [ ] Real commit SHAs are recorded.
- [ ] Relevant upstream package structure is preserved.
- [ ] Router exists and is concise.
- [ ] Task classification exists.
- [ ] Domain detection exists.
- [ ] Complexity/context-budget policy exists.
- [ ] Skills registry exists.
- [ ] Workflow registry exists.
- [ ] Domain registry exists.
- [ ] Conflict resolution prevents overlapping active owners.
- [ ] UI UX Pro Max is the default design owner.
- [ ] Anthropic frontend-design is disabled/optional and conflicts with UI UX Pro Max.
- [ ] Superpowers is the only general workflow engine.
- [ ] Matt Pocock package contributes research only to the active stack.
- [ ] React Best Practices activates only for React/Next tasks.
- [ ] Agent Browser activates only when browser verification is useful.
- [ ] Security guidance activates conditionally.
- [ ] Roadmap skill exists and does not implement code.
- [ ] AGENTS.md and CLAUDE.md are small routing adapters.
- [ ] Project adapter templates exist.
- [ ] Upstream update script exists.
- [ ] Registry validator passes.
- [ ] Router tests pass.
- [ ] README documents installation and natural-language usage.
- [ ] No active duplicate responsibility remains.
- [ ] No skill is loaded merely because it exists.
- [ ] Verification is required before “done”.

---

# 21. Implementation instructions to the receiving AI agent

You are implementing this repository, not merely explaining it.

Proceed autonomously:

1. Inspect this specification completely.
2. Check that each upstream URL/repository/package still exists.
3. Create the repository/folder structure.
4. Add/pin upstream dependencies.
5. Inspect actual upstream layouts before writing registry paths.
6. Do **not** assume every skill is a single `SKILL.md`.
7. Preserve scripts/references/assets/rules required by each upstream skill.
8. Build registry/router/profiles/workflows/adapters/scripts/tests.
9. Keep routing documents concise.
10. Avoid duplicated instructions across `AGENTS.md`, `CLAUDE.md`, router and profiles.
11. Run validation/tests.
12. Fix failures.
13. Report the final tree, pinned upstream revisions, validation results, and any deliberate deviations from this specification.

If an upstream structure changed, adapt to the current upstream structure while preserving the responsibility boundaries defined here.

If an upstream is unavailable, do not silently substitute an unrelated skill. Document the problem and use the smallest safe fallback.

Do not create large custom C++/Qt/ROS2/vision skills in V1 without evidence that they are needed. The framework must remain lean, flexible, context-aware and credit-efficient.

---

# 22. Desired end state

The final developer experience should be:

```bash
git clone <NEW_PROJECT>
cd <NEW_PROJECT>

git submodule add https://github.com/ltnguyenlt2k/agent-skill.git .agent-skill
git submodule update --init --recursive

.agent-skill/scripts/install-project.sh
```

Then the user can simply ask:

```text
"Fix the current camera freeze."
```

or:

```text
"Research this architecture and propose the best implementation plan."
```

or:

```text
"Redesign the current product page so it is premium and technically credible."
```

The agent must automatically determine the correct route without requiring the user to name a skill.

**The success metric is not how many skills are installed. The success metric is selecting the smallest correct context for each task while producing accurate, verified results.**
