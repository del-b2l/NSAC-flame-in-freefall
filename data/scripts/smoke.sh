#!/usr/bin/env bash
B=http://localhost:8000
for p in /health /habitats /tests /safety /safety/table /hardware /insights /investigations; do
  printf "%-22s" "GET $p"; curl -s -o /dev/null -w "%{http_code}\n" "$B$p"
done
printf "%-22s" "GET /brief"; curl -s -o /dev/null -w "%{http_code}\n" -G "$B/brief" --data-urlencode "habitat=Moon base"
printf "%-22s" "POST /rank"; curl -s -o /dev/null -w "%{http_code}\n" -X POST "$B/rank" -H "Content-Type: application/json" -d '{"habitat":"Moon base"}'
printf "%-22s" "POST /explain"; curl -s -o /dev/null -w "%{http_code}\n" -X POST "$B/explain/saffire-vi-3"