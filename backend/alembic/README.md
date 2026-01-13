# Alembic Database Migrations

Este directorio contiene las migraciones de base de datos para el proyecto ARGENTUM utilizando Alembic.

## Estructura de Archivos

```
alembic/
├── versions/          # Archivos de migración versionados
├── env.py            # Configuración del entorno de Alembic
├── script.py.mako    # Plantilla para generar nuevas migraciones
└── README            # Este archivo
```

## Configuración

Alembic está configurado para:
- Usar SQLAlchemy con soporte async (asyncpg para PostgreSQL)
- Cargar automáticamente todos los modelos desde `infrastructure.database.models`
- Leer la URL de la base de datos desde la variable de entorno `DATABASE_URL`

## Comandos Comunes

### Crear una nueva migración

Para generar una nueva migración automáticamente basada en los cambios de modelos:

```bash
# Desde el directorio backend/
uv run alembic revision --autogenerate -m "descripción_del_cambio"
```

Para crear una migración vacía (manual):

```bash
uv run alembic revision -m "descripción_del_cambio"
```

### Aplicar migraciones

Aplicar todas las migraciones pendientes:

```bash
uv run alembic upgrade head
```

Aplicar migraciones hasta una revisión específica:

```bash
uv run alembic upgrade <revision_id>
```

### Revertir migraciones

Revertir la última migración:

```bash
uv run alembic downgrade -1
```

Revertir hasta una revisión específica:

```bash
uv run alembic downgrade <revision_id>
```

Revertir todas las migraciones:

```bash
uv run alembic downgrade base
```

### Ver historial

Ver el historial de migraciones:

```bash
uv run alembic history
```

Ver el estado actual:

```bash
uv run alembic current
```

## Variables de Entorno Requeridas

Antes de ejecutar cualquier comando de Alembic, asegúrate de configurar:

```bash
DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"
```

Puedes definir esta variable en un archivo `.env` en el directorio `backend/`.

## Convenciones

### Nombres de Migraciones

Usa nombres descriptivos en snake_case que indiquen claramente el cambio:
- `add_user_role_field`
- `create_transactions_table`
- `add_index_on_email`

### Estructura de Migración

Cada archivo de migración debe contener:
- **upgrade()**: Aplica los cambios al esquema
- **downgrade()**: Revierte los cambios del upgrade

### Ejemplo de Migración

```python
"""add_user_role_field

Revision ID: 002
Revises: 001
Create Date: 2026-01-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add role field to users table."""
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=50), server_default="user", nullable=False)
    )


def downgrade() -> None:
    """Remove role field from users table."""
    op.drop_column("users", "role")
```

## Mejores Prácticas

1. **Siempre revisa las migraciones autogeneradas** antes de aplicarlas
2. **Prueba las migraciones** tanto en upgrade como downgrade
3. **Haz commits de las migraciones** junto con los cambios de código relacionados
4. **Usa transacciones** para operaciones complejas
5. **Documenta migraciones complejas** con comentarios en el código

## Resolución de Problemas

### Error: "Can't locate revision identified by 'xxxx'"

El historial de migraciones en tu base de datos no coincide con los archivos. Verifica:
- Que todos los archivos de migración estén presentes
- Que la tabla `alembic_version` en tu BD esté actualizada

### Error: "Target database is not up to date"

Aplica las migraciones pendientes:

```bash
uv run alembic upgrade head
```

### Error: "DATABASE_URL environment variable is required"

Configura la variable de entorno `DATABASE_URL` en tu archivo `.env`:

```bash
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/argentum"
```

## Recursos Adicionales

- [Documentación oficial de Alembic](https://alembic.sqlalchemy.org/)
- [Tutorial de Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
