FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install django djangorestframework psycopg2-binary

EXPOSE 8000

CMD ["sh", "-c", "python wait_for_db.py && python manage.py makemigrations app --noinput 2>/dev/null; python manage.py migrate --noinput && python manage.py seed_data && python manage.py runserver 0.0.0.0:8000"]
