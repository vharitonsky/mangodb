# mangodb

MangoDB is a very very thin wrapper around sync/async python mongo driver encapsulating
all details necessary for temporary file storage with zero maintenance.

1. Capped collection  - when mongo collection is capped, old data is delete when disk space is exhausted

2. TTL index - when an object has ttl index, mongo automatically deletes after ttl expires

3. Chunked storage - as mongo max document size is capped at 16Mb we have to chunkinate the documents
in the same manner GridFS does, but contrary to gridfs, we store metadata in the same collection as chunks,
this way it will be deleted along with the chunks.
