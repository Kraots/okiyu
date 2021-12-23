import random
from datetime import datetime, timezone
from asyncio import TimeoutError, sleep
from dateutil.relativedelta import relativedelta

import disnake
from disnake.ext import commands, tasks

import utils
from utils import (
    Context,
    Game,
    Characters
)

from main import Ukiyo

# TOTAL_XP = (LVL, NEEDED_XP)
LEVELS = {
    0: (1, 500),
    500: (2, 1700),
    2200: (3, 3300),
    5500: (4, 7000),
    12500: (5, 10000),
    22500: (6, 15000),
    37500: (7, 0)
}


class _Game(commands.Cog, name='Game'):
    """This category shows the base command for the game commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.coin_emoji = '🪙'
        self.in_game = []

        self.boss_fight.start()
        self.last_message: disnake.Message = None

        self.streaks_check.start()

    @property
    def display_emoji(self) -> str:
        return self.coin_emoji

    @tasks.loop(seconds=3.0)
    async def streaks_check(self):
        dailys: list[Game] = await Game.find().sort('daily', 1).to_list(10)
        for data in dailys:
            date = data.daily + relativedelta(days=1)
            if date <= datetime.now():
                data.streak = 0
                await data.commit()

    async def get_user(self, uid: int) -> Game:
        data: Game = await Game.find_one({'_id': uid})
        if data is None:
            data = Game(
                id=uid,
                daily=datetime.now()
            )
            await data.commit()

        return data

    @commands.group(name='game', aliases=('g',), invoke_without_command=True, case_insensitive=True)
    async def base_game(self, ctx: Context):
        """Base command for all the `game` commands. To see the commands, please type `!help game`

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is True:
            await ctx.send_help('game')

    @base_game.group(name='coins', invoke_without_command=True, case_insensitive=True)
    async def game_coins(self, ctx: Context):
        """See how many coins you currently have.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx.author.id)
        em = disnake.Embed(
            color=utils.blurple,
            description=f'You currently have `{data.coins:,}` {self.coin_emoji}'
        )
        em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
        em.set_thumbnail(url=ctx.author.display_avatar)
        if data.daily <= datetime.now():
            em.set_footer(text='• You can claim your daily!')

        await ctx.reply(embed=em)

    @game_coins.command(name='set')
    @utils.is_owner()
    async def coins_set(self, ctx: Context, amount: str = '1,000', member: disnake.Member = None):
        """Set the coins for the member.

        `amount` **->** The amount of coins you wish to set.
        `member` **->** The member that you wish to set the coins for. Defaults to yourself.
        """

        amount = utils.format_num(amount)
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.reply('The amount must be a number.')

        member = member or ctx.author
        data = await self.get_user(member.id)
        data.coins = amount
        await data.commit()

        await ctx.reply(f'Successfully set the amount of coins for `{member}` to **{amount:,}** {self.coin_emoji}')

    @game_coins.command(name='add')
    @utils.is_owner()
    async def coins_add(self, ctx: Context, amount: str = '1,000', member: disnake.Member = None):
        """Add the coins to the member's existing coins.

        `amount` **->** The amount of coins you wish to add.
        `member` **->** The member that you wish to add the coins for. Defaults to yourself.
        """

        amount = utils.format_num(amount)
        try:
            amount = int(amount)
        except ValueError:
            return await ctx.reply('The amount must be a number.')

        member = member or ctx.author
        data = await self.get_user(member.id)
        data.coins += amount
        await data.commit()

        await ctx.reply(f'Successfully added **{amount:,}** {self.coin_emoji} to `{member}`')

    @base_game.command(name='daily')
    async def game_daily(self, ctx: Context):
        """Get your daily coins.
        One streak is `200` coins, which gets multiplied by the amount of streaks you have accumulated. That means that a 10 day streak is `2000` extra coins.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx.author.id)
        if data.daily > datetime.now():
            em = utils.fail_embed(
                'You cannot claim your daily yet! Please come back in '
                f'`{utils.human_timedelta(data.daily, suffix=False)}`',
            )
            return await ctx.reply(embed=em)

        coins = 2000 + (data.streak * 200)
        data.coins += coins
        data.streak += 1
        data.daily = datetime.now() + relativedelta(days=1)
        await data.commit()
        em = disnake.Embed(
            title='Daily Claimed',
            description=f'You have successfully claimed your daily and got `{coins}` {self.coin_emoji}',
            color=utils.green
        )
        em.set_footer(text=f'Current Streak: {data.streak - 1}')

        await ctx.reply(embed=em)

    @base_game.command(name='streak')
    async def game_streak(self, ctx: Context):
        """Check your current daily streak.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx.author.id)
        em = disnake.Embed(
            description=f'Your current daily streak is `{data.streak}`',
            color=utils.blurple
        )
        em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
        if data.daily <= datetime.now():
            em.set_footer(text='• You can claim your daily!')

        await ctx.reply(embed=em)

    @base_game.command(name='inventory', aliases=('inv',))
    async def game_inventory(self, ctx: Context):
        """Shows your inventory which contains all of the characters that you own.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx.author.id)
        if not data.characters:
            em = utils.fail_embed(
                'You do not own any characters! See `!game shop` to buy a crate.'
            )
            return await ctx.reply(embed=em)

        commons = []
        uncommons = []
        rares = []
        epics = []
        legendaries = []
        for character_name, xp in data.characters.items():
            _lvl = 0
            needed_xp = 0
            _curr = 0
            for k, v in LEVELS.items():
                if xp >= k:
                    _lvl = v[0]
                    needed_xp = v[1]
                    _curr = k
                else:
                    break
            if _lvl == 7:
                _xp = 'MAX'
                lvl = '7 (MAX)'
            else:
                _xp = str(xp - _curr) + '/' + str(needed_xp)
                lvl = _lvl

            character: Characters = await Characters.find_one({'_id': character_name})
            em = disnake.Embed(
                title=f'`{character.name.title()}`',
                description=f'*{character.description}*',
                color=utils.blurple
            )
            em.add_field('Level', lvl, inline=False)
            em.add_field('XP', _xp, inline=False)
            em.add_field('Attack (DMG)', f'{(character.lowest_dmg * _lvl):,} **-** {(character.highest_dmg * _lvl):,}')
            em.add_field('Health (HP)', f'{(character.hp * _lvl):,}')
            em.add_field('Rarity', f'{character.rarity_level * "✮"}({character.rarity_level})')

            if character.rarity_level == 1:
                commons.append(em)
            elif character.rarity_level == 2:
                uncommons.append(em)
            elif character.rarity_level == 3:
                rares.append(em)
            elif character.rarity_level == 4:
                epics.append(em)
            elif character.rarity_level == 5:
                legendaries.append(em)

        embeds = uncommons + commons + rares + epics + legendaries
        paginator = utils.EmbedPaginator(ctx, embeds)
        await paginator.start()

    @base_game.group(name='shop', invoke_without_command=True, case_insensitive=True)
    async def game_shop(self, ctx: Context):
        """The shop from which you can buy boxes that contain a character.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        em = disnake.Embed(title='Box Shop', color=utils.blurple)
        em.add_field(
            f'Common Box — 2,500 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮(1)',
            inline=False
        )
        em.add_field(
            f'Uncommon Box — 10,000 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮✮(2)',
            inline=False
        )
        em.add_field(
            f'Rare Box — 60,000 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮✮✮(3)',
            inline=False
        )
        em.add_field(
            f'Epic Box — 250,000 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮✮✮✮(4)',
            inline=False
        )
        em.add_field(
            f'Legendary Box — 750,000 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮✮✮✮✮(5)',
            inline=False
        )
        await ctx.better_reply(embed=em)

    @game_shop.command(name='buy')
    async def shop_buy(self, ctx: Context, box_rarity: str):
        """Buy and open a box.

        `box_rarity` **->** The rarity of the box that you wish to open.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        boxes = {
            'common': (1, 2500),
            'uncommon': (2, 60000),
            'rare': (3, 30000),
            'epic': (4, 250000),
            'legendary': (5, 750000)
        }
        box: tuple | None = boxes.get(box_rarity.lower())
        if box is None:
            em = utils.fail_embed('That box rarity does not exist.')
            return await ctx.reply(embed=em)

        data = await self.get_user(ctx.author.id)
        if data.coins < box[1]:
            em = utils.fail_embed('You don\'t have enough money to buy that box.')
            return await ctx.reply(embed=em)
        data.coins -= box[1]

        characters = await Characters.find({'rarity_level': box[0], 'obtainable': True}).to_list(100_000)
        if len(characters) == 0:
            em = utils.fail_embed('There currently are no characters of that rarity.')
            return await ctx.reply(embed=em)
        for i in range(3):
            random.shuffle(characters)
        character: Characters = random.choice(characters)

        fmt = 'an ' if box_rarity.startswith(('a', 'e')) else 'a '
        if character.name in data.characters:
            if data.characters[character.name] >= 37500:
                return await ctx.reply(
                    f'You bought **{fmt + box_rarity}** box and got the character `{character.name.title()}`.\n'
                    'Since you already own this character, and it is max level, you get your money back.'
                )
            data.characters[character.name] += 10
            await ctx.reply(
                f'You bought **{fmt + box_rarity}** box and got the character `{character.name.title()}`.\n'
                'Since you already own this character, you have been awarded **10xp** for it.'
            )
        else:
            data.characters[character.name] = 0
            await ctx.reply(
                f'You bought **{fmt + box_rarity}** box and got the character `{character.name.title()}`.'
            )
        await data.commit()

    @base_game.command(name='fight')
    @utils.lock()
    async def game_fight(self, ctx: Context, *, member: disnake.Member):
        """Challenge a member to a fight using one of your characters.

        `member` **->** The member you want to challenge.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        if member.id in self.in_game:
            em = utils.fail_embed(
                'That member is already fighting someone. Let them finish their current fight first.'
            )
            return await ctx.reply(embed=em)
        elif ctx.author.id in self.in_game:
            em = utils.fail_embed(
                'You are already fighting someone. Please finish the current fight first.'
            )
            return await ctx.reply(embed=em)

        data1 = await self.get_user(ctx.author.id)
        if not data1.characters:
            em = utils.fail_embed('You don\'t have any characters.')
            return await ctx.reply(embed=em)
        elif data1.coins < 1500:
            em = utils.fail_embed(f'You must have at least **1,500** {self.coin_emoji}')
            return await ctx.reply(embed=em)

        data2 = await self.get_user(member.id)
        if not data2.characters:
            em = utils.fail_embed(f'`{member}` doesn\'t have any characters.')
            return await ctx.reply(embed=em)
        elif data2.coins < 1500:
            em = utils.fail_embed(f'{member.mention} must have at least **1,500** {self.coin_emoji}')
            return await ctx.reply(embed=em)

        view = utils.ConfirmView(ctx, react_user=member)
        view.message = await ctx.send(
            f'{ctx.author.mention} is challenging you to a fight, do you want to participate? {member.mention}',
            view=view
        )
        await view.wait()
        if view.response is False:
            return await ctx.reply(f'{member.mention} does not want to fight you.')
        await ctx.reply(
            f'`{member}` has agreed to have a fight with you. '
            'Please send the name of one of the characters you own that '
            'you wish to use in this fight.'
        )
        try:
            _p1 = await self.bot.wait_for(
                'message',
                check=lambda m: m.channel.id == ctx.channel.id and m.author.id == ctx.author.id,
                timeout=30.0
            )
            p1 = _p1.content.lower()
            __p1 = data1.characters.get(_p1.content.lower())
            if __p1 is None:
                return await _p1.reply('You do not own that character.')

            await ctx.send(
                f'{member.mention} Please send the name of one of the characters '
                'that you own that you wish to use in this fight.'
            )
            _p2 = await self.bot.wait_for(
                'message',
                check=lambda m: m.channel.id == ctx.channel.id and m.author.id == member.id,
                timeout=30.0
            )
            p2 = _p2.content.lower()
            __p2 = data2.characters.get(_p2.content.lower())
            if __p2 is None:
                return await _p2.reply('You do not own that character.')
        except TimeoutError:
            return await ctx.reply('Somebody ran out of time while picking their character.')

        p1: Characters = await Characters.find_one({'_id': p1})
        if p1 is None:
            return await ctx.reply(f'{ctx.author.mention} that character does not exist.')
        p2: Characters = await Characters.find_one({'_id': p2})
        if p2 is None:
            return await ctx.reply(f'{member.mention} that character does not exist.')

        lvl1 = 0
        lvl2 = 0
        for k, v in LEVELS.items():
            if data1.characters[p1.name] >= k:
                lvl1 = v[0]
            else:
                break
        for k, v in LEVELS.items():
            if data2.characters[p2.name] >= k:
                lvl2 = v[0]
            else:
                break

        p1.hp = p1.hp * lvl1
        p1.lowest_dmg = p1.lowest_dmg * lvl1
        p1.highest_dmg = p1.highest_dmg * lvl1

        p2.hp = p2.hp * lvl2
        p2.lowest_dmg = p2.lowest_dmg * lvl2
        p2.highest_dmg = p2.highest_dmg * lvl2

        pl = [(ctx.author, p1, lvl1), (member, p2, lvl2)]
        for i in range(5):
            random.shuffle(pl)

        self.in_game.append(ctx.author.id)
        self.in_game.append(member.id)
        game = utils.Fight(
            pl[0],
            pl[1],
            ctx
        )
        game.message = await ctx.send(f'{pl[0][0].mention} you start!', view=game)
        await game.wait()
        self.in_game.pop(self.in_game.index(ctx.author.id))
        self.in_game.pop(self.in_game.index(member.id))

    @base_game.command(name='profile')
    async def game_profile(self, ctx: Context, *, member: disnake.Member = None):
        """Check someone's game profile.

        `member` **->** The member you wish to see the profile of. If you want to see your own, then you can ignore this since it defaults to yourself.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        member = member or ctx.author
        data = await self.get_user(member.id)

        em = disnake.Embed(color=utils.blurple)
        em.set_author(name=f'{member}\'s game profile', icon_url=member.display_avatar)
        em.add_field('Coins', f'{data.coins:,} {self.coin_emoji}', inline=False)
        em.add_field('Total Characters', len(data.characters), inline=False)
        em.add_field('Current Streak', f'{data.streak:,}', inline=False)
        em.add_field('Total Matches', f'{data.total_matches:,}')
        em.add_field('Total Wins', f'{data.wins:,}')
        em.add_field('Total Loses', f'{data.loses:,}')
        em.set_footer(text=f'Requested By: {ctx.author}')

        await ctx.better_reply(embed=em)

    @base_game.group(name='character', aliases=('char',), invoke_without_command=True, case_insensitive=True)
    async def game_character(self, ctx: Context, *, character_name: str):
        """Shows info about a character based on its specific name.

        `character_name` **->** The full name of the character you want to see the info of.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        character_name = character_name.lower()
        data: Characters = await Characters.find_one({'_id': character_name})
        if data is None:
            em = utils.fail_embed('Character does not exist.')
            return await ctx.reply(embed=em)

        date = data.added_date.strftime('%d/%m/%Y')
        em = disnake.Embed(
            title=f'`{data.name.title()}`',
            description=f'*{data.description}*',
            color=utils.blurple
        )
        em.add_field('Attack (DMG)', f'{data.lowest_dmg:,} **-** {data.highest_dmg:,}')
        em.add_field('Health (HP)', f'{data.hp:,}')
        em.add_field('Rarity', f'{data.rarity_level * "✮"}({data.rarity_level})')
        em.add_field('Obtainable', 'Yes' if data.obtainable is True else 'No', inline=False)
        em.set_footer(text=f'Character added on {date}')

        await ctx.better_reply(embed=em)

    @game_character.command(name='all')
    async def character_all(self, ctx: Context):
        """Shows all of the existing obtainable characters.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        embeds = []
        async for data in Characters.find({'obtainable': True}).sort('rarity_level', 1):
            data: Characters
            date = data.added_date.strftime('%d/%m/%Y')

            em = disnake.Embed(
                title=f'`{data.name.title()}`',
                description=f'*{data.description}*',
                color=utils.blurple
            )
            em.add_field('Attack (DMG)', f'{data.lowest_dmg:,} **-** {data.highest_dmg:,}')
            em.add_field('Health (HP)', f'{data.hp:,}')
            em.add_field('Rarity', f'{data.rarity_level * "✮"}({data.rarity_level})')
            em.set_footer(text=f'Character added on {date}')

            embeds.append(em)

        if len(embeds) == 0:
            em = utils.fail_embed('There are currently no obtainable characters.')
            return await ctx.better_reply(embed=em)

        pag = utils.EmbedPaginator(ctx, embeds)
        await pag.start()

    @game_character.command(name='add', aliases=('create',))
    @utils.is_owner()
    async def character_add(self, ctx: Context):
        """Adds a character to the game."""

        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        await ctx.reply('What\'s the character\'s name?')
        try:
            _name = await self.bot.wait_for('message', check=check, timeout=45.0)
            if _name.content is None:
                return await ctx.reply('You did not give the character\'s name, cancelling.')
            name = _name.content.lower()
            data: Characters = await Characters.find_one({'_id': name})
            if data is not None:
                return await _name.reply('A character with that name already exists.')

            await _name.reply('Please send the character\'s description.')
            _description = await self.bot.wait_for('message', check=check, timeout=120.0)
            if _description.content is None:
                return await ctx.reply('You did not give the character\'s description, cancelling.')
            description = _description.content

            await _description.reply('Please send the character\'s lowest attack points (lowest DMG).')
            _lowest_dmg = await self.bot.wait_for('message', check=check, timeout=45.0)
            if _lowest_dmg.content is None:
                return await ctx.reply('You did not give the character\'s lowest attack points, cancelling.')
            lowest_dmg = int(_lowest_dmg.content)

            await _lowest_dmg.reply('Please send the character\'s highest attack points (highest DMG).')
            _highest_dmg = await self.bot.wait_for('message', check=check, timeout=45.0)
            if _highest_dmg.content is None:
                return await ctx.reply('You did not give the character\'s highest attack points, cancelling.')
            highest_dmg = int(_highest_dmg.content)

            await _highest_dmg.reply('Please send the character\'s health points (HP).')
            _hp = await self.bot.wait_for('message', check=check, timeout=45.0)
            if _hp.content is None:
                return await ctx.reply('You did not give the character\'s health points, cancelling.')
            hp = int(_hp.content)

            await _hp.reply('Please send the character\'s rarity level. (1-5)')
            _rarity = await self.bot.wait_for('message', check=check, timeout=45.0)
            if _rarity.content is None:
                return await ctx.reply('You did not give the character\'s rarity level, cancelling.')
            rarity_level = int(_rarity.content)
            if rarity_level < 1 or rarity_level > 5:
                return await ctx.reply('The rarity level cannot be less than 1 or greater than 5.')
        except TimeoutError:
            return await ctx.reply('Ran out of time.')
        except ValueError:
            return await ctx.reply(
                'The damage or the health points that you have given are not numbers, cancelling.'
            )

        await Characters(
            name=name,
            description=description,
            lowest_dmg=lowest_dmg,
            highest_dmg=highest_dmg,
            hp=hp,
            rarity_level=rarity_level,
            added_date=datetime.now()
        ).commit()

        await ctx.reply('Character has been successfully added.')

    @game_character.command(name='remove', aliases=('delete',))
    @utils.is_owner()
    async def character_remove(self, ctx: Context, *, character_name: str):
        """Remove a character from the game's characters.

        `character_name` **->** The full name of the character you want to remove.
        """

        data: Characters = await Characters.find_one({'_id': character_name.lower()})
        if data is None:
            return await ctx.reply('Character does not exist.')

        async for g in Game.find():
            g: Game
            if character_name.lower() in g.characters:
                del g.characters[character_name.lower()]
                await g.commit()

        await data.delete()
        await ctx.reply('Character has been successfully deleted and removed from everyone\'s inventory.')

    @game_character.command(name='toggle')
    @utils.is_owner()
    async def character_toggle(self, ctx: Context, *, character_name: str):
        """Toggle the character's obtainable status. What that means is that if this is toggled off, they can't be obtained anymore, but can still be used.

        `character_name` **->** The full name of the character you want to toggle the availability of.
        """

        data: Characters = await Characters.find_one({'_id': character_name.lower()})
        if data is None:
            return await ctx.reply('Character does not exist.')
        data.obtainable = not data.obtainable
        await data.commit()
        await ctx.reply(
            f'Successfully toggled the character to **{"be" if data.obtainable is True else "not be"}** obtainable.'
        )

    @base_game.command(name='reset')
    @utils.is_owner()
    async def game_reset(self, ctx: Context, *, member: disnake.Member):
        """Reset a user's game data.

        `member` **->** The member whose data you wish to reset.
        """

        data = await self.get_user(member.id)
        await data.delete()
        await ctx.reply(f'Successfully deleted the game data for {member.mention}')

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        data: Game = await Game.find_one({'_id': member.id})
        if data:
            await data.delete()

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.channel.id == 913330644875104306:
            self.last_message = message

    @tasks.loop(minutes=30.0)
    async def boss_fight(self):
        if self.last_message is not None:
            now = datetime.now(timezone.utc)
            _time = self.last_message.created_at + relativedelta(minutes=5)
            if now <= _time:
                em = disnake.Embed(
                    title='Evil Carrots',
                    description='An evil carrots has appeared! Press `Join Fight` '
                                'to be able to fight this boss and earn coins.',
                    color=utils.green
                )
                em.set_footer(text='You have exactly 2 minutes to fight this boss since its appearance time!')
                view = utils.BossFight(self.bot, LEVELS, em)
                msg = await self.last_message.channel.send(embed=em, view=view)
                await msg.pin()
                await msg.channel.purge(limit=25, check=lambda m: m.is_system())
                await sleep(120.0)
                view.stop()
                await msg.unpin()
                if len(view.participants) == 0:
                    await msg.edit(content='Oof... It seems no one wanted to fight the boss.', embed=None, view=None)
                    return await msg.delete(delay=30.0)

                await msg.reply('Boss fight ended!')
                guild = self.bot.get_guild(913310006814859334)
                participant_ids = sorted(view.participants, key=lambda k: view.participants[k].total_damage, reverse=True)
                awarded_first = False

                for uid in participant_ids:
                    participant = view.participants[uid]
                    mem = guild.get_member(uid)
                    data: Game = await Game.find_one({'_id': uid})
                    if data is None:
                        return

                    elif mem is None:
                        return

                    if awarded_first is False:
                        coins = int(participant.total_damage * 0.3)
                        data.characters[participant.character_name] += 30
                        em.title = 'Evil Carrots Defeated!'
                        em.description = f'Congratulations {mem.mention}, ' \
                                          'you have dealt the most damage in this' \
                                         f'boss fight (**{participant.total_damage:,}** total damage dealt) ' \
                                          'and have been awarded 3x more coins compared to the others, and your character ' \
                                          'has gotten **30xp**'  # noqa
                        em.color = utils.red
                        await msg.edit(embed=em, view=None)
                        awarded_first = True
                    else:
                        coins = int(participant.total_damage * 0.1)

                    if coins != 0:
                        data.coins += coins
                        await data.commit()
                        await mem.send(
                            'Hello, thank you for fighting the boss.\n'
                            f'You have been rewarded with **{coins:,}** {self.coin_emoji}'
                        )

    @boss_fight.before_loop
    async def before_boss_fight(self):
        await self.bot.wait_until_ready()

    @base_game.group(name='boss', invoke_without_command=True, case_insensitive=True)
    async def game_boss(self, ctx: Context):
        """See how much longer until the next boss fight begins.
        The boss fight can only begin if there's been a message sent in the last 5 minutes before actually starting the boss fight.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if utils.check_channel(ctx) is False:
            return

        em = disnake.Embed(
            title='Time left until next boss fight',
            description=f'Next boss fight is in `{utils.human_timedelta(self.boss_fight.next_iteration)}`',
            color=utils.blurple
        )
        em.set_footer(text=f'Requested By: {ctx.author}')
        await ctx.better_reply(embed=em)

    @game_boss.command(name='start', aliases=('s',))
    @utils.is_owner()
    async def boss_start(self, ctx: Context):
        """Start the boss fight earlier. This also means that the timer until the next boss fight will be reset."""

        await ctx.message.add_reaction(ctx.thumb)

        self.boss_fight.restart()


def setup(bot: Ukiyo):
    bot.add_cog(_Game(bot))
