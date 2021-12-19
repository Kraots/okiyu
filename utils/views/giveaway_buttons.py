from __future__ import annotations

import textwrap
from asyncio import TimeoutError
from typing import TYPE_CHECKING

import disnake
from disnake.ext import commands
from disnake.ui import View, button

import utils

if TYPE_CHECKING:
    from main import Ukiyo

__all__ = (
    'GiveAwayCreationView',
    'JoinGiveawayButton',
)


class JoinGiveawayButton(disnake.ui.Button):
    def __init__(self, label: str = '0'):
        super().__init__(
            label=f'🎉 {label} participants',
            custom_id='ukiyo:giveaways:join_btn',
            style=disnake.ButtonStyle.blurple
        )

    async def callback(self, inter: disnake.MessageInteraction):
        data: utils.GiveAway = await utils.GiveAway.find_one({'_id': inter.message.id})
        if inter.author.id in data.participants:
            return await inter.response.send_message(
                'You are already participating in this giveaway!',
                ephemeral=True
            )

        author_data: utils.Level = await utils.Level.find_one({'_id': inter.author.id})
        if author_data is None:
            return await inter.response.send_message(
                'You have never sent a message in the server. Cannot participate!',
                ephemeral=True
            )
        elif author_data.messages_count < data.messages_requirement:
            needed_messages = data.messages_requirement - author_data.messages_count
            return await inter.response.send_message(
                'Sorry! You don\'t seem to meet this giveaway\'s message requirement.\n'
                f'You need **{needed_messages:,}** more messages if you want to participate.\n\n'
                '**NOTE:** If you spam, your message count will be reset by one of our staff members, '
                'so please refrain from spamming.',
                ephemeral=True
            )

        data.participants.append(inter.author.id)
        await data.commit()

        self.label = f'🎉 {len(data.participants)} participants'
        view = self.view
        self.view.children[0] = self
        await inter.message.edit(view=view)

        await inter.response.send_message('You are now participating in this giveaway.', ephemeral=True)


class GiveAwayCreationView(View):
    def __init__(self, bot: Ukiyo, author: disnake.Member):
        super().__init__()
        self.bot = bot
        self.author = author

        self.prize = None
        self.message_req = 0
        self.expire_date = None
        self.ping_everyone = False

    async def on_error(self, error: Exception, item, interaction: disnake.MessageInteraction) -> None:
        if isinstance(error, TimeoutError):
            if interaction.response.is_done():
                method = self.message.edit
            else:
                method = interaction.response.edit_message
            await method(content='You took too long. Goodbye.', view=None, embed=None)
            return self.stop()
        await self.bot.inter_reraise(self.bot, interaction, item, error)

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
        if self.expire_date is not None:
            duration = utils.human_timedelta(self.expire_date, suffix=False)
        else:
            duration = str(self.expire_date)
        em = disnake.Embed(title='Giveaway Creation', color=utils.blurple)
        em.add_field(name='Prize', value=textwrap.shorten(str(self.prize), 1024), inline=False)
        em.add_field(name='Duration', value=duration, inline=False)
        em.add_field(name='Message Requirements', value=self.message_req, inline=False)

        if len(str(self.description)) > 1024:
            em.description = '\n**Hint:** Giveaway content reached embed field limitation, '\
                             'this will not affect the content itself.'
        return em

    @button(label='Prize', style=disnake.ButtonStyle.blurple)
    async def set_prize(self, button: disnake.Button, inter: disnake.MessageInteraction):
        self.lock_all()
        msg_content = 'Cool, let\'s set the prize. Send the giveaway\'s prize in the next message...'

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

        self.prize = clean_content

        self.unlock_all()
        await self.message.edit(embed=self.prepare_embed(), view=self)

    @button(label='Duration', style=disnake.ButtonStyle.blurple)
    async def set_duration(self, button: disnake.Button, inter: disnake.MessageInteraction):
        self.lock_all()
        msg_content = 'Cool, let\'s set the duration. Send how long you wish the givaway to last for in the next message...'

        await inter.response.edit_message(content=msg_content, view=self)
        msg = await self.bot.wait_for(
            'message',
            timeout=300.0,
            check=lambda m: m.author.id == inter.author.id and m.channel.id == inter.channel.id
        )
        if self.is_finished():
            return

        c = None
        content = msg.content
        ctx = await self.bot.get_context(msg, cls=utils.Context)
        try:
            duration = await utils.UserFriendlyTime(commands.clean_content).convert(ctx, content + ' -')
            self.expire_date = duration.dt
        except commands.BadArgument as e:
            c = f'> {ctx.disagree} {e}'

        self.unlock_all()
        await self.message.edit(content=c, embed=self.prepare_embed(), view=self)

    @button(label='Messages Requirement', style=disnake.ButtonStyle.blurple)
    async def set_message_req(self, button: disnake.Button, inter: disnake.MessageInteraction):
        self.lock_all()
        msg_content = 'Cool, let\'s set the messages requirement. Send the giveaway\'s message requirement in the next message...'

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

        c = None
        if clean_content is None:
            c = 'Message requirement cannot be empty.'
        else:
            try:
                clean_content = int(clean_content)
            except ValueError:
                c = 'Message requirement must be a number only!'
            else:
                self.message_req = clean_content

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
        if self.prize is None:
            return await inter.response.edit_message(content='You didn\'t set the prize!')
        elif self.expire_date is None:
            return await inter.response.edit_message(content='You didn\'t set the duration!')
        await inter.response.edit_message(view=None)

        guild = self.bot.get_guild(913310006814859334)
        news_channel = guild.get_channel(913331371282423808)
        em = disnake.Embed(
            colour=utils.green,
            title='🎁 New Giveaway',
            description='Press the button below that contains the reaction 🎉 to participate.'
        )
        em.add_field(
            'Prize',
            self.prize,
            inline=False
        )
        em.add_field(
            'Expires At',
            f'{utils.format_dt(self.expire_date, "F")} ({utils.format_relative(self.expire_date)})',
            inline=False
        )
        em.add_field(
            'Message Requirement',
            f'You need a total of **{self.message_req}** messages in order to participate to this giveaway.',
            inline=False
        )

        if inter.author.id != self.bot._owner_id:
            em.set_footer(text=f'Giveaway By: {inter.author}')
        if self.ping_everyone is False:
            allowed_mentions = disnake.AllowedMentions(everyone=False)
            content = None
        else:
            allowed_mentions = disnake.AllowedMentions(everyone=True)
            content = '@everyone'

        view = disnake.ui.View(timeout=None)
        view.add_item(JoinGiveawayButton())

        msg: disnake.Message = await news_channel.send(
            content=content,
            embed=em,
            allowed_mentions=allowed_mentions,
            view=view
        )
        await msg.pin(reason='New Giveaway.')
        await news_channel.purge(limit=1)
        await utils.GiveAway(
            id=msg.id,
            prize=self.prize,
            expire_date=self.expire_date,
            messages_requirement=self.message_req
        ).commit()

        v = View()
        v.add_item(disnake.ui.Button(label='Jump!', url=msg.jump_url))
        await inter.message.reply('Giveaway sent.', view=v)

        self.stop()

    @button(label='Abort', style=disnake.ButtonStyle.red, row=1)
    async def cancel(self, button: disnake.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message(
            content='Giveaway aborted.',
            view=None,
            embed=None
        )
        self.stop()
