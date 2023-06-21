#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip

pip install -r requirements/production.txt

python manage.py collectstatic --no-input

echo "INSERT INTO django_migrations (app, name, applied) VALUES ('users', 0001_initial', CURRENT_TIMESTAMP);" | python manage.py dbshell
echo "UPDATE django_content_type SET app_label = 'users' WHERE app_label = 'auth' and model = 'user';" | python manage.py dbshell

python manage.py migrate
