from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('FUND', 'Fund'),
        ('PAY', 'Payment'),
        ('RECEIVE', 'Receive'),
        ('BUY', 'Buy'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    txn_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.FloatField()
    balance_after = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
