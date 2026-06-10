from django.contrib import admin

# Register your models here.
from .models import Comentarios, Publicacion

admin.site.register(Publicacion)
admin.site.register(Comentarios)