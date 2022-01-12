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
    'NUMBERS_TABLE'
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
