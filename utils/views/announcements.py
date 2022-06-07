from __future__ import annotations

import textwrap
from asyncio import TimeoutError
from typing import TYPE_CHECKING

import disnake
from disnake.ui import View, button

import utils

if TYPE_CHECKING:
    from main import Okiyu

__all__ = ('AnnouncementView',)


class AnnouncementView(View):
    def __init__(self, bot: Okiyu, author: disnake.Member):
        super().__init__()
        self.bot = bot
        self.author = author

        self.description = None
        self.title = None
        self.ping_everyone = False

    async def on_error(self, error: Exception, item, interaction: disnake.MessageInteraction) -> None:
        if isinstance(error, TimeoutError):
            if interaction.response.is_done():
                method = self.message.edit
            else:
                method = interaction.response.edit_message
            await method(content='You took too long. Goodbye.', view=None, embed=None)
            return self.stop()
        await self.bot.inter_reraise(interaction, item, error)

    async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
        if inter.author.id != self.author.id:
            await inter.response.send_message(f'Only `{self.author}` can use the buttons on this message.', ephemeral=True)
            return False
        return True

    def lock_all(self):
        for child in self.children:
            if child.label == 'Abort':
                continue
            child.disabled = True

    def unlock_all(self):
        for child in self.children:
            if child.label == 'Confirm':
                if self.description is not None:
                    child.disabled = False
                else:
                    child.disabled = True
            else:
                child.disabled = False

    def prepare_embed(self):
        em = disnake.Embed(title='Announcement Creation', color=utils.blurple)
        em.add_field(name='Title', value=str(self.title), inline=False)
        em.add_field(name='Content', value=textwrap.shorten(str(self.description), 1024), inline=False)

        if len(str(self.description)) > 1024:
            em.description = '\n**Hint:** Announcement content reached embed field limitation, '\
                             'this will not affect the content itself.'
        return em

    @button(label='Title', style=disnake.ButtonStyle.blurple)
    async def set_title(self, button: disnake.Button, inter: disnake.MessageInteraction):
        self.lock_all()
        msg_content = 'Cool, let\'s set the title. Send the announcement title in the next message...'

        await inter.response.edit_message(content=msg_content, view=self)
        msg = await self.bot.wait_for(
            'message',
            timeout=300.0,
            check=lambda m: m.author.id == inter.author.id and m.channel.id == inter.channel.id
        )
        if self.is_finished():
            return

        if msg.content:
            clean_content = await utils.clean_inter_content()(inter, msg.content)
        else:
            clean_content = msg.content

        if msg.attachments:
            clean_content += f'\n{msg.attachments[0].url}'

        c = None
        if len(clean_content) > 250:
            c = 'Announcement title is a maximum of 250 characters.'
        else:
            self.title = clean_content

        self.unlock_all()
        await self.message.edit(content=c, embed=self.prepare_embed(), view=self)

    @button(label='Content', style=disnake.ButtonStyle.blurple)
    async def set_description(self, button: disnake.Button, inter: disnake.MessageInteraction):
        self.lock_all()
        msg_content = 'Cool, let\'s set the content. Send the announcement content in the next message...'

        await inter.response.edit_message(content=msg_content, view=self)
        msg = await self.bot.wait_for(
            'message',
            timeout=300.0,
            check=lambda m: m.author.id == inter.author.id and m.channel.id == inter.channel.id
        )
        if self.is_finished():
            return

        clean_content = msg.content

        if msg.attachments:
            clean_content += f'\n{msg.attachments[0].url}'

        c = None
        if len(clean_content) > 4000:
            c = 'Announcement content is a maximum of 4000 characters.'
        else:
            self.description = clean_content

        self.unlock_all()
        await self.message.edit(content=c, embed=self.prepare_embed(), view=self)

    @button(label='@everyone OFF')
    async def set_everyone_ping(self, button: disnake.Button, inter: disnake.MessageInteraction):
        if self.ping_everyone is False:
            self.ping_everyone = True
            button.label = '@everyone ON'
        else:
            self.ping_everyone = False
            button.label = '@everyone OFF'
        await inter.response.edit_message(view=self)

    @button(label='Confirm', style=disnake.ButtonStyle.green, row=1)
    async def confirm(self, button: disnake.Button, inter: disnake.MessageInteraction):
        if self.description is None:
            return await inter.response.edit_message(content='You didn\'t set the content!')
        await inter.response.edit_message(view=None)

        guild = self.bot.get_guild(938115625073639425)
        news_channel = guild.get_channel(utils.Channels.news)
        title = self.title or None
        em = disnake.Embed(colour=utils.red, title=title, description=self.description)
        if inter.author.id != self.bot._owner_id:
            em.set_footer(text=f'Announcement By: {inter.author}')
        if self.ping_everyone is False:
            allowed_mentions = disnake.AllowedMentions(everyone=False)
            content = None
        else:
            allowed_mentions = disnake.AllowedMentions(everyone=True)
            content = '@everyone'
        msg = await news_channel.send(content=content, embed=em, allowed_mentions=allowed_mentions)

        v = View()
        v.add_item(disnake.ui.Button(label='Jump!', url=msg.jump_url))
        await inter.message.reply('Announcement sent.', view=v)

        self.stop()

    @button(label='Abort', style=disnake.ButtonStyle.red, row=1)
    async def cancel(self, button: disnake.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(
            content='Announcement aborted.',
            view=None,
            embed=None
        )
        self.stop()
