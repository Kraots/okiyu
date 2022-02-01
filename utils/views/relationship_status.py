import disnake

all_relationship_status_roles = (
    913789939668385822, 913789939961954304
)

relationship_status_roles = {
    'okiyu:relationship_status_roles:Single': 913789939668385822,
    'okiyu:relationship_status_roles:Taken': 913789939961954304
}

__all__ = (
    'RelationshipStatusButtonRoles',
    'all_relationship_status_roles',
)


class RelationshipStatusButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='Single', custom_id='okiyu:relationship_status_roles:Single', row=0, style=disnake.ButtonStyle.blurple)
    async def Male(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_relationship_status_roles]
        roles.append(interaction.guild.get_role(relationship_status_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Relationship status role update.')
        await interaction.response.send_message(f'I have changed your relationship status role to `{button.label}`', ephemeral=True)

    @disnake.ui.button(label='Taken', custom_id='okiyu:relationship_status_roles:Taken', row=0, style=disnake.ButtonStyle.blurple)
    async def Female(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        roles = [role for role in interaction.author.roles if role.id not in all_relationship_status_roles]
        roles.append(interaction.guild.get_role(relationship_status_roles[button.custom_id]))
        await interaction.author.edit(roles=roles, reason='Relationship status role update.')
        await interaction.response.send_message(f'I have changed your relationship status role to `{button.label}`', ephemeral=True)
