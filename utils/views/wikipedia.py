import disnake
from disnake.ext import menus

import utils

import wikipedia

__all__ = (
    'WikiSelect',
    'FrontPageSource',
    'WikiView',
)


class WikiPageSource(menus.ListPageSource):
    def __init__(self, entries, title, title_url, footer, footer_icon):
        super().__init__(entries, per_page=1)
        self.initial_page = True
        self.entries = entries
        self.title = title
        self.title_url = title_url
        self.footer = footer
        self.footer_icon = footer_icon

    async def format_page(self, menu, entries: str):
        embed = disnake.Embed(title=self.title, url=self.title_url, color=utils.blurple)
        embed.set_footer(text=self.footer, icon_url=self.footer_icon)

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{maximum}')

        embed.description = entries.replace('=== ', '**').replace(' ===', '**').replace('== ', '**').replace(' ==', '**')
        return embed


class WikiSelect(disnake.ui.Select['WikiView']):
    def __init__(self, ctx: utils.Context, res: wikipedia.WikipediaPage):
        super().__init__(placeholder='Select a mode...', min_values=1, max_values=1)
        self.res = res
        self.ctx = ctx

        self.add_option(label='Content', description='The full content of the wiki page.')
        self.add_option(label='Summary', description='The summary of the wiki page.')

    async def callback(self, inter: disnake.MessageInteraction):
        assert self.view is not None
        value = self.values[0]
        kwargs = {
            'title': self.res.title,
            'title_url': self.res.url,
            'footer': self.ctx.author,
            'footer_icon': self.ctx.author.display_avatar
        }
        if value == 'Content':
            menu = WikiPageSource(
                [self.res.content[i: i + 4000] for i in range(0, len(self.res.content), 4000)],
                **kwargs
            )
        else:
            menu = WikiPageSource(
                [self.res.summary[i: i + 4000] for i in range(0, len(self.res.summary), 4000)],
                **kwargs
            )

        await self.view.rebind(menu, inter)


class FrontPageSource(menus.PageSource):
    def is_paginating(self) -> bool:
        # This forces the buttons to appear even in the front page
        return True

    def get_max_pages(self):
        # There's only one actual page in the front page
        # However we need at least 2 to show all the buttons
        return 2

    async def get_page(self, page_number: int):
        # The front page is a dummy
        self.index = page_number
        return self

    def format_page(self, menu, page):
        embed = disnake.Embed(
            description='Please select a category using the select menu from below to start.',
            color=utils.blurple
        )

        return embed


class WikiView(utils.RoboPages):
    def __init__(self, source: menus.PageSource, ctx: utils.Context):
        super().__init__(source, ctx=ctx, compact=True)

    async def rebind(self, source: menus.PageSource, interaction: disnake.Interaction) -> None:
        self.source = source
        self.current_page = 0

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        await interaction.response.edit_message(**kwargs, view=self)
