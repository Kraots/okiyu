from datetime import datetime
from dateutil.relativedelta import relativedelta

import disnake
from disnake.ext import commands, tasks

import utils
from utils import (
    Context,
    Game
)

from main import Ukiyo


class _Game(commands.Cog, name='Game'):
    """This category shows the base command for the game commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.streaks_check.start()

    @property
    def display_emoji(self) -> str:
        return '🪙'

    @tasks.loop(seconds=3.0)
    async def streaks_check(self):
        dailys: list[Game] = await Game.find().sort('daily', 1).to_list(10)
        for data in dailys:
            date = data.daily + relativedelta(days=1)
            if date <= datetime.now():
                data.streak = 0
                await data.commit()

    async def get_user(self, ctx: Context) -> Game:
        data: Game = await Game.find_one({'_id': ctx.author.id})
        if data is None:
            data = Game(
                id=ctx.author.id,
                coins=0,
                characters={},
                daily=datetime.now(),
                streak=0
            )
            await data.commit()

        return data

    def check_channel(self, ctx: Context) -> bool:
        if ctx.channel.id not in (913330644875104306, 913332335473205308, 913445987102654474) \
                and ctx.author.id != self.bot._owner_id:
            return False
        return True

    @commands.group(name='game', aliases=('g',), invoke_without_command=True, case_insensitive=True)
    async def base_game(self, ctx: Context):
        """Base command for all the `game` commands. To see the commands, please type `!help game`"""

        await ctx.send_help('game')

    @base_game.command(name='coins')
    async def game_coins(self, ctx: Context):
        """See how many coins you currently have.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx)
        em = disnake.Embed(
            color=utils.blurple,
            description=f'You currently have `{data.coins}` coins.'
        )
        em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
        em.set_thumbnail(url=ctx.author.display_avatar)
        if data.daily <= datetime.now():
            em.set_footer(text='You can claim your daily!')

        await ctx.reply(embed=em)

    @base_game.command(name='daily')
    async def game_daily(self, ctx: Context):
        """Get your daily coins.
        One streak is `100` coins, which gets multiplied by the amount of streaks you have accumulated. That means that a 10 day streak is `1000` extra coins.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx)
        if data.daily > datetime.now():
            em = disnake.Embed(
                title='Uh-oh',
                description='You cannot claim your daily yet! Please come back in '
                            f'`{utils.human_timedelta(data.daily, suffix=False)}`',
                color=utils.red
            )
            return await ctx.reply(embed=em)

        coins = 1000 + (data.streak * 100)
        data.coins += coins
        data.streak += 1
        data.daily = datetime.now() + relativedelta(days=1)
        await data.commit()
        em = disnake.Embed(
            title='Daily Claimed',
            description=f'You have successfully claimed your daily and got `{coins}` coins!',
            color=utils.green
        )
        em.set_footer(text=f'Current Streak: {data.streak}')

        await ctx.reply(embed=em)

    @base_game.command(name='characters', aliases=('chars',))
    async def game_characters(self, ctx: Context):
        """Take a look at the characters that you own.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx)
        if not data.characters:
            em = disnake.Embed(
                title='Uh-oh',
                description='You do not own any characters! See `!shop` to check all the available buyable characters.',
                color=utils.red
            )
            await ctx.reply(embed=em)

    @base_game.command(name='shop')
    async def game_shop(self, ctx: Context):
        """The shop from which you can buy characters with your coins.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        return await ctx.reply(
            'There have not been added any characters yet as this is still in development.'
        )


def setup(bot: Ukiyo):
    bot.add_cog(_Game(bot))
