flask db upgrade
exec gunicorn -b :5000 run:app