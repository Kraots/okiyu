import re

__all__ = (
    'invite_regex',
)

invite_regex = re.compile(r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?")
