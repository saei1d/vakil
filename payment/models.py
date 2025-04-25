from django.db import models
from users.models import Client
from service.models import UserServiceRequest

class Payment(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    service_request = models.ForeignKey(UserServiceRequest, on_delete=models.CASCADE)
    amount = models.BigIntegerField()  # Changed from DecimalField to BigIntegerField
    transaction_type = models.CharField(max_length=10, choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')])
    created_at = models.DateTimeField(auto_now_add=True)
    authority = models.CharField(max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
