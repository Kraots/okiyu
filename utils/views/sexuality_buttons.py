import disnake

all_sexuality_roles = (
    938433150906937384, 938433151359922247, 938433151917772810,
    938433152228130867, 938433153054425131, 938433153398366248,
    938433153540968489
)

sexuality_roles = {
    'okiyu:sexuality_roles:Straight': 938433150906937384, 'okiyu:sexuality_roles:Bisexual': 938433151359922247,
    'okiyu:sexuality_roles:Gay': 938433151917772810, 'okiyu:sexuality_roles:Lesbian': 938433152228130867,
    'okiyu:sexuality_roles:Asexual': 938433153054425131, 'okiyu:sexuality_roles:Queer': 938433153398366248,
    'okiyu:sexuality_roles:Other-Sexuality': 938433153540968489
}

__all__ = (
    'SexualityButtonRoles',
    'all_sexuality_roles',
)


class SexualityButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Straight', custom_id='okiyu:sexuality_roles:Straight', row=0, style=disnake.ButtonStyle.blurple)
    async def Straight(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Gay', custom_id='okiyu:sexuality_roles:Gay', row=0, style=disnake.ButtonStyle.blurple)
    async def Gay(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Lesbian', custom_id='okiyu:sexuality_roles:Lesbian', row=0, style=disnake.ButtonStyle.blurple)
    async def Lesbian(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Bisexual', custom_id='okiyu:sexuality_roles:Bisexual', row=1, style=disnake.ButtonStyle.blurple)
    async def Bisexual(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Asexual', custom_id='okiyu:sexuality_roles:Asexual', row=1, style=disnake.ButtonStyle.blurple)
    async def Asexual(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Queer', custom_id='okiyu:sexuality_roles:Queer', row=1, style=disnake.ButtonStyle.blurple)
    async def Queer(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Other Sexuality', custom_id='okiyu:sexuality_roles:Other-Sexuality', row=2, style=disnake.ButtonStyle.blurple)
    async def Other_Sexuality(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_sexuality_roles]
        roles.append(interaction.guild.get_role(sexuality_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Sexuality role update.')
        await interaction.response.send_message(f'I have changed your sexuality role to `{button.label}`', ephemeral=True)
