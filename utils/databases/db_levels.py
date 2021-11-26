from . import database2

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database2)


@instance.register
class Level(Document):
    id = IntField(attribute='_id', required=True)
    xp = IntField(required=True)
    messages_count = IntField(required=True)

    class Meta:
        collection_name = 'Levels'
