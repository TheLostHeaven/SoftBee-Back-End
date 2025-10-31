# 🔄 Sistema de Migraciones - SoftBee

## ✅ ¡Sistema Configurado!

Tu proyecto **SoftBee** ya tiene configurado un sistema completo de migraciones de base de datos. Esto significa que puedes:

- 📊 **Evolucionar** la estructura de tu BD sin perder datos
- 👥 **Colaborar** con tu equipo sincronizando cambios
- 🚀 **Desplegar** automáticamente cambios en producción
- 🔄 **Revertir** cambios si algo sale mal

## 🛠️ Comandos Rápidos

### Para Uso Diario (Recomendado)
```bash
# Ver estado actual
python softbee_migrate.py status

# Ver historial de cambios
python softbee_migrate.py history

# Crear nueva migración
python softbee_migrate.py create "Agregar campo teléfono a usuarios"

# Aplicar migraciones pendientes
python softbee_migrate.py apply
```

### Para Uso Avanzado
```bash
# Ver ayuda completa
python softbee_migrate.py help

# Usar el manager directo
python migrate_manager.py current
python migrate_manager.py migrate "mensaje"
python migrate_manager.py upgrade
```

## 📁 Archivos Importantes

```
SoftBee-Back-End/
├── migrations/                          # 📂 Carpeta de migraciones
│   └── versions/                       
│       ├── 001_initial_migration.py     # ✅ Migración inicial (aplicada)
│       └── 002_add_special_observations.py # ✅ Ejemplo (aplicada)
├── instance/
│   └── migrations_db.sqlite            # 💾 BD de migraciones
├── src/models/
│   └── sqlalchemy_models.py           # 🏗️ Modelos para migraciones
├── migrate_manager.py                 # 🔧 Manager de migraciones
├── softbee_migrate.py                # 🎯 Script simplificado
└── MIGRACIONES_GUIA.md              # 📚 Guía completa
```

## 🎯 Flujo de Trabajo Típico

### 1. Modificar Modelo
```python
# En src/models/sqlalchemy_models.py
class User(db.Model):
    # ... campos existentes ...
    
    # ⭐ AGREGAR NUEVO CAMPO
    phone = db.Column(db.String(20))
```

### 2. Crear Migración
```bash
python softbee_migrate.py create "Add phone field to users"
```

### 3. Revisar Migración Generada
- Se crea archivo en `migrations/versions/`
- Revisar que el código sea correcto
- Ajustar si es necesario

### 4. Aplicar Migración
```bash
python softbee_migrate.py apply
```

### 5. Verificar Estado
```bash
python softbee_migrate.py status
```

## 🔧 Ejemplos de Cambios Comunes

### ➕ Agregar Campo a Tabla Existente
```python
# 1. Modificar modelo en sqlalchemy_models.py
class Apiary(db.Model):
    # ... campos existentes ...
    email_contact = db.Column(db.String(255))  # NUEVO

# 2. Crear migración
python softbee_migrate.py create "Add email contact to apiaries"

# 3. Aplicar
python softbee_migrate.py apply
```

### 🆕 Agregar Nueva Tabla
```python
# 1. Agregar modelo en sqlalchemy_models.py
class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    apiary_id = db.Column(db.Integer, db.ForeignKey('apiaries.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 2. Crear migración
python softbee_migrate.py create "Add reports table"

# 3. Aplicar
python softbee_migrate.py apply
```

### 🔄 Modificar Campo Existente
```python
# 1. Cambiar en modelo (ej: aumentar tamaño de campo)
class User(db.Model):
    phone = db.Column(db.String(30))  # Era String(20)

# 2. Crear migración
python softbee_migrate.py create "Increase phone field length"

# 3. Aplicar
python softbee_migrate.py apply
```

## ⚠️ Consideraciones Importantes

### ✅ Hacer Siempre
- **Backup** antes de aplicar en producción
- **Probar** migraciones en desarrollo primero
- **Revisar** archivos de migración antes de aplicar
- **Usar nombres descriptivos** para las migraciones

### ❌ Nunca Hacer
- **Editar** migraciones ya aplicadas
- **Eliminar** archivos de migración
- **Cambios manuales** directos en BD

## 🚀 Para Producción

### Configuración en Servidor
```bash
# 1. Configurar variables de entorno
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host/softbee_prod

# 2. Aplicar migraciones
python softbee_migrate.py apply

# 3. Verificar estado
python softbee_migrate.py status
```

### CI/CD Integration
```yaml
# En tu pipeline de deployment
deploy:
  script:
    - python softbee_migrate.py apply
    - python app.py  # o tu comando de inicio
```

## 🆘 Solución de Problemas

### Error: "No changes detected"
- Verificar que el modelo esté importado en `sqlalchemy_models.py`
- Confirmar que la aplicación Flask detecte los modelos

### Error: "Database file not found"
- Verificar que el directorio `instance/` exista
- Confirmar permisos de escritura

### Error: "Migration conflicts"
- Revisar si hay migraciones paralelas
- Resolver conflictos manualmente

## 📚 Recursos Adicionales

- **Guía Completa**: Ver `MIGRACIONES_GUIA.md`
- **Documentación Alembic**: https://alembic.sqlalchemy.org/
- **Flask-Migrate**: https://flask-migrate.readthedocs.io/

---

**🎉 ¡Felicidades!** Tu sistema de migraciones está listo. Ahora puedes evolucionar tu base de datos de forma segura y profesional.