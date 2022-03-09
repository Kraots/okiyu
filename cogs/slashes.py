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
                label='Type',
                custom_id='recommendation-type',
                placeholder='Anime/Webtoon/Manga/Manhwa/Manhua...',
                style=TextInputStyle.short,
                max_length=30
            ),
            TextInput(
                label='Title',
                custom_id='recommendation-title',
                placeholder='The title of your recommendation...',
                style=TextInputStyle.short,
                max_length=100
            ),
            TextInput(
                label='Synopsis',
                custom_id='recommendation-synopsis',
                placeholder='A short synopsis of your recommendation...',
                style=TextInputStyle.paragraph,
                max_length=1024
            ),
            TextInput(
                label='Source/Website to watch/read it on',
                custom_id='recommendation-source',
                placeholder='The link to a website where to watch/read this recommendation...',
                style=TextInputStyle.short,
                max_length=300
            ),
            TextInput(
                label='Status',
                custom_id='recommendation-status',
                placeholder='Ongoing/Canceled/Hiatus...',
                style=TextInputStyle.short,
                max_length=15
            )
        ]
        super().__init__(
            title='Make Recommendation',
            components=components
        )

    async def callback(self, inter: ModalInteraction):
        channel = inter.guild.get_channel(utils.Channels.recommendations)
        values_ = inter.text_values.values()
        fields = ['Type', 'Title', 'Synopsis', 'Source/Website to watch/read it on', 'Status']
        values = zip(fields, values_)
        em = Embed(
            color=inter.author.color,
        )
        for k, v in values:
            em.add_field(
                k,
                v,
                inline=False
            )
        em.set_footer(
            text=f'Recommendation by: {utils.format_name(inter.author)}',
            icon_url=inter.author.display_avatar
        )
        m = await channel.send(embed=em, view=utils.TrashButtonDelete())
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
