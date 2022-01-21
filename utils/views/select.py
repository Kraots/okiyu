import disnake

__all__ = (
    'SelectView',
)


class Select(disnake.ui.Select['SelectView']):
    def __init__(self, options: list[str]):
        super().__init__(placeholder='Select one of the options...', min_values=1, max_values=1)
        self._fill_options(options)

    def _fill_options(self, options: list[str]):
        for option in options:
            self.add_option(option)

    async def callback(self, interaction: disnake.MessageInteraction):
        assert self.view is not None
        value = self.values[0]
        self.view.value = value
        self.view.stop()


class SelectView(disnake.ui.View):
    message: disnake.Message
    value: str | int | bool | float

    def __init__(self, options: list[str], *, timeout: float = 30.0):
        super().__init__(timeout=timeout)
        self.add_item(Select(options))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
