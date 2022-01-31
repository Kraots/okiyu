import disnake

game_roles = {
    'Apex': 937764676094292118, 'League of Legends': 937764676526276678, 'Genshin': 937764676861829170,
    'Grand Theft Auto V': 937764677306421279, 'Valorant': 937764677822345308, 'CS:GO': 937764678346629181,
    'Rocket League': 937764678837370900, 'Dead by Daylight': 937764679252594718, 'Minecraft': 937764679718146118,
    'Roblox': 937764679974023179, 'Fortnite': 937764680267620404
}

__all__ = (
    'GameButtonRoles',
)


class GameButtonRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def handle_role(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        roles = [r.id for r in inter.author.roles]
        role_id = game_roles[button.label]
        if role_id in roles:
            roles.remove(role_id)
            roles = [inter.guild.get_role(role) for role in roles]
            await inter.author.edit(roles=roles, reason='Game role update.')
            return await inter.send(f'I have removed `{button.label}` from your roles.', ephemeral=True)

        roles.append(role_id)
        roles = [inter.guild.get_role(role) for role in roles]
        await inter.author.edit(roles=roles, reason='Game role update.')
        return await inter.send(f'I have added `{button.label}` to your roles.', ephemeral=True)

    @disnake.ui.button(label='Apex', custom_id='ukiyo:game_roles:apex', row=0, style=disnake.ButtonStyle.blurple)
    async def apex(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='League of Legends', custom_id='ukiyo:game_roles:lol', row=0, style=disnake.ButtonStyle.blurple)
    async def lol(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Genshin', custom_id='ukiyo:game_roles:genshin', row=0, style=disnake.ButtonStyle.blurple)
    async def genshin(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Grand Theft Auto V', custom_id='ukiyo:game_roles:gtav', row=1, style=disnake.ButtonStyle.blurple)
    async def gtav(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Valorant', custom_id='ukiyo:game_roles:valo', row=1, style=disnake.ButtonStyle.blurple)
    async def valo(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='CS:GO', custom_id='ukiyo:game_roles:csgo', row=1, style=disnake.ButtonStyle.blurple)
    async def csgo(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Rocket League', custom_id='ukiyo:game_roles:rocket_league', row=2, style=disnake.ButtonStyle.blurple)
    async def rocket_league(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Dead by Daylight', custom_id='ukiyo:game_roles:dbd', row=2, style=disnake.ButtonStyle.blurple)
    async def dbd(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Minecraft', custom_id='ukiyo:game_roles:mc', row=2, style=disnake.ButtonStyle.blurple)
    async def mc(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Roblox', custom_id='ukiyo:game_roles:rblx', row=3, style=disnake.ButtonStyle.blurple)
    async def rblx(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)

    @disnake.ui.button(label='Fortnite', custom_id='ukiyo:game_roles:fortnite', row=3, style=disnake.ButtonStyle.blurple)
    async def fortnite(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await self.handle_role(button, inter)
