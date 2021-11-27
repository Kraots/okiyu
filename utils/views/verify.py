from __future__ import annotations

import random
from asyncio import TimeoutError
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
    user_id = user_id or ctx.author.id

    if not isinstance(ctx.channel, disnake.DMChannel):
        if ctx.channel.id not in (913330644875104306, 913332335473205308, 913445987102654474):
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return
        else:
            view = utils.ConfirmView
    else:
        view = utils.ConfirmViewDMS

    data = await utils.Intro.find_one({'_id': user_id})
    to_update = False
    if data:
        to_update = True
        view = view(ctx)
        view.message = await ctx.send('You already have an intro, do you want to edit it?', view=view)
        await view.wait()
        if view.response is False:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
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
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _name.reply(f'> {ctx.disagree} Name too long. Type `!intro` to redo.')

        await _name.reply('What\'s your age?')
        while True:
            try:
                _age = await bot.wait_for('message', timeout=180.0, check=check)
                age = int(_age.content)
            except ValueError:
                await ctx.send(f'> {ctx.disagree} Must be a number.')
            except TimeoutError:
                try:
                    bot.verifying.pop(bot.verifying.index(user_id))
                except (IndexError, ValueError):
                    pass
                return await ctx.reply(f'> {ctx.disagree} Ran out of time.')
            else:
                if age < 14 or age > 19:
                    await ctx.send(f'> {ctx.disagree} Sorry! This dating server is only for people between the ages of 14-19.')
                    try:
                        bot.verifying.pop(bot.verifying.index(user_id))
                    except (IndexError, ValueError):
                        pass
                    return await ctx.author.kick(reason='User does not match age limits.')
                else:
                    break

        await _age.reply('What\'s your gender? (e.g: male, female, non-binary, trans-male, trans-female, etc...)')
        _gender = await bot.wait_for('message', timeout=180.0, check=check)
        gender = _gender.content
        if len(gender) > 100:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _gender.reply(f'> {ctx.disagree} Gender too long. Type `!intro` to redo.')

        await _gender.reply('Where are you from?')
        _location = await bot.wait_for('message', timeout=180.0, check=check)
        location = _location.content
        if len(location) > 100:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _location.reply(f'> {ctx.disagree} Location too long. Type `!intro` to redo.')

        await _location.reply('Dms? `open` | `closed` | `ask`')
        while True:
            _dms = await bot.wait_for('message', timeout=180.0, check=check)
            dms = _dms.content
            if dms.lower() not in ('open', 'closed', 'ask'):
                await _dms.reply(f'> {ctx.disagree} Must only be `open` | `closed` | `ask`')
            else:
                break

        await _dms.reply('Are you currently looking for a date? `yes` | `no`')
        while True:
            _looking = await bot.wait_for('message', timeout=180.0, check=check)
            looking = _looking.content
            if looking.lower() not in ('yes', 'no'):
                await _looking.reply(f'> {ctx.disagree} Must only be `yes` | `no`')
            else:
                break

        await _looking.reply('What\'s your sexuality? (e.g: straight, bisexual, gay, lesbian, pansexual, etc...)')
        _sexuality = await bot.wait_for('message', timeout=180.0, check=check)
        sexuality = _sexuality.content
        if len(sexuality) > 100:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await ctx.reply(f'> {ctx.disagree} Sexuality too long. Type `!intro` to redo.')

        await _sexuality.reply('What\'s your current relationship status? `single` | `taken` | `complicated`')
        while True:
            _status = await bot.wait_for('message', timeout=180.0, check=check)
            status = _status.content
            if status.lower() not in ('single', 'taken', 'complicated'):
                await _status.reply(f'> {ctx.disagree} Must only be `single` | `taken` | `complicated`')
            else:
                break

        await _status.reply('What do you like?')
        _likes = await bot.wait_for('message', timeout=180.0, check=check)
        likes = _likes.content
        if len(likes) > 1024:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _likes.reply(f'> {ctx.disagree} You like too many things. Please don\'t go above 1024 '
                                      'characters next time. Type `!intro` to redo.')

        await _likes.reply('What do you dislike?')
        _dislikes = await bot.wait_for('message', timeout=180.0, check=check)
        dislikes = _dislikes.content
        if len(dislikes) > 1024:
            try:
                bot.verifying.pop(bot.verifying.index(user_id))
            except (IndexError, ValueError):
                pass
            return await _dislikes.reply(f'> {ctx.disagree} You dislike too many things. Please don\'t go above 1024 '
                                         'characters next time. Type `!intro` to redo.')
    except TimeoutError:
        try:
            bot.verifying.pop(bot.verifying.index(user_id))
        except (IndexError, ValueError):
            pass
        return await ctx.reply(f'> {ctx.disagree} Ran out of time. Type `!intro` to redo.')
    else:
        role = guild.get_role(random.choice(utils.all_colour_roles[:-1]))
        usr = guild.get_member(user_id)
        colour = role.color if to_update is False else usr.color
        em = disnake.Embed(colour=colour)
        em.set_author(name=usr, icon_url=usr.display_avatar)
        em.set_thumbnail(url=usr.display_avatar)
        em.add_field(name='Name', value=name)
        em.add_field(name='Age', value=age)
        em.add_field(name='Gender', value=gender)
        em.add_field(name='Location', value=location, inline=False)
        em.add_field(name='DMs', value=dms)
        em.add_field(name='Looking', value=looking)
        em.add_field(name='Sexuality', value=sexuality)
        em.add_field(name='Relationship Status', value=status)
        em.add_field(name='Likes', value=likes)
        em.add_field(name='Dislikes', value=dislikes)
        msg = await intro_channel.send(embed=em)

        if to_update is False:
            new_roles = [r for r in usr.roles if r.id != 913329062347423775] + [role]
            await usr.edit(roles=new_roles)
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
        disagree = '<:disagree:913895999125196860>'
        if inter.author.id in self.bot.verifying:
            return await inter.followup.send(
                f'> {disagree} Please complete your current verification before proceeding again!', ephemeral=True
            )
        self.bot.verifying.append(inter.author.id)
        try:
            msg = await inter.author.send('Starting the intro creation process...')
        except disnake.Forbidden:
            return await inter.followup.send(f'> {disagree} You have your dms off! Please enable them!!', ephemeral=True)
        ctx = await self.bot.get_context(msg, cls=utils.Context)
        await create_intro(ctx, self.bot, inter.author.id)
