from . import database3, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database3)


@instance.register
class GiveAway(Document, GetDoc):
    id = IntField(attribute='_id', required=True)
    prize = StrField(required=True)
    expire_date = DateTimeField(required=True)
    channel_id = IntField(default=938119688335007744)  # defaults to the news channel

    participants = ListField(IntField(), default=[])
    messages_requirement = IntField(default=0)

    class Meta:
        collection_name = 'GiveAways'
