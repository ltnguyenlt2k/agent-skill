# Progressive context

Start with router and registry metadata. Load a relevant workflow/profile only when
it changes decisions. Load skill bodies for the current phase and their referenced
resources only on demand. Preserve complete upstream packages on disk without loading
them all into context. Treat each skill's directory as the base for relative resources.

Use registry resources to resolve package-specific tools. UI UX Pro Max search lives
at upstream/ui-ux-pro-max/.claude/skills/ui-ux-pro-max/scripts/search.py; call this path
relative to the framework root, replacing plugin-only variable examples as needed.
Keep the project working directory for outputs. No upstream scripts run at bootstrap.

Budgets are 1/2/3/5 primary skills per phase for trivial/small/medium/complex. An added
skill needs an uncovered responsibility. Finish/release earlier owners before later
phases. Trivial edits use local verification without brainstorming/research/planning.
