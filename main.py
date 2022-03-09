import os
import aiohttp
import datetime
from typing import Optional
from collections import Counter
from traceback import format_exception

import disnake
from disnake.ext import commands

import utils
from utils.views.help_command import PaginatedHelpCommand

TOKEN = os.getenv('BOT_TOKEN')


class Okiyu(commands.Bot):
    def __init__(self):
        super().__init__(
            max_messages=100000,
            help_command=PaginatedHelpCommand(),
            command_prefix=('!', '?',),
            strip_after_prefix=True,
            case_insensitive=True,
            intents=disnake.Intents.all(),
            allowed_mentions=disnake.AllowedMentions(
                roles=False, everyone=False, users=True
            ),
            test_guilds=[938115625073639425]
        )
        self.add_check(self.check_dms)

        self.socket_events = Counter()

        self._owner_id = 938097236024360960

        self.added_views = False

        self.webhooks: dict[str, disnake.Webhook] = {}
        self.execs = {}
        self.bad_words = {}

        self.verifying = []

        self.calc_ternary = False

        self.serpapi_key = os.getenv('SERPAPI_KEY')

        self.load_extension('jishaku')
        os.environ['JISHAKU_NO_DM_TRACEBACK'] = '1'
        os.environ['JISHAKU_FORCE_PAGINATOR'] = '1'
        os.environ['JISHAKU_EMBEDDED_JSK'] = '1'
        os.environ['JISHAKU_EMBEDDED_JSK_COLOR'] = 'blurple'

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'cogs.{filename[:-3]}')

        for filename in os.listdir('./reload_cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'reload_cogs.{filename[:-3]}')

    @property
    def _owner(self) -> disnake.User:
        if self._owner_id:
            return self.get_user(self._owner_id)

    @property
    def session(self) -> aiohttp.ClientSession:
        return self._session

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        if not hasattr(self, '_session'):
            self._session = aiohttp.ClientSession(loop=self.loop)

        if not hasattr(self, '_presence_changed'):
            activity = disnake.Activity(type=disnake.ActivityType.watching, name='you date | !help')
            await self.change_presence(status=disnake.Status.dnd, activity=activity)
            self._presence_changed = True

        data: utils.BadWords = await utils.BadWords.get()
        if data and data.bad_words:
            for word, added_by in data.bad_words.items():
                self.bad_words[word] = added_by

        data: utils.Constants = await utils.Constants.get()
        if data is None:
            data = await utils.Constants().commit()
        self.calc_ternary = data.calculator_ternary
        for cmd_name in data.disabled_commands:
            cmd = self.get_command(cmd_name)
            if cmd is None:
                data.disabled_commands.remove(cmd_name)
                await data.commit()
            else:
                cmd.enabled = False

        if self.added_views is False:
            self.add_view(utils.Verify(self), message_id=938439017345736774)

            self.add_view(utils.ColourButtonRoles(), message_id=938429135800389673)
            self.add_view(utils.ColourButtonRoles(), message_id=938429211109109771)
            self.add_view(utils.ColourButtonRoles(), message_id=938429293371985950)
            self.add_view(utils.ColourButtonRoles(), message_id=938429380860989510)
            self.add_view(utils.ColourButtonRoles(), message_id=938429469910241322)
            self.add_view(utils.ColourButtonRoles(), message_id=938429554396127315)

            self.add_view(utils.GenderButtonRoles(), message_id=938437938646241391)
            self.add_view(utils.PronounsButtonRoles(), message_id=938437939405410334)
            self.add_view(utils.SexualityButtonRoles(), message_id=938437940193927259)
            self.add_view(utils.AgeButtonRoles(), message_id=938437940600799302)
            self.add_view(utils.RelationshipStatusButtonRoles(), message_id=938437951120105494)
            self.add_view(utils.DMButtonRoles(), message_id=938437952248352819)

            async for ticket in utils.Ticket.find():
                self.add_view(utils.TicketView(), message_id=ticket.message_id)

            self.added_views = True

        if len(self.webhooks) == 0:
            av = self.user.display_avatar
            logs = await self.get_webhook(
                self.get_channel(utils.Channels.logs),
                avatar=av
            )
            mod_logs = await self.get_webhook(
                self.get_channel(utils.Channels.moderation_logs),
                avatar=av
            )
            message_logs = await self.get_webhook(
                self.get_channel(utils.Channels.messages_logs),
                avatar=av
            )
            welcome_webhook = await self.get_webhook(
                self.get_channel(utils.Channels.welcome),
                avatar=av
            )
            self.webhooks['logs'] = logs
            self.webhooks['mod_logs'] = mod_logs
            self.webhooks['message_logs'] = message_logs
            self.webhooks['welcome_webhook'] = welcome_webhook

        # We do this cleanup in case the on_member_remove didn't trigger or
        # if the bot was offline during the time where the member left.
        guild = self.get_guild(938115625073639425)
        await self.collection_cleanup(guild, utils.Intro)
        await self.collection_cleanup(guild, utils.Level)
        await self.collection_cleanup(guild, utils.AFK)

        print('Bot is ready!')

    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def get_webhook(
        self,
        channel: disnake.TextChannel,
        *,
        name: str = "okiyu",
        avatar: disnake.Asset = None,
    ) -> disnake.Webhook:
        """Returns the general bot hook or creates one."""

        webhooks = await channel.webhooks()
        webhook = disnake.utils.find(lambda w: w.name and w.name.lower() == name.lower(), webhooks)

        if webhook is None:
            webhook = await channel.create_webhook(
                name=name,
                avatar=await avatar.read() if avatar else None,
                reason="Used ``get_webhook`` but webhook didn't exist",
            )

        return webhook

    async def reference_to_message(
        self, reference: disnake.MessageReference
    ) -> Optional[disnake.Message]:
        if reference._state is None or reference.message_id is None:
            return None

        channel = reference._state.get_channel(reference.channel_id)
        if channel is None:
            return None

        if not isinstance(channel, (disnake.TextChannel, disnake.Thread)):
            return None

        try:
            return await channel.fetch_message(reference.message_id)
        except disnake.NotFound:
            return None

    async def check_dms(self, ctx: utils.Context):
        if ctx.author.id == self.owner_id:
            return True
        if isinstance(ctx.channel, disnake.DMChannel):
            if ctx.command.qualified_name not in ('intro', 'ticket'):
                await ctx.send('Commands do not work in dm channels. Please use commands only in <#938119528464916530>')
                return False
        return True

    async def inter_reraise(self, inter, item: disnake.ui.Item, error):
        disagree = '<:disagree:938412196663271514>'
        get_error = "".join(format_exception(error, error, error.__traceback__))
        em = disnake.Embed(description=f'```py\n{get_error}\n```')
        await self._owner.send(
            content="**An error occurred with a view for the user "
                    f"`{inter.author}` (**{inter.author.id}**), "
                    "here is the error:**\n"
                    f"`View:` **{item.view.__class__}**\n"
                    f"`Item Type:` **{item.type}**\n"
                    f"`Item Row:` **{item.row or '0'}**",
            embed=em
        )
        fmt = f'> {disagree} An error occurred'
        if inter.response.is_done():
            await inter.followup.send(fmt, ephemeral=True)
        else:
            await inter.response.send_message(fmt, ephemeral=True)

    async def get_context(self, message, *, cls=utils.Context):
        return await super().get_context(message, cls=cls)

    @staticmethod
    async def collection_cleanup(guild: disnake.Guild, collection) -> None:
        """Searches and deletes every single document that is related to a user that isn't in okiyu anymore.

        Parameters
        ----------
            guild: :class:`.Guild`
                The guild to check for.

            collection: :class:`.AsyncIOMotorCollection`
                The collection object from which to delete.

        Return
        ------
            `None`
        """

        async for entry in collection.find():
            if entry.id not in [m.id for m in guild.members]:
                await entry.delete()


Okiyu().run(TOKEN)
