from . import database10, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database10)


@instance.register
class ToDo(Document, GetDoc):
    id = IntField(attribute='_id', required=True)
    todo_data = ListField(DictField(StrField(), StrField()), required=True)

    class Meta:
        collection_name = 'Todos'
