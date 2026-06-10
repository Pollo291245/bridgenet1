import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bridgenet.settings')
django.setup()
print("OK - Django cargó correctamente")