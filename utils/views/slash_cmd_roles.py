import disnake

import utils

__all__ = (
    'SlashColours',
)

all_colours_dict = {
    'Illusion': 913316657026437150, 'Black': 913316657844346921, 'Screaming Green': 913316658821603328,
    'Electric Violet': 913316657903063041, 'Red Orange': 913316659119407114, 'Dodger Blue': 913316659215880223,
    'Spring Green': 913316659652079616, 'Madang': 913316654962847784, 'Perfume': 913316656309223484,
    'Ice Cold': 913316655776542800, 'Primrose': 913316655512317962, 'Orchid': 913316655084486727,
    'Mandys Pink': 913316657089380354, 'Perano': 913316655843659827, 'Turquoise': 913316659731787858,
    'Wewak': 913316656233734145, 'Sunshade': 913316660277022730, 'White': 913316657550745610,
    'Broom': 913316658519609394, 'Owner Only Red': 913316660163772477
}


class SlashColoursSelect(disnake.ui.Select['SlashColours']):
    def __init__(self, *, is_owner: bool, placeholder: str = 'Select a colour...'):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1)
        self.is_owner = is_owner
        self._fill_options()

    def _fill_options(self):
        if self.is_owner:
            self.add_option(label='Owner Only Red', emoji='<:owner_only_red:888082854695829574>')
        self.add_option(label='Illusion', emoji='<:illusion:886669987660574803>')
        self.add_option(label='Black', emoji='<:black:886669987752841216>')
        self.add_option(label='Screaming Green', emoji='<:screaming_green:886669987769626636>')
        self.add_option(label='Electric Violet', emoji='<:electric_violet:886669987798986804>')
        self.add_option(label='Red Orange', emoji='<:red_orange:886669987798999062>')
        self.add_option(label='Dodger Blue', emoji='<:dodger_blue:886669987916427294>')
        self.add_option(label='Spring Green', emoji='<:spring_green:886669987924815923>')
        self.add_option(label='Madang', emoji='<:madang:886669987991941181>')
        self.add_option(label='Perfume', emoji='<:perfume:886669988008710174>')
        self.add_option(label='Ice Cold', emoji='<:ice_cold:886669988008710194>')
        self.add_option(label='Primrose', emoji='<:primrose:886669988008718336>')
        self.add_option(label='Orchid', emoji='<:orchid:886675375185350696>')
        self.add_option(label='Mandys Pink', emoji='<:mandys_pink:886669988038062154>')
        self.add_option(label='Perano', emoji='<:perano:886669988063227965>')
        self.add_option(label='Turquoise', emoji='<:turquoise:886669988176470046>')
        self.add_option(label='Wewak', emoji='<:wewak:886669988214243379>')
        self.add_option(label='Sunshade', emoji='<:sunshade:886669988289720410>')
        self.add_option(label='White', emoji='<:white:886669988558176306>')
        self.add_option(label='Broom', emoji='<:broom:886669989636100156>')

    async def callback(self, interaction: disnake.MessageInteraction):
        assert self.view is not None
        value = self.values[0]
        roles = [role for role in interaction.author.roles if role.id not in utils.all_colour_roles]
        roles.append(interaction.guild.get_role(all_colours_dict[value]))
        await interaction.author.edit(roles=roles, reason='Colour role update via select menu.')
        await interaction.response.edit_message(content=f'Changed your colour to `{value}`')


class SlashColours(disnake.ui.View):
    def __init__(self, inter, *, is_owner: bool = False):
        super().__init__(timeout=None)
        self.inter = inter
        placeholder = 'Select a colour master...' if is_owner is True else None
        self.add_item(SlashColoursSelect(is_owner=is_owner, placeholder=placeholder))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.inter.edit_message(view=self)
