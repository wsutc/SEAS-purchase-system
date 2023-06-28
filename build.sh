#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip

pip install -r requirements/production.txt

python manage.py collectstatic --no-input

# Fakes migration to use custom `user` model as well as other changes. Only needs to be run on dbs that had previous migrations
# and are switching mid-stream. New dbs will handle everything with standard (existing) migrations.
# python -m manage dbshell "INSERT INTO django_migrations (app, name, applied) VALUES ('users', '0001_initial', CURRENT_TIMESTAMP);"
# python -m manage dbshell "UPDATE django_content_type SET app_label = 'users' WHERE app_label = 'auth' and model = 'user';"

# pip install mysql

# echo "INSERT INTO django_migrations (app, name, applied) VALUES ('users', '0001_initial', CURRENT_TIMESTAMP);" | python manage.py dbshell
# echo "UPDATE django_content_type SET app_label = 'users' WHERE app_label = 'auth' and model = 'user';" | python manage.py dbshell

python manage.py migrate
