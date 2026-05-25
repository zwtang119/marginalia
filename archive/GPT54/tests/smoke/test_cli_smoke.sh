#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

python3 "${ROOT_DIR}/scripts/init.py" --root "${TMP_DIR}/repo"
python3 "${ROOT_DIR}/scripts/audit.py" --root "${TMP_DIR}/repo"
python3 "${ROOT_DIR}/scripts/verify.py" --root "${TMP_DIR}/repo"

echo "smoke-pass"
