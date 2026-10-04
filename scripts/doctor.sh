#!/usr/bin/env bash
set -euo pipefail
framework_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
command -v git >/dev/null
command -v python3 >/dev/null
python3 -c 'import sys; assert sys.version_info >= (3, 10); import yaml'
python3 "$framework_root/scripts/validate-registry.py"
python3 "$framework_root/scripts/test-router.py"
python3 "$framework_root/scripts/test-tooling.py"
echo "Doctor passed. Browser/device runtimes are task-specific and were not installed."
