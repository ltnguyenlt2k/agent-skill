#!/usr/bin/env bash
set -euo pipefail
framework_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$framework_root/scripts/update-upstream.py" "$@"
