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

# کپی کردن کد پروژه
COPY . /app/

# جمع‌آوری فایل‌های استاتیک (اختیاری)
RUN python manage.py collectstatic --noinput

# باز کردن پورت 80 (برای سازگاری با رانفلر)
EXPOSE 80

<<<<<<< HEAD
# باز کردن پورت
EXPOSE 80

# دستور اجرای پروژه
CMD ["gunicorn", "--bind", "0.0.0.0:80", "config.wsgi:application"]
=======
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# دستور اجرای پروژه
CMD ["gunicorn", "--bind", "0.0.0.0:80", "vakil.wsgi:application"]
>>>>>>> ef7a9cf565679c533787688e98d72fd28f1a1f64
