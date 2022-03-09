from disnake.ext import commands
from disnake.ui import Modal, TextInput
from disnake import (
    AppCmdInter,
    TextInputStyle,
    ModalInteraction,
    Embed
)

import utils

from main import Okiyu


class RecommendModal(Modal):
    def __init__(self):
        components = [
            TextInput(
                label='Title',
                placeholder='The World After The End',
                style=TextInputStyle.short,
                max_lenght=100
            ),
            TextInput(
                label='Chapters/Episodes Count',
                placeholder='11',
                style=TextInputStyle.short,
                max_lenght=15
            ),
            TextInput(
                label='Source/Website to watch/read it on',
                placeholder='https://www.asurascans.com/comics/the-world-after-the-end/',
                style=TextInputStyle.short,
                max_lenght=300
            ),
            TextInput(
                label='Status',
                placeholder='Ongoing',
                style=TextInputStyle.short,
                max_lenght=15
            )
        ]
        super().__init__(
            title='Make Recommendation',
            components=components
        )

    async def callback(self, inter: ModalInteraction):
        channel = inter.guild.get_channel(951210058870558740)
        values = inter.text_values.copy()
        em = Embed(
            color=inter.author.color,
            title=values['Title']
        )
        del values['Title']

        for k, v in values.items():
            em.add_field(
                k,
                v,
                inline=False
            )
        m = await channel.send(embed=em)
        await inter.send(
            'Recommendation succesfully submitted.',
            ephemeral=True,
            view=utils.UrlButton('Jump!', m.jump_url)
        )


class SlashCommands(commands.Cog):
    def __init__(self, bot: Okiyu):
        self.bot = bot

    @commands.slash_command(name='colours', description='Change your colour!')
    async def change_colour(self, inter: AppCmdInter):
        if inter.author.id == self.bot._owner_id:
            view = utils.SlashColours(inter, is_owner=True)
            await inter.response.send_message('**Please use me master 😩**', view=view, ephemeral=True)
        else:
            view = utils.SlashColours(inter)
            await inter.response.send_message('**Please use the select menu below:**', view=view, ephemeral=True)

    @commands.slash_command(name='recommend', description='Recommend an anime/manga/webtoon/manhwa.')
    async def recommend(self, inter: AppCmdInter):
        await inter.response.send_modal(RecommendModal())


def setup(bot: Okiyu):
    bot.add_cog(SlashCommands(bot))
