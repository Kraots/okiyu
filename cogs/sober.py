from asyncio import TimeoutError
from datetime import datetime

import disnake
from disnake.ext import commands

import utils
from utils import (
    Context,
    Sober
)

from main import Ukiyo


class SoberApp(commands.Cog, name='Sober App'):
    """Commands for the sober app to keep track of your time being sober of a certain something."""

    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @commands.group(
        name='sober',
        invoke_without_command=True,
        case_insensitive=True,
        hidden=True,
        aliases=('sobers',)
    )
    async def base_sober(self, ctx: Context):
        """Base command for all sober commands."""

        await ctx.send_help('Sober App')

    @base_sober.command(name='add')
    async def sober_add(self, ctx: Context):
        """Add a new sober to keep track of."""

        entries: list[Sober] = await Sober.find({'user_id': ctx.author.id}).to_list(20)
        if len(entries) == 20:
            return await ctx.reply(f'{ctx.denial} You can only have a total of **20** sober to keep track of.')

        check = lambda m: m.author.id == ctx.author.id and \
            m.channel.id == ctx.channel.id and m.content != ''  # noqa
        await ctx.reply('Please send a short title related to what this sober is about (max. 20 characters)')
        try:
            msg: disnake.Message = await self.bot.wait_for('message', check=check, timeout=60.0)
        except TimeoutError:
            return await ctx.reply(f'{ctx.denial} You didn\'t give the short title. Aborting.')
        short_title = msg.short_title

        try:
            await msg.reply('Please give a detailed(optional) description of what this sober is about.')
            msg: disnake.Message = await self.bot.wait_for('message', check=check, timeout=180.0)
        except TimeoutError:
            return await ctx.reply(f'{ctx.denial} You didn\'t give the description. Aborting.')
        description = msg.content

        try:
            await msg.reply(
                'When was the last time you have done this act? '
                'This is used to determine your current progress.\n\n'
                'The format in which this must be is **DD/MM/YYYY**\n'
                '**Example:**\n\u2800`24/08/2019`'
            )
            msg: disnake.Message = await self.bot.wait_for('message', check=check, timeout=180.0)
        except TimeoutError:
            return await ctx.reply(f'{ctx.denial} You didn\'t give the progress. Aborting.')
        progress = msg.content
        try:
            progress = datetime.strptime(progress, '%d/%m/%Y')
        except ValueError:
            return await ctx.reply(
                f'{ctx.denial} The format in which you gave your birthday date does not match the one you\'re supposed to give it in. '
            )

        await Sober(
            user_id=ctx.author.id,
            short_title=short_title,
            description=description,
            progress=progress
        ).commit()
        await ctx.reply('Successfully added your new sober to keep track of.')

    @base_sober.command(name='reset')
    async def sober_reset(self, ctx: Context):
        """Reset your progress on a sober that you're keeping track of."""

        entries: list[Sober] = await Sober.find({'user_id': ctx.author.id}).to_list(20)
        if len(entries) == 0:
            return await ctx.reply(
                f'{ctx.denial} You don\'t have any sober that you\'re keeping track of currently.'
            )

        view = utils.SelectView([f'{index + 1}. {entry.short_title}' for index, entry in enumerate(entries)])
        view.message = await ctx.reply(
            'Please select one of the sobers that you wish to reset from the select menu below.'
        )
        await view.wait()
        if view.value is None:
            return

        entry = [i for i in entries if i.short_title == view.value][0]
        entry.progress = datetime.now()
        await entry.commit()

        await ctx.reply(f'Successfully reset your progress for `{view.value}`')

    @base_sober.command(name='check', aliases=('list', 'all',))
    async def sober_check(self, ctx: Context):
        """Check your current sober progress."""

        entries: list[Sober] = await Sober.find({'user_id': ctx.author.id}).to_list(20)
        if len(entries) == 0:
            return await ctx.reply(
                f'{ctx.denial} You don\'t have any sober that you\'re keeping track of currently.'
            )

        view = utils.SelectView([f'{index + 1}. {entry.short_title}' for index, entry in enumerate(entries)])
        view.message = await ctx.reply(
            'Please select one of the sobers that you wish check your progress on.'
        )
        await view.wait()
        if view.value is None:
            return

        entry = [i for i in entries if i.short_title == view.value][0]
        em = disnake.Embed(title=entry.short_title, description=entry.description, color=utils.blurple)
        em.add_field(
            'Progress',
            f'{utils.format_dt(entry.progress, "F")} (`{utils.human_timedelta(entry.progress, accuracy=7)}`)'
        )

        await ctx.reply(embed=em)

    @base_sober.command(name='clear')
    async def sober_clear(self, ctx: Context):
        """Clears all of your sober data."""

        entries: list[Sober] = await Sober.find({'user_id': ctx.author.id}).to_list(20)
        if len(entries) == 0:
            return await ctx.reply(
                f'{ctx.denial} You don\'t have any sober that you\'re keeping track of currently.'
            )

        view = utils.ConfirmView(ctx, 'Did not react in time.')
        view.message = msg = await ctx.reply(
            'Are you sure you want to clear your sober data?',
            view=view
        )
        await view.wait()
        if view.response is True:
            for entry in entries:
                await entry.delete()
            e = 'Succesfully cleared all your sober data.'
            return await msg.edit(content=e, view=view)

        elif view.response is False:
            e = 'Your sober data has not been cleared.'
            return await msg.edit(content=e, view=view)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        async for entry in Sober.find({'user_id': member.id}):
            await entry.delete()


def setup(bot: Ukiyo):
    bot.add_cog(SoberApp(bot))
