import disnake
from disnake.ext import commands

import utils
from utils import (
    Context,
    ToDo,
)

from main import Ukiyo


class ToDos(commands.Cog):
    """Todo related commands."""

    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '📋'

    @commands.group(aliases=('todos',), invoke_without_command=True, case_insensitive=True, hidden=True)
    async def todo(self, ctx: Context):
        """Base command for all todo commands."""

        await ctx.send_help('ToDos')

    @todo.command(name='add')
    async def todo_add(self, ctx: Context, *, todo: str):
        """Add to your todo list."""

        res: ToDo = await ToDo.get(ctx.author.id)
        if res is None:
            await ToDo(
                id=ctx.author.id,
                todo_data=[{'url': ctx.message.jump_url, 'todo': todo}]
            ).commit()
            return await ctx.reply('Successfully added to your todo list.')

        res.todo_data += [{'url': ctx.message.jump_url, 'todo': todo}]
        await res.commit()
        await ctx.reply('Successfully added to your todo list.')

    @todo.command(name='list')
    async def todo_list(self, ctx: Context):
        """See your todo list, if you have any."""

        res: ToDo = await ToDo.get(ctx.author.id)
        if res is None:
            return await ctx.reply('You do not have any todos in your todo list.')

        entries = []
        for i, entry in enumerate(res.todo_data):
            entry = f"**[{i + 1}.]({entry['url']})** {entry['todo']}"
            entries.append(entry)

        pag = utils.RawSimplePages(ctx, entries, compact=True)
        pag.embed.set_author(name=utils.format_name(ctx.author), icon_url=ctx.author.display_avatar)
        pag.embed.title = 'Here\'s your todo list:'

        await pag.start()

    @todo.command(name='delete', aliases=['remove'])
    async def todo_remove(self, ctx: Context, index):
        """Remove a todo from your todo list based on its index."""

        index = utils.format_amount(str(index))
        try:
            index = int(index) - 1
        except ValueError:
            return await ctx.reply('That is not a number.')

        res: ToDo = await ToDo.get(ctx.author.id)
        if not res:
            return await ctx.reply('You do not have any todo in your todos list.')

        new_data = []
        if index < 0:
            return await ctx.reply('The index cannot be `0` or negative.')
        elif index > len(res.todo_data) - 1:
            return await ctx.reply('The index cannot be greater than the highest index in your todo list.')

        for i in range(len(res.todo_data)):
            if i != index:
                new_data.append(res.todo_data[i])

        if len(new_data) == 0:
            await res.delete()
        else:
            res.todo_data = new_data
            await res.commit()
        await ctx.reply('Successfully removed that todo from your todo list.')

    @todo.command(name='clear')
    async def todo_clear(self, ctx: Context):
        """Delete your todo list, completely."""

        res: ToDo = await ToDo.get(ctx.author.id)
        if not res:
            return await ctx.reply('You do not have any todos in your todo list.')

        view = utils.ConfirmView(ctx, f'{ctx.author.mention} Did not react in time.')
        view.message = msg = await ctx.send(f'Are you sure you want to delete your todo list? {ctx.author.mention}', view=view)
        await view.wait()
        if view.response is True:
            await res.delete()
            e = f'Succesfully cleared todo list. {ctx.author.mention}'
            return await msg.edit(content=e, view=view)

        elif view.response is False:
            e = f'Okay, your todo list has not been deleted. {ctx.author.mention}'
            return await msg.edit(content=e, view=view)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.id != self.bot._owner_id:
            async for todo in ToDo.find({'_id': member.id}):
                await todo.delete()


def setup(bot: Ukiyo):
    bot.add_cog(ToDos(bot))
