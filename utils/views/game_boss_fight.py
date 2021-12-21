from __future__ import annotations
from typing import TYPE_CHECKING

import random
import asyncio
from datetime import datetime
from dateutil.relativedelta import relativedelta

import disnake
from disnake import AppCmdInter, ButtonStyle
from disnake.ui import View, Button, button

from utils import Game, Characters

if TYPE_CHECKING:
    from main import Ukiyo

__all__ = ('BossFight',)


class Participant:
    total_damage: int = 0
    dmg: int = None
    character_name: str = None


class BossFight(View):
    def __init__(self, bot: Ukiyo, levels: dict, embed: disnake.Embed):
        super().__init__(timeout=120.0)
        self.bot = bot
        self.levels = levels
        self.embed = embed

        self.ends_date = datetime.now() + relativedelta(minutes=2)
        self.hp = random.randint(25000, 150000)

        self.participants: dict[int, Participant] = {}

    @button(label='Attack', style=ButtonStyle.red)
    async def attack_btn(self, button: Button, inter: AppCmdInter):
        if inter.author.id not in self.participants.keys():
            return await inter.send(
                'You are not participating in this boss fight. Press `Join Fight` to participate.',
                ephemeral=True
            )

        participant = self.participants[inter.author.id]
        dmg = random.randint(*participant.dmg)
        self.hp -= dmg
        participant.total_damage += dmg
        self.participants[inter.author.id] = participant

        self.embed.description = f'{inter.author.mention} just dealt **{dmg:,}** damage to the boss!\n\n' \
                                 f'**BOSS HP:** {self.hp:,}'
        await inter.response.edit_message(embed=self.embed)

    @button(label='Join Fight', style=ButtonStyle.green)
    async def join_btn(self, button: Button, inter: AppCmdInter):
        if inter.author.id in self.participants.keys():
            return await inter.send(
                'You are already participating in the boss fight.',
                ephemeral=True
            )

        data: Game = await Game.find_one({'_id': inter.author.id})
        if data is None:
            return await inter.send(
                'You don\'t have any characters. Cannot join this boss fight.',
                ephemeral=True
            )

        await inter.send(
            'Please send the full name of the character you wish to use in this fight.',
            ephemeral=True
        )
        try:
            msg: disnake.Message = await self.bot.wait_for(
                'message',
                check=lambda m: m.channel.id == inter.channel.id and m.author.id == inter.author.id,
                timeout=30.0
            )
        except asyncio.TimeoutError:
            if datetime.now() < self.ends_date:
                return await inter.send(
                    'You took too long to send your character\'s name!',
                    ephemeral=True
                )
        if datetime.now() < self.ends_date:
            await msg.delete()
            if not msg.content:
                return await inter.send(
                    'You must send a character\'s name.',
                    ephemeral=True
                )

            char = msg.content.lower()
            char_xp = data.characters.get(char)
            if char_xp is None:
                return await inter.send(
                    'You do not own that character.',
                    ephemeral=True
                )

            character: Characters = await Characters.find_one({'_id': char})
            for k, v in self.levels.items():
                if char_xp >= k:
                    lvl = v[0]
                else:
                    break

            dmg = (
                character.lowest_dmg * lvl,
                character.highest_dmg * lvl
            )

            participant = Participant()
            participant.dmg = dmg
            participant.character_name = char
            self.participants[inter.author.id] = participant
