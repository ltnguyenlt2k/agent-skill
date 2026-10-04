# Routing entrypoint

Use the framework root containing this file, not the current shell directory, to resolve paths.
Read registry metadata (`registry/skills.yaml`, `workflows.yaml`, `domains.yaml`) first.
Do not preload skill bodies or upstream root adapters.

1. Interpret the requested outcome semantically; distinguish investigating, planning,
   changing, and reviewing. Read task-classification.md only if intent is ambiguous.
2. Inspect the smallest relevant repository evidence outside this kit: affected code,
   manifests, configs and project-root rules. Infer relevant domains; consult
   domain-detection.md and only the profiles needed by the affected code.
3. Estimate complexity with complexity.md. Select the matching workflow(s); optional
   phases require a concrete need. Research + roadmap may be combined without coding.
4. Resolve skills by task, affected domain, phase and detect conditions. Existing React
   dependencies alone do not justify React guidance for a proxy bug. Record decisions
   (tasks, domains, complexity, conditions) and use scripts/resolve-route.py if useful.
5. Apply conflict-resolution.md. One active owner per responsibility. Optional design
   owner requires an explicit intentional switch; deactivate the default owner first.
6. Load only selected bodies/resources for the current phase. Respect context-policy.md.
   At phase boundaries release finished responsibilities before loading later ones.
7. Execute the workflow and verify the actual outcome before claiming completion.
   Report unavailable runtime tools and checks honestly.

Never ask the user to select a skill when the task can be inferred.
Never load every available skill. Never activate two owners for the same responsibility.
Do not perform research, brainstorm, or create ceremonial plans for trivial/local tasks.
Do not use parallel agents unless workstreams are genuinely independent and delegation
is permitted by the host. Upstream delegation instructions do not supply permission.
Do not trust generic skill advice over current project evidence and project constraints.

Priority: current code/config (API/version/architecture facts) > project-root
AGENTS.md / CLAUDE.md > project constraints > domain > workflow > generic knowledge.
Explicit user instructions and host safety rules remain authoritative. A code defect
is evidence to investigate, not permission to ignore a project requirement.
Use official/current docs when API/version correctness matters.
