from . import database3, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database3)


@instance.register
class Mutes(Document, GetDoc):
    id = IntField(attribute='_id', required=True)
    muted_by = IntField(required=True)
    muted_until = DateTimeField(required=True)
    reason = StrField(required=True)
    duration = StrField(required=True)
    jump_url = StrField(required=True)

    is_owner = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    is_mod = BooleanField(default=False)
    filter = BooleanField(default=False)
    muted = BooleanField(default=False)
    blocked = BooleanField(default=False)

    class Meta:
        collection_name = 'Mutes'
