python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn backend_shop.wsgi:application --bind 0.0.0.0:$PORT