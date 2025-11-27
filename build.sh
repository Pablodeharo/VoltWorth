#!/usr/bin/env bash
set -o errexit

pip install -r ../requirements.txt

python voltworth/manage.py collectstatic --no-input
python voltworth/manage.py migrate