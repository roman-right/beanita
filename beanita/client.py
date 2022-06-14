from mongita import MongitaClientDisk
from mongita.common import ok_name
from mongita.errors import InvalidName

from beanita.db import Database


class Client(MongitaClientDisk):
    def __getitem__(self, db_name):
        try:
            return self._cache[db_name]
        except KeyError:
            if not ok_name(db_name):
                raise InvalidName("Database cannot be named %r." % db_name)
            db = Database(db_name, self)
            self._cache[db_name] = db
            return db
