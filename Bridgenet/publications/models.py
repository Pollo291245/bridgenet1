from django.db import models

# Create your models here.
class Publicacion(models.Model):
    empresa_id = models.ForeignKey('enterprises.Enterprise', on_delete=models.CASCADE, related_name='publicaciones')
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='publicaciones/', blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    tipo_novedad = models.CharField(max_length=255)
    producto_referido = models.ForeignKey('products.Producto', on_delete=models.SET_NULL, null=True, blank=True, related_name='publicaciones_referidas')

    def __str__(self):
        return self.titulo
    class Meta:
        verbose_name_plural = "Publicaciones"

class Comentario(models.Model):
    autor_id = models.ForeignKey('enterprises.Enterprise', on_delete=models.CASCADE, related_name='comentarios_autor')
    producto_id = models.ForeignKey('products.Producto', on_delete=models.CASCADE, blank=True, null=True, related_name='comentarios_producto')
    publicacion_id = models.ForeignKey('Publicacion', on_delete=models.CASCADE, blank=True, null=True, related_name='comentarios_publicacion')
    comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.publicacion_id:
            return f"Comentario de {self.autor_id.nombre} en publicación: {self.publicacion_id.titulo}"
        elif self.producto_id:
            return f"Comentario de {self.autor_id.nombre} en producto: {self.producto_id.nombre_producto}"
        else:
            return f"Comentario huérfano de {self.autor.nombre}"
    class meta:
        verbose_name_plural = "Comentarios"