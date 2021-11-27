import disnake

all_sexuality_roles = (
    913771961845424159, 913771961530851368, 913771961249828964,
    913771961002364948, 913771960725549096, 913771960343867402,
    913771959987372073
)

sexuality_roles = {
    'ukiyo:sexuality_roles:Other-Sexuality': 913771961845424159, 'ukiyo:sexuality_roles:Queer': 913771961530851368,
    'ukiyo:sexuality_roles:Asexual': 913771961249828964, 'ukiyo:sexuality_roles:Bisexual': 913771961002364948,
    'ukiyo:sexuality_roles:Lesbian': 913771960725549096, 'ukiyo:sexuality_roles:Gay': 913771960343867402,
    'ukiyo:sexuality_roles:Straight': 913771959987372073
}

__all__ = (
    'SexualityButtonRoles',
    'all_sexuality_roles',
)


class SexualityButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Straight', custom_id='ukiyo:sexuality_roles:Straight', row=0, style=disnake.ButtonStyle.blurple)
    async def Straight(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Gay', custom_id='ukiyo:sexuality_roles:Gay', row=0, style=disnake.ButtonStyle.blurple)
    async def Gay(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Lesbian', custom_id='ukiyo:sexuality_roles:Lesbian', row=0, style=disnake.ButtonStyle.blurple)
    async def Lesbian(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Bisexual', custom_id='ukiyo:sexuality_roles:Bisexual', row=1, style=disnake.ButtonStyle.blurple)
    async def Bisexual(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Asexual', custom_id='ukiyo:sexuality_roles:Asexual', row=1, style=disnake.ButtonStyle.blurple)
    async def Asexual(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Queer', custom_id='ukiyo:sexuality_roles:Queer', row=1, style=disnake.ButtonStyle.blurple)
    async def Queer(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Other Sexuality', custom_id='ukiyo:sexuality_roles:Other-Sexuality', row=2, style=disnake.ButtonStyle.blurple)
    async def Other_Sexuality(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)
