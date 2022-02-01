import disnake
from disnake.ext import commands

import utils
from utils import Context

from main import Ukiyo


class Actions(commands.Cog):
    """Action commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '<:hug:914072588886614027>'

    @commands.command(name='huggles')
    async def _huggles(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Give somebody a hug ❤️

        `members` **->** The people you want to hug. Can be more than just one, or none.
        """

        mems = ' '.join([m.mention for m in members]) if members else None
        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://media.discordapp.net/attachments/737981297212915712/751115114106585243/938097236024360960.gif'
        )

        await ctx.reply(mems, embed=em)

    @commands.command(name='pat')
    async def _pat(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Give somebody a pat ❤️

        `members` **->** The people you want to pat. Can be more than just one, or none.
        """

        mems = ' '.join([m.mention for m in members]) if members else None
        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://cdn.discordapp.com/attachments/750160852380024893/751229628202483772/tenor_9.gif'
        )

        await ctx.reply(mems, embed=em)

    @commands.command(name='slap')
    async def _slap(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Give somebody a slap <:slap:914791660980953098>

        `members` **->** The people you want to slap. Can be more than just one, or none.
        """

        mems = []
        if members is not None:
            for mem in members:
                if mem.id == self.bot._owner_id:
                    mem = ctx.author
                mems.append(mem.mention)
        mems = ' '.join(mems) if mems else None

        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://cdn.discordapp.com/attachments/855126816271106061/894624778906910740/slap_gif.gif'
        )

        await ctx.reply(mems, embed=em)

    @commands.command(name='kill')
    async def _kill(self, ctx: Context, members: commands.Greedy[disnake.Member] = None):
        """Kill somebody 🪦

        `members` **->** The people you want to kill. Can be more than just one, or none.
        """

        mems = []
        if members is not None:
            for mem in members:
                if mem.id == self.bot._owner_id:
                    mem = ctx.author
                mems.append(mem.mention)
        mems = ' '.join(mems) if mems else None

        em = disnake.Embed(color=utils.red)
        em.set_image(
            url='https://cdn.discordapp.com/attachments/750160852380024893/751229626952581170/tenor_8.gif'
        )

        await ctx.reply(mems, embed=em)

    @commands.command(name='bonk')
    async def _bonk(self, ctx: Context, *, user: disnake.User):
        """Bonk someone.

        `user` **->** The user you want to bonk.
        """

        user = ctx.author if user.id == self.bot._owner_id else user

        await ctx.message.add_reaction(ctx.thumb)
        file = await utils.bonk_gif(user)
        em = disnake.Embed(color=utils.red)
        em.set_image(file=file)

        await ctx.reply(user.mention, embed=em)


def setup(bot: Ukiyo):
    bot.add_cog(Actions(bot))
