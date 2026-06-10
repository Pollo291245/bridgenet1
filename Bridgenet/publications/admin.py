from django.contrib import admin

# Register your models here.
from .models import Publicacion, Comentario

admin.site.register(Publicacion)
admin.site.register(Comentario)