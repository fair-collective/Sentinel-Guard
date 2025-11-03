@echo off
python -m venv .venv
.venv\Scripts\pip install -r backend\requirements.txt
start http://localhost:8000
python backend\guard_core.py
