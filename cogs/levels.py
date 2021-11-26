import disnake
from disnake.ext import commands

import utils
from utils import Level, Context

from main import Ukiyo


class Levels(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def update_data(self, message: disnake.Message):
        if not message.author.bot:
            data: Level = await Level.find_one({'_id': message.author.id})
            if data is None:
                return await Level(id=message.author.id, xp=5, messages_count=1).commit()
            data.xp += 5
            data.messages_count += 1
            await data.commit()

    @commands.group(
        name='level', invoke_without_command=True, case_insensitive=True, ignore_extra=False, aliases=('rank',)
    )
    async def level_cmd(self, ctx: Context, *, member: disnake.Member = None):
        """Check your current level or somebody else's."""

        if ctx.channel.id in (913330644875104306, 913332335473205308, 913445987102654474):
            member = member or ctx.author
            if member.bot:
                return await ctx.reply('Bot\'s do not have levels!')
            data: Level = await Level.find_one({'_id': member.id})
            if data is None:
                return await ctx.reply('User not in the database!')

            total_xp = data.xp
            rank = 0
            rankings: list[Level] = await Level.find().sort('xp', -1).to_list(100000)
            for _rank in rankings:
                rank += 1
                if data.id == _rank.id:
                    break

            lvl = int(-0.5 + 0.02 * (25 * 25 + 50 * total_xp) ** 0.5)
            current_xp = 50 * (lvl - 1) * lvl
            needed_xp = int(200 * ((1 / 2) * lvl))
            percent = round(float(current_xp * 100 / needed_xp), 2)
            guild = self.bot.get_guild(913310006814859334)
            members_count = [m for m in guild.members if not m.bot]

            rank_card = await utils.create_rank_card(
                member, lvl, rank, members_count, current_xp, needed_xp, percent
            )
            await ctx.reply(file=rank_card)

    @level_cmd.command(name='set')
    async def level_set(self, ctx: Context, level: int, *, member: disnake.Member = None):
        """Set the level for somebody."""

        member = member or ctx.author
        if level <= 0:
            return await ctx.reply('Level cannot be less or equal than `0`')

        total_xp = 50 * (level - 1) * 335
        data: Level = await Level.find_one({'_id': member.id})
        if data is not None:
            data.xp = total_xp
            await data.commit()
            return await ctx.reply(f'Successfully set `{member}` to level **{level}**')
        await ctx.reply('Member not in the database.')

    @level_cmd.command(name='leaderboard', aliases=('lb', 'top',))
    async def level_top(self, ctx: Context):
        """See the top people with the highest levels."""

        if ctx.channel.id in (913330644875104306, 913332335473205308, 913445987102654474):
            entries = []
            index = 0
            guild = self.bot.get_guild(913310006814859334)
            top_3_emojis = {1: '🥇', 2: '🥈', 3: '🥉'}
            async for res in Level.find().sort('xp', -1):
                res: Level
                index += 1
                lvl = int(-0.5 + 0.02 * (25 * 25 + 50 * res.xp) ** 0.5)
                user = guild.get_member(res.id)
                if index in (1, 2, 3):
                    place = top_3_emojis[index]
                else:
                    place = f'`#{index:,}`'

                if user == ctx.author:
                    to_append = (f"**{place} {user.name} (YOU)**", f"Level: `{lvl}`\nTotal XP: `{res.xp:,}`")
                    entries.append(to_append)
                else:
                    to_append = (f"{place} {user.name}", f"Level: `{lvl}`\nTotal XP: `{res.xp:,}`")
                    entries.append(to_append)

            source = utils.FieldPageSource(entries, per_page=10)
            source.embed.title = 'Rank Leaderboard'
            pages = utils.RoboPages(source, ctx=ctx)
            await pages.start()


def setup(bot: Ukiyo):
    bot.add_cog(Levels(bot))
