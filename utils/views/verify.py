from __future__ import annotations

from typing import TYPE_CHECKING

import disnake
from disnake.ui import View, button

if TYPE_CHECKING:
    from main import Ukiyo


class Verifiy(View):
    def __init__(self, bot: Ukiyo):
        super().__init__(timeout=None)
        self.bot = bot

    @button(label='Verify', style=disnake.ButtonStyle.green, custom_id='ukiyo:verify')
    async def verify(self, button: disnake.Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        msg = await inter.author.send('Starting the intro creation process...')
        ctx = await self.bot.get_context(msg)
        cmd = self.bot.get_command('intro')
        await cmd.invoke(ctx)
