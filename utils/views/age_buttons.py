import disnake

all_age_roles = (
    913771965553184768, 913771964949200907, 913771964718542914,
    913771964311666738, 913771963669958657, 913771963615424512
)

age_roles = {
    'okiyu:age_roles:19': 913771965553184768, 'okiyu:age_roles:18': 913771964949200907,
    'okiyu:age_roles:17': 913771964718542914, 'okiyu:age_roles:16': 913771964311666738,
    'okiyu:age_roles:15': 913771963669958657, 'okiyu:age_roles:14': 913771963615424512
}

__all__ = (
    'AgeButtonRoles',
    'all_age_roles',
)


class AgeButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='14', custom_id='okiyu:age_roles:14', row=0, style=disnake.ButtonStyle.blurple)
    async def _14(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='15', custom_id='okiyu:age_roles:15', row=0, style=disnake.ButtonStyle.blurple)
    async def _15(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='16', custom_id='okiyu:age_roles:16', row=0, style=disnake.ButtonStyle.blurple)
    async def _16(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='17', custom_id='okiyu:age_roles:17', row=1, style=disnake.ButtonStyle.blurple)
    async def _17(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='18', custom_id='okiyu:age_roles:18', row=1, style=disnake.ButtonStyle.blurple)
    async def _18(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='19', custom_id='okiyu:age_roles:19', row=1, style=disnake.ButtonStyle.blurple)
    async def _19(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_age_roles]
        roles.append(interaction.guild.get_role(age_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Age role update.')
        await interaction.response.send_message(f'I have changed your age role to `{button.label}`', ephemeral=True)
