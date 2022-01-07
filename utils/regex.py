import re

__all__ = (
    'INVITE_REGEX',
    'LANGUAGE_REGEX',
)

INVITE_REGEX = re.compile(r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?")
LANGUAGE_REGEX = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
