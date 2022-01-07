import random
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

from main import Ukiyo


class Featured(commands.Cog):
    """Featured cool commands."""

    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.github_client = utils.GithubClient(bot)

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

        total_tickets = await Ticket.find({'user_id': ctx.author.id}).sort('ticket_id', -1).to_list(5)
        if len(total_tickets) == 5:
            return await ctx.reply('You already have a max of `5` tickets created!')
        ticket_id = '1' if not total_tickets else str(int(total_tickets[0].ticket_id) + 1)
        ch_name = f'{ctx.author.name}-ticket #' + ticket_id

        categ = ctx.ukiyo.get_channel(914082225274912808)
        channel = await ctx.ukiyo.create_text_channel(
            ch_name,
            category=categ,
            reason=f'Ticket Creation by {ctx.author} (ID: {ctx.author.id})'
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
            view=TicketView()
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
        await ctx.reply('Ticket created!', view=v)
        await utils.log(
            self.bot.webhooks['mod_logs'],
            title='[TICKET OPENED]',
            fields=[
                ('Ticket Owner', f'{ctx.author} (`{ctx.author.id}`)'),
                ('Ticket ID', f'`#{ticket_id}`'),
                ('At', utils.format_dt(datetime.now(), 'F')),
            ]
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        async for ticket in Ticket.find({'owner_id': member.id}):
            guild = self.bot.get_guild(913310006814859334)
            ch = guild.get_channel(ticket.id)
            await ch.delete(reason='Member left.')
            await ticket.delete()

    @commands.command(name='newmembers', aliases=('newusers', 'new'))
    async def new_members(self, ctx: Context, count: int = 3):
        """See the newest joined members, in order.

        `count` **->** The amount of how many new users you want to see. The minimum is 3 and it defaults to 3.
        """

        count = min(max(count, 3), ctx.ukiyo.member_count)
        users: list[disnake.Member] = sorted(ctx.ukiyo.members, key=lambda m: m.joined_at, reverse=True)
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

    @commands.command(name='run', aliases=('code',))
    @commands.cooldown(1, 2.0, commands.BucketType.guild)
    async def run_code(self, ctx: Context, *, code: str):
        r"""Runs the code and returns the result, must be in a codeblock with the markdown of the desired language.

        `code` **->** The code to run.

        **Example:**
        \u2800\`\`\`language
        \u2800code
        \u2800\`\`\`
        """

        if await ctx.check_channel() is False:
            return

        matches = utils.LANGUAGE_REGEX.findall(code)
        if not matches:
            rand = (
                'Your code is not wrapped inside a codeblock.',
                'You forgot your codeblock.',
                'Missing the codeblock.',
            )
            return await ctx.reply(random.choice(rand))

        lang = matches[0][0] or matches[0][1]
        if not lang:
            rand = (
                'You did not specify the language markdown in your codeblock.',
                'Missing the language markdown in your codeblock.',
                'Your codeblock is missing the language markdown.',
            )
            return await ctx.reply(random.choice(rand))

        code = matches[0][2]
        await ctx.trigger_typing()
        _res = await self.bot.session.post(
            'https://emkc.org/api/v1/piston/execute',
            json={'language': lang, 'source': code}
        )
        res = await _res.json()
        if 'message' in res:
            em = disnake.Embed(
                title='An error occured while running the code',
                description=res['message']
            )
            return await ctx.reply(embed=em)

        output = res['output']
        if len(output) > 500:
            content = utils.GistContent(f'```{res["language"]}\n' + output + '\n```')
            url = await self.github_client.create_gist(
                content.source,
                description=f'(`{ctx.author.id}` {ctx.author}) code result',
                filename='code_output.txt',
                public=False
            )
            msg = await ctx.reply(f'Your output was too long so I sent it to <{url}>')
            data = self.bot.execs.get(ctx.author.id)
            if data is None:
                self.bot.execs[ctx.author.id] = {ctx.command.name: msg}
            else:
                self.bot.execs[ctx.author.id][ctx.command.name] = msg
            return

        em = disnake.Embed(
            title=f'Ran your {res["language"]} code',
            color=utils.blurple
        )
        output = output[:500].strip()
        lines = output.splitlines()
        shortened = (len(lines) > 15)
        output = "\n".join(lines[:15])
        output += shortened * '\n\n**Output shortened**'
        em.add_field(name='Output', value=output or '**<No output>**')

        msg = await ctx.reply(embed=em)
        data = self.bot.execs.get(ctx.author.id)
        if data is None:
            self.bot.execs[ctx.author.id] = {ctx.command.name: msg}
        else:
            self.bot.execs[ctx.author.id][ctx.command.name] = msg


def setup(bot: Ukiyo):
    bot.add_cog(Featured(bot))
