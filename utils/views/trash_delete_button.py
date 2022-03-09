from disnake import PartialEmoji, ButtonStyle, MessageInteraction, HTTPException
from disnake.ui import Button, View, button

from ..helpers import try_delete

__all__ = ('TrashButtonDelete',)


class TrashButtonDelete(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(
        style=ButtonStyle.red,
        emoji=PartialEmoji(name='trash', id=938412197967724554),
        custom_id='trash-button-delete'
    )
    async def btn(self, btn: Button, inter: MessageInteraction):
        try:
            await inter.response.defer()
        except HTTPException:
            pass
        await try_delete(inter.message)
