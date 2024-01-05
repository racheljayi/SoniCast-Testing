#!/usr/bin/env bash
# exit on error

source env/bin/activate
set -o errexit

pip install -r requirements.txt
cd SontiCast
python3 manage.py migrate