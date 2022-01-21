import textwrap
import datetime

import disnake
from disnake.ext import commands, tasks

import utils
from utils import (
    human_timedelta,
    UserFriendlyTime,
    Context,
    RoboPages,
    FieldPageSource,
    Reminder
)

from main import Ukiyo


class Reminders(commands.Cog):
    """Reminder related commands."""

    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.check_current_reminders.start()

    @property
    def display_emoji(self) -> str:
        return '⏰'

    @commands.group(invoke_without_command=True, case_insensitive=True, aliases=['reminder'])
    async def remind(
        self,
        ctx: Context,
        *,
        when_and_what: UserFriendlyTime(commands.clean_content, default='\u2026')  # noqa
    ):
        """Set your reminder.

        `when_and_what` **->** The time to remind you and what to remind you.

        **Example:**
            `!remind 30m sleep`
        """

        res: list[Reminder] = await Reminder.find({'user_id': ctx.author.id}).sort('reminder_id', -1).to_list(1)

        if res:
            new_id = res[0].reminder_id + 1
        else:
            new_id = 1

        await Reminder(
            reminder_id=new_id,
            user_id=ctx.author.id,
            channel_id=ctx.channel.id,
            remind_when=when_and_what.dt,
            remind_what=when_and_what.arg,
            time_now=datetime.datetime.utcnow(),
            message_url=ctx.message.jump_url
        ).commit()

        delta = human_timedelta(when_and_what.dt, accuracy=3)
        await ctx.send(f'Alright {ctx.author.mention}, in **{delta}**: {when_and_what.arg}')

    @remind.command(name='list')
    async def remind_list(self, ctx: Context):
        """See your list of reminders, if you have any."""

        reminders = []
        async for entry in Reminder.find({'user_id': ctx.author.id}).sort('remind_when', 1):
            entry: Reminder

            shorten = textwrap.shorten(entry.remind_what, width=320)
            reminders.append((
                f'(ID) `{entry.reminder_id}`: In {human_timedelta(entry.remind_when)}',
                f'{shorten}\n[Click here to go there]({entry.message_url})'
            ))

        if len(reminders) == 0:
            return await ctx.send('No currently running reminders.')

        src = FieldPageSource(reminders, per_page=5)
        src.embed.title = 'Reminders'
        src.embed.colour = utils.blurple
        pages = RoboPages(src, ctx=ctx, compact=True)
        await pages.start()

    @remind.command(name='remove', aliases=['delete', 'cancel'])
    @commands.max_concurrency(1, commands.BucketType.user)
    async def remind_remove(self, ctx: Context, reminder_id: int):
        """Remove a reminder from your list based on its id.

        `reminder_id` **->** The id of the reminder you want to delete. This can be found by looking at `!remind list`
        """

        entries: list[Reminder] = await Reminder.find({'user_id': ctx.author.id, 'reminder_id': reminder_id}).to_list(1)
        if entries:
            entry = entries[0]

            if entry.user_id == ctx.author.id:
                view = utils.ConfirmView(ctx, 'Did not react in time.')
                view.message = msg = await ctx.send(
                    'Are you sure you want to cancel that reminder?',
                    view=view
                )
                await view.wait()
                if view.response is True:
                    await entry.delete()
                    e = 'Succesfully cancelled the reminder.'
                    return await msg.edit(content=e, view=view)

                elif view.response is False:
                    e = 'Reminder has not been cancelled.'
                    return await msg.edit(content=e, view=view)
            else:
                await ctx.send('That reminder is not yours!')
                return
        else:
            await ctx.send('No reminder with that id.')
            return

    @remind.command(name='clear')
    @commands.max_concurrency(1, commands.BucketType.user)
    async def remind_clear(self, ctx: Context):
        """Delete all of your reminders."""

        res: Reminder = await Reminder.find_one({'user_id': ctx.author.id})
        if res is not None:
            view = utils.ConfirmView(ctx, 'Did not react in time.')
            view.message = msg = await ctx.reply(
                'Are you sure you want to clear your reminders?',
                view=view
            )
            await view.wait()
            if view.response is True:
                async for remind in Reminder.find({'user_id': ctx.author.id}):
                    await remind.delete()
                e = 'Succesfully cleared all your reminders.'
                return await msg.edit(content=e, view=view)

            elif view.response is False:
                e = 'Reminders have not been cleared.'
                return await msg.edit(content=e, view=view)
        else:
            await ctx.send('No currently running reminders.')

    @tasks.loop(seconds=5)
    async def check_current_reminders(self):
        await self.bot.wait_until_ready()
        current_time = datetime.datetime.utcnow()
        results: list[Reminder] = await Reminder.find().sort('remind_when', 1).to_list(5)
        for res in results:
            if current_time >= res.remind_when:
                remind_channel = self.bot.get_channel(res.channel_id)
                msg = f'<@!{res.user_id}>, **{human_timedelta(res.remind_when)}**: {res.remind_what}'
                await remind_channel.send(
                    msg,
                    view=utils.UrlButton('Go to the original message', res.message_url)
                )
                await res.delete()

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.id != self.bot._owner_id:
            async for remind in Reminder.find({'user_id': member.id}):
                await remind.delete()

    @remind.error
    async def remind_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send(str(error))
        else:
            await ctx.reraise(error)

    @remind_remove.error
    async def remind_remove_error(self, ctx: Context, error):
        if isinstance(error, commands.errors.TooManyArguments):
            return
        else:
            await ctx.reraise(error)


def setup(bot: Ukiyo):
    bot.add_cog(Reminders(bot))
