import disnake
from disnake.ext import commands

from utils import (
    Context,
    Intro,
    IntroFields,
    create_intro,
    is_mod,
)

from main import Ukiyo


class Intros(commands.Cog):
    """Intro related commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot

    @property
    def display_emoji(self) -> str:
        return '🙌'

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def intro(self, ctx: Context):
        """Create/Edit your intro.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if ctx.author.id in self.bot.verifying:
            return await ctx.send(
                f'{ctx.denial} Please complete your current intro before making another one!'
            )
        self.bot.verifying.append(ctx.author.id)
        await create_intro(self.bot.webhooks['mod_logs'], ctx, self.bot)

    @intro.command(name='edit')
    @commands.max_concurrency(1, commands.BucketType.user)
    async def intro_edit(self, ctx: Context):
        """Edit a field in your intro.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if await ctx.check_channel() is False:
            return

        data: Intro = await Intro.find_one({'_id': ctx.author.id})
        if data is None:
            return await ctx.reply(
                f'{ctx.denial} You don\'t have an intro. '
                'Please contact a staff member to unverify you! This is a bug.'
            )

        is_owner = True if ctx.author.id == self.bot._owner_id else False
        view = IntroFields(ctx, is_owner=is_owner)
        view.message = await ctx.reply(
            'Please select one of the fields that you wish to edit in your intro from the select menu below.',
            view=view
        )
        await view.wait()

    @commands.command(aliases=('wi',))
    async def whois(self, ctx: Context, *, member: disnake.Member = None):
        """Check somebody's intro!

        `member` **->** The member you want to see the intro of. If you want to see your own intro, you can just ignore this since it defaults to you.
        """

        member = member or ctx.author
        data: Intro = await Intro.get(member.id)
        if data is None:
            if member.id == self.bot._owner_id:
                return await ctx.better_reply('🤫 🤫 🤫')
            if member == ctx.author:
                return await ctx.reply(
                    f'{ctx.denial} You don\'t have an intro. '
                    'Please contact a staff member to unverify you! This is a bug.'
                )
            else:
                return await ctx.better_reply(
                    f'{ctx.denial} `{member}` doesn\'t have an intro. '
                    'Please contact a staff member to unverify them! This is a bug.'
                )
        intro_channel = ctx.ukiyo.get_channel(913331578606854184)
        msg = await intro_channel.fetch_message(data.message_id)
        if msg:
            view = disnake.ui.View()
            view.add_item(disnake.ui.Button(label='Jump!', url=msg.jump_url))
        else:
            view = None

        em = disnake.Embed(colour=member.color)
        em.set_author(name=member.display_name, icon_url=member.display_avatar)
        em.set_thumbnail(url=member.display_avatar)
        em.add_field(name='Name', value=data.name)
        em.add_field(name='Age', value=data.age)
        em.add_field(name='Pronouns', value=data.pronouns)
        em.add_field(name='Gender', value=data.gender)
        em.add_field(name='Location', value=data.location)
        em.add_field(name='\u200b', value='\u200b')
        em.add_field(name='DMs', value=data.dms)
        em.add_field(name='Looking', value=data.looking)
        em.add_field(name='Sexuality', value=data.sexuality)
        em.add_field(name='Relationship Status', value=data.status)
        em.add_field(name='Likes', value=data.likes)
        em.add_field(name='Dislikes', value=data.dislikes)
        em.set_footer(text=f'Requested by: {ctx.author}')
        await ctx.better_reply(embed=em, view=view)

    @commands.command(name='unverify')
    @is_mod()
    async def intro_unverify(self, ctx: Context, *, member: disnake.Member):
        """Unverify a member if their intro is a troll or if you consider that their intro is inappropriate.

        `member` **->** The member you want to unverify.
        """

        if await ctx.check_perms(
            member,
            reason='You cannot unverify somebody that is a higher or equal role than you.'
        ) is False:
            return

        unverified_role = ctx.ukiyo.get_role(913329062347423775)
        data = await Intro.get(member.id)
        if data is not None:
            intro_channel = ctx.ukiyo.get_channel(913331578606854184)
            msg = await intro_channel.fetch_message(data.message_id)
            if msg:
                await msg.delete()
            await data.delete()
        await member.edit(roles=[r for r in member.roles if r.id == 913376647422545951] + [unverified_role])
        await member.send(
            'You have been unverified in `Ukiyo` by one of our staff members. '
            'Please be serious when you\'re making your intro!'
        )
        await ctx.reply(f'> 👌 `{member}` has been successfully unverified.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data = await Intro.get(member.id)
        if data:
            guild = self.bot.get_guild(913310006814859334)
            intro_channel = guild.get_channel(913331578606854184)
            msg = await intro_channel.fetch_message(data.message_id)
            if msg:
                await msg.delete()
            await data.delete()


def setup(bot: Ukiyo):
    bot.add_cog(Intros(bot))
