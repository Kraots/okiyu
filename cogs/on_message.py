import asyncio
import datetime

import disnake
from disnake.ext import commands

import utils

from main import Ukiyo


async def send_webhook(em: disnake.Embed, view: disnake.ui.View, bot: Ukiyo):
    webhook = await bot.get_webhook(
        bot.get_channel(913332431417925634),
        avatar=bot.user.display_avatar
    )
    await webhook.send(embed=em, view=view)


class OnMessage(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @commands.Cog.listener('on_message_delete')
    async def on_message_delete(self, message: disnake.Message):
        if message.author.bot:
            return

        if message.author.id == self.bot._owner_id:
            return

        else:
            em = disnake.Embed(
                color=utils.red,
                description=f'Message deleted in <#{message.channel.id}> \n\n'
                            f'**Content:** \n```{message.content}```',
                timestamp=datetime.datetime.utcnow()
            )
            em.set_author(name=f'{message.author}', icon_url=f'{message.author.display_avatar}')
            em.set_footer(text=f'User ID: {message.author.id}')
            if message.attachments:
                em.set_image(url=message.attachments[0].proxy_url)
            ref = message.reference
            if ref and isinstance(ref.resolved, disnake.Message):
                em.add_field(
                    name='Replying to...',
                    value=f'[{ref.resolved.author}]({ref.resolved.jump_url})',
                    inline=False
                )

            await asyncio.sleep(0.5)
            try:
                btn = disnake.ui.View()
                btn.add_item(disnake.ui.Button(label='Jump!', url=message.jump_url))
                await send_webhook(em, btn, self.bot)
            except Exception as e:
                ctx = await self.bot.get_context(message)
                await self.bot.reraise(ctx, e)

    @commands.Cog.listener('on_message_edit')
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message):
        if before.author.bot:
            return
        if before.author.id == self.bot._owner_id:
            return
        else:
            em = disnake.Embed(
                color=utils.yellow,
                description=f'Message edited in <#{before.channel.id}>\n\n**Before:**\n```{before.content}```\n\n**After:**\n```{after.content}```',  # noqa
                timestamp=datetime.datetime.utcnow()
            )
            em.set_author(name=f'{before.author}', icon_url=f'{before.author.display_avatar}')
            em.set_footer(text=f'User ID: {before.author.id}')
            ref = after.reference
            if ref and isinstance(ref.resolved, disnake.Message):
                em.add_field(
                    name='Replying to...',
                    value=f'[{ref.resolved.author}]({ref.resolved.jump_url})',
                    inline=False
                )

            await asyncio.sleep(0.5)
            try:
                btn = disnake.ui.View()
                btn.add_item(disnake.ui.Button(label='Jump!', url=after.jump_url))
                await send_webhook(em, btn, self.bot)
            except Exception as e:
                ctx = await self.bot.get_context(after)
                await self.bot.reraise(ctx, e)

    @commands.Cog.listener('on_message_edit')
    async def repeat_command(self, before: disnake.Message, after: disnake.Message):
        if after.content.lower().startswith(('!e', '!eval')):
            ctx = await self.bot.get_context(after)
            cmd = self.bot.get_command(after.content.lower().replace('!', ''))
            await after.add_reaction('🔁')
            try:
                await self.bot.wait_for(
                    'reaction_add',
                    check=lambda r, u: str(r.emoji) == '🔁' and u.id == after.author.id,
                    timeout=360.0
                )
            except asyncio.TimeoutError:
                await after.clear_reaction('🔁')
            else:
                curr: disnake.Message = self.bot.execs[after.author.id].get(cmd.name)
                if curr:
                    await curr.delete()
                await after.clear_reaction('🔁')
                await cmd.invoke(ctx)

    @commands.Cog.listener('on_message')
    async def check_for_invalid_name(self, message: disnake.Message):
        if message.guild:
            await utils.check_username(self.bot, member=message.author)


def setup(bot: Ukiyo):
    bot.add_cog(OnMessage(bot))
