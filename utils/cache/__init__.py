from ._webhooks import CachedWebhooks

__all__ = ('Cache',)


class Cache:
    def __init__(self) -> None:
        self.webhooks = CachedWebhooks()
