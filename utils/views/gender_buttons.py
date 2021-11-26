import disnake

all_gender_roles = (
    913771963099541524, 913771962835271820,
    913771962256482346, 913771962155810846,
    913771963346989117
)

gender_roles = {
    'ukiyo:gender_roles:Trans-Female': 913771963099541524, 'ukiyo:gender_roles:Trans-Male': 913771962835271820,
    'ukiyo:gender_roles:Female': 913771962256482346, 'ukiyo:gender_roles:Male': 913771962155810846,
    'ukiyo:gender_roles:Other-Gender': 913771963346989117
}

__all__ = (
    'GenderButtonRoles',
    'all_gender_roles',
)


class GenderButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Male', custom_id='ukiyo:gender_roles:Male', row=0, style=disnake.ButtonStyle.blurple)
    async def Male(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Female', custom_id='ukiyo:gender_roles:Female', row=0, style=disnake.ButtonStyle.blurple)
    async def Female(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Trans Male', custom_id='ukiyo:gender_roles:Trans-Male', row=1, style=disnake.ButtonStyle.blurple)
    async def Trans_Male(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Trans Female', custom_id='ukiyo:gender_roles:Trans-Female', row=1, style=disnake.ButtonStyle.blurple)
    async def Trans_Female(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Other Gender', custom_id='ukiyo:gender_roles:Other-Gender', row=2, style=disnake.ButtonStyle.blurple)
    async def Other_Gender(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_gender_roles]
        roles.append(interaction.guild.get_role(gender_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Gender role update.')
        await interaction.response.send_message(f'I have changed your gender role to `{button.label}`', ephemeral=True)
