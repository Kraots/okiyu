import disnake

all_pronouns_roles = (
    928682922112864266, 928682922465181736, 928682922968481892,
    928682923446652928, 928682923895443467
)

pronouns_roles = {
    'ukiyo:pronouns_roles:he_him': 928682922112864266, 'ukiyo:pronouns_roles:she_her': 928682922465181736,
    'ukiyo:pronouns_roles:they_them': 928682922968481892, 'ukiyo:pronouns_roles:he_they': 928682923446652928,
    'ukiyo:pronouns_roles:she_they': 928682923895443467
}

__all__ = (
    'PronounsButtonRoles',
    'all_pronouns_roles',
)


class PronounsButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='He/Him', custom_id='ukiyo:pronouns_roles:he_him', row=0, style=disnake.ButtonStyle.blurple)
    async def _he_him(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_pronouns_roles]
        roles.append(interaction.guild.get_role(pronouns_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Pronouns role update.')
        await interaction.response.send_message(f'I have changed your pronouns role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='She/Her', custom_id='ukiyo:pronouns_roles:she_her', row=0, style=disnake.ButtonStyle.blurple)
    async def _she_her(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_pronouns_roles]
        roles.append(interaction.guild.get_role(pronouns_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Pronouns role update.')
        await interaction.response.send_message(f'I have changed your pronouns role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='They/Them', custom_id='ukiyo:pronouns_roles:they_them', row=0, style=disnake.ButtonStyle.blurple)
    async def _they_them(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_pronouns_roles]
        roles.append(interaction.guild.get_role(pronouns_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Pronouns role update.')
        await interaction.response.send_message(f'I have changed your pronouns role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='He/They', custom_id='ukiyo:pronouns_roles:he_they', row=1, style=disnake.ButtonStyle.blurple)
    async def _he_they(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_pronouns_roles]
        roles.append(interaction.guild.get_role(pronouns_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Pronouns role update.')
        await interaction.response.send_message(f'I have changed your pronouns role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='She/They', custom_id='ukiyo:pronouns_roles:she_they', row=1, style=disnake.ButtonStyle.blurple)
    async def _she_they(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_pronouns_roles]
        roles.append(interaction.guild.get_role(pronouns_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Pronouns role update.')
        await interaction.response.send_message(f'I have changed your pronouns role to `{button.label}`', ephemeral=True)
