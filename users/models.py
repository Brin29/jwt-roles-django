from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Admin'),
        ('CONTADOR', 'Contador'),
        ('AUDITOR', 'Auditor'),
        ('CLIENTE', 'Cliente')
    )
    phone_number = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLES, default='CLIENTE')