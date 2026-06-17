from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "Usuarios"

    productos_guardados = models.ManyToManyField(
        'products.Producto', 
        blank=True, 
        related_name='usuarios_que_guardaron'
    )
    
    proveedores_favoritos = models.ManyToManyField(
        'enterprises.Empresa', 
        blank=True, 
        related_name='empresas_seguidoras'
    )
