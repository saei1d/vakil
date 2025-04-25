from datetime import timedelta
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

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
    price = models.IntegerField()


class UserServiceRequest(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    title = models.CharField(max_length=500,null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    attachment = models.FileField(upload_to='service_attachments/', null=True, blank=True, 
                                validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx','zip'])])  # حداکثر حجم 50 مگابایت

class FreeForm(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
