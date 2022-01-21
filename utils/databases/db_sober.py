from . import database11, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database11)


@instance.register
class Sober(Document, GetDoc):
    user_id = IntField(required=True)
    short_title = StrField(required=True)
    description = StrField(required=True)
    progress = DateTimeField(required=True)

    class Meta:
        collection_name = 'Sober Data'
