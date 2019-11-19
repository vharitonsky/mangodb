from io import BytesIO
from mangodb.client import MangoDB
client = MangoDB('mongodb://127.0.0.1:27017','uaprom', 'images', 100, 100)
client.put('test', BytesIO(b'fdsfds'))
print(client.get('test'))

