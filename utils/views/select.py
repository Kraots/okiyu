import disnake

__all__ = (
    'SelectView',
)


class Select(disnake.ui.Select['SelectView']):
    def __init__(self, options: list[str], *, enumerated: bool = False):
        super().__init__(placeholder='Select one of the options...', min_values=1, max_values=1)
        self.enumerated = enumerated
        self._fill_options(options)

    def _fill_options(self, options: list[str]):
        if self.enumerated is False:
            for option in options:
                self.add_option(label=option)
        else:
            for index, option in enumerate(options):
                self.add_option(label=f'{index + 1}. {option}', value=option)

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()

        assert self.view is not None
        value = self.values[0]
        self.view.value = value
        self.view.stop()


class SelectView(disnake.ui.View):
    message: disnake.Message
    value: str | int | bool | float = None

    def __init__(self, options: list[str], *, timeout: float = 30.0, enumerated: bool = False):
        super().__init__(timeout=timeout)
        self.add_item(Select(options, enumerated=enumerated))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
