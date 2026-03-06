"""
ECO COMPANY — Database Indexes Migration
Samaradorlikni oshirish uchun muhim indekslar
"""
from alembic import op


# revision identifiers
revision = "002_add_indexes"
down_revision = None  # initial migration keyin o'zgartiriladi
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Products
    op.create_index("idx_products_category", "products", ["category_id"])
    op.create_index("idx_products_active", "products", ["is_active", "order_index"])
    op.create_index("idx_products_sale", "products", ["is_on_sale"], postgresql_where="is_on_sale = TRUE")
    op.create_index("idx_products_featured", "products", ["is_featured"], postgresql_where="is_featured = TRUE")

    # Gallery
    op.create_index("idx_gallery_items_album", "gallery_items", ["album_id", "order_index"])
    op.create_index("idx_gallery_albums_category", "gallery_albums", ["category", "is_active"])

    # Contacts
    op.create_index("idx_contact_read", "contact_messages", ["is_read", "created_at"])
    op.create_index("idx_contact_archived", "contact_messages", ["is_archived", "is_read"])

    # Instagram
    op.create_index("idx_instagram_timestamp", "instagram_posts", ["timestamp"])

    # Audit
    op.create_index("idx_audit_user", "audit_logs", ["user_id", "created_at"])
    op.create_index("idx_audit_entity", "audit_logs", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_index("idx_audit_entity")
    op.drop_index("idx_audit_user")
    op.drop_index("idx_instagram_timestamp")
    op.drop_index("idx_contact_archived")
    op.drop_index("idx_contact_read")
    op.drop_index("idx_gallery_albums_category")
    op.drop_index("idx_gallery_items_album")
    op.drop_index("idx_products_featured")
    op.drop_index("idx_products_sale")
    op.drop_index("idx_products_active")
    op.drop_index("idx_products_category")
