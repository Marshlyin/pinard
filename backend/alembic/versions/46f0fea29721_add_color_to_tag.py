"""add color to tag

Revision ID: 46f0fea29721
Revises: 42f9c1f61159
Create Date: 2026-10-17 11:31:07.840173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '46f0fea29721'
down_revision: Union[str, Sequence[str], None] = '42f9c1f61159'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # server_default temporaire : donne la couleur par défaut (gris neutre) aux étiquettes existantes, retiré juste après
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('color', sqlmodel.sql.sqltypes.AutoString(length=7), nullable=False, server_default='#9e9e9e')
        )

    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.alter_column('color', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.drop_column('color')
