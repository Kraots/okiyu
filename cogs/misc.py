import time

import disnake
from disnake.ext import commands

import utils
from utils import Context, Rules

from main import Ukiyo

SERVER_AD = """
☞ Ukiyo ☜
✯ Looking for a great partner or friendship? This is the perfect server!! ✯

⇨ This server:
➢ Amazing owner, admins and mods ☺︎
➢ Exclusive bot ☻︎
➢ Roles and intros ☺︎
➢ Possible relationships ☻︎
➢ An active and fun server ☺︎
➢ Exclusive emotes ☻︎
➢ And over all an inclusive server for everyone ☺︎


☀︎ Link: https://discord.gg/fQ6Nb4ac9x ☀︎
"""


class Misc(commands.Cog):
    """Miscellaneous commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '🔧'

    @commands.command()
    async def ping(self, ctx: Context):
        """See the bot's ping."""

        ping = disnake.Embed(title="Pong!", description="_Pinging..._", color=utils.blurple)
        start = time.time() * 1000
        msg = await ctx.send(embed=ping)
        end = time.time() * 1000
        ping = disnake.Embed(
            title="Pong!",
            description=f"Websocket Latency: `{(round(self.bot.latency * 1000, 2))}ms`"
            f"\nBot Latency: `{int(round(end-start, 0))}ms`"
            f"\nResponse Time: `{(msg.created_at - ctx.message.created_at).total_seconds()/1000}` ms",
            color=utils.blurple
        )
        ping.set_footer(text=f"Online for {utils.human_timedelta(dt=self.bot.uptime, suffix=False)}")
        await msg.edit(embed=ping)

    @commands.command()
    async def uptime(self, ctx: Context):
        """See how long the bot has been online for."""

        uptime = disnake.Embed(
            description=f"Bot has been online since {utils.format_dt(self.bot.uptime, 'F')} "
                        f"(`{utils.human_timedelta(dt=self.bot.uptime, suffix=False)}`)",
            color=utils.blurple
        )
        uptime.set_footer(text=f'Bot made by: {self.bot._owner}')
        await ctx.send(embed=uptime)

    @commands.command(name='invite', aliases=('inv',))
    async def _invite(self, ctx: Context):
        """Sends an invite that never expires."""

        await ctx.send('https://discord.gg/fQ6Nb4ac9x')

    @commands.command(aliases=('ad',))
    async def serverad(self, ctx: Context):
        """See the server's ad."""

        await ctx.message.delete()
        ad = disnake.Embed(color=utils.blurple, title='Here\'s the ad to the server:', description=SERVER_AD)
        ad.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.display_avatar)

        await ctx.send(embed=ad, reference=ctx.replied_reference)

    @commands.group(
        name='rules', invoke_without_command=True, case_insensitive=True, ignore_extra=False, aliases=('rule',)
    )
    async def server_rules(self, ctx: Context, *, rule: int = None):
        """Sends the server's rules. If ``rule`` is given, it will only send that rule."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'> {ctx.disagree} There are currently no rules set. Please contact an admin about this!')
        em = disnake.Embed(title='Rules', color=utils.blurple)

        if rule is None:
            for index, rule in enumerate(rules.rules):
                if em.description == disnake.embeds.EmptyEmbed:
                    em.description = f'`{index + 1}.` {rule}'
                else:
                    em.description += f'\n\n`{index + 1}.` {rule}'
        else:
            if rule <= 0:
                return await ctx.reply(f'> {ctx.disagree} Rule cannot be equal or less than `0`')
            try:
                _rule = rules.rules[rule - 1]
                em.description = f'`{rule}.` {_rule}'
            except IndexError:
                return await ctx.reply(f'> {ctx.disagree} Rule does not exist!')

        await ctx.send(embed=em, reference=ctx.replied_reference)

    @server_rules.command(name='add')
    @utils.is_admin()
    async def server_rules_add(self, ctx: Context, *, rule: str):
        """Adds a rule to the server's rules."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            await Rules(
                id=self.bot._owner_id,
                rules=[rule]
            ).commit()
        else:
            rules.rules += [rule]
            await rules.commit()

        await ctx.reply(f'> 👌 `{rule}` successfully **added** to the rules.')

    @server_rules.command(name='remove', aliases=('delete',))
    @utils.is_admin()
    async def server_rules_remove(self, ctx: Context, *, rule: int):
        """Removes a rule from the server's rules by its number."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'> {ctx.disagree} There are currently no rules set.')
        else:
            if rule <= 0:
                return await ctx.reply(f'> {ctx.disagree} Rule cannot be equal or less than `0`')
            try:
                rules.rules.pop(rule - 1)
            except IndexError:
                return await ctx.reply(f'> {ctx.disagree} Rule does not exist!')
            await rules.commit()

        await ctx.reply(f'> 👌 `{rule}` successfully **removed** to the rules.')

    @server_rules.command(name='clear')
    @utils.is_owner()
    async def server_rules_clear(self, ctx: Context):
        """Deletes all the rules."""

        rules: Rules = await Rules.find_one({'_id': self.bot._owner_id})
        if rules is None:
            return await ctx.reply(f'> {ctx.disagree} There are currently no rules set.')
        else:
            await rules.delete()

        await ctx.reply('> 👌 successfully **cleared** to the rules.')

    @commands.group(
        name='nick', invoke_without_command=True, case_insensitive=True, ignore_extra=False, aliases=('nickname',)
    )
    async def change_nick(self, ctx: Context, *, new_nickname: str):
        """Change your nickname to your desired one."""

        res = await utils.check_username(self.bot, word=new_nickname)
        if res is True:
            return await ctx.reply(f'> {ctx.disagree} That nickname is not pingable or is too short!')
        await ctx.author.edit(nick=new_nickname)
        await ctx.reply(f'I have changed your nickname to `{new_nickname}`')

    @change_nick.command(name='reset', aliases=('remove',))
    async def remove_nick(self, ctx: Context):
        """Removes your nickname."""

        res = await utils.check_username(self.bot, word=ctx.author.display_name)
        if res is True:
            return await ctx.reply(f'> {ctx.disagree} Cannot remove your nickname because your username is unpingable or is too short.')
        await ctx.author.edit(nick=None)
        await ctx.reply('I have removed your nickname.')

    @commands.command(name='avatar', aliases=('av',))
    async def _av(self, ctx: Context, *, member: disnake.Member = None):
        """Check the avatar ``member`` has."""

        member = member or ctx.author
        em = disnake.Embed(colour=utils.blurple, title=f'`{member.display_name}`\'s avatar')
        em.set_image(url=member.display_avatar)
        em.set_footer(text=f'Requested By: {ctx.author}')
        await ctx.reply(embed=em)

    @commands.command()
    async def created(self, ctx: Context, *, member: disnake.Member = None):
        """Check the date when the ``member`` created their account."""

        member = member or ctx.author
        em = disnake.Embed(
            colour=utils.blurple,
            title='Creation Date',
            description=f'{member.mention} created their account '
                        f'on {utils.format_dt(member.created_at, "F")} '
                        f'(`{utils.human_timedelta(member.created_at)}`)'
        )
        await ctx.reply(embed=em)

    @commands.command()
    async def joined(self, ctx: Context, *, member: disnake.Member = None):
        """Check the date when the ``member`` joined the server."""

        member = member or ctx.author
        em = disnake.Embed(
            colour=utils.blurple,
            title='Join Date',
            description=f'{member.mention} joined the server '
                        f'on {utils.format_dt(member.joined_at, "F")} '
                        f'(`{utils.human_timedelta(member.joined_at)}`)'
        )
        await ctx.reply(embed=em)


def setup(bot: Ukiyo):
    bot.add_cog(Misc(bot))
