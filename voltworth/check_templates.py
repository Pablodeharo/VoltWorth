# check_templates.py
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voltworth.settings')
django.setup()

from django.template.loader import get_template

def check_templates():
    print("🔍 VERIFICANDO TEMPLATES...")
    
    templates_to_check = [
        'base.html',
        'demo.html'
    ]
    
    for template_name in templates_to_check:
        try:
            template = get_template(template_name)
            print(f"✅ {template_name} - ENCONTRADO")
            print(f"   Ruta: {template.origin.name}")
        except Exception as e:
            print(f"❌ {template_name} - NO ENCONTRADO: {e}")
    
    print(f"\n📁 Directorios de templates configurados:")
    for template_config in settings.TEMPLATES:
        if 'DIRS' in template_config:
            for dir_path in template_config['DIRS']:
                exists = "✅ EXISTE" if os.path.exists(dir_path) else "❌ NO EXISTE"
                print(f"   {exists}: {dir_path}")

if __name__ == "__main__":
    check_templates()
