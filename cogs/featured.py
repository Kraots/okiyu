from datetime import datetime

import disnake
from disnake.ext import commands
from disnake.ui import View, Button

import utils
from utils import (
    Context,
    Ticket,
    TicketView
)

from main import Okiyu


class Featured(commands.Cog):
    """Featured cool commands."""

    def __init__(self, bot: Okiyu):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '⭐'

    @commands.command(name='timediff')
    async def time_difference(self, ctx: Context, date1: str, date2: str):
        """Compare 2 dates. The format in which you give this must be **day/month/year**.

        `time1` **->** The first date you want to compare the second date to.
        `time2` **->** The second date you want to compare the first date to.

        **Example:**
        `!timediff 24/08/2005 23/12/2021` **->** This will show the exact difference (not hour/sec precise) between 23rd December 2021 and 25th August 2005 (also the owner's birthday :flushed:)
        """  # noqa

        try:
            time1 = datetime.strptime(date1, '%d/%m/%Y')
            time2 = datetime.strptime(date2, '%d/%m/%Y')
        except ValueError:
            return await ctx.reply(
                'One of the dates you have given does not match the format in which a date should be given.'
            )
        diff = utils.human_timedelta(time2, source=time1, suffix=False, accuracy=5)

        _time1 = time1.strftime('%d %B %Y')
        _time2 = time2.strftime('%d %B %Y')

        em = disnake.Embed(
            color=utils.blurple,
            description=f'The difference between **{_time1}** and **{_time2}** is `{diff}`'
        )

        await ctx.better_reply(embed=em)

    @commands.command(name='ticket')
    @commands.cooldown(1, 60.0, commands.BucketType.member)
    async def ticket_cmd(self, ctx: Context):
        """Create a ticket."""

        if not isinstance(ctx.channel, disnake.DMChannel):
            await ctx.message.delete()

        total_tickets = await Ticket.find({'user_id': ctx.author.id}).sort('ticket_id', -1).to_list(5)
        if len(total_tickets) == 5:
            return await ctx.reply('Cannot create ticket because ticket limit reached (`5`).')
        ticket_id = '1' if not total_tickets else str(int(total_tickets[0].ticket_id) + 1)
        ch_name = f'{ctx.author.name}-ticket #' + ticket_id

        categ = ctx.okiyu.get_channel(utils.Categories.tickets)
        channel = await ctx.okiyu.create_text_channel(
            ch_name,
            category=categ,
            reason=f'Ticket Creation by {utils.format_name(ctx.author)} (ID: {ctx.author.id})'
        )
        em = disnake.Embed(
            title=f'Ticket #{ticket_id}',
            description='Hello, thanks for creating a ticket. '
                        'Please write out what made you feel like you needed to create a ticket '
                        'and be patient until one of our staff members is available '
                        'to help.'
        )
        m = await channel.send(
            ctx.author.mention,
            embed=em,
            view=TicketView(self.bot)
        )

        ticket = Ticket(
            channel_id=channel.id,
            message_id=m.id,
            owner_id=ctx.author.id,
            ticket_id=ticket_id,
            created_at=datetime.utcnow()
        )
        await ticket.commit()

        await m.pin()
        await channel.purge(limit=1)
        await channel.set_permissions(ctx.author, read_messages=True)

        v = View()
        v.add_item(Button(label='Jump!', url=m.jump_url))
        await utils.try_dm(ctx.author, 'Ticket created!', view=v)
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[TICKET OPENED]',
            fields=[
                ('Ticket Owner', f'{utils.format_name(ctx.author)} (`{ctx.author.id}`)'),
                ('Ticket ID', f'`#{ticket_id}`'),
                ('At', utils.format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        async for ticket in Ticket.find({'owner_id': member.id}):
            guild = self.bot.get_guild(938115625073639425)
            ch = guild.get_channel(ticket.id)
            await ch.delete(reason='Member left.')
            await ticket.delete()

    @commands.command(name='newmembers', aliases=('newusers', 'new'))
    async def new_members(self, ctx: Context, count: int = 3):
        """See the newest joined members, in order.

        `count` **->** The amount of how many new users you want to see. The minimum is 3 and it defaults to 3.
        """

        count = min(max(count, 3), ctx.okiyu.member_count)
        users: list[disnake.Member] = sorted(ctx.okiyu.members, key=lambda m: m.joined_at, reverse=True)
        entries = []
        for index, user in enumerate(users):
            if index >= count:
                break

            entries.append(
                (
                    f'`#{index + 1}` {user.display_name}',
                    f'Joined at {utils.format_dt(user.joined_at, "F")} (`{utils.human_timedelta(user.joined_at)}`)\n'
                    f'Created at {utils.format_dt(user.created_at, "F")} (`{utils.human_timedelta(user.created_at)}`)\n\n'
                )
            )

        source = utils.FieldPageSource(entries, per_page=5)
        source.embed.title = f'Here\'s the top `{count}` newly joined members'
        paginator = utils.RoboPages(source, ctx=ctx, compact=True)
        await paginator.start()


def setup(bot: Okiyu):
    bot.add_cog(Featured(bot))
