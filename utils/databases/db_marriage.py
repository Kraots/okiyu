from . import database5, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database5)


@instance.register
class Marriage(Document, GetDoc):
    id = IntField(attribute='_id', required=True)
    married_to = IntField()
    married_since = DateTimeField()

    adoptions = ListField(IntField())

    class Meta:
        collection_name = 'Marriages'
