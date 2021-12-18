import random
from datetime import datetime
from asyncio import TimeoutError
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


class _Game(commands.Cog, name='Game'):
    """This category shows the base command for the game commands."""
    def __init__(self, bot: Ukiyo):
        self.bot = bot
        self.coin_emoji = '🪙'

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

    async def get_user(self, uid: Context) -> Game:
        data: Game = await Game.find_one({'_id': uid})
        if data is None:
            data = Game(
                id=uid,
                coins=5000,
                characters={},
                daily=datetime.now(),
                streak=0
            )
            await data.commit()

        return data

    def check_channel(self, ctx: Context) -> bool:
        if ctx.channel.id not in (913330644875104306, 913332335473205308, 913445987102654474) \
                and ctx.author.id != self.bot._owner_id:
            return False
        return True

    @commands.group(name='game', aliases=('g',), invoke_without_command=True, case_insensitive=True)
    async def base_game(self, ctx: Context):
        """Base command for all the `game` commands. To see the commands, please type `!help game`

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is True:
            await ctx.send_help('game')

    @base_game.group(name='coins', invoke_without_command=True, case_insensitive=True)
    async def game_coins(self, ctx: Context):
        """See how many coins you currently have.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
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
    async def coins_set(self, ctx: Context, amount: int = 1000, member: disnake.Member = None):
        """Set the coins for the member.

        `amount` **->** The amount of coins you wish to set.
        `member` **->** The member that you wish to set the coins for. Defaults to yourself.
        """

        member = member or ctx.author
        data = await self.get_user(member.id)
        data.coins = amount
        await data.commit()

        await ctx.reply(f'Successfully set the amount of coins for `{member}` to **{amount}** {self.coin_emoji}')

    @game_coins.command(name='add')
    @utils.is_owner()
    async def coins_add(self, ctx: Context, amount: int = 1000, member: disnake.Member = None):
        """Add the coins to the member's existing coins.

        `amount` **->** The amount of coins you wish to add.
        `member` **->** The member that you wish to add the coins for. Defaults to yourself.
        """

        member = member or ctx.author
        data = await self.get_user(member.id)
        data.coins += amount
        await data.commit()

        await ctx.reply(f'Successfully added **{amount}** {self.coin_emoji} to `{member}`')

    @base_game.command(name='daily')
    async def game_daily(self, ctx: Context):
        """Get your daily coins.
        One streak is `100` coins, which gets multiplied by the amount of streaks you have accumulated. That means that a 10 day streak is `1000` extra coins.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx.author.id)
        if data.daily > datetime.now():
            em = disnake.Embed(
                title='Uh-oh',
                description='You cannot claim your daily yet! Please come back in '
                            f'`{utils.human_timedelta(data.daily, suffix=False)}`',
                color=utils.red
            )
            return await ctx.reply(embed=em)

        coins = 1000 + (data.streak * 100)
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

        if self.check_channel(ctx) is False:
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

        if self.check_channel(ctx) is False:
            return

        data = await self.get_user(ctx.author.id)
        if not data.characters:
            em = disnake.Embed(
                title='Uh-oh',
                description='You do not own any characters! See `!game shop` to check all the available buyable characters.',
                color=utils.red
            )
            await ctx.reply(embed=em)

    @base_game.group(name='shop', invoke_without_command=True, case_insensitive=True)
    async def game_shop(self, ctx: Context):
        """The shop from which you can buy boxes that contain a character.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
            return

        em = disnake.Embed(title='Box Shop', color=utils.blurple)
        em.add_field(
            f'Common Box — 2,500 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮(1)',
            inline=False
        )
        em.add_field(
            f'Uncommon Box — 5,000 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮✮(2)',
            inline=False
        )
        em.add_field(
            f'Rare Box — 15,000 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮✮✮(3)',
            inline=False
        )
        em.add_field(
            f'Epic Box — 65,000 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮✮✮✮(4)',
            inline=False
        )
        em.add_field(
            f'Legendary Box — 150,000 {self.coin_emoji}',
            'This box will get you characters that have a rarity of ✮✮✮✮✮(5)',
            inline=False
        )
        await ctx.reply(embed=em)

    @game_shop.command(name='use')
    async def shop_use(self, ctx: Context, box_rarity: str):
        """Buy and open a box.

        `box_rarity` **->** The rarity of the box that you wish to open.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
            return

        boxes = {
            'common': (1, 2500),
            'uncommon': (2, 5000),
            'rare': (3, 15000),
            'epic': (4, 65000),
            'legendary': (5, 150000)
        }
        box: tuple | None = boxes.get(box_rarity.lower())
        if box is None:
            return await ctx.reply('That box rarity does not exist.')

        data = await self.get_user(ctx.author.id)
        if data.coins < box[1]:
            return await ctx.reply('You don\'t have enough money to buy that box.')
        data.coins -= box[1]

        characters = await Characters.find({'rarity_level': box[0]}).to_list(100_000)
        if len(characters) == 0:
            return await ctx.reply('There currently are no characters of that rarity.')
        for i in range(3):
            random.shuffle(characters)
        character: Characters = random.choice(characters)

        fmt = 'an' if box_rarity.startswith(('a', 'e')) else 'a'
        if character.name in data.characters:
            data.characters[character.name] += 10
            await ctx.reply(
                f'You bought **{fmt + box_rarity}** box and got `{character.name.title()}`.\n'
                'Since you already own this character, you have been awarded 10xp for it.'
            )
        else:
            data.characters[character.name] = 0
            await ctx.reply(
                f'You bought **{fmt + box_rarity}** box and got `{character.name.title()}`.'
            )
        await data.commit()

    @base_game.group(name='character', aliases=('char',), invoke_without_command=True, case_insensitive=True)
    async def game_character(self, ctx: Context, *, character_name: str):
        """Shows info about a character based on its specific name.

        `character_name` **->** The full name of the character you want to see the info of.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
            return

        character_name = character_name.lower()
        data: Characters = await Characters.find_one({'_id': character_name})
        if data is None:
            return await ctx.reply('Character does not exist.')

        date = data.added_date.strftime('%d/%m/%Y')
        em = disnake.Embed(
            title=f'`{data.name.title()}`',
            description=f'*{data.description}*',
            color=utils.blurple
        )
        em.add_field('Attack (DMG)', data.dmg)
        em.add_field('Health (HP)', data.hp)
        em.add_field('Rarity', f'{data.rarity_level * "✮"}({data.rarity_level})')
        em.add_field('Obtainable', 'Yes' if data.obtainable is True else 'No', inline=False)
        em.set_footer(text=f'Character added on {date}')

        await ctx.reply(embed=em)

    @game_character.command(name='all')
    async def character_all(self, ctx: Context):
        """Shows all of the existing obtainable characters.

        **NOTE:** This command can only be used in <#913330644875104306>
        """

        if self.check_channel(ctx) is False:
            return

        embeds = []
        async for data in Characters.find({'obtainable': True}):
            data: Characters
            date = data.added_date.strftime('%d/%m/%Y')

            em = disnake.Embed(
                title=f'`{data.name.title()}`',
                description=f'*{data.description}*',
                color=utils.blurple
            )
            em.add_field('Attack (DMG)', data.dmg)
            em.add_field('Health (HP)', data.hp)
            em.add_field('Rarity', f'{data.rarity_level * "✮"}({data.rarity_level})')
            em.set_footer(text=f'Character added on {date}')

            embeds.append(em)

        if len(embeds) == 0:
            return await ctx.reply('There are currently no obtainable characters.')

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

            await _description.reply('Please send the character\'s attack points (DMG).')
            _dmg = await self.bot.wait_for('message', check=check, timeout=45.0)
            if _dmg.content is None:
                return await ctx.reply('You did not give the character\'s attack points, cancelling.')
            dmg = int(_dmg.content)

            await _dmg.reply('Please send the character\'s health points (HP).')
            _hp = await self.bot.wait_for('message', check=check, timeout=45.0)
            if _hp.content is None:
                return await ctx.reply('You did not give the character\'s health points, cancelling.')
            hp = int(_hp.content)

            await _hp.reply('Please send the character\'s rarity level.')
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
            dmg=dmg,
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
        await data.delete()
        await ctx.reply('Character has been successfully deleted.')

    @game_character.command(name='toggle')
    @utils.is_owner()
    async def character_toggle(self, ctx: Context, *, character_name: str):
        """Toggle the character's obtainable status. What that means is that if this is toggled off, they can't be obtained anymore, but can still be used.

        `character_name` **->** The full name of the character you want to remove.
        """

        data: Characters = await Characters.find_one({'_id': character_name.lower()})
        if data is None:
            return await ctx.reply('Character does not exist.')
        data.obtainable = not data.obtainable
        await data.commit()
        await ctx.reply(
            f'Successfully toggled the character to **{"be" if data.obtainable is True else "not be"}** obtainable.'
        )


def setup(bot: Ukiyo):
    bot.add_cog(_Game(bot))
