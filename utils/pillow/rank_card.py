from io import BytesIO

from PIL import Image, ImageFont, ImageDraw

import disnake

import utils

LARGE_DIAMETER = 250
LARGE_MASK = Image.new('L', (LARGE_DIAMETER,) * 2)
draw = ImageDraw.Draw(LARGE_MASK)
draw.ellipse((0, 0, LARGE_DIAMETER, LARGE_DIAMETER), fill=255)

GRAY = (48, 48, 48)
ORANGE = (255, 128, 0)
TRANSPARENT = (0, 0, 0, 0)
BLUE = (22, 160, 245)
BLACK = (0, 0, 0)
TTF_FONT = './assets/Milliard.otf'


@utils.run_in_executor
def draw_progress_bar(d, x, y, w, h, progress, bg="white", fg="black"):
    # draw background
    d.ellipse((x + w, y, x + h + w, y + h), fill=bg)
    d.ellipse((x, y, x + h, y + h), fill=bg)
    d.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=bg)

    # draw progress bar
    w *= progress
    if w != 0.0:
        d.ellipse((x + w, y, x + h + w, y + h), fill=fg)
        d.ellipse((x, y, x + h, y + h), fill=fg)
        d.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=fg)

    return d


def get_font(text, image):
    fontsize = 1
    font = ImageFont.truetype(TTF_FONT, fontsize)
    while font.getsize(text)[0] < image.size[0]:
        fontsize += 1
        font = ImageFont.truetype(TTF_FONT, fontsize)
    while font.getsize(text)[1] > image.size[1]:
        fontsize -= 1
        font = ImageFont.truetype(TTF_FONT, fontsize)
    fontsize -= 1
    font = ImageFont.truetype(TTF_FONT, fontsize)
    return font


async def create_rank_card(
    user: disnake.Member,
    level: int,
    rank: int,
    members_count: int,
    current_xp: int,
    needed_xp: int,
    percentage: float
):
    img = Image.new("RGBA", (1000, 350), GRAY)

    av = Image.open(BytesIO(await user.display_avatar.read()))

    orange_line = Image.new("RGBA", (500, 10), ORANGE)

    _user = Image.new("RGBA", (500, 50), TRANSPARENT)
    draw = ImageDraw.Draw(_user)
    txt = str(user.display_name) + '#' + str(user.discriminator)
    font = get_font(txt, _user)
    draw.text((0, 0), txt, font=font)

    has_xp = Image.new("RGBA", (200, 40), TRANSPARENT)
    draw = ImageDraw.Draw(has_xp)
    font = ImageFont.truetype(TTF_FONT, 35)
    draw.text((0, 0), f"{current_xp:,}xp", font=font, fill=BLACK)

    percent = Image.new("RGBA", (140, 40), TRANSPARENT)
    draw = ImageDraw.Draw(percent)
    font = ImageFont.truetype(TTF_FONT, 35)
    draw.text((10, 0), f"{percentage}%", font=font, fill=BLACK)

    next_xp = Image.new("RGBA", (200, 40), TRANSPARENT)
    draw = ImageDraw.Draw(next_xp)
    font = ImageFont.truetype(TTF_FONT, 35)
    if len(str(needed_xp)) == 3:
        z = f"    {needed_xp:,}xp"
    else:
        z = f"{needed_xp:,}xp"
    draw.text((0, 0), z, font=font, fill=BLACK)

    progressbar = Image.new("RGBA", (750, 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(progressbar)
    d = await draw_progress_bar(d, 0, 0, 650, 45, percentage / 100, fg=BLUE)

    _rank = Image.new("RGBA", (235, 100))
    draw = ImageDraw.Draw(_rank)
    font = ImageFont.truetype(TTF_FONT, 35)
    draw.text((0, 0), f"     Rank:\n        {rank}/{members_count}", font=font)

    _level = Image.new("RGBA", (235, 100))
    draw = ImageDraw.Draw(_level)
    font = ImageFont.truetype(TTF_FONT, 35)
    draw.text((0, 0), f"     Level:\n        {level}", font=font)

    img.paste(av.resize((LARGE_DIAMETER,) * 2), (10, 50), mask=LARGE_MASK)
    img.paste(im=orange_line, box=(350, 100))
    img.paste(im=_user, mask=_user, box=(350, 50))
    img.paste(im=progressbar, mask=progressbar, box=(275, 250))
    img.paste(im=has_xp, mask=has_xp, box=(285, 260))
    img.paste(im=next_xp, mask=next_xp, box=(800, 260))
    img.paste(im=percent, mask=percent, box=(550, 260))
    img.paste(im=_rank, mask=_rank, box=(325, 125))
    img.paste(im=_level, mask=_level, box=(600, 125))
    img.save('rank_card.png')

    f = disnake.File(fp='rank_card.png', filename='rank_card.png')

    return f
