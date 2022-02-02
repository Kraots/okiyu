import disnake

all_colour_roles = (
    913316657026437150, 913316657844346921, 913316658821603328, 913316657903063041,
    913316659119407114, 913316659215880223, 913316659652079616, 913316654962847784,
    913316656309223484, 913316655776542800, 913316655512317962, 913316655084486727,
    913316657089380354, 913316655843659827, 913316659731787858, 913316656233734145,
    913316660277022730, 913316657550745610, 913316658519609394, 913316660163772477  # The last one is the owner only red
)

colour_roles = {
    'okiyu:colour_roles:Illusion': 913316657026437150, 'okiyu:colour_roles:Black': 913316657844346921,
    'okiyu:colour_roles:Screaming_Green': 913316658821603328, 'okiyu:colour_roles:Electric_Violet': 913316657903063041,
    'okiyu:colour_roles:Red_Orange': 913316659119407114, 'okiyu:colour_roles:Dodger_Blue': 913316659215880223,
    'okiyu:colour_roles:Spring_Green': 913316659652079616, 'okiyu:colour_roles:Madang': 913316654962847784,
    'okiyu:colour_roles:Perfume': 913316656309223484, 'okiyu:colour_roles:Ice_Cold': 913316655776542800,
    'okiyu:colour_roles:Primrose': 913316655512317962, 'okiyu:colour_roles:Orchid': 913316655084486727,
    'okiyu:colour_roles:Mandys_Pink': 913316657089380354, 'okiyu:colour_roles:Perano': 913316655843659827,
    'okiyu:colour_roles:Turquoise': 913316659731787858, 'okiyu:colour_roles:Wewak': 913316656233734145,
    'okiyu:colour_roles:Sunshade': 913316660277022730, 'okiyu:colour_roles:White': 913316657550745610,
    'okiyu:colour_roles:Broom': 913316658519609394
}

__all__ = (
    'ColourButtonRoles',
    'all_colour_roles',
)


class ColourButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Illusion', custom_id='okiyu:colour_roles:Illusion', emoji='<:illusion:938412173846270004>')
    async def Illusion(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Black', custom_id='okiyu:colour_roles:Black', emoji='<:black:938412174785785886>')
    async def Black(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Screaming Green', custom_id='okiyu:colour_roles:Screaming_Green', emoji='<:screaming_green:938412175763050547>')
    async def Screaming_Green(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Electric Violet', custom_id='okiyu:colour_roles:Electric_Violet', emoji='<:electric_violet:938412176723558431>')
    async def Electric_Violet(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Red Orange', custom_id='okiyu:colour_roles:Red_Orange', emoji='<:red_orange:938412177944088647>')
    async def Red_Orange(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Dodger Blue', custom_id='okiyu:colour_roles:Dodger_Blue', emoji='<:dodger_blue:938412178808135720>')
    async def Dodger_Blue(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Spring Green', custom_id='okiyu:colour_roles:Spring_Green', emoji='<:spring_green:938412179290460191>')
    async def Spring_Green(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Madang', custom_id='okiyu:colour_roles:Madang', emoji='<:madang:938412180511006720>')
    async def Madang(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Perfume', custom_id='okiyu:colour_roles:Perfume', emoji='<:perfume:938412181534437446>')
    async def Perfume(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Ice Cold', custom_id='okiyu:colour_roles:Ice_Cold', emoji='<:ice_cold:938412182411034654>')
    async def Ice_Cold(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Primrose', custom_id='okiyu:colour_roles:Primrose', emoji='<:primrose:938412183262478377>')
    async def Primrose(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Orchid', custom_id='okiyu:colour_roles:Orchid', emoji='<:orchid:938412192196350003>')
    async def Orchid(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Mandys Pink', custom_id='okiyu:colour_roles:Mandys_Pink', emoji='<:mandys_pink:938412184302657566>')
    async def Mandys_Pink(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Perano', custom_id='okiyu:colour_roles:Perano', emoji='<:perano:938412185762291812>')
    async def Perano(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Turquoise', custom_id='okiyu:colour_roles:Turquoise', emoji='<:turquoise:938412186924109874>')
    async def Turquoise(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Wewak', custom_id='okiyu:colour_roles:Wewak', emoji='<:wewak:938412188165632010>')
    async def Wewak(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Sunshade', custom_id='okiyu:colour_roles:Sunshade', emoji='<:sunshade:938412189172265050>')
    async def Sunshade(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='White', custom_id='okiyu:colour_roles:White', emoji='<:white:886669988558176306>')
    async def White(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Broom', custom_id='okiyu:colour_roles:Broom', emoji='<:broom:938412190996774974>')
    async def Broom(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        _roles = [role for role in interaction.author.roles if role.id not in all_colour_roles]
        _roles.append(interaction.guild.get_role(colour_roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)
