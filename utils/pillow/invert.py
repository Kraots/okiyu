from io import BytesIO
from PIL import Image, ImageOps

import disnake


__all__ = ('mirror_avatar',)


async def mirror_avatar(user: disnake.Member | disnake.User):
    av = Image.open(BytesIO(await user.display_avatar.read()))
    av = ImageOps.mirror(av)

    buff = BytesIO()
    av.save(buff, 'png')
    buff.seek(0)

    file = disnake.File(buff, filename=f'mirrored_{user.display_name}.png')
    return file
