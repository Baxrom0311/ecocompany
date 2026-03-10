"""
ECO COMPANY — Site settings key rules
"""

ENV_MANAGED_SETTING_KEYS = frozenset(
    {
        "admin_email",
        "deepseek_api_key",
        "deepseek_base_url",
        "deepseek_model",
        "instagram_access_token",
        "instagram_cache_hours",
        "instagram_user_id",
        "smtp_host",
        "smtp_password",
        "smtp_port",
        "smtp_user",
        "telegram_bot_token",
        "telegram_chat_ids",
    }
)

NON_PUBLIC_SETTING_KEYS = frozenset(
    {
        "ai_system_prompt",
        "instagram_video_links",
    }
)


def is_env_managed_setting(key: str | None) -> bool:
    """Runtime config env orqali boshqariladigan keylar."""
    return bool(key) and key in ENV_MANAGED_SETTING_KEYS


def is_non_public_setting(key: str | None) -> bool:
    """DB da saqlansa ham public API ga chiqmasligi kerak bo'lgan keylar."""
    return bool(key) and key in NON_PUBLIC_SETTING_KEYS


def is_excluded_from_public(key: str | None) -> bool:
    """Public settings javobidan chiqarib tashlanadigan keylar."""
    return is_env_managed_setting(key) or is_non_public_setting(key)
