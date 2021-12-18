from __future__ import annotations

import random
import inspect
from typing import TYPE_CHECKING

import disnake

import utils
from utils.context import Context

if TYPE_CHECKING:
    from main import Ukiyo


__all__ = (
    'Fight',
)


class Fight(disnake.ui.View):
    def __init__(
        self,
        pl1: tuple[disnake.Member, utils.Characters, int],
        pl2: tuple[disnake.Member, utils.Characters, int],
        ctx: Context,
        *,
        timeout=30.0
    ):
        super().__init__(timeout=timeout)
        self.p1 = pl1[0]
        self._p1 = pl1[1]
        self.p1_lvl = pl1[2]
        self.p2 = pl2[0]
        self._p2 = pl2[1]
        self.p2_lvl = pl2[2]

        self.ctx = ctx
        self.bot: Ukiyo = ctx.bot

        self.hp = {self.p1: pl1[1].hp, self.p2: pl2[1].hp}
        self.dmg = {
            self.p1: (pl1[1].lowest_dmg, pl1[1].highest_dmg),
            self.p2: (pl2[1].lowest_dmg, pl2[1].highest_dmg)
        }

        self.turn = self.p1
        self.ended = False

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if interaction.author.id != self.turn.id:
            if interaction.author.id not in (self.p1.id, self.p2.id):
                await interaction.response.send_message(
                    'You are not playing in this game! To start a game with someone you must type `!game fight <member>`',
                    ephemeral=True
                )
                return False
            await interaction.response.send_message(f'Not your turn, it\'s {self.turn.display_name}\'s turn', ephemeral=True)
            return False
        return True

    async def on_error(self, error: Exception, item, interaction):
        return await self.bot.reraise(self.ctx, error)

    async def on_timeout(self):
        for item in self.children:
            item.style = disnake.ButtonStyle.grey
            item.disabled = True
        if self.turn == self.p1:
            winner = self.p2
            winner_charact = self._p2
        else:
            winner = self.p1
            winner_charact = self._p1
        await self.message.edit(
            content=f'{self._data}\n\n**___TIMEOUT___**\n**{self.turn.display_name}** took too much to react and lost **1,500** 🪙. '
                    f'{winner.mention} won **2,500** 🪙 and their character got **25xp**.',
            view=self
        )
        await self.award(winner.id, self.turn.id, winner_charact)

    def update_turn(self):
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1

    async def award(self, winner_id: int, loser_id: int, winner_character: utils.Characters):
        winner_db: utils.Game = await utils.Game.find_one({'_id': winner_id})
        loser_db: utils.Game = await utils.Game.find_one({'_id': loser_id})
        winner_db.characters[winner_character.name] += 25

        winner_db.coins += 2500
        winner_db.wins += 1
        winner_db.total_matches += 1
        loser_db.coins -= 1500
        winner_db.loses += 1
        winner_db.total_matches += 1

        await winner_db.commit()
        await loser_db.commit()

    @property
    def _data(self) -> str:
        data = inspect.cleandoc(
            f'''
            `{self.p1.display_name} (lvl {self.p1_lvl} {self._p1.name})` **==> {self.hp[self.p1]} hp**
            `{self.p2.display_name} (lvl {self.p2_lvl} {self._p2.name})` **==> {self.hp[self.p2]} hp**
            '''
        )
        return data

    async def check_health(self) -> bool:
        winner = None
        if self.hp[self.p1] <= 0:
            winner = self.p2
            winner_charact = self._p2
        elif self.hp[self.p2] <= 0:
            winner = self.p1
            winner_charact = self._p1

        if winner is not None:
            self.ended = True
            for item in self.children:
                item.style = disnake.ButtonStyle.grey
                item.disabled = True

            await self.message.edit(
                content=f'{self._data}\n\n**{winner.display_name}** won and got **2,500** 🪙 and their character got **25xp**.'
                        f'\n{self.turn.mention} you lost **1,500** 🪙!',
                view=self
            )
            await self.award(winner.id, self.turn.id, winner_charact)
            self.stop()

    @disnake.ui.button(label='Fight', style=disnake.ButtonStyle.red)
    async def _fight_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()

        p = self.turn
        lowest_dmg, highest_dmg = self.dmg[self.turn]
        self.update_turn()
        curr_hp = self.hp[self.turn]
        dmg = random.randint(lowest_dmg, highest_dmg)
        new_hp = curr_hp - dmg
        self.hp[self.turn] = new_hp
        await self.check_health()
        if self.ended is False:
            await self.message.edit(
                content=f'{self._data}\n\n**{p.display_name}** chose to fight and dealt `{dmg}` damage. '
                        f'Your turn now: {self.turn.mention}'
            )

    @disnake.ui.button(label='Forfeit', style=disnake.ButtonStyle.blurple)
    async def _forfeit_button(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await inter.response.defer()

        p = self.turn
        self.update_turn()
        for item in self.children:
            item.style = disnake.ButtonStyle.grey
            item.disabled = True
        await self.message.edit(
            content=f'{self._data}\n\n**___FORFEIT___**\n**{p.display_name}** forfeited and lost **1,500** 🪙\n'
                    f'{self.turn.mention} you won **2,500** 🪙 and your character gets **25xp**!',
            view=self
        )
        winner_charact = self._p1 if p == self.p1 else self._p2
        await self.award(p.id, self.turn.id, winner_charact)
        self.stop()
