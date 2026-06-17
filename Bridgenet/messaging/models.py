from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from enterprises.models import Empresa

class Conversacion(models.Model):
    empresa_solicitante = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='conversaciones_iniciadas')
    empresa_receptora = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='conversaciones_recibidas')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        # Evita que existan dos salas duplicadas entre las mismas dos empresas
        unique_together = ('empresa_solicitante', 'empresa_receptora')

    def __str__(self):
        return f"{self.empresa_solicitante.nombre} y {self.empresa_receptora.nombre}"

    def get_otra_empresa(self, mi_empresa):
        """Método útil para saber con quién estoy hablando"""
        if self.empresa_solicitante == mi_empresa:
            return self.empresa_receptora
        return self.empresa_solicitante

class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    empresa_remitente = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    contenido = models.TextField(verbose_name="Mensaje")
    leido = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado_en'] # Orden cronológico (antiguos arriba, nuevos abajo)

    def __str__(self):
        return f"De {self.empresa_remitente.nombre}: {self.contenido[:20]}..."