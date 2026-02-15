"""FK added for users and books

Revision ID: 034e2bc28609
Revises: fd851797d4f5
Create Date: 2026-02-15 08:54:54.085861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '034e2bc28609'
down_revision: Union[str, Sequence[str], None] = 'fd851797d4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
