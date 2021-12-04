from datetime import datetime

import disnake
from disnake.ext import commands

import utils
from utils import Context, Marriage

from main import Ukiyo


class Marriages(commands.Cog):
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
            return await ctx.reply(f'> {ctx.disagree} You cannot marry yourself.')
        elif member.bot:
            return await ctx.reply(f'> {ctx.disagree} You cannot marry bots.')
        data: Marriage = await Marriage.find_one({'_id': ctx.author.id})
        if data is not None:
            mem = guild.get_member(member.id)
            return await ctx.reply(f'> {ctx.disagree} You are already married to {mem.mention}')
        data: Marriage = await Marriage.find_one({'_id': member.id})
        if data is not None:
            mem = guild.get_member(data.married_to)
            return await ctx.reply(f'> {ctx.disagree} `{member}` is already married to {mem.mention}')

        view = utils.ConfirmView(ctx, f'> {ctx.disagree} {member.mention} Did not react in time.', member)
        view.message = msg = await ctx.send(f'{member.mention} do you want to marry {ctx.author.mention}?', view=view)
        await view.wait()
        if view.response is True:
            taken_role = guild.get_role(913789939961954304)
            now = datetime.utcnow()
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

            new_roles_1 = [r for r in ctx.author.roles if not r.id == 913789939668385822] + [taken_role]
            new_roles_2 = [r for r in member.roles if not r.id == 913789939668385822] + [taken_role]
            await ctx.author.edit(roles=new_roles_1)
            await member.edit(roles=new_roles_2)
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
            return await ctx.send(f'> {ctx.disagree} You are not married to anyone.')

        else:
            guild = self.bot.get_guild(913310006814859334)
            usr = guild.get_member(data.married_to)

            view = utils.ConfirmView(ctx, f'{ctx.author.mention} Did not react in time.')
            view.message = msg = await ctx.send(f'Are you sure you want to divorce {usr.mention}?', view=view)
            await view.wait()
            if view.response is True:
                single_role = guild.get_role(913789939668385822)
                mem: Marriage = await Marriage.find_one({'_id': usr.id})
                await data.delete()
                await mem.delete()

                new_roles_1 = [r for r in ctx.author.roles if not r.id == 913789939961954304] + [single_role]
                new_roles_2 = [r for r in usr.roles if not r.id == 913789939961954304] + [single_role]
                await ctx.author.edit(roles=new_roles_1)
                await usr.edit(roles=new_roles_2)

                e = f'You divorced {usr.mention} that you have been married ' \
                    f'since {utils.format_dt(data.married_since, "F")} ' \
                    f'(`{utils.human_timedelta(data.married_since)}`)'
                return await msg.edit(content=e, view=view)

            elif view.response is False:
                e = f'You did not divorce {usr.mention}'
                return await msg.edit(content=e, view=view)

    @commands.command()
    async def marriedwho(self, ctx: Context, *, member: disnake.Member = None):
        """See who, the date and how much it's been since the member/you married their/your partner if they/you have one."""

        member = member or ctx.author
        data: Marriage = await Marriage.find_one({'_id': member.id})
        if data is None:
            if member == ctx.author:
                i = f'> {ctx.disagree} You\'re not married to anyone.'
            else:
                i = f'> {ctx.disagree} {member.mention} is not married to anyone.'
            return await ctx.reply(i)
        guild = self.bot.get_guild(913310006814859334)
        mem = guild.get_member(data.married_to)
        em = disnake.Embed(title=f'Married to {mem.display_name}', colour=utils.blurple)
        if member == ctx.author:
            i = 'You\'re married to'
        else:
            i = f'{member.mention} is married to'
        em.description = f'{i} {mem.mention} ' \
                         f'since {utils.format_dt(data.married_since, "F")} ' \
                         f'(`{utils.human_timedelta(data.married_since)}`)'
        await ctx.reply(embed=em)

    @commands.command(name='kiss')
    async def _kiss(self, ctx: Context, *, member: disnake.Member):
        """Kiss the person you are married with."""

        data: Marriage = await Marriage.find_one({'_id': ctx.author.id})
        if data is None:
            return await ctx.reply(f'You must be married to {member.mention} in order to kiss them.')

        if member.id != data.married_to:
            mem = self.bot.get_user(data.married_to)
            return await ctx.reply(f'You cannot kiss `{member}`!! You can only kiss {mem.mention}')

        em = disnake.Embed(color=utils.red)
        em.set_image(url='https://cdn.discordapp.com/attachments/752148605753884792/754984869569888276/KIS.gif')
        await ctx.send(
            f'{ctx.author.mention} is giving you a hot kiss {member.mention} 🥺 💋',
            embed=em
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data = await Marriage.find_one({'_id': member.id})
        if data:
            await data.delete()
            mem = await Marriage.find_one({'married_to': member.id})
            await mem.delete()


def setup(bot: Ukiyo):
    bot.add_cog(Marriages(bot))
