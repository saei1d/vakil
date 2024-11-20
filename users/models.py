from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class Client(AbstractUser):
    name = models.CharField(max_length=120, null=True, blank=True)
    username = models.CharField(max_length=11, unique=True)  # تغییر فیلد username برای ذخیره شماره تلفن
    is_questioned = models.BooleanField(default=False)
    otp = models.IntegerField()
    timestamp = models.DateTimeField(default=now)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
