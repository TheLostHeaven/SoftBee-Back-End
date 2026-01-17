# 🔄 Guía Completa de Migraciones para SoftBee

## ¿Qué son las Migraciones?

Las **migraciones** son scripts versionados que permiten evolucionar la estructura de tu base de datos de forma controlada y reproducible. Imagínate como un **sistema de control de versiones para tu base de datos**.

### 🎯 Ventajas de las Migraciones

1. **📖 Historial Completo**: Cada cambio en la estructura está documentado
2. **🔄 Reversibilidad**: Puedes deshacer cambios si algo sale mal
3. **👥 Colaboración**: Todo el equipo puede sincronizar cambios de BD
4. **🚀 Despliegue Seguro**: Cambios automáticos en producción
5. **💾 Preservación de Datos**: Los datos existentes se mantienen intactos

## 🛠️ Cómo Funcionan

### Conceptos Clave

- **Revisión**: Cada migración tiene un ID único (ej: `001_create_users`)
- **Up/Upgrade**: Script que aplica cambios (crear tabla, agregar columna, etc.)
- **Down/Downgrade**: Script que revierte cambios (eliminar tabla, quitar columna, etc.)
- **Metadata**: Información sobre qué migraciones se han aplicado

### Flujo de Trabajo

```
1. Modificas un modelo (agregar campo)
   ↓
2. Generas migración automática
   ↓
3. Revisas y ajustas la migración
   ↓
4. Aplicas la migración
   ↓
5. La BD se actualiza preservando datos
```

## 📁 Estructura de Archivos de Migración

```
migrations/
├── versions/                          # Carpeta con todas las migraciones
│   ├── 001_initial_migration.py      # Primera migración
│   ├── 002_add_user_phone.py         # Agregar teléfono a usuarios
│   └── 003_create_inspections.py     # Crear tabla inspecciones
├── alembic.ini                       # Configuración de Alembic
├── env.py                           # Configuración del entorno
└── script.py.mako                  # Plantilla para nuevas migraciones
```

## 🚀 Comandos Principales

### Inicializar Sistema de Migraciones
```bash
flask db init
```
- Crea la estructura de carpetas
- Configura Alembic (motor de migraciones)
- Solo se ejecuta una vez por proyecto

### Crear Nueva Migración
```bash
flask db migrate -m "Descripción del cambio"
```
- Compara modelos actuales vs base de datos
- Genera automáticamente scripts up/down
- Requiere revisión manual antes de aplicar

### Aplicar Migraciones
```bash
flask db upgrade
```
- Ejecuta todas las migraciones pendientes
- Actualiza la base de datos al estado actual
- Registra qué migraciones se aplicaron

### Ver Estado Actual
```bash
flask db current    # Mostrar revisión actual
flask db history    # Mostrar historial completo
flask db show <id>  # Mostrar detalles de una migración
```

### Revertir Cambios
```bash
flask db downgrade <revision>  # Volver a revisión específica
flask db downgrade -1          # Revertir última migración
```

## 🔧 Ejemplo Práctico

### Situación: Agregar campo "teléfono" a usuarios

#### 1. Modificar el modelo
```python
# En src/models/sqlalchemy_models.py
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # ⭐ NUEVO CAMPO
    phone = db.Column(db.String(20))  # Agregar teléfono
```

#### 2. Generar migración
```bash
flask db migrate -m "Add phone field to users"
```

#### 3. Revisar migración generada
```python
# migrations/versions/002_add_phone_field.py
def upgrade():
    # Agregar columna
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    # Quitar columna
    op.drop_column('users', 'phone')
```

#### 4. Aplicar migración
```bash
flask db upgrade
```

## 📋 Tipos Comunes de Migraciones

### ➕ Agregar Tabla Nueva
```python
def upgrade():
    op.create_table('inspections',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('hive_id', sa.Integer, sa.ForeignKey('hives.id')),
        sa.Column('date', sa.DateTime, default=datetime.utcnow),
        sa.Column('notes', sa.Text)
    )

def downgrade():
    op.drop_table('inspections')
```

