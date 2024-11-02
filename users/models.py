from django.contrib.auth.models import AbstractUser
from django.db import models


class Client(AbstractUser):
    name = models.CharField(max_length=120, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_questioned = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
