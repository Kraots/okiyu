from .dbs import (  # noqa
    database1,
    database2,
    database3,
    database4,
    database5,
    database6,
    database7,
    database8,
    database9,
    database10,
    database11
)


class GetDoc:
    @classmethod
    async def get(cls, id=938097236024360960):
        """|coro|

        This method is a shortcut for ``await .find_one({'_id': id})``
        If the ``id`` isn't given, then it will use the owner's id by default (938097236024360960)
        """

        return await cls.find_one({'_id': id})


from .db_intros import Intro
from .db_rules import Rules
from .db_mutes import Mutes
from .db_levels import Level
from .db_invalid_names import InvalidName
from .db_marriage import Marriage
from .db_tickets import Ticket
from .db_afks import AFK
from .db_game import Game, Characters
from .db_giveaways import GiveAway
from .db_bdays import Birthday
from .db_confesscord import Restrictions
from .db_bad_words import BadWords
from .db_constants import Constants
from .db_reminders import Reminder
from .db_todos import ToDo
from .db_sober import Sober

__all__ = (
    'Intro',
    'Rules',
    'Mutes',
    'Level',
    'InvalidName',
    'Marriage',
    'Ticket',
    'AFK',
    'Game',
    'Characters',
    'GiveAway',
    'Birthday',
    'Restrictions',
    'BadWords',
    'Constants',
    'Reminder',
    'ToDo',
    'Sober',
)
