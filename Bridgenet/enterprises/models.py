from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class Enterprise(models.Model):
    rut= models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=255)
    area_produccion = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    direccion = models.CharField(max_length=255)
    sitio_web = models.URLField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    empresa_favorita = models.ManyToManyField('self', through='EmpresasFavoritas', symmetrical=False, related_name='empresas_favoritas_rel')
    
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name_plural = "Empresas"

class Valoracion(models.Model):
    autor = models.ForeignKey('enterprises.Enterprise', on_delete=models.CASCADE, related_name='valoraciones_autor')
    valoracion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    empresa_evaluada = models.ForeignKey('enterprises.Enterprise', on_delete=models.CASCADE, related_name='valoraciones_recibidas')
    fecha_valoracion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Valoración de {self.autor.nombre} a {self.empresa_evaluada.nombre}: {self.valoracion}"
    class Meta:
        verbose_name_plural = "Valoraciones"
    
    
class EmpresasFavoritas(models.Model):
    empresa_a = models.ForeignKey('enterprises.Enterprise', on_delete=models.CASCADE, related_name='empresa_fav')
    empresa_b = models.ForeignKey('enterprises.Enterprise', on_delete=models.CASCADE, related_name='empresa_favorita_rel')
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empresa_a.nombre} tiene como favorita a {self.empresa_b.nombre}"
    class Meta:
        verbose_name_plural = "Empresas Favoritas"
