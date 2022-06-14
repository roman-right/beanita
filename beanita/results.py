class InsertOneResult:
    def __init__(self, inserted_id):
        self.acknowledged = True
        self.inserted_id = inserted_id


class InsertManyResult:
    def __init__(self, documents):
        self.acknowledged = True
        self.inserted_ids = [d["_id"] for d in documents]


class UpdateResult:
    def __init__(
        self, matched_count, modified_count, upserted_id=None, **kwargs
    ):
        self.acknowledged = True
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id
        self.updatedExisting = modified_count

    @property
    def raw_result(self):
        return self.__dict__

    @classmethod
    def from_mongita_result(cls, res):
        return cls(**res.__dict__)


class DeleteResult:
    def __init__(self, deleted_count):
        self.acknowledged = True
        self.deleted_count = deleted_count