### 📝 Agregar Columna
```python
def upgrade():
    op.add_column('users', sa.Column('birth_date', sa.Date, nullable=True))

def downgrade():
    op.drop_column('users', 'birth_date')
```

### 🔄 Modificar Columna
```python
def upgrade():
    # Cambiar tipo de columna
    op.alter_column('users', 'phone', 
                   type_=sa.String(25),  # Era String(20)
                   nullable=False)       # Era nullable=True

def downgrade():
    op.alter_column('users', 'phone',
                   type_=sa.String(20),
                   nullable=True)
```

### 🔗 Agregar Índice
```python
def upgrade():
    op.create_index('idx_user_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_user_email', 'users')
```

### 🔑 Agregar Clave Foránea
```python
def upgrade():
    op.add_column('hives', sa.Column('owner_id', sa.Integer))
    op.create_foreign_key('fk_hive_owner', 'hives', 'users', 
                         ['owner_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_hive_owner', 'hives', type_='foreignkey')
    op.drop_column('hives', 'owner_id')
```

## 🚨 Mejores Prácticas

### ✅ Hacer

1. **Siempre revisar** migraciones antes de aplicar
2. **Hacer backup** antes de migraciones en producción
3. **Usar nombres descriptivos** para las migraciones
4. **Probar en desarrollo** antes de producción
5. **Migrar datos** cuando sea necesario

### ❌ Evitar

1. **No editar** migraciones ya aplicadas
2. **No eliminar** archivos de migración
3. **No hacer** cambios manuales directos en BD
4. **No ignorar** errores de migración

## 🔍 Migración de Datos

Cuando necesites migrar datos existentes:

```python
def upgrade():
    # 1. Crear nueva columna
    op.add_column('users', sa.Column('full_name', sa.String(200)))
    
    # 2. Migrar datos existentes
    connection = op.get_bind()
    connection.execute("""
        UPDATE users 
        SET full_name = name || ' ' || last_name
        WHERE full_name IS NULL
    """)
    
    # 3. Hacer obligatorio el campo (opcional)
    op.alter_column('users', 'full_name', nullable=False)

def downgrade():
    op.drop_column('users', 'full_name')
```

## 🔧 Configuración para SoftBee

### Archivo .env para Migraciones
```bash
# Para desarrollo local
FLASK_ENV=local
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/softbee_local

# Para desarrollo
DATABASE_URL=postgresql://user:pass@localhost:5432/softbee_dev

# Para producción
# DATABASE_URL=postgresql://user:pass@host/softbee_prod
```

### Comandos para SoftBee
```bash
# Configurar entorno
export FLASK_APP=flask_app.py
export FLASK_ENV=local

# Inicializar (solo primera vez)
flask db init

# Crear migración inicial con todas las tablas
flask db migrate -m "Initial SoftBee schema"

# Aplicar migraciones
flask db upgrade

# Ver estado
flask db current
```

## 🌟 Beneficios para tu Proyecto

1. **🔄 Evolución Gradual**: Puedes ir agregando funcionalidades sin perder datos
2. **👥 Trabajo en Equipo**: Cada developer puede sincronizar cambios de BD
3. **🚀 Despliegues Automatizados**: Scripts de CI/CD pueden aplicar migraciones
4. **📊 Historial Completo**: Sabes exactamente qué cambió y cuándo
5. **🛡️ Seguridad**: Rollback rápido si algo sale mal

## 🎯 Próximos Pasos

1. ✅ Configurar migraciones (hecho)
2. 📝 Crear migración inicial
3. 🧪 Probar agregar/quitar campos
4. 📋 Documentar flujo de trabajo del equipo
5. 🚀 Configurar migraciones automáticas en CI/CD

---

**💡 Consejo**: Las migraciones son tu mejor amigo para mantener la integridad de datos mientras evoluciona tu aplicación. ¡Úsalas desde el principio!