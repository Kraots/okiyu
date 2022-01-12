import os
import aiohttp
import asyncio
import datetime
from typing import Optional
from traceback import format_exception

import disnake
from disnake.ext import commands

import utils
from utils.views.help_command import PaginatedHelpCommand

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')


class Ukiyo(commands.Bot):
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
            test_guilds=[913310006814859334]
        )
        self.loop.run_until_complete(self._fill_attrs())  # Fill all of them concurrently in the background.
        self.add_check(self.check_dms)

        self._owner_id = 374622847672254466
        self.added_views = False
        self.webhooks = {}
        self.execs = {}
        self.verifying = []
        self.bad_words = {}
        self.calc_ternary = False

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

    async def _fill_attrs(self):
        async def _fill_views():
            if self.added_views is False:
                self.add_view(utils.Verify(self), message_id=913512065799421953)
                self.add_view(utils.ColourButtonRoles(), message_id=913763247927218177)
                self.add_view(utils.ColourButtonRoles(), message_id=913763329816821780)
                self.add_view(utils.ColourButtonRoles(), message_id=913763420644462603)
                self.add_view(utils.ColourButtonRoles(), message_id=913763496448110603)
                self.add_view(utils.ColourButtonRoles(), message_id=913763571853303858)
                self.add_view(utils.ColourButtonRoles(), message_id=913763639922659358)
                self.add_view(utils.PronounsButtonRoles(), message_id=928684415452856381)
                self.add_view(utils.GenderButtonRoles(), message_id=913788066114719785)
                self.add_view(utils.AgeButtonRoles(), message_id=913788068031496192)
                self.add_view(utils.SexualityButtonRoles(), message_id=913788069373681685)
                self.add_view(utils.RelationshipStatusButtonRoles(), message_id=913790418959876097)

                async for ticket in utils.Ticket.find():
                    self.add_view(utils.TicketView(), message_id=ticket.message_id)

                self.added_views = True

        async def _fill_bad_words():
            data: utils.BadWords = await utils.BadWords.get(self._owner_id)
            if data and data.bad_words and not self.bad_words:
                for word, added_by in data.bad_words.items():
                    self.bad_words[word] = added_by

        async def _fill_constants():
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

        asyncio.gather(_fill_constants(), _fill_bad_words(), _fill_views())

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        if not hasattr(self, '_session'):
            self._session = aiohttp.ClientSession(loop=self.loop)

        if not hasattr(self, '_presence_changed'):
            activity = disnake.Activity(type=disnake.ActivityType.watching, name='you date | !help')
            await self.change_presence(status=disnake.Status.dnd, activity=activity)
            self._presence_changed = True

        if len(self.webhooks) == 0:
            av = self.user.display_avatar
            logs = await self.get_webhook(
                self.get_channel(913332408537976892),
                avatar=av
            )
            mod_logs = await self.get_webhook(
                self.get_channel(914257049456607272),
                avatar=av
            )
            message_logs = await self.get_webhook(
                self.get_channel(913332431417925634),
                avatar=av
            )
            self.webhooks['logs'] = logs
            self.webhooks['mod_logs'] = mod_logs
            self.webhooks['message_logs'] = message_logs

        print('Bot is ready!')

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=utils.Context)
        await self.invoke(ctx)

    async def get_webhook(
        self,
        channel: disnake.TextChannel,
        *,
        name: str = "ukiyo",
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
            if ctx.command.qualified_name != 'intro':
                await ctx.send('Commands do not work in dm channels. Please use commands only in <#913330644875104306>')
                return False
        return True

    async def inter_reraise(self, inter, item: disnake.ui.Item, error):
        disagree = '<:disagree:913895999125196860>'
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


Ukiyo().run(TOKEN)
