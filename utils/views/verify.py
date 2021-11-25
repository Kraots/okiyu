import disnake
from disnake.ui import View, button

from main import Ukiyo


class Verifiy(View):
    def __init__(self, bot: Ukiyo):
        super().__init__(timeout=None)
        self.bot = bot

    @button(label='Verify', style=disnake.ButtonStyle.green, custom_id='ukiyo:verify')
    async def verify(self, button: disnake.Button, inter: disnake.MessageInteraction):
        msg = await inter.author.send('Starting the intro creation process...')
        ctx = await self.bot.get_context(msg)
        cmd = self.bot.get_command('intro')
        await cmd.invoke(ctx)
