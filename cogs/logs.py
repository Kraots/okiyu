from typing import Union, Sequence
import asyncio
import datetime

import disnake
from disnake.ext import commands, tasks

import utils

from main import Ukiyo


# Webhook that sends a message in logs channel
async def send_webhook(em: disnake.Embed, bot: Ukiyo):
    webhook = await bot.get_webhook(
        bot.get_channel(913332408537976892),
        avatar=bot.user.display_avatar
    )
    if isinstance(em, disnake.Embed):
        await webhook.send(embed=em)
    else:
        count = 0
        embeds = []
        for embed in em:
            embeds.append(embed)
            count += 1
            if count == 10:
                await webhook.send(embeds=embeds)
                count = 0
                embeds = []
        else:
            if count != 0:
                await webhook.send(embeds=embeds)
                embeds = []


class Logs(commands.Cog):
    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.send_embeds.start()
        self.embeds = []

    @tasks.loop(seconds=15.0)
    async def send_embeds(self):
        if len(self.embeds) != 0:
            try:
                await send_webhook(self.embeds, self.bot)
            except Exception:
                pass
            self.embeds = []

    @commands.Cog.listener()
    async def on_user_update(self, before: disnake.User, after: disnake.User):
        em = disnake.Embed(
            description=f'**{after.mention} updated their profile:**',
            timestamp=datetime.datetime.utcnow(),
            color=disnake.Color.yellow()
        )
        em.set_author(name=before, icon_url=before.display_avatar)
        em.set_thumbnail(url=after.display_avatar)
        em.set_footer(text=f'User ID: {after.id}')

        if before.name != after.name:
            em.add_field(name='Username', value=f'`{before.name}` **->** `{after.name}`', inline=False)
        if before.discriminator != after.discriminator:
            em.add_field(name='Discriminator', value=f'`#{before.discriminator}` **->** `#{after.discriminator}`', inline=False)
        if before.avatar != after.avatar:
            em.add_field(name='Avatar', value=f'[`Before`]({before.display_avatar}) -> [`After`]({after.display_avatar})', inline=False)

        if len(em.fields) != 0:
            self.embeds.append(em)

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        if before.guild.id != 913310006814859334:
            return

        em = disnake.Embed(timestamp=datetime.datetime.utcnow(), color=disnake.Color.yellow())
        em.set_author(name=before, icon_url=before.display_avatar)
        em.set_thumbnail(url=after.display_avatar)
        em.set_footer(text=f'Member ID: {after.id}')

        if before.nick != after.nick:
            em.add_field(name='Nickname', value=f'`{before.nick}` **->** `{after.nick}`', inline=False)
        if before.roles != after.roles:
            removed_roles = []
            added_roles = []
            for role in before.roles:
                if role not in after.roles:
                    removed_roles.append(role)
            for role in after.roles:
                if role not in before.roles:
                    added_roles.append(role)
            if len(added_roles) != 0:
                em.add_field(name=r'\✅ Added Roles', value=', '.join([role.name for role in added_roles]), inline=False)
            if len(removed_roles) != 0:
                em.add_field(name=r'\❌ Removed Roles', value=', '.join([role.name for role in removed_roles]), inline=False)

        if len(em.fields) != 0:
            self.embeds.append(em)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if member.guild.id != 913310006814859334:
            return

        em = disnake.Embed(description=f'📥 **{member.mention} joined the server**', timestamp=datetime.datetime.utcnow(), color=disnake.Color.green())
        em.set_author(name=member, icon_url=member.display_avatar)
        em.set_thumbnail(url=member.display_avatar)
        em.set_footer(text=f'Member ID: {member.id}')
        em.add_field(name='Account Creation', value=str(utils.human_timedelta(member.created_at)))

        self.embeds.append(em)

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        if member.guild.id != 913310006814859334:
            return

        em = disnake.Embed(description=f'📤 **{member.mention} left the server**', timestamp=datetime.datetime.utcnow(), color=disnake.Color.red())
        em.set_author(name=member, icon_url=member.display_avatar)
        em.set_thumbnail(url=member.display_avatar)
        em.set_footer(text=f'User ID: {member.id}')

        await asyncio.sleep(1)
        await send_webhook(em, self.bot)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: disnake.Guild, member: Union[disnake.Member, disnake.User]):
        if guild.id != 913310006814859334:
            return

        em = disnake.Embed(description=f'👮‍♂️🔒 **{member.mention} was banned**', timestamp=datetime.datetime.utcnow(), color=disnake.Color.red())
        em.set_author(name=member, icon_url=member.display_avatar)
        em.set_thumbnail(url=member.display_avatar)
        em.set_footer(text=f'User ID: {member.id}')

        await asyncio.sleep(1)
        await send_webhook(em, self.bot)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: disnake.Guild, user: disnake.User):
        em = disnake.Embed(description=f'👮‍♂️🔓 **{user.mention} was unbanned**', timestamp=datetime.datetime.utcnow(), color=disnake.Color.green())
        em.set_author(name=user, icon_url=user.display_avatar)
        em.set_thumbnail(url=user.display_avatar)
        em.set_footer(text=f'User ID: {user.id}')

        await send_webhook(em, self.bot)

    @commands.Cog.listener()
    async def on_guild_update(self, before: disnake.Guild, after: disnake.Guild):
        if before.id != 913310006814859334:
            return

        em = disnake.Embed(color=disnake.Color.yellow(), timestamp=datetime.datetime.utcnow())
        if before.name != after.name:
            em.description = f'**Name Changed**\n`{before.name}` **->** `{after.name}`'
            em.set_thumbnail(url=after.icon.url)
            em.title = 'Guild Updated'
            self.embeds.append(em)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: disnake.Role):
        if role.guild.id != 913310006814859334:
            return

        em = disnake.Embed(title=f'Role Created: {role.name}', color=disnake.Color.green(), timestamp=datetime.datetime.utcnow())
        em.add_field(name='Permissions', value=', '.join((perm[0].replace('_', ' ') for perm in (p for p in role.permissions) if perm[1] is True)))

        self.embeds.append(em)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: disnake.Role):
        if role.guild.id != 913310006814859334:
            return

        em = disnake.Embed(title=f'Role Deleted: {role.name}', color=disnake.Color.red(), timestamp=datetime.datetime.utcnow())
        em.add_field(name='Colour', value=f'[`{role.colour}`](https://www.color-hex.com/color/{str(role.colour).replace("#", "")})')
        em.add_field(name='Hoisted', value='No' if role.hoist is False else 'Yes')
        em.add_field(name='Mentionable', value='No' if role.mentionable is False else True)
        em.add_field(name='Permissions', value=', '.join((perm[0].replace('_', ' ') for perm in (p for p in role.permissions) if perm[1] is True)))
        em.set_footer(text=f'Role ID: {role.id}')

        self.embeds.append(em)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: disnake.Role, after: disnake.Role):
        if before.guild.id != 913310006814859334:
            return

        em = disnake.Embed(
            title=f'Role Updated: {after.name}',
            description=f'`{before.name}` has been updated',
            color=disnake.Color.yellow(),
            timestamp=datetime.datetime.utcnow()
        )
        em.set_footer(text=f'Role ID: {after.id}')
        em.set_thumbnail(url=before.guild.icon.url)

        if before.name != after.name:
            em.add_field(name='Name', value=f'`{before.name}` **->** `{after.name}`', inline=False)
        if before.color != after.color:
            em.add_field(name='Colour', value=f'`{before.colour}` **->** `{after.colour}`', inline=False)
        if before.hoist != after.hoist:
            em.add_field(name='Hoisted', value=f'`{before.hoist}` **->** `{after.hoist}`', inline=False)
        if before.mentionable != after.mentionable:
            em.add_field(name='Mentionable', value=f'`{before.mentionable}` **->** `{after.mentionable}`', inline=False)
        if before.permissions != after.permissions:
            added_perms = []
            removed_perms = []

            old_perms = {}
            for perm in before.permissions:
                old_perms[perm[0]] = perm[1]

            for perm in after.permissions:
                if perm[1] != old_perms[perm[0]]:
                    if perm[1] is False:
                        removed_perms.append(perm[0].replace('_', ' ').title())
                    elif perm[1] is True:
                        added_perms.append(perm[0].replace('_', ' ').title())

            if len(added_perms) != 0:
                em.add_field(name=r'\✅ Added Permissions', value=f'`{"`, `".join(added_perms)}`', inline=False)
            if len(removed_perms) != 0:
                em.add_field(name=r'\❌ Removed Permissions', value=f'`{"`, `".join(removed_perms)}`', inline=False)

        if len(em.fields) != 0:
            self.embeds.append(em)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: disnake.Guild, before: Sequence[disnake.Emoji], after: Sequence[disnake.Emoji]):
        if guild.id != 913310006814859334:
            return

        em = disnake.Embed(title='Emoji Updated', color=disnake.Color.yellow(), timestamp=datetime.datetime.utcnow())
        added_emoji = None
        removed_emoji = None
        old_name = None
        new_name = None
        for emoji in before:
            if emoji.id in (e.id for e in after):
                if emoji.name != ''.join([e.name for e in after if e.id == emoji.id]):
                    old_name = emoji.name
                    new_name = ''.join([e.name for e in after if e.id == emoji.id])
                    break
        for emoji in before:
            if emoji.id not in (e.id for e in after):
                removed_emoji = (emoji.name, emoji.url)
                break
        for emoji in after:
            if emoji.id not in (e.id for e in before):
                added_emoji = emoji
                break
        if new_name is not None:
            em.add_field(name='Emoji Name Changed', value=f'`{old_name}` **->** `{new_name}`', inline=False)
        if added_emoji is not None:
            em.add_field(name=r'\✅ Added Emoji', value=str(added_emoji), inline=False)
            em.set_thumbnail(url=emoji.url)
        if removed_emoji is not None:
            em.add_field(name=r'\❌ Removed Emoji', value=f'[`{removed_emoji[0]}`]({removed_emoji[1]})', inline=False)
            em.set_thumbnail(url=removed_emoji[1])

        if len(em.fields) != 0:
            self.embeds.append(em)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: disnake.abc.GuildChannel):
        if channel.guild.id != 913310006814859334:
            return

        em = disnake.Embed(title='Channel Created', color=disnake.Color.green(), timestamp=datetime.datetime.utcnow())
        em.set_footer(text=f'Channel ID: {channel.id}')
        em.add_field(name='Name', value=f'`{channel.name}`', inline=False)
        em.add_field(name='Type', value=f'`{str(channel.type).title()} Channel`', inline=False)

        self.embeds.append(em)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: disnake.abc.GuildChannel):
        if channel.guild.id != 913310006814859334:
            return

        em = disnake.Embed(title='Channel Deleted', color=disnake.Color.red(), timestamp=datetime.datetime.utcnow())
        em.add_field(name='Name', value=f'`{channel.name}`', inline=False)
        em.add_field(name='Type', value=f'`{str(channel.type).title()} Channel`', inline=False)

        self.embeds.append(em)

    @commands.Cog.listener('on_guild_channel_update')
    async def mem_perm_add(self, before: disnake.abc.GuildChannel, after: disnake.abc.GuildChannel):
        if before.guild.id != 913310006814859334:
            return

        em = disnake.Embed(title=f'Channel Updated: {before.name}', color=disnake.Color.yellow(), timestamp=datetime.datetime.utcnow())
        em.set_footer(text=f'Channel ID: {after.id}')
        if before.name != after.name:
            em.add_field(name='Name', value=f'`{before.name}` **->** `{after.name}`', inline=False)
        if before.overwrites != after.overwrites:
            added_overwrites = []
            removed_overwrites = []

            for overwrite in after.overwrites:
                if overwrite not in before.overwrites:
                    added_overwrites.append(f'`{overwrite.name}`')
            for overwrite in before.overwrites:
                if overwrite not in after.overwrites:
                    removed_overwrites.append(f'`{overwrite.name}`')
            if len(added_overwrites) != 0:
                em.description = f'Added permissions for {", ".join(added_overwrites)}'
                em.color = disnake.Colour.green()
                self.embeds.append(em)
                return
            if len(removed_overwrites) != 0:
                em.description = f'Removed permissions for {", ".join(removed_overwrites)}'
                em.color = disnake.Colour.red()
                self.embeds.append(em)
                return

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: disnake.abc.GuildChannel, after: disnake.abc.GuildChannel):
        if before.guild.id != 913310006814859334:
            return

        em = disnake.Embed(title=f'Channel Updated: {before.name}', color=disnake.Color.yellow(), timestamp=datetime.datetime.utcnow())
        em.set_footer(text=f'Channel ID: {after.id}')
        if before.overwrites != after.overwrites:
            allowed_perms = []
            neutral_perms = []
            denied_perms = []
            old_perms = {}

            for k in before.overwrites:
                perms = {}
                for v in before.overwrites[k]:
                    perms[v[0]] = v[1]
                old_perms[k.id] = perms

            for k in after.overwrites:
                for v in after.overwrites[k]:
                    try:
                        if v[1] != old_perms[k.id][v[0]]:
                            em.description = f'Edited permissions for `{k}`'
                            if v[1] is False:
                                denied_perms.append(v[0])
                            elif v[1] is None:
                                neutral_perms.append(v[0])
                            elif v[1] is True:
                                allowed_perms.append(v[0])
                    except KeyError:
                        pass

            if len(allowed_perms) != 0:
                em.add_field(name=r'\✅ Allowed Perms', value=', '.join(allowed_perms), inline=False)
            if len(neutral_perms) != 0:
                em.add_field(name='⧄ Neutral Perms', value=', '.join(neutral_perms), inline=False)
            if len(denied_perms) != 0:
                em.add_field(name=r'\❌ Denied Perms', value=', '.join(denied_perms), inline=False)

        if len(em.fields) != 0:
            self.embeds.append(em)


def setup(bot: Ukiyo):
    bot.add_cog(Logs(bot))
