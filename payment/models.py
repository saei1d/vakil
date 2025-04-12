from django.db import models
from users.models import Client


class Payment(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')])
    created_at = models.DateTimeField(auto_now_add=True)
    authority = models.CharField(max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.amount} - {'Paid' if self.is_paid else 'Not paid'}"