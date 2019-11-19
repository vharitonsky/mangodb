import asyncio
from io import BytesIO
from mangodb.client import MangoDB
client = MangoDB('mongodb://127.0.0.1:27017', 'uaprom', 'images_2', 1000000, 100000000)
client.put('test', BytesIO(b'fdsfds'))
print(client.get('test'))

from mangodb.async_client import MangoDB
client = MangoDB('mongodb://127.0.0.1:27017', 'uaprom', 'images_2', 100000000, 100000000)
loop = asyncio.get_event_loop()
loop.run_until_complete(client.put('test_async', BytesIO(b'fdsfdsfdfds')))
print(loop.run_until_complete(client.get('test_async')))
