from datetime import timedelta

from django.db import models

from users.models import Client


# Create your models here.


class Service(models.Model):
    SERVICE_CHOICES = [
        ('call', 'تماس تلفنی'),
        ('text', 'پیام متنی'),
        ('complaint', 'تنظیم شکایت'),
        ('ekhtesasi', 'اختصاصی'),
    ]
    name = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    price = models.DecimalField(max_digits=5, decimal_places=2)


class UserServiceRequest(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    title = models.CharField(max_length=500,null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)


class FreeForm(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    description = models.TextField()
