from typing import NamedTuple

import string as st
from pathlib import Path
from datetime import datetime

__all__ = (
    'FIRST_JANUARY_1970',
    'ALLOWED_CHARACTERS',
    'BAD_WORDS',
    'EDGE_CHARACTERS_CASES',
    'EDGE_CHARACTERS_TABLE',
    'PUNCTUATIONS_AND_DIGITS',
    'PAD_TABLE',
    'LETTERS_EMOJI',
    'LETTERS_TABLE',
    'EMOJIS_TABLE',
    'NUMBERS_EMOJI',
    'NUMBERS_TABLE',
    'Channels',
    'Categories'
)

FIRST_JANUARY_1970 = datetime(1970, 1, 1, 0, 0, 0, 0)
ALLOWED_CHARACTERS = tuple(st.printable)
BAD_WORDS = Path('./bad_words.txt').read_text().splitlines()
EDGE_CHARACTERS_CASES = {
    '@': 'a',
    '0': 'o',
    '1': 'i',
    '$': 's',
    '!': 'i',
    '9': 'g',
    '5': 's',
}
EDGE_CHARACTERS_TABLE = str.maketrans(EDGE_CHARACTERS_CASES)
PUNCTUATIONS_AND_DIGITS = tuple(list(st.punctuation) + list(st.digits))
PAD_TABLE = str.maketrans({k: '' for k in PUNCTUATIONS_AND_DIGITS})

LETTERS_EMOJI = {
    'a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩',
    'e': '🇪', 'f': '🇫', 'g': '🇬', 'h': '🇭',
    'i': '🇮', 'j': '🇯', 'k': '🇰', 'l': '🇱',
    'm': '🇲', 'n': '🇳', 'o': '🇴', 'p': '🇵',
    'q': '🇶', 'r': '🇷', 's': '🇸', 't': '🇹',
    'u': '🇺', 'v': '🇻', 'w': '🇼', 'x': '🇽',
    'y': '🇾', 'z': '🇿'
}
NUMBERS_EMOJI = {
    '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣',
    '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣',
    '8': '8️⃣', '9': '9️⃣'
}
LETTERS_TABLE = str.maketrans(LETTERS_EMOJI)
NUMBERS_TABLE = str.maketrans(NUMBERS_EMOJI)

EMOJIS_TABLE = str.maketrans({v: k for k, v in LETTERS_EMOJI.items()})


class Channels(NamedTuple):
    news = 938119688335007744
    boosts = 938119709046485103
    rules = 938119722929639444
    welcome = 938119788666978314
    intros = 938119739572633680
    roles = 938120396467757056
    colours = 938120414633291868
    birthdays = 938119754001031259

    general = 938115789553299456
    venting = 938117846137974836
    nsfw = 938117888085196840

    bots = 938119528464916530
    memes = 938118626702163998
    anime = 938118844252319814
    animals = 938118656389447762
    gaming = 938118866586964078

    selfies = 938118641831006268
    artwork = 938118927639261215
    photos = 938118803890503700
    videos = 938118818226663445

    confesscord = 938135131728785430
    bump = 938135144848564224

    no_mic_chat = 938119894778658946
    music_commands = 938121801685422101
    music = 938121774141435904
    lobby_1 = 938120000147947571
    lobby_2 = 938120022801408060
    sleep = 938120080603095050

    staff_chat = 938119766453919835
    logs = 938119993185423390
    messages_logs = 938120008041660517
    moderation_logs = 938120042678210610
    github = 938119954316800012
    bot_commands = 938120063037345865


class Categories(NamedTuple):
    server = 938119657892749394
    general = 938117469304926228
    fun = 938118602555555940
    media = 938118785859223583
    extra = 938135097515851806
    music = 938119318649045033
    staff = 938119702503379025
