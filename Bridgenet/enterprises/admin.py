from django.contrib import admin

# Register your models here.
from .models import Enterprise, EmpresasFavoritas

admin.site.register(Enterprise)
admin.site.register(EmpresasFavoritas)

