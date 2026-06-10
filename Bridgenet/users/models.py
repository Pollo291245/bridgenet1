from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    empresa_rel = models.ForeignKey('enterprises.Enterprise', on_delete=models.SET_NULL, null=True, blank=True) 

    def __str__(self):        
        return self.username
    class Meta:
        verbose_name_plural = "Usuarios"
