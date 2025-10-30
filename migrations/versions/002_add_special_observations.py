"""Add special_observations field to apiaries

Revision ID: 002_add_special_observations
Revises: 001_initial
Create Date: 2024-10-29 10:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_special_observations'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """Add special_observations field to apiaries table"""
    
    # Agregar nueva columna para observaciones especiales
    op.add_column('apiaries', sa.Column('special_observations', sa.Text(), nullable=True))
    
    # Agregar un índice para búsquedas rápidas si el campo contiene texto
    # op.create_index('idx_apiaries_special_obs', 'apiaries', ['special_observations'])


def downgrade():
    """Remove special_observations field from apiaries table"""
    
    # Quitar índice (si lo agregamos)
    # op.drop_index('idx_apiaries_special_obs', 'apiaries')
    
    # Quitar columna
    op.drop_column('apiaries', 'special_observations')