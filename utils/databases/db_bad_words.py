from . import database8, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database8)


@instance.register
class BadWords(Document, GetDoc):
    id = IntField(attribute='_id', default=374622847672254466)
    bad_words = DictField(StrField(), IntField(), default={})

    class Meta:
        collection_name = 'Bad Words'
