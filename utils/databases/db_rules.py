from . import database3, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database3)


@instance.register
class Rules(Document, GetDoc):
    id = IntField(attribute='_id', default=374622847672254466)
    rules = ListField(StrField(), required=True)

    class Meta:
        collection_name = 'Rules'
