import asyncio
import functools
from concurrent import futures
from io import BytesIO

import disnake
from PIL import Image, ImageFile, ImageSequence

from .round_image import paste_rounded_image

__all__ = ('bonk_gif',)

ImageFile.LOAD_TRUNCATED_IMAGES = True

LARGE_DIAMETER = 110
SMALL_DIAMETER = 80

BONK_GIF = Image.open('assets/yodabonk.gif')

PFP_ENTRY_FRAME = 31
BONK_FRAME = 43
PFP_EXIT_FRAME = 56
PFP_CENTRE = (355, 73)


def _generate_frame(
    frame_number: int,
    frame: Image.Image,
    pfps_by_size: dict[str, int]
) -> Image.Image:
    canvas = Image.new("RGBA", BONK_GIF.size)
    canvas.paste(frame.convert("RGBA"), (0, 0))

    if PFP_ENTRY_FRAME <= frame_number <= PFP_EXIT_FRAME:
        if frame_number == BONK_FRAME:
            paste_rounded_image(
                canvas,
                pfps_by_size["small"],
                SMALL_DIAMETER,
                (
                    PFP_CENTRE[0] - SMALL_DIAMETER // 2,
                    PFP_CENTRE[1] - SMALL_DIAMETER // 2 + 10,  # Shift avatar down by 10 px in the bonk frame
                )
            )
        else:
            paste_rounded_image(
                canvas,
                pfps_by_size["large"],
                LARGE_DIAMETER,
                (
                    PFP_CENTRE[0] - LARGE_DIAMETER // 2,
                    PFP_CENTRE[1] - LARGE_DIAMETER // 2,
                )
            )

    return canvas


def _generate_gif(pfp: bytes) -> BytesIO:
    pfp = Image.open(BytesIO(pfp))
    pfps_by_size = {
        "large": pfp.resize((LARGE_DIAMETER,) * 2),
        "small": pfp.resize((SMALL_DIAMETER,) * 2),
    }

    out_images = [
        _generate_frame(i, frame, pfps_by_size)
        for i, frame in enumerate(ImageSequence.Iterator(BONK_GIF))
    ]

    out_gif = BytesIO()
    out_images[0].save(
        out_gif,
        "GIF",
        save_all=True,
        append_images=out_images[1:],
        loop=0,
        duration=50,
    )

    return out_gif


async def bonk_gif(user: disnake.User):
    avatar = await user.display_avatar.read()
    out_filename = f'bonk_{user.id}.gif'
    func = functools.partial(_generate_gif, avatar)

    with futures.ThreadPoolExecutor() as pool:
        out_gif = await asyncio.get_running_loop().run_in_executor(pool, func)

        out_gif.seek(0)
        file = disnake.File(out_gif, out_filename)

        return file
