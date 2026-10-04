# Semantic task classification

Classify by the desired outcome, not isolated trigger words. A timeout in a page is
usually a bugfix, not a redesign; a document mentioning React is not React code work.

| Task | Outcome |
| --- | --- |
| trivial | Bounded mechanical edit: typo, rename, tiny config/copy adjustment |
| research | Answer an uncertain technical question with primary-source evidence |
| roadmap | Long-term phases, milestones, dependencies, risks; no implementation |
| feature | Add behavior; clarify/plan only where decisions or sequencing require it |
| bugfix | Reproduce symptom, establish root cause, fix and verify |
| design | Change visual direction, interaction or layout |
| refactor | Improve structure while preserving observable behavior |
| review | Assess existing work or handle review feedback |
| test | Add/run meaningful tests for specified behavior |
| security_review | Assess trust boundaries and security behavior |

Use multiple tasks when the user asks for multiple outcomes (research + roadmap).
Use the more specific non-trivial task if a small edit changes a security contract.
Derive conditions from actual scope: ambiguous, plan_needed, regression_needed,
review_needed, review_feedback, worktree_needed, independent_workstreams,
touches_react, ui_audit, browser_needed, research_needed, security_sensitive.
Conditions are deliberate decisions, not automatically true for every feature.
Explicit research sets research_needed; explicit security review sets security_sensitive.
