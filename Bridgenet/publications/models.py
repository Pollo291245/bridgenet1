from django.db import models

class Publicacion(models.Model):
    empresa = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='publicaciones')
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


class Comentarios(models.Model):
    autor = models.ForeignKey('enterprises.Empresa', on_delete=models.CASCADE, related_name='comentarios_autor')
    producto = models.ForeignKey('products.Producto', on_delete=models.CASCADE, blank=True, null=True, related_name='comentarios_producto')
    publicacion = models.ForeignKey('Publicacion', on_delete=models.CASCADE, blank=True, null=True, related_name='comentarios_publicacion')
    comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.publicacion:
            return f"Comentario de {self.autor.nombre} en publicación: {self.publicacion.titulo}"
        elif self.producto:
            return f"Comentario de {self.autor.nombre} en producto: {self.producto.nombre_producto}"
        else:
            return f"Comentario huérfano de {self.autor.nombre}"

    class Meta:
        verbose_name_plural = "Comentarios"