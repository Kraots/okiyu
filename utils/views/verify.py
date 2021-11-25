from __future__ import annotations

from typing import TYPE_CHECKING

import disnake
from disnake.ui import View, button

import utils

if TYPE_CHECKING:
    from main import Ukiyo

__all__ = (
    'create_intro',
    'Verify',
)


async def create_intro(ctx: utils.Context, bot: Ukiyo, user_id: int = None):
    if not isinstance(ctx.channel, disnake.DMChannel):
        if ctx.channel.id not in (913330644875104306, 913332335473205308, 913445987102654474):
            return
        else:
            view = utils.ConfirmViewDMS
    else:
        view = utils.ConfirmView

    user_id = user_id or ctx.author.id

    data = await utils.Intro.find_one({'_id': user_id})
    to_update = False
    if data:
        to_update = True
        view = view(ctx)
        view.message = await ctx.send('You already have an intro, do you want to edit it?', view=view)
        await view.wait()
        if view.response is False:
            return

    def check(m):
        return m.channel.id == ctx.channel.id and m.author.id == user_id
    guild = bot.get_guild(913310006814859334)
    intro_channel = guild.get_channel(913331578606854184)

    await ctx.reply('What\'s your name?')
    try:
        _name = await bot.wait_for('message', timeout=180.0, check=check)
        name = _name.content
        if len(name) > 100:
            return await _name.reply('Name too long. Type `!intro` to redo.')

        await _name.reply('What\'s your age?')
        while True:
            try:
                _age = await bot.wait_for('message', timeout=180.0, check=check)
                age = int(_age.content)
            except ValueError:
                await ctx.send('Must be a number.')
            except TimeoutError:
                return await ctx.reply('Ran out of time.')
            else:
                if age < 13 or age > 19:
                    await ctx.send('Sorry! This dating server is only for people between the ages of 13-19.')
                    return await ctx.author.kick(reason='User does not match age limits.')
                else:
                    break

        await _age.reply('What\'s your gender?')
        _gender = await bot.wait_for('message', timeout=180.0, check=check)
        gender = _gender.content
        if len(gender) > 100:
            return await _gender.reply('Gender too long. Type `!intro` to redo.')

        await _gender.reply('Where are you from?')
        _location = await bot.wait_for('message', timeout=180.0, check=check)
        location = _location.content
        if len(location) > 100:
            return await _location.reply('Location too long. Type `!intro` to redo.')

        await _location.reply('Dms? `open` | `closed` | `ask`')
        while True:
            _dms = await bot.wait_for('message', timeout=180.0, check=check)
            dms = _dms.content
            if dms not in ('open', 'closed', 'ask'):
                await _dms.reply('Must only be `open` | `closed` | `ask`')
            else:
                break

        await _dms.reply('Are you currently looking for a date? `yes` | `no`')
        while True:
            _looking = await bot.wait_for('message', timeout=180.0, check=check)
            looking = _looking.content
            if looking not in ('yes', 'no'):
                await _looking.reply('Must only be `yes` | `no`')
            else:
                break

        await _looking.reply('What\'s your sexuality?')
        _sexuality = await bot.wait_for('message', timeout=180.0, check=check)
        sexuality = _sexuality.content
        if len(sexuality) > 100:
            return await ctx.reply('Sexuality too long. Type `!intro` to redo.')

        await _sexuality.reply('What\'s your current relationship status? `single` | `taken` | `complicated`')
        while True:
            _status = await bot.wait_for('message', timeout=180.0, check=check)
            status = _status.content
            if status not in ('single', 'taken', 'complicated'):
                await _status.reply('Must only be `single` | `taken` | `complicated`')
            else:
                break

        await _status.reply('What do you like?')
        _likes = await bot.wait_for('message', timeout=180.0, check=check)
        likes = _likes.content
        if len(likes) > 1024:
            return await _likes.reply('You like too many things. Please don\'t go above 1024 '
                                      'characters next time. Type `!intro` to redo.')

        await _likes.reply('What do you dislike?')
        _dislikes = await bot.wait_for('message', timeout=180.0, check=check)
        dislikes = _dislikes.content
        if len(dislikes) > 1024:
            return await _likes.reply('You dislike too many things. Please don\'t go above 1024 '
                                      'characters next time. Type `!intro` to redo.')
    except TimeoutError:
        return await ctx.reply('Ran out of time.')
    else:
        em = disnake.Embed()
        em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
        em.set_thumbnail(url=ctx.author.display_avatar)
        em.add_field(name='Name', value=name)
        em.add_field(name='Age', value=age)
        em.add_field(name='Gender', value=gender)
        em.add_field(name='Location', value=location)
        em.add_field(name='DMs', value=dms)
        em.add_field(name='Looking', value=looking)
        em.add_field(name='Sexuality', value=sexuality)
        em.add_field(name='Relationship Status', value=status)
        em.add_field(name='Likes', value=likes)
        em.add_field(name='Dislikes', value=dislikes)
        msg = await intro_channel.send(embed=em)

        if to_update is False:
            unverified_role = guild.get_role(913329062347423775)
            usr = guild.get_member(user_id)
            await usr.remove_roles(unverified_role)
            await utils.Intro(
                id=user_id,
                name=name,
                age=age,
                gender=gender,
                location=location,
                dms=dms,
                looking=looking,
                sexuality=sexuality,
                status=status,
                likes=likes,
                dislikes=dislikes,
                message_id=msg.id
            ).commit()
        else:
            old_msg = await intro_channel.fetch_message(data.message_id)
            if old_msg:
                await old_msg.delete()

            data.name = name
            data.age = age
            data.gender = gender
            data.location = location
            data.dms = dms
            data.looking = looking
            data.sexuality = sexuality
            data.status = status
            data.likes = likes
            data.dislikes = dislikes
            data.message_id = msg.id
            await data.commit(replace=True)

        await ctx.reply(
            f'Successfully {"edited" if to_update else "created"} your intro. You can see it in {intro_channel.mention}'
        )


class Verify(View):
    def __init__(self, bot: Ukiyo):
        super().__init__(timeout=None)
        self.bot = bot

    @button(label='Verify', style=disnake.ButtonStyle.green, custom_id='ukiyo:verify')
    async def verify(self, button: disnake.Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        msg = await inter.author.send('Starting the intro creation process...')
        ctx = await self.bot.get_context(msg)
        await create_intro(ctx, self.bot, inter.author.id)
