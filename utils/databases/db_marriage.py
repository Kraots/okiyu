from . import database5

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

from ..helpers import FIRST_JANUARY_1970

instance = Instance(database5)


@instance.register
class Marriage(Document):
    id = IntField(attribute='_id', required=True)
    married_to = IntField(default=0)
    married_since = DateTimeField(default=FIRST_JANUARY_1970)

    adoptions = ListField(IntField(), default=[])

    class Meta:
        collection_name = 'Marriages'
