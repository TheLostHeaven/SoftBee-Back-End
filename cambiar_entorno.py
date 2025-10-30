#!/usr/bin/env python3
"""
Script para cambiar entre entornos de desarrollo
Uso: python cambiar_entorno.py [local|development|production|testing]
"""

import sys
import os

def cambiar_entorno(entorno='local'):
    """Cambia el entorno de la aplicación"""
    
    entornos_validos = ['local', 'development', 'production', 'testing']
    
    if entorno not in entornos_validos:
        print(f"❌ Entorno no válido: {entorno}")
        print(f"Entornos disponibles: {', '.join(entornos_validos)}")
        return False
    
    # Escribir archivo .env
    try:
        with open('.env', 'w') as f:
            f.write(f'FLASK_ENV={entorno}\n')
        
        # Configurar variable de entorno para la sesión actual
        os.environ['FLASK_ENV'] = entorno
        
        # Mostrar información del entorno
        if entorno == 'local':
            print("🔧 Cambiando a entorno LOCAL (SQLite)")
            print("📂 Base de datos: SQLite (instance/local_database.db)")
            print("🌐 URLs: Frontend: http://localhost:3000, Backend: http://localhost:5000")
            
        elif entorno == 'development':
            print("🔧 Cambiando a entorno DEVELOPMENT (PostgreSQL local)")
            print("📂 Base de datos: PostgreSQL local (softbee_dev)")
            print("⚠️  Asegúrate de que PostgreSQL esté ejecutándose")
            print("🌐 URLs: Configuradas via variables de entorno")
            
        elif entorno == 'production':
            print("🔧 Cambiando a entorno PRODUCTION (PostgreSQL remoto)")
            print("📂 Base de datos: PostgreSQL remoto")
            print("⚠️  Verifica que todas las variables estén configuradas")
            print("🌐 URLs: Configuradas via variables de entorno")
            
        elif entorno == 'testing':
            print("🔧 Cambiando a entorno TESTING (SQLite en memoria)")
            print("📂 Base de datos: SQLite en memoria")
            print("🌐 URLs: URLs de prueba")
        
        print(f"✅ Entorno configurado: {entorno.upper()}")
        print()
        print("🚀 Para ejecutar la aplicación:")
        print("   python index.py")
        print()
        print("📋 Para verificar el entorno actual:")
        print("   python verificar_entorno.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al cambiar entorno: {e}")
        return False

def mostrar_entorno_actual():
    """Muestra información del entorno actual"""
    try:
        # Leer de archivo .env
        entorno_archivo = None
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for linea in f:
                    if linea.startswith('FLASK_ENV='):
                        entorno_archivo = linea.split('=')[1].strip()
                        break
        
        # Leer de variable de entorno
        entorno_var = os.getenv('FLASK_ENV')
        
        print("📋 Estado actual del entorno:")
        print(f"   Archivo .env: {entorno_archivo or 'No encontrado'}")
        print(f"   Variable FLASK_ENV: {entorno_var or 'No configurada'}")
        
        entorno_final = entorno_var or entorno_archivo or 'local'
        print(f"   Entorno efectivo: {entorno_final}")
        
    except Exception as e:
        print(f"❌ Error al leer entorno: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        entorno = sys.argv[1].lower()
        cambiar_entorno(entorno)
    else:
        print("🔧 Script para cambiar entornos de SoftBee Backend")
        print()
        mostrar_entorno_actual()
        print()
        print("Uso: python cambiar_entorno.py [entorno]")
        print("Entornos disponibles: local, development, production, testing")
        print()
        print("Ejemplos:")
        print("   python cambiar_entorno.py development")
        print("   python cambiar_entorno.py local")