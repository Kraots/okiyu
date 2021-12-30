from datetime import datetime

import disnake
from disnake.ext import commands

import utils
from utils import Context, Marriage

from main import Ukiyo


class Marriages(commands.Cog):
    """Marriage commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '❤️'

    @commands.command()
    @utils.lock()
    async def marry(self, ctx: Context, *, member: disnake.Member):
        """Marry the member if they want to and if you're/they're not taken by somebody else already.

        `member` **->** The member you wish to marry. You can either ping them, give their discord id, or just type in their username
        """

        guild = self.bot.get_guild(913310006814859334)
        if ctx.author == member:
            return await ctx.reply(f'{ctx.denial} You cannot marry yourself.')
        elif member.bot:
            return await ctx.reply(f'{ctx.denial} You cannot marry bots.')

        data1: Marriage = await Marriage.find_one({'_id': ctx.author.id})
        if data1 is not None:
            if data1.married_to != 0:
                mem = guild.get_member(data1.married_to)
                return await ctx.reply(f'{ctx.denial} You are already married to {mem.mention}')
            elif member.id in data1.adoptions:
                return await ctx.reply(
                    f'{ctx.denial} You cannot marry the person that you adopted.'
                )
        else:
            data1 = Marriage(id=ctx.author.id)

        data2: Marriage = await Marriage.find_one({'_id': member.id})
        if data2 is not None:
            if data2.married_to != 0:
                mem = guild.get_member(data2.married_to)
                return await ctx.reply(f'{ctx.denial} `{member}` is already married to {mem.mention}')
            elif ctx.author.id in data2.adoptions:
                return await ctx.reply(
                    f'{ctx.denial} You cannot marry the person that adopted you.'
                )
        else:
            data2 = Marriage(id=member.id)

        view = utils.ConfirmView(ctx, f'{ctx.denial} {member.mention} Did not react in time.', member)
        view.message = msg = await ctx.send(f'{member.mention} do you want to marry {ctx.author.mention}?', view=view)
        await view.wait()
        if view.response is True:
            taken_role = guild.get_role(913789939961954304)
            now = datetime.utcnow()

            data1.married_to = member.id
            data1.married_since = now
            await data1.commit()

            data2.married_to = ctx.author.id
            data2.married_since = now
            await data2.commit()

            new_roles_1 = [r for r in ctx.author.roles if not r.id == 913789939668385822] + [taken_role]
            new_roles_2 = [r for r in member.roles if not r.id == 913789939668385822] + [taken_role]
            try:
                await ctx.author.edit(roles=new_roles_1)
            except disnake.HTTPException:
                pass
            try:
                await member.edit(roles=new_roles_2)
            except disnake.HTTPException:
                pass
            await ctx.send(f'`{ctx.author.display_name}` married `{member.display_name}`!!! :heart: :tada: :tada:')
            await msg.delete()

        elif view.response is False:
            await ctx.send(f'`{member.display_name}` does not want to marry you. {ctx.author.mention} :pensive: :fist:')
            await msg.delete()

    @commands.command()
    @utils.lock()
    async def divorce(self, ctx: Context):
        """Divorce the person you're married with in case you're married with anybody."""

        data: Marriage = await Marriage.find_one({'_id': ctx.author.id})

        if data.married_to == 0:
            return await ctx.reply(f'{ctx.denial} You are not married to anyone.')

        else:
            guild = self.bot.get_guild(913310006814859334)
            usr = guild.get_member(data.married_to)

            view = utils.ConfirmView(ctx, f'{ctx.author.mention} Did not react in time.')
            view.message = msg = await ctx.reply(f'Are you sure you want to divorce {usr.mention}?', view=view)
            await view.wait()
            if view.response is True:
                single_role = guild.get_role(913789939668385822)
                mem: Marriage = await Marriage.find_one({'_id': usr.id})
                if len(data.adoptions) == 0:
                    await data.delete()
                else:
                    data.married_to = 0
                    data.married_since = utils.FIRST_JANUARY_1970
                    await data.commit()

                if len(mem.adoptions) == 0:
                    await data.delete()
                else:
                    mem.married_to = 0
                    mem.married_since = utils.FIRST_JANUARY_1970
                    await mem.commit()

                new_roles_1 = [r for r in ctx.author.roles if not r.id == 913789939961954304] + [single_role]
                new_roles_2 = [r for r in usr.roles if not r.id == 913789939961954304] + [single_role]
                try:
                    await ctx.author.edit(roles=new_roles_1)
                except disnake.HTTPException:
                    pass
                try:
                    await usr.edit(roles=new_roles_2)
                except disnake.HTTPException:
                    pass

                e = f'You divorced {usr.mention} that you have been married ' \
                    f'since {utils.format_dt(data.married_since, "F")} ' \
                    f'(`{utils.human_timedelta(data.married_since)}`)'
                return await msg.edit(content=e, view=view)

            elif view.response is False:
                e = f'You did not divorce {usr.mention}'
                return await msg.edit(content=e, view=view)

    @commands.command()
    async def marriedwho(self, ctx: Context, *, member: disnake.Member = None):
        """See who, who, the date and how much it's been since the member married their partner if they have one.

        `member` **->** The member you want to see who they are married with. If you want to see who you married, you can ignore this.
        """

        member = member or ctx.author
        data: Marriage = await Marriage.find_one({'_id': member.id})
        if data.married_to == 0:
            if member == ctx.author:
                i = f'{ctx.denial} You\'re not married to anyone.'
                fn = ctx.reply
            else:
                i = f'{ctx.denial} {member.mention} is not married to anyone.'
                fn = ctx.better_reply
            return await fn(i)

        guild = self.bot.get_guild(913310006814859334)
        mem = guild.get_member(data.married_to)
        em = disnake.Embed(title=f'Married to `{mem.display_name}`', colour=utils.blurple)
        if member == ctx.author:
            i = 'You\'re married to'
            fn = ctx.reply
        else:
            i = f'{member.mention} is married to'
            fn = ctx.better_reply
        em.description = f'{i} {mem.mention} ' \
                         f'since {utils.format_dt(data.married_since, "F")} ' \
                         f'(`{utils.human_timedelta(data.married_since)}`)'
        await fn(embed=em)

    @commands.command(name='kiss')
    async def _kiss(self, ctx: Context, *, member: disnake.Member):
        """Kiss the person you are married with.

        `member` **->** The member you want to kiss. You can only kiss the person you are married with.

        If for some reason you don't know who you're married to, you are a complete jerk but luckily for you, there's the command `!marriedwho` which reminds you who you are married to, and for how long.
        """  # noqa

        data: Marriage = await Marriage.find_one({'_id': ctx.author.id})
        if data.married_to == 0:
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
