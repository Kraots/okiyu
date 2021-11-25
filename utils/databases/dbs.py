import os
import motor.motor_asyncio


key1 = os.getenv('MONGODBKEY1')
cluster1 = motor.motor_asyncio.AsyncIOMotorClient(key1)
database1 = cluster1['Ukiyo']

key2 = os.getenv('MONGODBKEY2')
cluster2 = motor.motor_asyncio.AsyncIOMotorClient(key2)
database2 = cluster2['Ukiyo']
