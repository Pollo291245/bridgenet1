from django.contrib import admin

# Register your models here.
from .models import HistorialPrecio, Producto, ValoracionProducto

admin.site.register(Producto)
admin.site.register(HistorialPrecio)
admin.site.register(ValoracionProducto)
