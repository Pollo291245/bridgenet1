from django.contrib import admin

# Register your models here.
from .models import Empresa, EmpresaFavorita, MiembroEmpresa, ValoracionEmpresa

admin.site.register(Empresa)
admin.site.register(EmpresaFavorita)
admin.site.register(MiembroEmpresa)
admin.site.register(ValoracionEmpresa)

