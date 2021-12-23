import os
import motor.motor_asyncio


key1 = os.getenv('MONGODBKEY1')
cluster1 = motor.motor_asyncio.AsyncIOMotorClient(key1)
database1 = cluster1['Ukiyo']  # Mainly stores intros

key2 = os.getenv('MONGODBKEY2')
cluster2 = motor.motor_asyncio.AsyncIOMotorClient(key2)
database2 = cluster2['Ukiyo']  # Mainly stores levels

key3 = os.getenv('MONGODBKEY3')
cluster3 = motor.motor_asyncio.AsyncIOMotorClient(key3)
database3 = cluster3['Ukiyo']  # Extra stuff (mutes, rules, etc...)

key4 = os.getenv('MONGODBKEY4')
cluster4 = motor.motor_asyncio.AsyncIOMotorClient(key4)
database4 = cluster4['Ukiyo2']  # AFKs

key5 = os.getenv('MONGODBKEY5')
cluster5 = motor.motor_asyncio.AsyncIOMotorClient(key5)
database5 = cluster5['Ukiyo2']  # Marriages

key6 = os.getenv('MONGODBKEY6')
cluster6 = motor.motor_asyncio.AsyncIOMotorClient(key6)
database6 = cluster6['Ukiyo3']  # Game

key7 = os.getenv('MONGODBKEY7')
cluster7 = motor.motor_asyncio.AsyncIOMotorClient(key7)
database7 = cluster7['Ukiyo3']  # Birthdays
