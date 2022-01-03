from . import database3, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database3)


@instance.register
class InvalidName(Document, GetDoc):
    id = IntField(attribute='_id', required=True)
    last_pos = IntField()

    class Meta:
        collection_name = 'InvalidNameFilter'
