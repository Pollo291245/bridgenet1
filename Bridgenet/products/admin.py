from django.contrib import admin

# Register your models here.
from .models import Producto, HistorialPrecio, ValoracionProducto

admin.site.register(Producto)
admin.site.register(HistorialPrecio)
admin.site.register(ValoracionProducto)
