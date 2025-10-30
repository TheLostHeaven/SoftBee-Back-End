"""Initial migration - All SoftBee models

Revision ID: 001_initial
Revises: 
Create Date: 2024-10-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create all initial tables for SoftBee application"""
    
    # Crear tabla users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('profile_picture', sa.String(length=255), nullable=True),
        sa.Column('user_type', sa.Enum('ADMIN', 'USER', name='usertypeenum'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Crear tabla password_reset_tokens
    op.create_table('password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_reset_tokens_token'), 'password_reset_tokens', ['token'], unique=True)
    
    # Crear tabla apiaries
    op.create_table('apiaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla apiary_access
    op.create_table('apiary_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('apiary_id', sa.Integer(), nullable=False),
        sa.Column('access_level', sa.Enum('READ', 'WRITE', 'ADMIN', name='accesslevelenum'), nullable=False),
        sa.Column('granted_by', sa.Integer(), nullable=False),
        sa.Column('granted_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['apiary_id'], ['apiaries.id'], ),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'apiary_id', name='unique_user_apiary_access')
    )
    
    # Crear tabla hives
    op.create_table('hives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('apiary_id', sa.Integer(), nullable=False),
        sa.Column('location_in_apiary', sa.String(length=100), nullable=True),
        sa.Column('hive_type', sa.String(length=50), nullable=True),
        sa.Column('installation_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'MAINTENANCE', 'LOST', name='hivestatusenum'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['apiary_id'], ['apiaries.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla inventory
    op.create_table('inventory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('apiary_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('item_type', sa.Enum('EQUIPMENT', 'MEDICATION', 'FOOD', 'TOOL', 'CONSUMABLE', name='inventorytypeenum'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('minimum_stock', sa.Integer(), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('supplier', sa.String(length=100), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['apiary_id'], ['apiaries.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla questions
    op.create_table('questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.Enum('MULTIPLE_CHOICE', 'YES_NO', 'TEXT', 'SCALE', name='questiontypeenum'), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla inspections
    op.create_table('inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hive_id', sa.Integer(), nullable=False),
        sa.Column('inspector_id', sa.Integer(), nullable=False),
        sa.Column('inspection_date', sa.DateTime(), nullable=False),
        sa.Column('weather_conditions', sa.String(length=100), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('queen_present', sa.Boolean(), nullable=True),
        sa.Column('queen_laying', sa.Boolean(), nullable=True),
        sa.Column('brood_pattern', sa.String(length=50), nullable=True),
        sa.Column('population_level', sa.String(length=50), nullable=True),
        sa.Column('disease_signs', sa.Boolean(), nullable=True),
        sa.Column('disease_description', sa.Text(), nullable=True),
        sa.Column('pest_presence', sa.Boolean(), nullable=True),
        sa.Column('pest_description', sa.Text(), nullable=True),
        sa.Column('honey_production', sa.Float(), nullable=True),
        sa.Column('frames_with_honey', sa.Integer(), nullable=True),
        sa.Column('frames_with_brood', sa.Integer(), nullable=True),
        sa.Column('actions_taken', sa.Text(), nullable=True),
        sa.Column('medication_applied', sa.String(length=255), nullable=True),
        sa.Column('general_notes', sa.Text(), nullable=True),
        sa.Column('next_inspection_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['hive_id'], ['hives.id'], ),
        sa.ForeignKeyConstraint(['inspector_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla monitoreo
    op.create_table('monitoreo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('apiary_id', sa.Integer(), nullable=False),
        sa.Column('hive_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('bee_activity_level', sa.String(length=20), nullable=True),
        sa.Column('entrance_activity', sa.Integer(), nullable=True),
        sa.Column('is_automated', sa.Boolean(), nullable=True),
        sa.Column('sensor_data', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['apiary_id'], ['apiaries.id'], ),
        sa.ForeignKeyConstraint(['hive_id'], ['hives.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Drop all tables"""
    op.drop_table('monitoreo')
    op.drop_table('inspections')
    op.drop_table('questions')
    op.drop_table('inventory')
    op.drop_table('hives')
    op.drop_table('apiary_access')
    op.drop_table('apiaries')
    op.drop_index(op.f('ix_password_reset_tokens_token'), table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')