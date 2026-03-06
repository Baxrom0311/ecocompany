"""
ECO COMPANY — Input Sanitization
XSS himoya uchun HTML tags tozalash
"""
import bleach


def sanitize_html(text: str) -> str:
    """Barcha HTML tags olib tashlanadi (XSS himoya)"""
    if not text:
        return text
    return bleach.clean(text, tags=[], attributes={}, strip=True)


def sanitize_dict(data: dict) -> dict:
    """Dict ichidagi barcha string maydonlarni tozalash"""
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned[key] = sanitize_html(value)
        elif isinstance(value, dict):
            cleaned[key] = sanitize_dict(value)
        elif isinstance(value, list):
            cleaned[key] = [
                sanitize_html(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            cleaned[key] = value
    return cleaned
