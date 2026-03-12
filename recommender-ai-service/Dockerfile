FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install django djangorestframework requests

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
