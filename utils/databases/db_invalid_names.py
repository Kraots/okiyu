from . import database2

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database2)


@instance.register
class InvalidName(Document):
    id = IntField(attribute='_id', required=True)
    pos = IntField()
    last_pos = IntField()

    class Meta:
        collection_name = 'InvalidNameFilter'
