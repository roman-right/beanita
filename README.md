## Beanita

Local MongoDB-like database, based on [Mongita](https://github.com/scottrogowski/mongita) and prepared to work with [Beanie ODM](https://github.com/roman-right/beanie)

I highly recommend using it only for experiment purposes. It is safer to use a real MongoDB database and for testing, and for production.

### Init

```python
from beanie import init_beanie, Document
from beanita import Client


class Sample(Document):
    name: str


async def init_database():
    cli = Client("LOCAL_DIRECTORY")
    db = cli["DATABASE_NAME"]
    await init_beanie(
        database=db,
        document_models=[Sample],
    )
```

### Not supported

- Links
- Aggregations
- Union Documents
- other features, that were not implemented in Mongita