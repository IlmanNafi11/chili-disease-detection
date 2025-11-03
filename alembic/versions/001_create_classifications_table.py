
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('classifications',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('hasil', sa.Boolean(), nullable=False),
        sa.Column('path', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classifications_id'), 'classifications', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_classifications_id'), table_name='classifications')
    op.drop_table('classifications')