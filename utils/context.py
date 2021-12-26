from aiohttp import ClientSession

import disnake
from disnake.ext import commands

__all__ = ('Context',)


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self) -> ClientSession:
        return self.bot.session

    @property
    def agree(self) -> disnake.PartialEmoji:
        return disnake.PartialEmoji(name='agree', id=913895978535374898)

    @property
    def disagree(self) -> disnake.PartialEmoji:
        return disnake.PartialEmoji(name='disagree', id=913895999125196860)

    @property
    def thumb(self) -> disnake.PartialEmoji:
        return disnake.PartialEmoji(name='thumb', id=923542820273418290)

    @property
    def denial(self) -> str:
        return f'>>> {self.disagree}'

    @disnake.utils.cached_property
    def replied_reference(self) -> disnake.MessageReference | None:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, disnake.Message):
            return ref.resolved.to_reference()
        return None

    async def trigger_typing(self) -> None:
        try:
            channel = await self._get_channel()
            await self._state.http.send_typing(channel.id)
        except disnake.Forbidden:
            pass

    async def better_reply(self, *args, **kwargs) -> disnake.Message:
        if self.replied_reference is not None:
            try:
                del kwargs['reference']
            except KeyError:
                pass
            return await self.send(*args, reference=self.replied_reference, **kwargs)
        else:
            return await super().reply(*args, **kwargs)

    async def check_channel(self) -> bool:
        if self.channel.id not in (913330644875104306, 913332335473205308, 913445987102654474) \
                and self.author.id != 374622847672254466:
            await self.reply(f'{self.denial} Sorry! This command can only be used in <#913330644875104306>', delete_after=10.0)
            return False
        return True

    async def check_perms(
        self,
        member: disnake.Member,
        *,
        reason: str = 'That member is above or equal to you. Cannot do that.'
    ) -> bool:
        if self.author.id == 374622847672254466:
            return True
        elif member.id == 374622847672254466:
            await self.reply(
                f'{self.denial} That member is above or equal to you. '
                'Cannot do that. (above in this case you sub bottom <:kek:913339277939720204>)'
            )
            return False
        elif self.author.top_role <= member.top_role:
            await self.reply(f'{self.denial} {reason}')
            return False
        return True
