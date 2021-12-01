from . import database3

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database3)


@instance.register
class Marriage(Document):
    id = IntField(attribute='_id', required=True)
    married_to = IntField(required=True)
    married_since = DateTimeField(required=True)

    class Meta:
        collection_name = 'Marriages'
