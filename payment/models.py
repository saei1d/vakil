from django.db import models
from users.models import Client


class WalletTransaction(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')])
    created_at = models.DateTimeField(auto_now_add=True)
