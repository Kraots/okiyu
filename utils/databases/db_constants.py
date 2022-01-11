from . import database8, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database8)


@instance.register
class Constants(Document, GetDoc):
    """This is really just meant to store random stuff, enabled/disabled stuff or values."""

    id = IntField(attribute='_id', default=374622847672254466)
    disabled_commands = ListField(StrField(), default=[])
    calculator_ternary = BooleanField(default=False)

    class Meta:
        collection_name = 'Constants'
