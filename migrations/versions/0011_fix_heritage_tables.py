"""fix heritage tables: rename tables and fix enum values

Revision ID: 0011
Revises: 0010
Create Date: 2026-04-05 11:45:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0011'
down_revision: Union[str, Sequence[str], None] = '0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix enum values and rename tables to heritage_ namespace."""
    # Fix enum values to match StrEnum values (Portuguese lowercase)
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'PENDING' TO 'pendente'")
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'APPROVED' TO 'aprovado'")
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'REJECTED' TO 'reprovado'")
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'DELIVERED' TO 'entregue'")
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'RETURNED' TO 'devolvido'")

    # Rename tables to heritage_ namespace
    op.rename_table('item', 'heritage_item')
    op.rename_table('request', 'heritage_request')
    op.rename_table('request_item', 'heritage_request_item')

    # Rename indexes
    op.execute("ALTER INDEX ix_item_id RENAME TO ix_heritage_item_id")
    op.execute("ALTER INDEX ix_request_id RENAME TO ix_heritage_request_id")
    op.execute("ALTER INDEX ix_request_item_id RENAME TO ix_heritage_request_item_id")


def downgrade() -> None:
    """Reverse table renames and enum value changes."""
    op.execute("ALTER INDEX ix_heritage_request_item_id RENAME TO ix_request_item_id")
    op.execute("ALTER INDEX ix_heritage_request_id RENAME TO ix_request_id")
    op.execute("ALTER INDEX ix_heritage_item_id RENAME TO ix_item_id")

    op.rename_table('heritage_request_item', 'request_item')
    op.rename_table('heritage_request', 'request')
    op.rename_table('heritage_item', 'item')

    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'devolvido' TO 'RETURNED'")
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'entregue' TO 'DELIVERED'")
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'reprovado' TO 'REJECTED'")
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'aprovado' TO 'APPROVED'")
    op.execute("ALTER TYPE requeststatusconcept RENAME VALUE 'pendente' TO 'PENDING'")
