from . import database8

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database8)


@instance.register
class Restrictions(Document):
    id = IntField(attribute='_id', required=True)
    restricted_by = IntField(required=True)

    class Meta:
        collection_name = 'Confesscord Restrictions'
