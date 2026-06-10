from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    empresa_rel = models.ForeignKey('enterprises.Empresa', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "Usuarios"
