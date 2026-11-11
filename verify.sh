#!/usr/bin/env bash
# Evaluates your ten LogQL queries and reads your report. Run with: ./verify.sh
cd "$(dirname "$0")" || exit 1
curl -fs http://127.0.0.1:3199/ready 2>/dev/null | grep -q ready || { echo "Loki is not running. Run ./setup.sh first." >&2; exit 1; }
[ -f .lab/.window.json ] || { echo "Run ./setup.sh first." >&2; exit 1; }
exec python3 .lab/logqlcheck.py
