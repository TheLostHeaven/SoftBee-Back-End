#!/usr/bin/env python3
"""
Script para verificar la configuración actual del entorno
"""

import os
import sys
from dotenv import load_dotenv

def verificar_entorno():
    """Verifica y muestra la configuración actual del entorno"""
    
    print("🔍 Verificando configuración del entorno SoftBee Backend")
    print("=" * 60)
    
    # Cargar .env
    load_dotenv()
    
    # Leer entorno
    entorno_archivo = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            print(f"📄 Contenido de .env:")
            print(f"   {content.strip()}")
            for linea in content.split('\n'):
                if linea.startswith('FLASK_ENV='):
                    entorno_archivo = linea.split('=')[1].strip()
                    break
    else:
        print("📄 Archivo .env: No encontrado")
    
    entorno_var = os.getenv('FLASK_ENV')
    entorno_final = entorno_var or entorno_archivo or 'local'
    
    print()
    print("🌍 Variables de entorno:")
    print(f"   FLASK_ENV (archivo): {entorno_archivo or 'No encontrado'}")
    print(f"   FLASK_ENV (variable): {entorno_var or 'No configurada'}")
    print(f"   Entorno efectivo: {entorno_final}")
    
    print()
    print("⚙️  Configuración que se aplicará:")
    
    # Importar y mostrar configuración
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from config import get_config
        
        config_class = get_config()
        config_instance = config_class()
        
        print(f"   Clase de configuración: {config_class.__name__}")
        print(f"   Debug: {getattr(config_instance, 'DEBUG', 'No definido')}")
        print(f"   Testing: {getattr(config_instance, 'TESTING', 'No definido')}")
        print(f"   Base de datos: {getattr(config_instance, 'DATABASE_URL', 'No definida')}")
        print(f"   Frontend URL: {getattr(config_instance, 'FRONTEND_URL', 'No definida')}")
        print(f"   Backend URL: {getattr(config_instance, 'BASE_URL', 'No definida')}")
        
    except Exception as e:
        print(f"   ❌ Error al cargar configuración: {e}")
    
    print()
    print("📁 Archivos de configuración:")
    archivos_env = ['.env', '.env.local', '.env.development', '.env.production', '.env.testing']
    for archivo in archivos_env:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}: Existe")
        else:
            print(f"   ❌ {archivo}: No existe")
    
    print()
    print("🚀 Para cambiar entorno:")
    print("   python cambiar_entorno.py [local|development|production|testing]")

if __name__ == '__main__':
    verificar_entorno()