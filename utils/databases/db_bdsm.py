from . import database12, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database12)


@instance.register
class BDSM(Document, GetDoc):
    id = IntField(attribute='_id', required=True)
    result = StrField(required=True)
    set_date = DateTimeField(required=True)

    class Meta:
        collection_name = 'BDSM Tests'
