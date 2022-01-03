from . import database6, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database6)


@instance.register
class Game(Document, GetDoc):
    id = IntField(attribute='_id', required=True)
    coins = IntField(default=5000)
    characters = DictField(StrField(), IntField(), default={})  # CHARACTER_NAME: CHARACTER_XP
    wins = IntField(default=0)
    loses = IntField(default=0)
    total_matches = IntField(default=0)

    daily = DateTimeField(required=True)
    streak = IntField(default=0)

    class Meta:
        collection_name = 'Game'


@instance.register
class Characters(Document, GetDoc):
    name = StrField(attribute='_id', required=True)
    description = StrField(required=True)
    lowest_dmg = IntField(required=True)
    highest_dmg = IntField(required=True)
    hp = IntField(required=True)
    rarity_level = IntField(required=True)

    obtainable = BoolField(default=True)
    added_date = DateTimeField(required=True)

    class Meta:
        collection_name = 'Characters'
