from . import database3

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database3)


@instance.register
class Ticket(Document):
    channel_id = IntField(attribute='_id', required=True)
    message_id = IntField(required=True)
    owner_id = IntField(required=True)
    ticket_id = StrField(required=True)
    created_at = DateTimeField(required=True)

    class Meta:
        collection_name = 'Tickets'
