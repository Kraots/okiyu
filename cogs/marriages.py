from datetime import datetime

import disnake
from disnake.ext import commands

import utils
from utils import Context, Marriage

from main import Ukiyo


class Marriages(commands.Bot):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '❤️'

    @commands.command()
    async def marry(self, ctx: Context, *, member: disnake.Member):
        """Marry the member if they want to and if you're/they're not taken by somebody else already."""

        guild = self.bot.get_guild(913310006814859334)
        if ctx.author == member:
            return await ctx.reply('You cannot marry yourself.')
        elif member.bot:
            return await ctx.reply('You cannot marry bots.')
        data: Marriage = await Marriage.find_one({'_id': ctx.author.id})
        if data is not None:
            mem = guild.get_member(member.id)
            return await ctx.reply(f'You are already married to {mem.mention}')
        data: Marriage = await Marriage.find_one({'_id': member.id})
        if data is not None:
            mem = guild.get_member(data.married_to)
            return await ctx.reply(f'`{member}` is already married to {mem.mention}')

        view = utils.ConfirmView(ctx, f'{member.mention} Did not react in time.', member)
        view.message = msg = await ctx.send(f'{member.mention} do you want to marry {ctx.author.mention}?', view=view)
        await view.wait()
        if view.response is True:
            now = datetime.datetime.utcnow()
            await Marriage(
                id=ctx.author.id,
                married_to=member.id,
                married_since=now
            ).commit()
            await Marriage(
                id=member.id,
                married_to=ctx.author.id,
                married_since=now
            ).commit()

            await ctx.send(f'`{ctx.author.display_name}` married `{member.display_name}`!!! :heart: :tada: :tada:')
            await msg.delete()

        elif view.response is False:
            await ctx.send(f'`{member.display_name}` does not want to marry you. {ctx.author.mention} :pensive: :fist:')
            await msg.delete()

    @commands.command()
    async def divorce(self, ctx: Context):
        """Divorce the person you're married with in case you're married with anybody."""

        data: Marriage = await Marriage.find_one({'_id': ctx.author.id})

        if data is None:
            return await ctx.send('You are not married to anyone.')

        else:
            guild = self.bot.get_guild(913310006814859334)
            usr = guild.get_member(data.married_to)

            view = self.bot.confirm_view(ctx, f'{ctx.author.mention} Did not react in time.')
            view.message = msg = await ctx.send(f'Are you sure you want to divorce {usr.mention}?', view=view)
            await view.wait()
            if view.response is True:
                mem: Marriage = await Marriage.find_one({'_id': usr.id})
                await data.delete()
                await mem.delete()

                e = f'You divorced {usr.mention} :cry:'
                return await msg.edit(content=e, view=view)

            elif view.response is False:
                e = 'You did not divorce that person :D'
                return await msg.edit(content=e, view=view)

    @commands.command()
    async def marriedsince(self, ctx: Context):
        """See the date and how much it's been since you married your partner if you have one."""

        data: Marriage = await Marriage.find_one({'_id': ctx.author.id})
        if data is None:
            return await ctx.reply('You are not married to anyone.')
        guild = self.bot.get_guild(913310006814859334)
        mem = guild.get_member(data.married_to)
        em = disnake.Embed(title=f'Married to {mem.display_name}')
        em.description = f'You\'re married to {mem.mention} '\
                         f'since {utils.format_dt(data.married_since, "F")} ' \
                         f'(`{utils.human_timedelta(data.married_since)}`)'
        await ctx.reply(embed=em)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data = await Marriage.find_one({'_id': member.id})
        if data:
            await data.delete()
            mem = await Marriage.find_one({'married_to': member.id})
            await mem.delete()


def setup(bot: Ukiyo):
    bot.add_cog(Marriages(bot))
