import pytz
from datetime import datetime
from asyncio import TimeoutError
from dateutil.relativedelta import relativedelta

import disnake
from disnake.ext import commands, tasks

import utils
from utils import Context, Birthday

from main import Ukiyo


class Birthdays(commands.Cog):
    """Birthday related commands."""

    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.check_birthday.start()

    @property
    def display_emoji(self) -> str:
        return '🍰'

    @tasks.loop(seconds=30.0)
    async def check_birthday(self):
        datas: list[Birthday] = await Birthday.find().sort('next_birthday', 1).to_list(15)
        now = datetime.now()
        for data in datas:
            if now >= data.next_birthday:
                data.next_birthday += relativedelta(years=1)
                await data.commit()

                guild = self.bot.get_guild(913310006814859334)
                channel = guild.get_channel(923681449490669628)
                mem = guild.get_member(data.id)
                next_birthday = data.next_birthday.strftime('%d %B %Y')
                age = utils.human_timedelta(data.birthday_date, accuracy=1, suffix=False) \
                    .replace(' years', '') \
                    .replace(' year', '')

                em = disnake.Embed(title=f'Happy {age}th birthday {mem.name}!!! :tada: :tada:', color=mem.color)
                em.set_image(url='https://cdn.discordapp.com/attachments/787359417674498088/901940653762687037/happy_bday.gif')
                em.set_footer(text=f'Your next birthday is on {next_birthday}')

                msg = await channel.send(mem.mention, embed=em)
                await msg.add_reaction('🍰')

    @check_birthday.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.group(name='birthday', aliases=('bday', 'b-day',), invoke_without_command=True, case_insensitive=True)
    async def base_birthday(self, ctx: Context, *, member: disnake.Member = None):
        """See how much time left there is until the member's birthday, if they set it.

        `member` **->** The member that you wish to set the coins for. Defaults to yourself.
        """

        member = member or ctx.author
        data: Birthday = await Birthday.find_one({'_id': member.id})
        if data is None:
            if member.id == ctx.author.id:
                return await ctx.reply('You did not set your birthday.')
            else:
                return await ctx.better_reply(f'`{member}` did not set their birthday.')

        em = disnake.Embed(title=f'`{member}`\'s birthday', color=utils.blurple)
        em.add_field(
            'Birthday date',
            data.birthday_date.strftime('%d %B %Y'),
            inline=False
        )
        em.add_field(
            'Time left until their next birthday',
            utils.human_timedelta(data.next_birthday, accuracy=6, suffix=False),
            inline=False
        )
        em.add_field(
            'Timezone',
            data.timezone,
            inline=False
        )
        em.set_footer(text=f'Requested by: {ctx.author}')

        await ctx.better_reply(embed=em)

    @base_birthday.command(name='set')
    @utils.lock()
    async def birthday_set(self, ctx: Context, date: str):
        """Set your birthday.

        `date` **->** The exact date when you were born. The format in which you set this is **day/month/year**.

        **Example:**
        `!birthday set 24/08/2005`

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        data: Birthday = await Birthday.find_one({'_id': ctx.author.id})
        if data is None:
            data = Birthday(id=ctx.author.id)

        try:
            birthday_date = datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            return await ctx.reply(
                'The format in which you gave your birthday date does not match the one you\'re supposed to give it in. '
                'Doing `!help birthday set` will show you the correct format.'
            )
        data.birthday_date = birthday_date

        await ctx.reply(
            'Please send your exact location in order to get your timezone.\n'
            'The format in which you must send this must be **Region/Capital**. (e.g: Europe/London, America/Los Angeles, etc...)'
        )
        try:
            _birthday_timezone = await self.bot.wait_for(
                'message',
                check=lambda m: m.channel.id == ctx.channel.id and m.author.id == ctx.author.id,
                timeout=45.0
            )
        except TimeoutError:
            return await ctx.reply('Ran out of time.')

        if _birthday_timezone.content is None:
            return await ctx.reply('You didn\'t give a valid timezone.')

        try:
            birthday_timezone = pytz.timezone(_birthday_timezone.content.replace(' ', '_'))
        except pytz.UnknownTimeZoneError:
            return await _birthday_timezone.reply(
                'That Region/Capital does not exist. Please pick one that has the exact same timezone as yours.'
            )
        data.timezone = birthday_timezone.zone.replace('_', ' ')

        now = datetime.now()
        offset = birthday_timezone.utcoffset(now)
        seconds = offset.total_seconds()
        next_birthday = birthday_date - relativedelta(year=now.year, seconds=seconds)
        if now > next_birthday:
            next_birthday += relativedelta(years=1)
        data.next_birthday = next_birthday

        await data.commit()
        await ctx.reply('Your birthday has been set.')

    @base_birthday.command(name='remove')
    @utils.lock()
    async def birthday_remove(self, ctx: Context):
        """Remove your birthday, if you have it set.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        data: Birthday = await Birthday.find_one({'_id': ctx.author.id})
        if data is None:
            return await ctx.reply('You did not set your birthday.')

        view = utils.ConfirmView(ctx)
        view.message = await ctx.reply('Are you sure you want to remove your birthday?', view=view)
        await view.wait()
        if view.response is True:
            await data.delete()
            await view.message.edit(content='Successfully removed your birthday.')
        else:
            await view.message.edit(content='Did not remove your birthday.')

    @base_birthday.command(name='top', aliases=('upcoming',))
    async def bday_top(self, ctx: Context):
        """See top 5 upcoming birthdays.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        index = 0

        def format_date(dt1):
            return f'Birthday in `{utils.human_timedelta(dt1, accuracy=6)}`'

        em = disnake.Embed(color=disnake.Color.blurple(), title='***Top `5` upcoming birthdays***\n _ _ ')

        datas: list[Birthday] = await Birthday.find().sort('next_birthday', 1).to_list(5)
        for data in datas:
            user = self.bot.get_user(data.id)
            index += 1
            next_birthday_date = data.next_birthday.strftime('%d %B %Y')
            next_birthday = utils.human_timedelta(data.next_birthday, accuracy=3)
            em.add_field(
                name=f"`{index}`. _ _ _ _ {user.name}",
                value=f'Birthday in `{next_birthday}` ( **{next_birthday_date}** )',
                inline=False
            )

        await ctx.send(embed=em)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data: Birthday = await Birthday.find_one({'_id': member.id})
        if data is not None:
            await data.delete()


def setup(bot: Ukiyo):
    bot.add_cog(Birthdays(bot))
