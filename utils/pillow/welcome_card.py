from io import BytesIO

from PIL import Image, ImageDraw

import utils
from .rank_card import GRAY, TRANSPARENT, get_font

import disnake

WHITE = (255, 255, 255)

__all__ = ('create_welcome_card',)


async def create_welcome_card(member: disnake.Member, join_pos: str) -> disnake.File:
    img = Image.new("RGBA", (1000, 600), TRANSPARENT)
    av = Image.open(BytesIO(await member.display_avatar.read()))

    bg = Image.new("RGBA", (1000, 425), GRAY)
    img.paste(bg, (0, 175))

    welcome = Image.new("RGBA", (750, 150), TRANSPARENT)
    draw = ImageDraw.Draw(welcome)
    txt = f'Welcome {utils.format_name(member)}'
    font = get_font(txt, welcome)
    draw.text((0, 0), txt, font=font)
    img.paste(welcome, (135, 300), welcome)

    pos = Image.new("RGBA", (900, 150), TRANSPARENT)
    draw = ImageDraw.Draw(pos)
    txt = f'You are our {utils.format_position(join_pos)} member'
    font = utils.pillow.rank_card.get_font(txt, pos)
    draw.text((0, 0), txt, font=font)
    img.paste(pos, (50, 375), pos)

    acc_age = Image.new("RGBA", (700, 100), TRANSPARENT)
    draw = ImageDraw.Draw(acc_age)
    txt = 'Joined discord  ' + utils.human_timedelta(member.created_at)
    font = utils.pillow.rank_card.get_font(txt, acc_age)
    draw.text((0, 0), txt, font=font)
    img.paste(acc_age, (150, 500), acc_age)

    utils.paste_rounded_image(img, av, 250, (370, 25))
    img.save('welcome.png')
    f = disnake.File(fp='welcome.png', filename='welcome.png')

    return f
