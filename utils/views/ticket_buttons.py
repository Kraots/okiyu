import disnake
from disnake.ui import View, Button

import utils

__all__ = ('TicketView',)


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Close', emoji='<:trash:914081331762307093>', custom_id='ukiyo:tickets')
    async def close(self, button: Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        ticket: utils.Ticket = await utils.Ticket.find_one({'_id': inter.channel.id})
        em = disnake.Embed(title='Ticket Closed', colour=utils.blurple)
        if inter.author.id == ticket.user_id:
            em.description = f'You closed ticket `#{ticket.ticket_id}` ' \
                             f'that you created on {utils.format_dt(ticket.created_at, "F")} ' \
                             f'(`{utils.human_timedelta(ticket.created_at)}`)'
        else:
            em.description = f'You closed **{(inter.guild.get_member(ticket.user_id)).name}**\'s ticket ' \
                             f'that was created on {utils.format_dt(ticket.created_at, "F")} ' \
                             f'(`{utils.human_timedelta(ticket.created_at)}`)'
            em_2 = disnake.Embed(
                colour=utils.blurple,
                title='Ticket Closed',
                description=f'Your ticket (`#{ticket.ticket_id}`) '
                            f'that you created on {utils.format_dt(ticket.created_at, "F")} '
                            f'(`{utils.human_timedelta(ticket.created_at)}`)'
                            f'was closed by **{inter.author}**'
            )
            await (inter.guild.get_member(ticket.user_id)).send(embed=em_2)
        await inter.author.send(embed=em)
        await inter.channel.delete(reason=f'Ticket Closed by {inter.author} (ID: {inter.author.id})')
        await ticket.delete()
