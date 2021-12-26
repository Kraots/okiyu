import disnake

__all__ = (
    'ConfirmView',
    'ConfirmViewDMS',
)


class ConfirmView(disnake.ui.View):
    """
    This class is a view with `Confirm` and `Cancel` buttons,
    this checks which button the user has pressed and returns
    True via the self.response if the button they clicked was
    Confirm else False if the button they clicked is Cancel.
    """

    def __init__(self, ctx, new_message: str = 'Time Expired.', react_user: disnake.Member = None, *, timeout=180.0):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.new_message = new_message
        self.member = react_user
        self.response = False

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        check_for = self.ctx.author.id if self.member is None else self.member.id
        if interaction.author.id not in (check_for, self.ctx.bot._owner_id):
            await interaction.response.send_message(
                f'Only {self.ctx.author.display_name if self.member is None else self.member.display_name} can use the buttons on this message!',
                ephemeral=True
            )
            return False
        return True

    async def on_error(self, error, item, inter):
        await self.bot.inter_reraise(inter, item, error)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
        await self.message.edit(content=self.new_message, embed=None, view=self)

    @disnake.ui.button(label='Yes', style=disnake.ButtonStyle.green)
    async def yes_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        self.response = True
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
            if item.label == button.label:
                item.style = disnake.ButtonStyle.blurple
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label='No', style=disnake.ButtonStyle.red)
    async def no_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
            if item.label == button.label:
                item.style = disnake.ButtonStyle.blurple
        await self.message.edit(view=self)
        self.stop()


class ConfirmViewDMS(disnake.ui.View):
    """
    This class is a view with `Confirm` and `Cancel` buttons
    which only works in dms, this checks which button the user
    has pressed and returns True via the self.response if the
    button they clicked was Confirm else False if the button
    they clicked is Cancel.
    """

    def __init__(self, ctx, *, timeout=180.0, new_message: str = 'Time Expired.'):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.new_message = new_message
        self.response = False

    async def on_error(self, error, item, inter):
        await self.bot.inter_reraise(inter, item, error)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
        await self.message.edit(content=self.new_message, embed=None, view=self)

    @disnake.ui.button(label='Yes', style=disnake.ButtonStyle.green)
    async def yes_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        self.response = True
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
            if item.label == button.label:
                item.style = disnake.ButtonStyle.blurple
        await self.message.edit(view=self)
        self.stop()

    @disnake.ui.button(label='No', style=disnake.ButtonStyle.red)
    async def no_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()
        for item in self.children:
            item.disabled = True
            item.style = disnake.ButtonStyle.grey
            if item.label == button.label:
                item.style = disnake.ButtonStyle.blurple
        await self.message.edit(view=self)
        self.stop()
