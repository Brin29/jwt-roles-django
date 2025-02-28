from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
    password_set_date = models.DateTimeField(auto_now_add=True, null=True)
    is_temp_password = models.BooleanField(default=False, null=True) # Validar que la contraseña es temporal
    temp_password_date = models.DateTimeField(null=True, blank=True) # Fecha de creacion de la contraseña temporal