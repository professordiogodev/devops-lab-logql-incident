#!/usr/bin/env bash
# Starts Loki and Grafana, then pushes about 100 minutes of Beanie logs. Run: ./setup.sh
set -u
cd "$(dirname "$0")"
for c in docker python3 curl; do command -v "$c" >/dev/null || { echo "MISSING: $c"; exit 1; }; done
docker info >/dev/null 2>&1 || { echo "Docker is not running."; exit 1; }
if docker ps -a --filter name=logql- -q | grep -q .; then echo "The lab is already set up. Run ./teardown.sh first to start over."; exit 1; fi
for port in 3199 3198; do if (exec 3<>"/dev/tcp/127.0.0.1/$port") 2>/dev/null; then echo "Port $port is in use on your machine."; exit 1; fi; done
docker network create logql-net >/dev/null
docker run -d --name logql-loki --network logql-net --user 0:0 -p 127.0.0.1:3199:3100 -v "$PWD/loki:/etc/loki:ro" grafana/loki:3.2.1 -config.file=/etc/loki/loki.yaml >/dev/null || { echo "could not start Loki"; exit 1; }
docker run -d --name logql-grafana --network logql-net -p 127.0.0.1:3198:3000 -e GF_AUTH_ANONYMOUS_ENABLED=true -e GF_AUTH_ANONYMOUS_ORG_ROLE=Admin -v "$PWD/grafana/provisioning:/etc/grafana/provisioning:ro" grafana/grafana:11.3.1 >/dev/null || { echo "could not start Grafana"; exit 1; }
for _ in $(seq 1 60); do curl -fs http://127.0.0.1:3199/ready 2>/dev/null | grep -q ready && break; sleep 2; done
sleep 8
python3 gym/gen_logs.py http://127.0.0.1:3199 || { echo "could not push the logs"; exit 1; }
cat <<TXT

Ready.
  Grafana (no login):  http://localhost:3198   Explore > Loki  (use the Code mode to type LogQL)
  Loki API:            http://localhost:3199
The logs are from the last ~105 minutes. In queries.yaml, "end" means just after the last log line and "start+55m" means
55 minutes after the first one. Open .lab/.window.json to see both as unix times. In Explore, set the time range to cover everything
and use "Instant" query type for questions that ask for one number.
TXT
