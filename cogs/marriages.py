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
    @commands.max_concurrency(1, commands.BucketType.user)
    async def marry(self, ctx: Context, *, member: disnake.Member):
        """Marry the member if they want to and if you're/they're not taken by somebody else already.

        `member` **->** The member you wish to marry. You can either ping them, give their discord id, or just type in their username
        """

        if ctx.author == member:
            return await ctx.reply(f'{ctx.denial} You cannot marry yourself.')
        elif member.bot and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'{ctx.denial} You cannot marry bots.')

        data1: Marriage = await Marriage.get(ctx.author.id)
        if data1 and data1.married_to != 0:
            mem = ctx.ukiyo.get_member(data1.married_to)
            return await ctx.reply(f'{ctx.denial} You are already married to {mem.mention}')
        elif data1 and member.id in data1.adoptions:
            return await ctx.reply(
                f'{ctx.denial} You cannot marry the person that you adopted.'
            )

        data2: Marriage = await Marriage.get(member.id)
        if data2 and data2.married_to != 0:
            mem = ctx.ukiyo.get_member(data2.married_to)
            return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is already married to {mem.mention}')
        elif data2 and ctx.author.id in data2.adoptions:
            return await ctx.reply(
                f'{ctx.denial} You cannot marry the person that adopted you.'
            )

        view = utils.ConfirmView(ctx, f'{ctx.denial} {member.mention} Did not react in time.', member)
        view.message = msg = await ctx.send(f'{member.mention} do you want to marry {ctx.author.mention}?', view=view)
        await view.wait()
        if view.response is True:
            taken_role = ctx.ukiyo.get_role(913789939961954304)
            now = datetime.utcnow()

            if data1 is None:
                data1 = Marriage(
                    id=ctx.author.id,
                    married_to=0,
                    married_since=utils.FIRST_JANUARY_1970,
                    adoptions=[]
                )
                await data1.commit()

            if data2 is None:
                data2 = Marriage(
                    id=member.id,
                    married_to=0,
                    married_since=utils.FIRST_JANUARY_1970,
                    adoptions=[]
                )
                await data2.commit()

            data1.married_to = member.id
            data1.married_since = now
            for adoption in data2.adoptions:
                if adoption not in data1.adoptions:
                    data1.adoptions.append(adoption)
            await data1.commit()

            data2.married_to = ctx.author.id
            data2.married_since = now
            for adoption in data1.adoptions:
                if adoption not in data2.adoptions:
                    data2.adoptions.append(adoption)
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
            await utils.try_delete(msg)

        elif view.response is False:
            await ctx.send(f'`{member.display_name}` does not want to marry you. {ctx.author.mention} :pensive: :fist:')
            await utils.try_delete(msg)

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def divorce(self, ctx: Context):
        """Divorce the person you're married with in case you're married with anybody."""

        data: Marriage = await Marriage.get(ctx.author.id)

        if data is None or data.married_to == 0:
            return await ctx.reply(f'{ctx.denial} You are not married to anyone.')

        else:
            usr = ctx.ukiyo.get_member(data.married_to)

            view = utils.ConfirmView(ctx, f'{ctx.author.mention} Did not react in time.')
            view.message = msg = await ctx.reply(f'Are you sure you want to divorce {usr.mention}?', view=view)
            await view.wait()
            if view.response is True:
                single_role = ctx.ukiyo.get_role(913789939668385822)
                mem: Marriage = await Marriage.get(usr.id)
                await data.delete()
                await mem.delete()

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
        data: Marriage = await Marriage.get(member.id)
        if data is None or data.married_to == 0:
            if member == ctx.author:
                i = f'{ctx.denial} You\'re not married to anyone.'
                fn = ctx.reply
            else:
                i = f'{ctx.denial} {member.mention} is not married to anyone.'
                fn = ctx.better_reply
            return await fn(i)

        mem = ctx.ukiyo.get_member(data.married_to)
        em = disnake.Embed(title=f'Married to `{mem.display_name}`', colour=utils.blurple)
        if member == ctx.author:
            i = 'You\'re married to'
            fn = ctx.reply
        else:
            i = f'{member.mention} is married to'
            fn = ctx.better_reply
        em.description = f'{i} {mem.mention} ' \
                         f'since {utils.format_dt(data.married_since, "F")} ' \
                         f'(`{utils.human_timedelta(data.married_since, accuracy=6)}`)'
        await fn(embed=em)

    @commands.command(name='kiss')
    async def _kiss(self, ctx: Context, *, member: disnake.Member):
        """Kiss the person you are married with.

        `member` **->** The member you want to kiss. You can only kiss the person you are married with.

        If for some reason you don't know who you're married to, you are a complete jerk but luckily for you, there's the command `!marriedwho` which reminds you who you are married to, and for how long.
        """  # noqa

        data = await Marriage.get(ctx.author.id)
        if data is None or data.married_to == 0:
            return await ctx.reply(f'{ctx.denial} You must be married to {member.mention} in order to kiss them.')

        if member.id != data.married_to:
            mem = ctx.ukiyo.get_member(data.married_to)
            return await ctx.reply(
                f'{ctx.denial} You cannot kiss `{utils.format_name(member)}`!! You can only kiss {mem.mention}'
            )

        em = disnake.Embed(color=utils.red)
        em.set_image(url='https://cdn.discordapp.com/attachments/752148605753884792/754984869569888276/KIS.gif')
        await ctx.send(
            f'{ctx.author.mention} is giving you a hot kiss {member.mention} 🥺 💋',
            embed=em
        )

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def adopt(self, ctx: Context, *, member: disnake.Member):
        """Adopt someone.

        `member` **->** The member you want to adopt.
        """

        if member.id == ctx.author.id:
            return await ctx.reply(f'{ctx.denial} You cannot adopt yourself.')
        elif member.bot and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'{ctx.denial} You cannot adopt bots.')

        partner = False
        data1: Marriage = await Marriage.get(ctx.author.id)
        if data1 and len(data1.adoptions) > 7 and ctx.author.id != self.bot._owner_id:
            return await ctx.reply(f'{ctx.denial} You cannot adopt more than **7** people.')

        data2: Marriage = await Marriage.get(member.id)
        if data2 and ctx.author.id in data2.adoptions:
            return await ctx.reply(
                f'{ctx.denial} You cannot adopt the person that adopted you, what are you, dumb???'
            )
        elif data1 and member.id in data1.adoptions:
            return await ctx.reply(f'{ctx.denial} You already adopted that person.')
        else:
            filter2: list[Marriage] = await Marriage.find({'adoptions': member.id}).to_list(1)
            if len(filter2) == 1:
                mem = ctx.ukiyo.get_member(filter2[0].id)
                return await ctx.reply(f'{ctx.denial} `{utils.format_name(member)}` is already adopted by {mem.mention}')

        if data1 and data1.married_to != 0:
            mem = ctx.ukiyo.get_member(data1.married_to)
            view = utils.ConfirmView(ctx, react_user=mem)
            view.message = await ctx.send(
                f'{mem.mention} your partner wants to adopt {member.mention}. Do you agree?',
                view=view
            )
            await view.wait()
            if view.response is False:
                return await view.message.edit(
                    content=f'{ctx.author.mention} It seems like your partner did not want to adopt {member.mention}.'
                )
            else:
                partner = True

        view = utils.ConfirmView(ctx, react_user=member)
        view.message = await ctx.send(
            f'{member.mention} do you wish to be part of **{ctx.author.display_name}**\'s family?',
            view=view
        )
        await view.wait()
        if view.response is False:
            return await view.message.edit(
                content=f'{ctx.author.mention} It seems like {member.mention} does not want to be part of your family.'
            )
        else:
            await view.message.edit(
                content=f'{member.mention} You are now part of **{ctx.author.display_name}**\'s family.'
            )

        if partner is True:
            data2: Marriage = await Marriage.get(data1.married_to)
            data2.adoptions.append(member.id)
            await data2.commit()

        if data1 is None:
            data1 = Marriage(
                id=ctx.author.id,
                married_to=0,
                married_since=utils.FIRST_JANUARY_1970,
                adoptions=[]
            )
            await data1.commit()
        data1.adoptions.append(member.id)
        await data1.commit()

        await ctx.reply(f'You have adopted {member.mention} :heart: :tada:')

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def unadopt(self, ctx: Context, *, member: disnake.Member):
        """Unadopt a member.

        `member` **->** The member you want to not be adopted by you anymore.
        """

        data: Marriage = await Marriage.get(ctx.author.id)
        if data is None or len(data.adoptions) == 0:
            return await ctx.reply(f'You\'ve never adopted {member.mention}.')
        elif data.married_to != 0:
            mem = ctx.ukiyo.get_member(data.married_to)
            data2: Marriage = await Marriage.get(data.married_to)
            view = utils.ConfirmView(ctx, react_user=mem)
            view.message = await ctx.send(
                f'{mem.mention} your partner wants to adopt {member.mention}. Do you agree?',
                view=view
            )
            await view.wait()
            if view.response is False:
                return await view.message.edit(
                    content=f'{ctx.author.mention} It seems like your partner did not want to adopt {member.mention}.'
                )
            else:
                data2.adoptions.remove(member.id)
                await data2.commit()
        data.adoptions.remove(member.id)
        if len(data.adoptions) == 0 and data.married_to == 0:
            await data.delete()
        else:
            await data.commit()

        await ctx.reply(f'You have unadopted {member.mention}')

    @commands.command()
    async def runaway(self, ctx: Context):
        """Run away from your family. That means you will "unadopt" yourself."""

        data: Marriage = await Marriage.find({'adoptions': ctx.author.id}).to_list(2)
        if not data:
            return await ctx.reply(f'{ctx.denial} You are not adopted by anybody.')
        else:
            async for entry in Marriage.find({'adoptions': ctx.author.id}):
                entry: Marriage

                if entry.id == self.bot._owner_id:
                    await self.bot._owner.send(
                        f'{utils.format_name(ctx.author)}` Has tried to run away.',
                        view=utils.UrlButton('Jump!', ctx.message.jump_url)
                    )
                    return await ctx.reply(
                        'You cannot run away from my master. '
                        'He\'s been notified about your misbehaviour.'
                    )

                entry.adoptions.remove(ctx.author.id)
                await entry.commit()
                mem = ctx.ukiyo.get_member(entry.id)
                await mem.send(
                    f'`{utils.format_name(ctx.author)}` Has run away from your family. '
                    'They are no longer adopted by you.',
                    view=utils.UrlButton('Jump!', ctx.message.jump_url)
                )
        await ctx.reply(
            'You have run away from your family. '
            'You are not adopted anymore and your ex-step-parents have been notified about this.'
        )

    @commands.command()
    async def family(self, ctx: Context, *, member: disnake.Member = None):
        """See your family members. This basically shows you who you have adopted, and who you are married to.

        `member` **->** The member who's family you want to see. Defaults to you.
        """

        member = member or ctx.author
        if member.bot:
            if member.id in (783587403716624416, 787596672128909323, 913415084179611678):
                return await ctx.better_reply(
                    f'{member.mention}\'s family will always be {self.bot._owner.mention}',
                    allowed_mentions=disnake.AllowedMentions(users=False)
                )

        em = disnake.Embed(color=utils.blurple)
        em.set_author(name=f'{member.display_name}\'s family', icon_url=member.display_avatar)
        data: Marriage = await Marriage.get(member.id)
        _adopted_by: Marriage = await Marriage.find({'adoptions': member.id}).to_list(2)
        if data is None and len(_adopted_by) == 0:
            if member.id == ctx.author.id:
                return await ctx.reply('You don\'t have a family :frowning:')
            else:
                return await ctx.reply(f'{member.mention} doesn\'t have a family :frowning:')
        adopted_by = []
        for uid in _adopted_by:
            mem = ctx.ukiyo.get_member(uid.id)
            adopted_by.append(mem.mention)
        adopted_by = ' and '.join(adopted_by) if len(adopted_by) != 0 else 'No one.'

        married_to = 'No partner.'
        adoptions = []
        if data is not None:
            if data.married_to != 0:
                mem = ctx.ukiyo.get_member(data.married_to)
                married_since = utils.human_timedelta(data.married_since)
                married_to = f'{mem.mention} (married since `{married_since}`)'
            for adoption in data.adoptions:
                mem = ctx.ukiyo.get_member(adoption)
                adoptions.append(f'{mem.mention} (`{mem.display_name}`)')
        adoptions_count = len(adoptions)
        adoptions = '\n'.join(adoptions) if len(adoptions) != 0 else 'No adoptions.'

        em.add_field('Married To', married_to, inline=False)
        em.add_field(f'Adoptions ({adoptions_count})', adoptions, inline=False)
        em.add_field('Adopted By', adopted_by, inline=False)
        em.set_footer(text=f'Requested By: {utils.format_name(ctx.author)}')

        await ctx.better_reply(embed=em)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        entry = await Marriage.get(member.id)
        if entry:
            await entry.delete()
            mem = await Marriage.find_one({'married_to': member.id})
            await mem.delete()
        async for entry in Marriage.find({'adoptions': member.id}):
            entry.adoptions.remove(member.id)
            await entry.commit()


def setup(bot: Ukiyo):
    bot.add_cog(Marriages(bot))
