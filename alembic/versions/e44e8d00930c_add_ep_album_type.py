"""Add EP album type

Revision ID: e44e8d00930c
Revises: 4517cd471ffb
Create Date: 2026-11-17 12:48:39.993164

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e44e8d00930c"
down_revision: Union[str, Sequence[str], None] = "4517cd471ffb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("albums") as batch_op:
        batch_op.drop_constraint(
            "ck_albums_vaild_type_data",
            type_="check",
        )

        batch_op.create_check_constraint(
            "ck_albums_vaild_type_data",
            """
            (type = 'collection' AND disc IS NOT NULL) OR
            (type = 'setlist' AND date IS NOT NULL) OR
            (type = 'ep' AND date IS NOT NULL)
            """,
        )


def downgrade() -> None:
    with op.batch_alter_table("albums") as batch_op:
        batch_op.drop_constraint(
            "ck_albums_vaild_type_data",
            type_="check",
        )

        batch_op.create_check_constraint(
            "ck_albums_vaild_type_data",
            """
            (type = 'collection' AND disc IS NOT NULL) OR
            (type = 'setlist' AND date IS NOT NULL)
            """,
        )
