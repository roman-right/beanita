from mongita.collection import (
    Collection as MongitaCollection,
    _validate_filter,
    _get_item_from_doc,
)
from mongita.common import support_alert
from mongita.errors import MongitaError

from beanita.cursor import Cursor
from beanita.results import UpdateResult


class Collection(MongitaCollection):
    UNIMPLEMENTED = [
        "aggregate",
        "aggregate_raw_batches",
        "bulk_write",
        "codec_options",
        "ensure_index",
        "estimated_document_count",
        "find_one_and_delete",
        "find_one_and_replace",
        "find_one_and_update",
        "find_raw_batches",
        "inline_map_reduce",
        "list_indexes",
        "map_reduce",
        "next",
        "options",
        "read_concern",
        "read_preference",
        "rename",
        "watch",
    ]

    @support_alert
    async def index_information(self):
        ret = {"_id_": {"key": [("_id", 1)]}}
        metadata = self.__get_metadata()
        for idx in metadata.get("indexes", {}).values():
            ret[idx["_id"]] = {"key": [(idx["key_str"], idx["direction"])]}
        return ret

    async def create_indexes(self, indexes):
        return []  # TODO create indexes here

    @support_alert
    async def insert_one(self, document, session):
        return super().insert_one(document)

    @support_alert
    async def insert_many(self, documents, ordered=True, session=None):
        return super().insert_many(documents, ordered)

    @support_alert
    async def find_one(
        self, filter=None, sort=None, skip=None, session=None, projection=None
    ):
        return super().find_one(filter, sort, skip)

    @support_alert
    def find(
        self,
        filter=None,
        sort=None,
        limit=None,
        skip=None,
        projection=None,
        session=None,
    ):
        print(filter)
        res = super().find(filter, sort, limit, skip)
        print(res)
        return Cursor(res)

    @support_alert
    async def update_one(self, filter, update, upsert=False, session=None):
        return super().update_one(filter, update, upsert)

    @support_alert
    async def update_many(self, filter, update, upsert=False, session=None):
        return super().update_many(filter, update, upsert)

    @support_alert
    async def replace_one(
        self, filter, replacement, upsert=False, session=None
    ):
        res = super().replace_one(filter, replacement, upsert)
        return UpdateResult.from_mongita_result(res)

    @support_alert
    async def delete_one(self, filter, session=None):
        return super().delete_one(filter)

    @support_alert
    async def delete_many(self, filter, session=None):
        return super().delete_many(filter)

    @support_alert
    async def count_documents(self, filter):
        return super().count_documents(filter)

    @support_alert
    async def distinct(self, key, filter=None, session=None):
        """
        Given a key, return all distinct documents matching the key

        :param key str:
        :param filter dict|None:
        :rtype: list[str]
        """

        if not isinstance(key, str):
            raise MongitaError("The 'key' parameter must be a string")
        filter = filter or {}
        _validate_filter(filter)
        uniq = set()
        for doc in await self.find(filter).to_list():
            uniq.add(_get_item_from_doc(doc, key))
        uniq.discard(None)
        return list(uniq)

    async def drop(self):
        await self.delete_many({})

    async def drop_indexes(self):
        pass  # TODO add index dropping
        # for index_name in (await self.index_information()).keys():
        #     self.drop_index(index_name)
