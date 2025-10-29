#!/bin/bash

# Script para cambiar entre entornos de desarrollo
# Uso: ./cambiar_entorno.sh [local|development|production|testing]

ENTORNO=${1:-local}

case $ENTORNO in
    "local")
        echo "🔧 Cambiando a entorno LOCAL (SQLite)"
        export FLASK_ENV=local
        echo "FLASK_ENV=local" > .env
        echo "✅ Entorno configurado: LOCAL"
        echo "📂 Base de datos: SQLite (instance/local_database.db)"
        ;;
    "development")
        echo "🔧 Cambiando a entorno DEVELOPMENT (PostgreSQL local)"
        export FLASK_ENV=development
        echo "FLASK_ENV=development" > .env
        echo "✅ Entorno configurado: DEVELOPMENT"
        echo "📂 Base de datos: PostgreSQL local (softbee_dev)"
        echo "⚠️  Asegúrate de que PostgreSQL esté ejecutándose"
        ;;
    "production")
        echo "🔧 Cambiando a entorno PRODUCTION (PostgreSQL remoto)"
        export FLASK_ENV=production
        echo "FLASK_ENV=production" > .env
        echo "✅ Entorno configurado: PRODUCTION"
        echo "📂 Base de datos: PostgreSQL remoto"
        echo "⚠️  Verifica que todas las variables estén configuradas en .env.production"
        ;;
    "testing")
        echo "🔧 Cambiando a entorno TESTING (SQLite en memoria)"
        export FLASK_ENV=testing
        echo "FLASK_ENV=testing" > .env
        echo "✅ Entorno configurado: TESTING"
        echo "📂 Base de datos: SQLite en memoria"
        ;;
    *)
        echo "❌ Entorno no válido: $ENTORNO"
        echo "Entornos disponibles: local, development, production, testing"
        exit 1
        ;;
esac

echo ""
echo "🚀 Para ejecutar la aplicación:"
echo "   python app.py"
echo ""
echo "📋 Para ver el entorno actual:"
echo "   echo \$FLASK_ENV"