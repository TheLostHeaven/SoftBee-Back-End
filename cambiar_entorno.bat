@echo off
REM Script para cambiar entre entornos de desarrollo en Windows
REM Uso: cambiar_entorno.bat [local|development|production|testing]

set ENTORNO=%1
if "%ENTORNO%"=="" set ENTORNO=local

if "%ENTORNO%"=="local" (
    echo 🔧 Cambiando a entorno LOCAL ^(SQLite^)
    set FLASK_ENV=local
    echo FLASK_ENV=local > .env
    echo ✅ Entorno configurado: LOCAL
    echo 📂 Base de datos: SQLite ^(instance/local_database.db^)
    goto end
)

if "%ENTORNO%"=="development" (
    echo 🔧 Cambiando a entorno DEVELOPMENT ^(PostgreSQL local^)
    set FLASK_ENV=development
    echo FLASK_ENV=development > .env
    echo ✅ Entorno configurado: DEVELOPMENT
    echo 📂 Base de datos: PostgreSQL local ^(softbee_dev^)
    echo ⚠️  Asegúrate de que PostgreSQL esté ejecutándose
    goto end
)

if "%ENTORNO%"=="production" (
    echo 🔧 Cambiando a entorno PRODUCTION ^(PostgreSQL remoto^)
    set FLASK_ENV=production
    echo FLASK_ENV=production > .env
    echo ✅ Entorno configurado: PRODUCTION
    echo 📂 Base de datos: PostgreSQL remoto
    echo ⚠️  Verifica que todas las variables estén configuradas en .env.production
    goto end
)

if "%ENTORNO%"=="testing" (
    echo 🔧 Cambiando a entorno TESTING ^(SQLite en memoria^)
    set FLASK_ENV=testing
    echo FLASK_ENV=testing > .env
    echo ✅ Entorno configurado: TESTING
    echo 📂 Base de datos: SQLite en memoria
    goto end
)

echo ❌ Entorno no válido: %ENTORNO%
echo Entornos disponibles: local, development, production, testing
exit /b 1

:end
echo.
echo 🚀 Para ejecutar la aplicación:
echo    python app.py
echo.
echo 📋 Para ver el entorno actual:
echo    echo %FLASK_ENV%