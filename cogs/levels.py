import disnake
from disnake.ext import commands

import utils
from utils import Level, Context

from main import Ukiyo


class Levels(commands.Cog):
    """Level and message related commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> disnake.PartialEmoji:
        return disnake.PartialEmoji(name='super_mario_green_shroom', id=913886905182064690)

    @commands.Cog.listener('on_message')
    async def update_data(self, message: disnake.Message):
        if not message.author.bot and message.guild:
            data: Level = await Level.get(message.author.id)
            if data is None:
                return await Level(id=message.author.id, xp=5, messages_count=1).commit()
            if message.author.id == self.bot._owner_id:
                data.xp += 30
            else:
                if message.channel.id not in (913330644875104306, 913335107564208158):
                    data.xp += 5
            data.messages_count += 1
            await data.commit()

    @commands.group(
        name='level', invoke_without_command=True, case_insensitive=True, aliases=('rank',)
    )
    async def level_cmd(self, ctx: Context, *, member: disnake.Member = None):
        """Check your current level or somebody else's.

        `member` **->** The member you want to see the level of. If you want to see your own, you can ignore this since it defaults to yourself.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await ctx.check_channel() is False:
            return

        member = member or ctx.author
        if member.bot:
            return await ctx.better_reply(f'{ctx.denial} Bot\'s do not have levels!')
        data: Level = await Level.get(member.id)
        if data is None:
            return await ctx.better_reply(f'{ctx.denial} User not in the database!')

        rank = 0
        rankings: list[Level] = await Level.find().sort('xp', -1).to_list(100000)
        for _rank in rankings:
            rank += 1
            if data.id == _rank.id:
                break

        lvl = 0
        xp = data.xp
        while True:
            if xp < ((50 * (lvl**2)) + (50 * (lvl - 1))):
                break
            lvl += 1
        xp -= ((50 * ((lvl - 1)**2)) + (50 * (lvl - 1)))
        if xp < 0:
            lvl = lvl - 1
            xp = data.xp
            xp -= ((50 * ((lvl - 1)**2)) + (50 * (lvl - 1)))
        if str(xp).endswith(".0"):
            x = str(xp).replace(".0", "")
            x = int(x)
        else:
            x = int(xp)

        current_xp = x
        needed_xp = int(200 * ((1 / 2) * lvl))
        percent = round(float(current_xp * 100 / needed_xp), 2)
        members_count = len([m for m in ctx.ukiyo.members if not m.bot])

        rank_card = await utils.create_rank_card(
            member, lvl, rank, members_count, current_xp, needed_xp, percent
        )
        await ctx.better_reply(file=rank_card)

    @level_cmd.command(name='set')
    @utils.is_owner()
    async def level_set(self, ctx: Context, level: int, *, member: disnake.Member = None):
        """Set the level for somebody.

        `level` **->** The level to set.
        `member` **->** The member to set the level for.
        """

        member = member or ctx.author
        if await ctx.check_perms(member) is False:
            return

        if level < 0:
            return await ctx.reply(f'{ctx.denial} Level cannot be less than `0`')

        xp = ((50 * ((level - 1)**2)) + (50 * (level - 1)))
        data: Level = await Level.get(member.id)
        if data is not None:
            data.xp = xp
            await data.commit()
            return await ctx.reply(f'Successfully set `{member}` to level **{level}**')
        await ctx.reply(f'{ctx.denial} Member not in the database.')

    @level_cmd.command(name='leaderboard', aliases=('lb', 'top',))
    async def level_top(self, ctx: Context):
        """See the top people with the highest levels.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await ctx.check_channel() is False:
            return

        entries = []
        index = 0
        top_3_emojis = {1: '🥇', 2: '🥈', 3: '🥉'}
        async for entry in Level.find().sort('xp', -1):
            entry: Level

            index += 1
            lvl = 0
            while True:
                if entry.xp < ((50 * (lvl**2)) + (50 * (lvl - 1))):
                    break
                lvl += 1
            user = ctx.ukiyo.get_member(entry.id)
            if index in (1, 2, 3):
                place = top_3_emojis[index]
            else:
                place = f'`#{index:,}`'

            if user == ctx.author:
                to_append = (f"**{place} {user.name} (YOU)**", f"Level: `{lvl}`\nTotal XP: `{entry.xp:,}`")
                entries.append(to_append)
            else:
                to_append = (f"{place} {user.name}", f"Level: `{lvl}`\nTotal XP: `{entry.xp:,}`")
                entries.append(to_append)

        source = utils.FieldPageSource(entries, per_page=10)
        source.embed.title = 'Rank Leaderboard'
        pages = utils.RoboPages(source, ctx=ctx)
        await pages.start()

    @commands.group(
        name='messages', invoke_without_command=True, case_insensitive=True, aliases=('msg',)
    )
    async def _msgs(self, ctx: Context, *, member: disnake.Member = None):
        """Check yours or somebody else's total messages.

        `member` **->** The member you want to see the total messages of. If you want to see your own, you can ignore this since it defaults to yourself.
        """

        member = member or ctx.author

        user_db: Level = await Level.get(member.id)
        if user_db is None:
            return await ctx.better_reply(f'`{member.display_name}` sent no messages.')
        rank = 0
        async for entry in Level.find().sort('messages_count', -1):
            rank += 1
            if entry.id == user_db.id:
                break
        em = disnake.Embed(color=utils.blurple)
        em.set_author(name=f'{member.display_name}\'s message stats', icon_url=member.display_avatar)
        em.add_field(name='Total Messages', value=f"`{user_db.messages_count:,}`")
        em.add_field(name='Rank', value=f"`#{rank:,}`")
        em.set_footer(text=f'Requested by: {ctx.author}')
        await ctx.better_reply(embed=em)

    @_msgs.command(name='leaderboard', aliases=('top', 'lb',))
    async def msg_top(self, ctx: Context):
        """See a top of most active users."""

        index = 0
        data = []
        top_3_emojis = {1: '🥇', 2: '🥈', 3: '🥉'}

        for entry in Level.find().sorted('messages_count', -1):
            entry: Level

            if entry.messages_count != 0:
                index += 1
                mem = ctx.ukiyo.get_member(entry.id)
                if index in (1, 2, 3):
                    place = top_3_emojis[index]
                else:
                    place = f'`#{index:,}`'
                if mem == ctx.author:
                    to_append = (f'**{place} {mem.name} (YOU)**', f'**{entry.messages_count:,}** messages')
                    data.append(to_append)
                else:
                    to_append = (f'{place} {mem.name}', f'**{entry.messages_count:,}** messages')
                    data.append(to_append)
        source = utils.FieldPageSource(data, per_page=10)
        source.embed.title = 'Top Most Active Users'
        pages = utils.RoboPages(source, ctx=ctx)
        await pages.start()

    @_msgs.command(name='add')
    @utils.is_admin()
    async def msg_add(self, ctx: Context, member: disnake.Member, *, amount: str):
        """Add a certain amount of messages for the member.

        `member` **->** The member to add the amount of messages messages to.
        `amount` **->** The amount of messages to add.
        """

        if await ctx.check_perms(member) is False:
            return
        usr_db: Level = await Level.get(member.id)
        if usr_db is None:
            return await ctx.reply(f'{ctx.denial} User not in the database.')

        try:
            amount = utils.format_amount(amount)
            amount = int(amount)
        except ValueError:
            return await ctx.reply(f'{ctx.denial} The amount must be an integer.')

        usr_db.messages_count += amount
        await usr_db.commit()
        await ctx.send(content=f'Added `{amount:,}` messages to {member.mention}')

    @_msgs.command(name='set')
    @utils.is_admin()
    async def msg_set(self, ctx: Context, member: disnake.Member, *, amount: str):
        """Set the amount of messages for the member.

        `member` **->** The member to set the amount of messages messages to.
        `amount` **->** The amount of messages to set.
        """

        if await ctx.check_perms(member) is False:
            return

        usr_db: Level = await Level.get(member.id)
        if usr_db is None:
            return await ctx.reply(f'{ctx.denial} User not in the database.')

        try:
            amount = utils.format_amount(amount)
            amount = int(amount)
        except ValueError:
            return await ctx.reply(f'{ctx.denial} The amount must be an integer.')

        usr_db.messages_count = amount
        await usr_db.commit()
        await ctx.send(content=f'Set the amount of messages for {member.mention} to `{amount:,}` messages.')

    @_msgs.command(name='reset')
    @utils.is_admin()
    async def msg_reset(self, ctx: Context, member: disnake.Member):
        """Reset the amount of total messages for the member.

        `member` **->** The member for who to reset the total messages count for.
        """

        if await ctx.check_perms(member) is False:
            return

        usr_db: Level = await Level.get(member.id)
        if usr_db is None:
            return await ctx.reply(f'{ctx.denial} User not in the database.')

        view = utils.ConfirmView(ctx, f"{ctx.author.mention} Did not react in time.")
        view.message = msg = await ctx.send(
            f"Are you sure you want to reset the total message count for member {member.mention}?",
            view=view
        )
        await view.wait()
        if view.response is True:
            usr_db.messages_count = 0
            await usr_db.commit()
            return await msg.edit(
                content=f'The total message count for member **{member}** has been reset successfully.',
            )

        elif view.response is False:
            return await msg.edit(
                content=f"Command to reset the message count for user `{member}` has been cancelled.",
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data = await Level.get(member.id)
        if data:
            await data.delete()


def setup(bot: Ukiyo):
    bot.add_cog(Levels(bot))
