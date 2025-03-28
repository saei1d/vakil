# استفاده از تصویر پایه پایتون
FROM python:3.10-slim

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تنظیم دایرکتوری کاری
WORKDIR /app

# نصب پیش‌نیازها
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌های پایتون
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# کپی کردن کد پروژه
COPY . /app/

# جمع‌آوری فایل‌های استاتیک
RUN python manage.py collectstatic --noinput

# اجرای مهاجرت‌های پایگاه داده
RUN python manage.py migrate

# باز کردن پورت
EXPOSE 8000

# دستور اجرای پروژه
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
