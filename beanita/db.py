from mongita.common import ok_name
from mongita.database import Database as MongitaDatabase
from mongita.errors import InvalidName

from beanita.collection import Collection


class Database(MongitaDatabase):
    UNIMPLEMENTED = [
        "aggregate",
        "codec_options",
        "create_collection",
        "dereference",
        "get_collection",
        "next",
        "profiling_info",
        "profiling_level",
        "read_concern",
        "read_preference",
        "set_profiling_level",
        "validate_collection",
        "watch",
        "with_options",
        "write_concern",
    ]

    def __getitem__(self, collection_name):
        try:
            return self._cache[collection_name]
        except KeyError:
            if not ok_name(collection_name):
                raise InvalidName(
                    "Collection cannot be named %r." % collection_name
                )
            coll = Collection(collection_name, self)
            self._cache[collection_name] = coll
            return coll

    async def command(self, *args, **kwargs):
        return {"version": "4.4"}

    async def list_collection_names(self):
        return super().list_collection_names()
