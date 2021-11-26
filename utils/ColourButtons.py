import disnake

all_roles = [
    913316657026437150, 913316657844346921, 913316658821603328, 913316657903063041,
    913316659119407114, 913316659215880223, 913316659652079616, 913316654962847784,
    913316656309223484, 913316655776542800, 913316655512317962, 913316655084486727,
    913316657089380354, 913316655843659827, 913316659731787858, 913316656233734145,
    913316660277022730, 913316657550745610, 913316658519609394
]

roles = {
    'ukiyo:colour_roles:Illusion': 913316657026437150, 'ukiyo:colour_roles:Black': 913316657844346921,
    'ukiyo:colour_roles:Screaming_Green': 913316658821603328, 'ukiyo:colour_roles:Electric_Violet': 913316657903063041,
    'ukiyo:colour_roles:Red_Orange': 913316659119407114, 'ukiyo:colour_roles:Dodger_Blue': 913316659215880223,
    'ukiyo:colour_roles:Spring_Green': 913316659652079616, 'ukiyo:colour_roles:Madang': 913316654962847784,
    'ukiyo:colour_roles:Perfume': 913316656309223484, 'ukiyo:colour_roles:Ice_Cold': 913316655776542800,
    'ukiyo:colour_roles:Primrose': 913316655512317962, 'ukiyo:colour_roles:Orchid': 913316655084486727,
    'ukiyo:colour_roles:Mandys_Pink': 913316657089380354, 'ukiyo:colour_roles:Perano': 913316655843659827,
    'ukiyo:colour_roles:Turquoise': 913316659731787858, 'ukiyo:colour_roles:Wewak': 913316656233734145,
    'ukiyo:colour_roles:Sunshade': 913316660277022730, 'ukiyo:colour_roles:White': 913316657550745610,
    'ukiyo:colour_roles:Broom': 913316658519609394
}

__all__ = (
    'ColourButtonRoles',
)


class ColourButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Illusion', custom_id='ukiyo:colour_roles:Illusion', emoji='<:illusion:886669987660574803>')
    async def Illusion(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Black', custom_id='ukiyo:colour_roles:Black', emoji='<:black:886669987752841216>')
    async def Black(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Screaming Green', custom_id='ukiyo:colour_roles:Screaming_Green', emoji='<:screaming_green:886669987769626636>')
    async def Screaming_Green(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Electric Violet', custom_id='ukiyo:colour_roles:Electric_Violet', emoji='<:electric_violet:886669987798986804>')
    async def Electric_Violet(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Red Orange', custom_id='ukiyo:colour_roles:Red_Orange', emoji='<:red_orange:886669987798999062>')
    async def Red_Orange(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Dodger Blue', custom_id='ukiyo:colour_roles:Dodger_Blue', emoji='<:dodger_blue:886669987916427294>')
    async def Dodger_Blue(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Spring Green', custom_id='ukiyo:colour_roles:Spring_Green', emoji='<:spring_green:886669987924815923>')
    async def Spring_Green(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Madang', custom_id='ukiyo:colour_roles:Madang', emoji='<:madang:886669987991941181>')
    async def Madang(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Perfume', custom_id='ukiyo:colour_roles:Perfume', emoji='<:perfume:886669988008710174>')
    async def Perfume(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Ice Cold', custom_id='ukiyo:colour_roles:Ice_Cold', emoji='<:ice_cold:886669988008710194>')
    async def Ice_Cold(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Primrose', custom_id='ukiyo:colour_roles:Primrose', emoji='<:primrose:886669988008718336>')
    async def Primrose(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Orchid', custom_id='ukiyo:colour_roles:Orchid', emoji='<:orchid:886675375185350696>')
    async def Orchid(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Mandys Pink', custom_id='ukiyo:colour_roles:Mandys_Pink', emoji='<:mandys_pink:886669988038062154>')
    async def Mandys_Pink(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Perano', custom_id='ukiyo:colour_roles:Perano', emoji='<:perano:886669988063227965>')
    async def Perano(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Turquoise', custom_id='ukiyo:colour_roles:Turquoise', emoji='<:turquoise:886669988176470046>')
    async def Turquoise(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Wewak', custom_id='ukiyo:colour_roles:Wewak', emoji='<:wewak:886669988214243379>')
    async def Wewak(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Sunshade', custom_id='ukiyo:colour_roles:Sunshade', emoji='<:sunshade:886669988289720410>')
    async def Sunshade(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='White', custom_id='ukiyo:colour_roles:White', emoji='<:white:886669988558176306>')
    async def White(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Broom', custom_id='ukiyo:colour_roles:Broom', emoji='<:broom:886669989636100156>')
    async def Broom(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        _roles = [role for role in interaction.author.roles if role.id not in all_roles]
        _roles.append(interaction.guild.get_role(roles[button.custom_id]))
        await interaction.author.edit(roles=_roles, reason='Colour role update.')
        await interaction.response.send_message(f'I have changed your colour to `{button.label}`', ephemeral=True)
