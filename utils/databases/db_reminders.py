from . import database9, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database9)


@instance.register
class Reminder(Document, GetDoc):
    reminder_id = IntField(required=True)
    user_id = IntField(required=True)
    channel_id = IntField(required=True)
    message_url = StrField(required=True)
    remind_what = StrField(required=True)
    remind_when = DateTimeField(required=True)
    time_now = DateTimeField(required=True)

    class Meta:
        collection_name = 'Reminders'
