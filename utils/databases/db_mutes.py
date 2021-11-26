from . import database2

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database2)


@instance.register
class Mutes(Document):
    id = IntField(attribute='_id', required=True)
    muted_by = IntField(required=True)
    muted_until = DateTimeField(required=True)
    reason = StrField(required=True)

    is_owner = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    is_mod = BooleanField(default=False)
    bot = BooleanField(default=False)

    class Meta:
        collection_name = 'Mutes'
