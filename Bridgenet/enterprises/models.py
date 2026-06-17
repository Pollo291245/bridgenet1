from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Empresa(models.Model):
    class estado_choices(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'

    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=255)
    area_produccion = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    direccion = models.CharField(max_length=255)
    sitio_web = models.URLField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='logos_empresas/', null=True, blank=True)
    estado = models.CharField(max_length=10, choices=estado_choices.choices, default=estado_choices.ACTIVO)
    empresa_favorita = models.ManyToManyField('self', through='EmpresaFavorita', symmetrical=False, related_name='empresas_favoritas_rel')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Empresas"


class ValoracionEmpresa(models.Model):
    autor = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='valoraciones_autor')
    valoracion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    empresa_evaluada = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='valoraciones_recibidas')
    fecha_valoracion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Valoración de {self.autor.nombre} a {self.empresa_evaluada.nombre}: {self.valoracion}"

    class Meta:
        verbose_name_plural = "Valoraciones"


class EmpresaFavorita(models.Model):
    empresa_a = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='empresa_fav')
    empresa_b = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='empresa_favorita_rel')
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empresa_a.nombre} tiene como favorita a {self.empresa_b.nombre}"

    class Meta:
        verbose_name_plural = "Empresas Favoritas"


class MiembroEmpresa(models.Model):
    class rol_choices(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        EDITOR = 'editor', 'Editor'
        VIEWER = 'viewer', 'Lector'

    empresa = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='miembros_empresa')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='empresas_miembro')
    rol = models.CharField(max_length=20, choices=rol_choices.choices, default=rol_choices.EDITOR)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    es_responsable_chat = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Miembro de empresa"
        verbose_name_plural = "Miembros de empresa"
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'usuario'], name='unique_empresa_user_membership'),
        ]

    def __str__(self):
        return f"{self.usuario.username} en {self.empresa.nombre} ({self.rol})"

