# V1 implementation report

## Pinned dependencies

| Upstream | Commit | Strategy |
| --- | --- | --- |
| superpowers | `8ca22dba9a94f28898bbce59f2537ff4d87c747d` | submodule |
| ui-ux-pro-max | `477bcb28c9812b385cb51a4605ddf30d7b2266e2` | submodule |
| vercel-agent-skills | `063bee94c3f4df8453406c830b0a7df0f2860278` | submodule |
| agent-browser | `526157cfd4ec64f45939f9ba0f10d5936aa7ac33` | submodule |
| matt-pocock-skills | `24fe0ef7737efae15c87225755e9f6f5965e4888` | submodule |
| security-guidance | `2bfb629dfaff0c8318047a4beb93cf1dc5b58b18` | vendor |
| anthropic-frontend-design | `8a1541c4a3ffa5a20a5a91de0dcf3f0bab1d1ef4` | vendor |

## Specification interpretations

- Context budgets apply to concurrently active skill bodies in a phase. This supports sequential design/implementation/audit/verification without preloading the union of owners.
- Semantic classification remains agent-driven. The route resolver and recorded cases validate deterministic constraints; they are not represented as a natural-language classifier.
- Security-guidance is a preserved plugin package with README entrypoint, hooks, metadata and upstream terms, because the current upstream has no SKILL.md. Hooks are not installed or executed by bootstrap.
- Five core upstreams are full submodules; two Anthropic packages are complete controlled vendor copies with SHA, file hashes, Git modes and license/attribution.
- UI UX Pro Max and Matt Pocock sources use their actual current layouts. No upstream bodies were modified or flattened.
- Bootstrap verifies checked-in pins and paths instead of silently generating or changing the lock.
- Reserved custom domain directories contain only .gitkeep; no speculative domain skill was added.
- install-project appends/updates a managed block, preserving existing project rules instead of replacing root adapters.

## Acceptance checks

The repository includes all required registries, routing policies, ten domain profiles,
task workflows, root/project adapters, roadmap skill and bootstrap/install/update/doctor
scripts. Validator checks enabled owners, sources/resources, workflows/domains, conflicts,
upstream revisions and vendor integrity. Test suites cover the five required routing
examples plus additional false-positive, security, desktop, optional-owner and ROS2 cases.

Verified on 2026-10-04:

- `scripts/bootstrap.sh`: passed with exact pinned submodules and registry validation.
- `scripts/test-router.py`: 12 test methods passed, including 14 recorded routing cases.
- `scripts/test-tooling.py`: 6 test methods passed, including real offline Git preview,
  apply and failure rollback for both vendor and submodule strategies.
- Skill Creator `quick_validate.py custom/roadmap`: passed.
- Bash syntax checks and Python compilation: passed.
- Fresh committed checkout installed into a temporary project's `.agent-skill/`:
  all five upstreams initialized at their pins; project adapter constraints preserved;
  repeat installation unchanged; bootstrap, route CLI and same-pin update passed.
  This smoke test used local Git clones of the verified upstream checkouts.
- Local framework whitespace checks passed. Upstream whitespace is preserved byte-for-byte.

`.gitattributes` prevents newline conversion of vendor copies so locked file hashes
remain meaningful on Windows as well as Linux. No browser/hardware or API-backed
security hook was required or executed to validate this framework.
