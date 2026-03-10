"""
ECO COMPANY — Database Indexes Migration
Samaradorlikni oshirish uchun muhim indekslar
"""
from alembic import op
from sqlalchemy import inspect

from app.database import Base
from app.models import *  # noqa: F403,F401


# revision identifiers
revision = "002_add_indexes"
down_revision = None  # initial migration keyin o'zgartiriladi
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    inspector = inspect(bind)

    def create_index_if_missing(index_name: str, table_name: str, columns: list[str], **kwargs) -> None:
        existing = {index["name"] for index in inspector.get_indexes(table_name)}
        if index_name not in existing:
            op.create_index(index_name, table_name, columns, **kwargs)

    # Products
    create_index_if_missing("idx_products_category", "products", ["category_id"])
    create_index_if_missing("idx_products_active", "products", ["is_active", "order_index"])
    create_index_if_missing("idx_products_sale", "products", ["is_on_sale"], postgresql_where="is_on_sale = TRUE")
    create_index_if_missing("idx_products_featured", "products", ["is_featured"], postgresql_where="is_featured = TRUE")

    # Gallery
    create_index_if_missing("idx_gallery_items_album", "gallery_items", ["album_id", "order_index"])
    create_index_if_missing("idx_gallery_albums_category", "gallery_albums", ["category", "is_active"])

    # Contacts
    create_index_if_missing("idx_contact_read", "contact_messages", ["is_read", "created_at"])
    create_index_if_missing("idx_contact_archived", "contact_messages", ["is_archived", "is_read"])

    # Instagram
    create_index_if_missing("idx_instagram_timestamp", "instagram_posts", ["timestamp"])

    # Audit
    create_index_if_missing("idx_audit_user", "audit_logs", ["user_id", "created_at"])
    create_index_if_missing("idx_audit_entity", "audit_logs", ["entity_type", "entity_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    def drop_index_if_exists(index_name: str, table_name: str) -> None:
        existing = {index["name"] for index in inspector.get_indexes(table_name)}
        if index_name in existing:
            op.drop_index(index_name, table_name=table_name)

    drop_index_if_exists("idx_audit_entity", "audit_logs")
    drop_index_if_exists("idx_audit_user", "audit_logs")
    drop_index_if_exists("idx_instagram_timestamp", "instagram_posts")
    drop_index_if_exists("idx_contact_archived", "contact_messages")
    drop_index_if_exists("idx_contact_read", "contact_messages")
    drop_index_if_exists("idx_gallery_albums_category", "gallery_albums")
    drop_index_if_exists("idx_gallery_items_album", "gallery_items")
    drop_index_if_exists("idx_products_featured", "products")
    drop_index_if_exists("idx_products_sale", "products")
    drop_index_if_exists("idx_products_active", "products")
    drop_index_if_exists("idx_products_category", "products")
