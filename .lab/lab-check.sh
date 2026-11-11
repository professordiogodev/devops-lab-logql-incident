#!/usr/bin/env bash
rc=0
grep -q 'TODO' REPORT.md && { echo "- ❌ REPORT.md still has TODO"; rc=1; } || echo "- ✅ REPORT.md is written"
grep -qE '^\s*expr: TODO' queries.yaml && { echo "- ❌ queries.yaml still has TODO"; rc=1; } || echo "- ✅ queries.yaml has no TODO"
grep -qE '^ALL CHECKS PASSED \(' SUBMISSION.md && echo "- ✅ SUBMISSION.md shows ALL CHECKS PASSED" || { echo "- ❌ paste the verify.sh output ('ALL CHECKS PASSED') into SUBMISSION.md"; rc=1; }
exit $rc
