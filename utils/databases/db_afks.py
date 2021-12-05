from . import database4

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database4)


@instance.register
class AFK(Document):
    id = IntField(attribute='_id', required=True)
    reason = StrField(required=True)
    date = DateTimeField(required=True)

    class Meta:
        collection_name = 'AFK'
