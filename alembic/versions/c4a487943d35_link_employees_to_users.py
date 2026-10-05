"""link employees to users

Revision ID: c4a487943d35
Revises: 0bc75b4adc28
Create Date: 2026-08-18 16:00:49.790946

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4a487943d35"
down_revision: Union[str, Sequence[str], None] = "0bc75b4adc28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add user_id temporarily as nullable.
    op.add_column(
        "employees",
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True
        )
    )

    # 2. Add employee profile fields to users.
    op.add_column(
        "users",
        sa.Column(
            "position",
            sa.String(length=100),
            nullable=True
        )
    )

    op.add_column(
        "users",
        sa.Column(
            "profile_image",
            sa.String(length=500),
            nullable=True
        )
    )

    # 3. Link existing employees to matching users by email.
    #    TRIM + LOWER makes the match safer.
    op.execute(
        """
        UPDATE employees AS e
        SET user_id = u.id
        FROM users AS u
        WHERE LOWER(TRIM(e.email)) = LOWER(TRIM(u.email))
          AND e.user_id IS NULL
        """
    )

    # 4. Create a unique index.
    #    user_id remains nullable for employees that do not
    #    have a user account yet.
    op.create_index(
        "ix_employees_user_id",
        "employees",
        ["user_id"],
        unique=True
    )

    # 5. Create foreign key.
    op.create_foreign_key(
        "fk_employees_user_id_users",
        "employees",
        "users",
        ["user_id"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_employees_user_id_users",
        "employees",
        type_="foreignkey"
    )

    op.drop_index(
        "ix_employees_user_id",
        table_name="employees"
    )

    op.drop_column(
        "employees",
        "user_id"
    )

    op.drop_column(
        "users",
        "profile_image"
    )

    op.drop_column(
        "users",
        "position"
    )