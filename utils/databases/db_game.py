from . import database6

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database6)


@instance.register
class Game(Document):
    id = IntField(attribute='_id', required=True)
    coins = IntField(required=True)
    characters = DictField(StrField(), IntField(), required=True)  # CHARACTER_NAME: CHARACTER_XP

    daily = DateTimeField(required=True)
    streak = IntField(required=True)

    class Meta:
        collection_name = 'Game'


@instance.register
class Characters(Document):
    name = StrField(attribute='_id', required=True)
    description = StrField(required=True)
    dmg = IntField(required=True)
    hp = IntField(required=True)
    rarity_level = IntField(required=True)

    obtainable = BoolField(default=True)
    added_date = DateTimeField(required=True)

    class Meta:
        collection_name = 'Characters'
