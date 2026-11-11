#!/usr/bin/env bash
# Removes the containers, the network and the generated files. Run with: ./teardown.sh
cd "$(dirname "$0")" || exit 1
for c in logql-grafana logql-loki; do docker rm -f $c >/dev/null 2>&1 && echo "removed $c"; done
docker network rm logql-net >/dev/null 2>&1
rm -f .lab/.window.json
echo "Now run ./verify-teardown.sh"
