from . import database6

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database6)


@instance.register
class Game(Document):
    id = IntField(attribute='_id', required=True)
    coins = IntField(required=True)
    characters = DictField(StrField(), IntField(), required=True)  # CHARACTER_NAME: CHARACTER_LEVEL

    daily = DateTimeField(required=True)
    streak = IntField(required=True)

    class Meta:
        collection_name = 'Game'
