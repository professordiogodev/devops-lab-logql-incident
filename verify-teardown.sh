#!/usr/bin/env bash
# Proves the lab left nothing on your machine. Run with: ./verify-teardown.sh
cd "$(dirname "$0")" || exit 1
pass=0; failn=0
check() { local d="$1"; shift; if "$@" >/dev/null 2>&1; then echo "PASS  $d"; pass=$((pass+1)); else echo "FAIL  $d"; failn=$((failn+1)); fi; }
check "no container of the lab (logql-loki, logql-grafana)" bash -c '[ -z "$(docker ps -aq --filter name=logql-)" ]'
check "the network logql-net is gone" bash -c '! docker network inspect logql-net'
check "the generated window file is gone" bash -c '[ ! -f .lab/.window.json ]'
echo
if [ "$failn" -eq 0 ]; then echo "TEARDOWN VERIFIED ($pass/$pass) on this machine"; else echo "NOT CLEAN: $failn leftover(s)."; fi
exit "$failn"
