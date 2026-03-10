"""Change isms primary key to composite

Revision ID: c542342a70aa
Revises: 774747aea383
Create Date: 2026-03-10 19:46:34.281801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c542342a70aa'
down_revision: Union[str, None] = '774747aea383'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing isms table (will lose data - rebuild required)
    op.drop_table('isms')

    # Recreate enums (use existing types, don't create new ones)
    from sqlalchemy.dialects import postgresql
    numberenum = postgresql.ENUM('SINGULAR', 'DUAL', 'PLURAL', name='numberenum', create_type=False)
    genderenum = postgresql.ENUM('MASCULINE', 'FEMININE', name='genderenum', create_type=False)
    heavinessenum = postgresql.ENUM('LIGHT', 'HEAVY', name='heavinessenum', create_type=False)
    ismtypeenum = postgresql.ENUM('PROPER', 'COMMON', name='ismtypeenum', create_type=False)
    flexibilityenum = postgresql.ENUM('FLEXIBLE', 'PARTIAL', 'NON_FLEXIBLE', name='flexibilityenum', create_type=False)

    # Recreate isms table with composite primary key
    op.create_table(
        'isms',
        sa.Column('chapter', sa.Integer(), nullable=False),
        sa.Column('verse', sa.Integer(), nullable=False),
        sa.Column('word_num', sa.Integer(), nullable=False),
        sa.Column('token', sa.Integer(), nullable=False),
        sa.Column('ism', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('number', numberenum, nullable=False),
        sa.Column('gender', genderenum, nullable=False),
        sa.Column('heaviness', heavinessenum),
        sa.Column('ism_type', ismtypeenum),
        sa.Column('flexibility', flexibilityenum),
        sa.Column('root', sa.String(length=255)),
        sa.Column('lem', sa.String(length=255)),
        sa.PrimaryKeyConstraint('chapter', 'verse', 'word_num', 'token')
    )
    op.create_index(op.f('ix_isms_ism'), 'isms', ['ism'], unique=False)


def downgrade() -> None:
    # Drop new table
    op.drop_index(op.f('ix_isms_ism'), table_name='isms')
    op.drop_table('isms')

    # Recreate old table with single primary key
    op.create_table(
        'isms',
        sa.Column('ism', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('number', sa.Enum('SINGULAR', 'DUAL', 'PLURAL', name='numberenum'), nullable=False),
        sa.Column('gender', sa.Enum('MASCULINE', 'FEMININE', name='genderenum'), nullable=False),
        sa.Column('heaviness', sa.Enum('LIGHT', 'HEAVY', name='heavinessenum')),
        sa.Column('ism_type', sa.Enum('PROPER', 'COMMON', name='ismtypeenum')),
        sa.Column('flexibility', sa.Enum('FLEXIBLE', 'PARTIAL', 'NON_FLEXIBLE', name='flexibilityenum')),
        sa.Column('root', sa.String(length=255)),
        sa.Column('lem', sa.String(length=255)),
        sa.Column('chapter', sa.Integer(), nullable=False),
        sa.Column('verse', sa.Integer(), nullable=False),
        sa.Column('word_num', sa.Integer(), nullable=False),
        sa.Column('token', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('ism')
    )
