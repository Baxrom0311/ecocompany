"""
ECO COMPANY — Database Indexes Migration
Samaradorlikni oshirish uchun muhim indekslar
"""
from alembic import op
from sqlalchemy import inspect

import sqlalchemy as sa


# revision identifiers
revision = "002_add_indexes"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    _create_initial_tables(bind)
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


def _create_initial_tables(bind):
    # Frozen initial schema; future model edits must use new revisions.
    existing_tables = set(inspect(bind).get_table_names())
    if 'categories' not in existing_tables:
        op.create_table('categories',
        sa.Column('name_uz', sa.String(length=255), nullable=False),
        sa.Column('name_ru', sa.String(length=255), nullable=True),
        sa.Column('name_en', sa.String(length=255), nullable=True),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('icon', sa.String(length=255), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'categories' not in existing_tables:
        op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
        op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=True)
    if 'certificates' not in existing_tables:
        op.create_table('certificates',
        sa.Column('title_uz', sa.String(length=500), nullable=False),
        sa.Column('title_ru', sa.String(length=500), nullable=True),
        sa.Column('title_en', sa.String(length=500), nullable=True),
        sa.Column('file_url', sa.String(length=1000), nullable=False),
        sa.Column('file_type', sa.String(length=20), nullable=True),
        sa.Column('preview_url', sa.String(length=1000), nullable=True),
        sa.Column('issued_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_downloadable', sa.Boolean(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'certificates' not in existing_tables:
        op.create_index(op.f('ix_certificates_id'), 'certificates', ['id'], unique=False)
    if 'chat_sessions' not in existing_tables:
        op.create_table('chat_sessions',
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('messages', sa.JSON(), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'chat_sessions' not in existing_tables:
        op.create_index(op.f('ix_chat_sessions_id'), 'chat_sessions', ['id'], unique=False)
        op.create_index(op.f('ix_chat_sessions_session_id'), 'chat_sessions', ['session_id'], unique=True)
    if 'contact_messages' not in existing_tables:
        op.create_table('contact_messages',
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'contact_messages' not in existing_tables:
        op.create_index(op.f('ix_contact_messages_id'), 'contact_messages', ['id'], unique=False)
    if 'gallery_albums' not in existing_tables:
        op.create_table('gallery_albums',
        sa.Column('title_uz', sa.String(length=500), nullable=False),
        sa.Column('title_ru', sa.String(length=500), nullable=True),
        sa.Column('title_en', sa.String(length=500), nullable=True),
        sa.Column('description_uz', sa.Text(), nullable=True),
        sa.Column('description_ru', sa.Text(), nullable=True),
        sa.Column('description_en', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('cover_item_id', sa.UUID(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'gallery_albums' not in existing_tables:
        op.create_index(op.f('ix_gallery_albums_id'), 'gallery_albums', ['id'], unique=False)
    if 'instagram_posts' not in existing_tables:
        op.create_table('instagram_posts',
        sa.Column('instagram_id', sa.String(length=255), nullable=False),
        sa.Column('media_type', sa.String(length=50), nullable=False),
        sa.Column('media_url', sa.String(length=1000), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=1000), nullable=True),
        sa.Column('permalink', sa.String(length=1000), nullable=False),
        sa.Column('caption', sa.String(length=500), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cached_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    if 'instagram_posts' not in existing_tables:
        op.create_index(op.f('ix_instagram_posts_id'), 'instagram_posts', ['id'], unique=False)
        op.create_index(op.f('ix_instagram_posts_instagram_id'), 'instagram_posts', ['instagram_id'], unique=True)
    if 'site_settings' not in existing_tables:
        op.create_table('site_settings',
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    if 'site_settings' not in existing_tables:
        op.create_index(op.f('ix_site_settings_id'), 'site_settings', ['id'], unique=False)
        op.create_index(op.f('ix_site_settings_key'), 'site_settings', ['key'], unique=True)
    if 'users' not in existing_tables:
        op.create_table('users',
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'users' not in existing_tables:
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    if 'audit_logs' not in existing_tables:
        op.create_table('audit_logs',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    if 'audit_logs' not in existing_tables:
        op.create_index(op.f('ix_audit_logs_entity_id'), 'audit_logs', ['entity_id'], unique=False)
        op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
        op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    if 'gallery_items' not in existing_tables:
        op.create_table('gallery_items',
        sa.Column('album_id', sa.UUID(), nullable=False),
        sa.Column('file_url', sa.String(length=1000), nullable=False),
        sa.Column('file_type', sa.String(length=20), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=1000), nullable=True),
        sa.Column('duration_sec', sa.Integer(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['album_id'], ['gallery_albums.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
    if 'gallery_items' not in existing_tables:
        op.create_index(op.f('ix_gallery_items_album_id'), 'gallery_items', ['album_id'], unique=False)
        op.create_index(op.f('ix_gallery_items_id'), 'gallery_items', ['id'], unique=False)
    if 'products' not in existing_tables:
        op.create_table('products',
        sa.Column('category_id', sa.UUID(), nullable=True),
        sa.Column('name_uz', sa.String(length=500), nullable=False),
        sa.Column('name_ru', sa.String(length=500), nullable=True),
        sa.Column('name_en', sa.String(length=500), nullable=True),
        sa.Column('desc_uz', sa.Text(), nullable=True),
        sa.Column('desc_ru', sa.Text(), nullable=True),
        sa.Column('desc_en', sa.Text(), nullable=True),
        sa.Column('original_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('discount_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('discount_label', sa.String(length=100), nullable=True),
        sa.Column('discount_until', sa.Date(), nullable=True),
        sa.Column('is_on_sale', sa.Boolean(), nullable=False),
        sa.Column('images', sa.JSON(), nullable=False),
        sa.Column('is_featured', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_new', sa.Boolean(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    if 'products' not in existing_tables:
        op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], unique=False)
        op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
