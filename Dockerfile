# استفاده از تصویر پایه پایتون
FROM python:3.10-slim

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /env
ENV PATH="/env/bin:$PATH"

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

EXPOSE 80

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "config.wsgi:application"]
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:80", "vakil.wsgi:application"]
