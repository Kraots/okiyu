import disnake
from disnake.ext import commands

__all__ = ('Context',)


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self):
        return self.bot.session

    @property
    def agree(self) -> disnake.PartialEmoji:
        return disnake.PartialEmoji(name='agree', id=913895978535374898)

    @property
    def disagree(self) -> disnake.PartialEmoji:
        return disnake.PartialEmoji(name='disagree', id=913895999125196860)

    @disnake.utils.cached_property
    def replied_reference(self):
        ref = self.message.reference
        if ref and isinstance(ref.resolved, disnake.Message):
            return ref.resolved.to_reference()
        return self.message

    async def trigger_typing(self):
        try:
            channel = await self._get_channel()
            await self._state.http.send_typing(channel.id)
        except disnake.Forbidden:
            pass
