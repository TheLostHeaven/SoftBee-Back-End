#!/usr/bin/env python3
"""
🔄 SoftBee Migration Manager
Herramienta simplificada para manejar migraciones de base de datos
"""

import os
import sys
import subprocess
from datetime import datetime

def print_header():
    print("=" * 60)
    print("🐝 SoftBee - Gestor de Migraciones de Base de Datos")
    print("=" * 60)

def print_help():
    print("""
📋 Comandos disponibles:

🆕 Comandos principales:
   init           - Inicializar sistema de migraciones (solo primera vez)
   create <msg>   - Crear nueva migración con mensaje
   apply          - Aplicar todas las migraciones pendientes
   status         - Ver estado actual de migraciones
   history        - Ver historial completo
   
🔧 Comandos avanzados:
   rollback <id>  - Revertir a una migración específica
   rollback-1     - Revertir última migración
   show <id>      - Mostrar detalles de una migración
   
📚 Ejemplos:
   python softbee_migrate.py create "Add phone to users"
   python softbee_migrate.py apply
   python softbee_migrate.py status
   python softbee_migrate.py rollback 001_initial
""")

def run_migration_command(cmd):
    """Ejecutar comando de migración usando nuestro migrate_manager.py"""
    try:
        result = subprocess.run([sys.executable, 'migrate_manager.py'] + cmd, 
                                capture_output=True, text=True, cwd=os.getcwd())
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("❌ Error:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def main():
    print_header()
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help' or command == '--help' or command == '-h':
        print_help()
        
    elif command == 'init':
        print("🚀 Inicializando sistema de migraciones...")
        if run_migration_command(['init']):
            print("✅ Sistema de migraciones inicializado correctamente")
        else:
            print("❌ Error al inicializar migraciones")
            
    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ Error: Debes proporcionar un mensaje para la migración")
            print("   Ejemplo: python softbee_migrate.py create \"Add phone to users\"")
            return
            
        message = ' '.join(sys.argv[2:])
        print(f"📝 Creando migración: {message}")
        if run_migration_command(['migrate', message]):
            print("✅ Migración creada correctamente")
        else:
            print("❌ Error al crear migración")
            
    elif command == 'apply':
        print("⬆️  Aplicando migraciones pendientes...")
        if run_migration_command(['upgrade']):
            print("✅ Migraciones aplicadas correctamente")
        else:
            print("❌ Error al aplicar migraciones")
            
    elif command == 'status':
        print("📊 Estado actual de migraciones:")
        run_migration_command(['current'])
        
    elif command == 'history':
        print("📜 Historial de migraciones:")
        run_migration_command(['history'])
        
    elif command == 'rollback':
        if len(sys.argv) < 3:
            print("❌ Error: Debes especificar la revisión de destino")
            print("   Ejemplo: python softbee_migrate.py rollback 001_initial")
            return
            
        target = sys.argv[2]
        print(f"⬇️  Revirtiendo a migración: {target}")
        print("⚠️  ADVERTENCIA: Esto puede causar pérdida de datos")
        confirm = input("¿Estás seguro? (sí/no): ").lower()
        
        if confirm in ['sí', 'si', 'yes', 'y']:
            # Aquí usaríamos flask db downgrade, por ahora mostramos mensaje
            print(f"🔄 Para revertir manualmente usa:")
            print(f"   set FLASK_APP=migrate_manager.py && flask db downgrade {target}")
        else:
            print("❌ Operación cancelada")
            
    elif command == 'rollback-1':
        print("⬇️  Revirtiendo última migración...")
        print("⚠️  ADVERTENCIA: Esto puede causar pérdida de datos")
        confirm = input("¿Estás seguro? (sí/no): ").lower()
        
        if confirm in ['sí', 'si', 'yes', 'y']:
            print(f"🔄 Para revertir manualmente usa:")
            print(f"   set FLASK_APP=migrate_manager.py && flask db downgrade -1")
        else:
            print("❌ Operación cancelada")
            
    elif command == 'show':
        if len(sys.argv) < 3:
            print("❌ Error: Debes especificar el ID de la migración")
            return
            
        migration_id = sys.argv[2]
        print(f"🔍 Detalles de migración: {migration_id}")
        # Aquí podríamos mostrar detalles del archivo de migración
        
    else:
        print(f"❌ Comando desconocido: {command}")
        print_help()

if __name__ == '__main__':
    main()