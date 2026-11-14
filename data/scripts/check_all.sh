#!/usr/bin/env bash
echo "== .env tracked in git? =="
git ls-files | grep -E '(^|/)\.env$' && echo "PROBLEM: .env is tracked" || echo ok
echo "== lint =="; ruff check backend data
echo "== tests =="; python -m pytest backend/tests -q
echo "== data and routes =="; python data/scripts/check_backend.py