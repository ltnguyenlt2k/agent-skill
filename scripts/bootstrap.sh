#!/usr/bin/env bash
set -euo pipefail
framework_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
for tool in git python3; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 1; }
done
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"; import yaml' || {
  echo "Install Python 3.10+ and PyYAML in a virtualenv; see requirements.txt." >&2
  exit 1
}
# No --remote: initialize exact gitlinks, never silently track latest.
git -C "$framework_root" submodule update --init --recursive
python3 "$framework_root/scripts/validate-registry.py"
python3 "$framework_root/scripts/test-router.py"
python3 "$framework_root/scripts/test-tooling.py"
echo "Bootstrap complete: pinned dependencies, registry, routing and tooling checked."
