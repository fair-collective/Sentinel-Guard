#!/bin/bash
echo "Installing Sentinel Guard v1.1..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt --quiet
echo "Dashboard: http://localhost:8000"
open http://localhost:8000
python backend/guard_core.py
