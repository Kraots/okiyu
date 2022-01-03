from . import database7, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database7)


@instance.register
class Birthday(Document, GetDoc):
    id = IntField(attribute='_id', required=True)
    timezone = StrField(required=True)
    birthday_date = DateTimeField(required=True)
    next_birthday = DateTimeField(required=True)

    class Meta:
        collection_name = 'Birthdays'
