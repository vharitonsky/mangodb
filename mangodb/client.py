import sys
import logging
from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

from mangodb.types import Bytes, Seconds
from mangodb.exceptions import NotFoundError

CHUNK_SIZE = 10 * 1024 * 1024 * 1024  # 10 Mb

log = logging.getLogger()


class DataBuffer:

    def __init__(self, key, data_getter):
        self.chunks = None
        self.current_chunk = None
        self.tail = b''
        self.key = key
        self.data_getter = data_getter

    def read(self, n=-1):
        if n == -1:
            n = sys.maxsize
        if not self.chunks:
            chunks_doc = self.data_getter(filter={'key': self.key})
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
                doc = self.data_getter(
                    filter={'_id': ObjectId(self.current_chunk)}
                )
                if doc is None:
                    raise NotFoundError
                self.tail = doc['blob']

            content += self.tail[:n - len(content)]
            self.tail = self.tail[n - len(content):]

            if not self.tail:
                self.current_chunk = None


class MangoDB:

    def __init__(self, dsn, db, collection: str, cap: Bytes, ttl: Seconds):
        self.client = MongoClient(dsn)
        self.db = db
        self.collection = collection
        self.cap = cap
        self.ttl = ttl
        self.collection_created = False

    def _read(self, **kwargs):
        return self.client[self.db][self.collection].find_one(**kwargs)

    def _write_chunk(self, data):
        return str(
            self.client[self.db][self.collection].insert_one({
                'blob': data,
                'date': datetime.utcnow(),
            }).inserted_id
        )

    def _ensure_collection(self):
        if self.collection_created:
            return
        try:
            self.client[self.db].create_collection(
                self.collection, capped=True, size=self.cap
            )
        except CollectionInvalid:
            collection = self.client[self.db].get_collection(self.collection)
            if not collection.options().get('capped'):
                log.warning(
                    "Collection is not capped, perform "
                    "https://docs.mongodb.com/manual/core/capped-collections"
                    "/#convert-a-collection-to-capped"
                )
        self.collection_created = True

    def _ensure_index(self):
        self.client[self.db][self.collection].ensure_index(
            'date',
            name='date_expire',
            expireAfterSeconds=self.ttl
        )

    def _write_chunk_ids(self, key, chunk_ids):
        self.client[self.db][self.collection].insert_one({
            'key': key,
            'chunks': ' '.join(chunk_ids),
            'date': datetime.utcnow(),
        })

    def put(self, key, buffer):
        self._ensure_collection()
        self._ensure_index()
        chunk_ids = []
        while True:
            chunk = buffer.read(CHUNK_SIZE)
            if not chunk:
                break
            chunk_ids.append(self._write_chunk(chunk))
        self._write_chunk_ids(key, chunk_ids)

    def get_buffer(self, key):
        return DataBuffer(key, self._read)

    def get(self, key):
        return self.get_buffer(key).read(-1)
