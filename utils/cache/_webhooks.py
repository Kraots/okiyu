from typing import Optional

from disnake import Webhook


class CachedWebhooks:
    def __init__(self):
        self.__webhooks = {}

    def __getitem__(self, name: str) -> Optional[Webhook]:
        return self.get(name)

    def __setitem__(self, name: str, value: Webhook):
        return self.add(name, value)

    def __delitem__(self, name: str) -> Optional[Webhook]:
        return self.remove(name)

    def __contains__(self, webhook: Webhook) -> bool:
        if not isinstance(webhook, Webhook):
            raise TypeError(
                "Can only check if an object of type 'disnake.Webhook' "
                f"exists in the cache, not {webhook.__class__}"
            )
        return webhook in self.__webhooks.values()

    def __len__(self):
        return len(self.__webhooks)

    def add(self, name: str, webhook: Webhook) -> None:
        """Adds the webhook to the cached :class:``.Webhook`` objects.

        Parameters
        ----------
        name: :class:`str`
            The name under which to cache the webhook object.
        webhook: :class:`.Webhook`
            The Webhook object to cache.

        Raises
        ------
        TypeError
            The ``name`` or the ``webhook`` type is not corresponding
            to their respective type-hint.

        Returns
        -------
            ``None``
        """

        if not isinstance(name, str):
            raise TypeError(
                "expected 'name' to be of type "
                f"'str' not {webhook.__class__}"
            )
        elif not isinstance(webhook, Webhook):
            raise TypeError(
                "expected 'webhook' to be of type "
                f"'disnake.Webhook' not {webhook.__class__}"
            )

        self.__webhooks[name] = webhook

    def get(self, name: str) -> Optional[Webhook]:
        """Gets a webhook

        Parameters
        ----------
        name: :class:`str`
            The name by which the webhook is stored in the cache.

        Returns
        -------
            Optional[:class:`.Webhook`]
        """

        return self.__webhooks.get(name)

    def remove(self, name: str) -> Optional[Webhook]:
        """Removes the webhook from the cached webhooks.

        Parameters
        ----------
        name: :class:`str`
            The name under which the Webhook object is stored.

        Returns
        -------
            Optional[:class:``.Webhook``] The webhook object that was stored.
        """

        webhook = self.__webhooks.get(name)
        if webhook is not None:
            del self.__webhooks[name]
        return webhook

    def update(self, name: str, webhook: Webhook) -> Optional[dict[str, Webhook]]:
        """Updates an webhook from the internal cache of webhooks.

        Parameters:
        ----------
        name: :class:`str`
            The name of the webhook to update.

        Returns
        -------
            If found, returns a dict with the keys of ``old_webhook`` and ``new_webhook``,
            each having the value of their corresponding webhook. If not found, returns
            ``None``.
        """

        if not isinstance(webhook, Webhook):
            raise TypeError(
                "expected 'webhook' to be of type "
                f"'disnake.Webhook' not {webhook.__class__}"
            )

        old_webhook = self.__webhooks.get(name)
        if old_webhook is not None:
            self.__webhooks[name] = webhook
            return {'old_webhook': old_webhook, 'new_webhook': webhook}
