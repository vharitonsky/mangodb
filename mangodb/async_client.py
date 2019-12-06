import sys
import logging
from datetime import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import CollectionInvalid, OperationFailure

from mangodb.constants import CHUNK_SIZE
from mangodb.types import Bytes, Seconds
from mangodb.exceptions import NotFoundError, DuplicateKeyError

log = logging.getLogger()


class DataBuffer:

    def __init__(self, key, data_getter):
        self.chunks = None
        self.current_chunk = None
        self.tail = b''
        self.key = key
        self.data_getter = data_getter

    async def read(self, n=-1):
        if n == -1:
            n = sys.maxsize
        if self.chunks is None:
            chunks_doc = await self.data_getter(filter={'key': self.key})
            if chunks_doc is None:
                raise NotFoundError
            self.chunks = chunks_doc['chunks'].split()

        content = b''

        while len(content) < n:
            if not self.current_chunk:
                try:
                    self.current_chunk = self.chunks.pop()
                except IndexError:
                    return content + self.tail
                doc = await self.data_getter(
                    filter={'_id': ObjectId(self.current_chunk)}
                )
                if doc is None:
                    raise NotFoundError
                self.tail = doc['blob']

            content += self.tail[:n - len(content)]
            self.tail = self.tail[n - len(content):]

            if not self.tail:
                self.current_chunk = None
        return content


class MangoDB:

    def __init__(self, dsn, db, collection: str, cap: Bytes, ttl: Seconds):
        self.client = AsyncIOMotorClient(dsn)
        self.db = db
        self.collection = collection
        self.cap = cap
        self.ttl = ttl
        self.collection_created = False

    async def _read(self, **kwargs):
        return await self.client[self.db][self.collection].find_one(**kwargs)

    async def _write_chunk(self, data):
        return str(
            (await self.client[self.db][self.collection].insert_one({
                'blob': data,
                'date': datetime.utcnow(),
            })).inserted_id
        )

    async def _ensure_collection(self):
        if not self.cap:
            return
        if self.collection_created:
            return
        try:
            await self.client[self.db].create_collection(
                self.collection, capped=True, size=self.cap
            )
        except CollectionInvalid:
            options = await self.client[self.db].get_collection(self.collection).options()
            if not options.get('capped'):
                log.warning(
                    "Collection is not capped, perform "
                    "https://docs.mongodb.com/manual/core/capped-collections"
                    "/#convert-a-collection-to-capped"
                )
        self.collection_created = True

    async def _ensure_index(self):
        collection = self.client[self.db][self.collection]
        await collection.create_index('key')
        if not self.ttl:
            return
        try:
            await collection.create_index(
                'date',
                name='date_expire',
                expireAfterSeconds=self.ttl
            )
        except OperationFailure:
            log.warning("Index already exists")

    async def _write_chunk_ids(self, key, chunk_ids):
        await self.client[self.db][self.collection].insert_one({
            'key': key,
            'chunks': ' '.join(chunk_ids),
            'date': datetime.utcnow(),
        })

    async def put(self, key, buffer):
        await self._ensure_collection()
        await self._ensure_index()
        if await self._read(filter={'key': key}):
            raise DuplicateKeyError
        chunk_ids = []
        while True:
            chunk = buffer.read(CHUNK_SIZE)
            if not chunk:
                break
            chunk_ids.append(await self._write_chunk(chunk))
        await self._write_chunk_ids(key, reversed(chunk_ids))

    async def put_buffer(self, buffer):
        await self._ensure_collection()
        await self._ensure_index()
        chunk_ids = []
        while True:
            chunk = buffer.read(CHUNK_SIZE)
            if not chunk:
                break
            chunk_ids.append(self._write_chunk(chunk))
        return list(reversed(chunk_ids))

    async def save_chunk_ids(self, key, chunk_ids):
        existing = await self._read(filter={'key': key})
        if existing:
            raise DuplicateKeyError
        await self._write_chunk_ids(key, chunk_ids)

    def get_buffer(self, key):
        return DataBuffer(key, self._read)

    async def get(self, key):
        return await self.get_buffer(key).read(-1)
