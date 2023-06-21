#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip

pip install -r requirements/production.txt

python manage.py collectstatic --no-input

python -m manage dbshell "INSERT INTO django_migrations (app, name, applied) VALUES ('users', '0001_initial', CURRENT_TIMESTAMP);"
python -m manage dbshell "UPDATE django_content_type SET app_label = 'users' WHERE app_label = 'auth' and model = 'user';"

python manage.py migrate
