from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

import disnake
from disnake.ui import View, Button

import utils

if TYPE_CHECKING:
    from main import Ukiyo

__all__ = ('TicketView',)


class TicketView(View):
    def __init__(self, bot: Ukiyo):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Close', emoji='<:trash:914081331762307093>', custom_id='ukiyo:tickets')
    async def close(self, button: Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        ticket: utils.Ticket = await utils.Ticket.get(inter.channel.id)
        em = disnake.Embed(title='Ticket Closed', colour=utils.blurple)
        ticket_owner = inter.guild.get_member(ticket.owner_id)
        if inter.author.id == ticket.owner_id:
            em.description = f'You closed ticket `#{ticket.ticket_id}` ' \
                             f'that you created on {utils.format_dt(ticket.created_at, "F")} ' \
                             f'(`{utils.human_timedelta(ticket.created_at, accuracy=6)}`)'
        else:
            em.description = f'You closed **{ticket_owner.name}**\'s ticket ' \
                             f'that was created on {utils.format_dt(ticket.created_at, "F")} ' \
                             f'(`{utils.human_timedelta(ticket.created_at, accuracy=6)}`)'
            em_2 = disnake.Embed(
                colour=utils.blurple,
                title='Ticket Closed',
                description=f'Your ticket (`#{ticket.ticket_id}`) '
                            f'that you created on {utils.format_dt(ticket.created_at, "F")} '
                            f'(`{utils.human_timedelta(ticket.created_at, accuracy=6)}`)'
                            f'was closed by **{inter.author}**'
            )
            try:
                await ticket_owner.send(embed=em_2)
            except disnake.Forbidden:
                pass
        await utils.try_dm(inter.author, embed=em)
        await inter.channel.delete(reason=f'Ticket Closed by {inter.author} (ID: {inter.author.id})')
        await ticket.delete()
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[TICKET CLOSED]',
            fields=[
                ('Ticket Owner', f'{ticket_owner} (`{ticket_owner.id}`)'),
                ('Ticket ID', f'`#{ticket.ticket_id}`'),
                ('Closed By', f'{inter.author} (`{inter.author.id}`)'),
                ('At', utils.format_dt(datetime.now(), 'F')),
            ]
        )
