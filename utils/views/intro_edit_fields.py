from asyncio import TimeoutError
import datetime

import disnake

import utils

__all__ = ('IntroFields', 'CancelButton',)


class CancelButton(disnake.ui.View):
    def __init__(
        self,
        ctx: utils.Context,
        *,
        timeout: float = 180.0,
        delete_after: bool = False
    ):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.bot = ctx.bot
        self.delete_after = delete_after
        self.message = None

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if interaction.author.id != self.ctx.author.id:
            await interaction.response.send_message(
                f'Only **{self.ctx.author.display_name}** can use the menus on this message!',
                ephemeral=True
            )
            return False
        return True

    async def on_error(self, error, item, inter):
        await self.bot.inter_reraise(inter, item, error)

    async def on_timeout(self):
        if self.delete_after is False:
            return await self.message.edit(view=None)

        await utils.try_delete((self.message, self.ctx.message))

    @disnake.ui.button(label='Cancel', style=disnake.ButtonStyle.red)
    async def quit(self, button: disnake.ui.Button, inter: disnake.Interaction):
        """Deletes the user's message along with the bot's message."""

        await inter.response.defer()
        await utils.try_delete((self.message, self.ctx.message))
        self.stop()


class IntroField(disnake.ui.Select['IntroFields']):
    def __init__(self, *, placeholder: str = 'Select a field that you want to edit in your intro...'):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1)
        self._fill_options()

    def _fill_options(self):
        self.add_option(label='Name')
        self.add_option(label='Age')
        self.add_option(label='Pronouns')
        self.add_option(label='Gender')
        self.add_option(label='Location')
        self.add_option(label='DMs')
        self.add_option(label='Looking')
        self.add_option(label='Sexuality')
        self.add_option(label='Relationship Status')
        self.add_option(label='Likes')
        self.add_option(label='Dislikes')

    async def delete_intro_message(self, data: utils.Intro):
        channel = self.view.ctx.ukiyo.get_channel(913331578606854184)
        await utils.try_delete(channel=channel, message_id=data.message_id)

    async def callback(self, inter: disnake.MessageInteraction):
        assert self.view is not None
        value = self.values[0]
        await inter.response.defer()
        await utils.try_delete((self.view.message, self.view.ctx.message))

        await inter.send(
            f'Alright, please send the new info that you wish to update your `{value}` field to...',
            ephemeral=True
        )

        try:
            msg: disnake.Message = await self.view.ctx.bot.wait_for(
                'message',
                check=lambda m: m.channel.id == inter.channel.id and m.author.id == inter.author.id,
                timeout=180.0
            )
        except TimeoutError:
            self.view.stop()
            return
        self.view.stop()

        new_data = msg.content
        await utils.try_delete(msg)
        value = value.lower()
        data: utils.Intro = await utils.Intro.get(inter.author.id)

        if value == 'age':
            try:
                new_data = int(new_data)
            except (ValueError, TypeError):
                return await inter.send(f'{self.view.ctx.denial} Must be a number.', ephemeral=True)
            else:
                if new_data < 14 or new_data > 19:
                    await self.delete_intro_message(data)
                    await utils.try_dm(
                        inter.author,
                        f'{self.view.ctx.denial} Sorry! This dating server is only for people between the ages of 14-19.'
                    )
                    await inter.author.ban(reason='User does not match age requirements.')
                    await utils.log(
                        self.view.ctx.bot.webhooks['mod_logs'],
                        title='[BAN]',
                        fields=[
                            ('Member', f'{inter.author} (`{inter.author.id}`)'),
                            ('Reason', f'User does not match age requirements. (`{new_data} y/o`)'),
                            ('By', f'{self.view.ctx.bot.user.mention} (`{self.view.ctx.bot.user.id}`)'),
                            ('At', utils.format_dt(datetime.datetime.now(), 'F')),
                        ]
                    )
                    return
        elif value == 'dms':
            if new_data not in ('open', 'closed', 'ask'):
                return await inter.send(
                    f'{self.view.ctx.denial} Must only be `open` | `closed` | `ask`',
                    ephemeral=True
                )
        elif value == 'looking':
            if new_data not in ('yes', 'no'):
                return await inter.send(f'{self.view.ctx.denial} Must only be `yes` | `no`', ephemeral=True)
        elif value == 'relationship status':
            if new_data not in ('single', 'taken', 'complicated'):
                return await inter.send(
                    f'{self.view.ctx.denial} Must only be `single` | `taken` | `complicated`',
                    ephemeral=True
                )
        elif value in ('likes', 'dislikes'):
            if len(new_data) > 1024:
                _ = 'like' if value == 'likes' else 'dislikes'
                return await inter.send(
                    f'{self.view.ctx.denial} You {_} too many things. Please type less next time.',
                    ephemeral=True
                )

        else:
            if value != 'age':
                if len(new_data) > 100:
                    return await inter.send(
                        f'{self.view.ctx.denial} Your `{value.title()}` field must be less than **100** characters.'
                    )

        if value == 'relationship status':
            value = 'status'
        data[value] = new_data

        em = disnake.Embed(colour=inter.author.color)
        em.set_author(name=utils.format_name(inter.author), icon_url=inter.author.display_avatar)
        em.set_thumbnail(url=inter.author.display_avatar)
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

        await self.delete_intro_message(data)

        channel = self.view.ctx.ukiyo.get_channel(913331578606854184)
        m = await channel.send(embed=em)

        data.message_id = m.id
        await data.commit()

        v = disnake.ui.View()
        v.add_item(disnake.ui.Button(label='Jump!', url=m.jump_url))
        await inter.send(f'Successfully updated your `{value.title()}` field.', ephemeral=True, view=v)


class IntroFields(CancelButton):
    def __init__(self, ctx: utils.Context, *, is_owner: bool = False):
        super().__init__(ctx=ctx, delete_after=True)
        self.ctx = ctx
        placeholder = 'Select a field that you want to edit in your intro master...' if is_owner is True else None
        self.clear_items()
        self.add_item(IntroField(placeholder=placeholder))
        self.add_item(self.quit)
