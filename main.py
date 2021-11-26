import os
import aiohttp
import datetime
from typing import Optional

import disnake
from disnake.ext import commands

import utils
from utils.views.help_command import PaginatedHelpCommand

TOKEN = os.getenv('BOT_TOKEN')


class Ukiyo(commands.Bot):
    def __init__(self):
        super().__init__(
            help_command=PaginatedHelpCommand(),
            command_prefix='!',
            case_insensitive=True,
            intents=disnake.Intents.all(),
            allowed_mentions=disnake.AllowedMentions(
                roles=False, everyone=False, users=True
            ),
            test_guilds=[913310006814859334]
        )
        self.added_views = False
        self.reraise = utils.reraise
        self.execs = {}
        self.verifying = []

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

        if not hasattr(self, '_owner_id'):
            app = await self.application_info()
            self._owner_id = app.owner.id

        if self.added_views is False:
            self.add_view(utils.Verify(self), message_id=913512065799421953)
            self.add_view(utils.ColourButtonRoles(), message_id=913763247927218177)
            self.add_view(utils.ColourButtonRoles(), message_id=913763329816821780)
            self.add_view(utils.ColourButtonRoles(), message_id=913763420644462603)
            self.add_view(utils.ColourButtonRoles(), message_id=913763496448110603)
            self.add_view(utils.ColourButtonRoles(), message_id=913763571853303858)
            self.add_view(utils.ColourButtonRoles(), message_id=913763639922659358)
            self.add_view(utils.GenderButtonRoles(), message_id=913788066114719785)
            self.add_view(utils.AgeButtonRoles(), message_id=913788068031496192)
            self.add_view(utils.SexualityButtonRoles(), message_id=913788069373681685)
            self.added_views = True

        print('Bot is ready!')

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=utils.Context)
        await self.invoke(ctx)

    async def get_webhook(
        self,
        channel: disnake.TextChannel,
        *,
        name: str = "Ukiyo",
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


Ukiyo().run(TOKEN)
