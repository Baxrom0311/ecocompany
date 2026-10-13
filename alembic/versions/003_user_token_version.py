"""Add token revocation version, supporting existing and fresh databases."""
from alembic import op
import sqlalchemy as sa

revision = "003_user_token_version"
down_revision = "002_add_indexes"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "token_version" not in columns:
        op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))


def downgrade():
    with op.batch_alter_table("users") as batch:
        batch.drop_column("token_version")
