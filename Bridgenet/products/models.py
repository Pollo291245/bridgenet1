from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Producto(models.Model):
    # Opciones de categoría para facilitar los filtros futuros
    class CategoriaChoices(models.TextChoices):
        TECNOLOGIA = 'tecnologia', 'Tecnología y Software'
        MAQUINARIA = 'maquinaria', 'Maquinaria y Equipos'
        INSUMOS = 'insumos', 'Insumos y Materias Primas'
        SERVICIOS = 'servicios', 'Servicios Profesionales'
        OTROS = 'otros', 'Otros'

    nombre_producto = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    descripcion_producto = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_minima_pedido = models.IntegerField()
    categoria = models.CharField(max_length=50, choices=CategoriaChoices.choices, default=CategoriaChoices.OTROS)
    unidad_medida = models.CharField(max_length=50)
    stock_disponible = models.IntegerField()
    
    # Cambio de empresa_id a empresa
    empresa = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='productos')

    def save(self, *args, **kwargs):
        if self.pk:
            producto_actual = Producto.objects.get(pk=self.pk)
            if producto_actual.precio != self.precio:
                HistorialPrecio.objects.create(
                    producto_precio=self,
                    precio_antiguo=producto_actual.precio
                )
        super().save(*args, **kwargs)    

    def __str__(self):
        return self.nombre_producto

    class Meta:
        verbose_name_plural = "Productos"


class HistorialPrecio(models.Model):
    precio_antiguo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_actualizacion = models.DateTimeField(auto_now_add=True)
    producto_precio = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='historial_precios')

    def __str__(self):
        return f"Historial de precios para {self.producto_precio.nombre_producto} - {self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        verbose_name_plural = "Historiales de Precios"


class ValoracionProducto(models.Model):
    autor = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='valoraciones_producto_autor')
    valoracion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True) # <-- Nuevo campo opcional
    producto_evaluado = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='valoraciones_recibidas')
    fecha_valoracion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Valoración de {self.autor.nombre} a {self.producto_evaluado.nombre_producto}: {self.valoracion}"

    class Meta:
        verbose_name_plural = "Valoraciones de Productos"