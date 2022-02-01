from aiohttp import ClientSession
from traceback import format_exception

import disnake
from disnake.ext import commands

import utils
from utils import Channels

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

    @property
    def okiyu(self) -> disnake.Guild:
        return self.bot.get_guild(938115625073639425)

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
        if self.channel.id not in (
            Channels.bots, Channels.bot_commands, Channels.staff_chat
        ) \
                and self.author.id != 938097236024360960:
            await utils.try_delete(self.message, delay=10.0)
            await self.reply(
                f'{self.denial} Sorry! This command can only be used in <#{Channels.bots}>',
                delete_after=10.0
            )
            return False
        return True

    async def check_perms(
        self,
        member: disnake.Member,
        *,
        reason: str = 'That member is above or equal to you. Cannot do that.'
    ) -> bool:
        if self.author.id == 938097236024360960:
            return True
        elif member.id == 938097236024360960:
            await self.reply(
                f'{self.denial} That member is above or equal to you. '
                'Cannot do that. (above in this case you sub bottom <:kek:913339277939720204>)'
            )
            return False
        elif self.author.top_role <= member.top_role:
            await self.reply(f'{self.denial} {reason}')
            return False
        return True

    async def reraise(self, error):
        if isinstance(error, commands.NotOwner):
            await self.reply(f'{self.denial} You do not own this bot, this is an owner only command.', delete_after=8)
            await utils.try_delete(self.message, delay=8)
            return

        elif isinstance(error, commands.CommandOnCooldown):
            if error.retry_after > 60.0:
                time = utils.time_phaser(error.retry_after)
            else:
                time = f'{error.retry_after:.2f} seconds'
            return await self.reply(
                f'{self.denial} You are on cooldown, **`{time}`** remaining.'
            )

        elif isinstance(error, commands.DisabledCommand):
            self.command.reset_cooldown(self)
            return await self.reply('This command is currently disabled!')

        elif isinstance(error, commands.MaxConcurrencyReached):
            await utils.try_delete(self.message, delay=5.0)
            await self.reply(
                'You are already using this command! Please wait until you complete it first.',
                delete_after=5.0
            )
            return

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            _missing_args = list(self.command.clean_params)
            missing_args = [f'`{arg}`' for arg in _missing_args[_missing_args.index(error.param.name):]]
            return await self.reply(
                f"{self.denial} You are missing the following required arguments for this command:\n "
                f"\u2800\u2800{utils.human_join(missing_args, final='and')}\n\n"
                "If you don't know how to use this command, please type "
                f"`!help {self.command.qualified_name}` for more information on how to use it and what each "
                "argument means."
            )

        elif isinstance(error, commands.errors.MemberNotFound):
            await self.reply(f"{self.denial} Could not find member.")
            self.command.reset_cooldown(self)
            return

        elif isinstance(error, commands.errors.UserNotFound):
            await self.reply(f"{self.denial} Could not find user.")
            self.command.reset_cooldown(self)
            return

        elif isinstance(error, commands.errors.CheckFailure):
            self.command.reset_cooldown(self)
            return

        elif isinstance(error, commands.ExpectedClosingQuoteError):
            self.command.reset_cooldown(self)
            return await self.reply(f'Expected closing `{error.close_quote}`')

        elif isinstance(error, commands.InvalidEndOfQuotedStringError):
            self.command.reset_cooldown(self)
            return await self.reply(f'Expected space after ending the quote, not `{error.char}`')

        elif (
            isinstance(error, commands.TooManyArguments) or
            isinstance(error, commands.BadArgument) or
            isinstance(error, commands.CommandNotFound)
        ):
            return

        else:
            get_error = "".join(format_exception(error, error, error.__traceback__))
            em = disnake.Embed(description=f'```py\n{get_error}\n```')
            await self.bot._owner.send(
                content=f"**An error occurred with the command `{self.command}`, "
                        "here is the error:**",
                embed=em
            )
            await self.reply(f'{self.denial} An error occurred')
