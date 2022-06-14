import datetime

import pytest
from pydantic import BaseModel
from pydantic.color import Color

from beanie.odm.enums import SortDirection
from tests.odm.models import Sample, DocumentWithBsonEncodersFiledsTypes, House


async def test_find_query():
    q = Sample.find_many(Sample.integer == 1).get_filter_query()
    assert q == {"integer": 1}

    q = Sample.find_many(
        Sample.integer == 1, Sample.nested.integer >= 2
    ).get_filter_query()
    assert q == {"$and": [{"integer": 1}, {"nested.integer": {"$gte": 2}}]}

    q = (
        Sample.find_many(Sample.integer == 1)
        .find_many(Sample.nested.integer >= 2)
        .get_filter_query()
    )
    assert q == {"$and": [{"integer": 1}, {"nested.integer": {"$gte": 2}}]}

    q = Sample.find().get_filter_query()
    assert q == {}


async def test_find_many(preset_documents):
    result = await Sample.find_many(Sample.integer > 1).to_list()  # noqa
    assert len(result) == 4
    for a in result:
        assert a.integer > 1

    len_result = 0
    async for a in Sample.find_many(Sample.integer > 1):  # noqa
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_many_skip(preset_documents):
    q = Sample.find_many(Sample.integer > 1, skip=2)
    assert q.skip_number == 2

    q = Sample.find_many(Sample.integer > 1).skip(2)
    assert q.skip_number == 2

    result = await Sample.find_many(Sample.increment > 2).skip(1).to_list()
    assert len(result) == 7
    for sample in result:
        assert sample.increment > 2

    len_result = 0
    async for sample in Sample.find_many(Sample.increment > 2).skip(1):  # noqa
        assert sample in result
        len_result += 1

    assert len_result == len(result)


async def test_find_many_limit(preset_documents):
    q = Sample.find_many(Sample.integer > 1, limit=2)
    assert q.limit_number == 2

    q = Sample.find_many(Sample.integer > 1).limit(2)
    assert q.limit_number == 2

    result = (
        await Sample.find_many(Sample.increment > 2)
        .sort(Sample.increment)
        .limit(2)
        .to_list()
    )  # noqa
    assert len(result) == 2
    for a in result:
        assert a.increment > 2

    len_result = 0
    async for a in Sample.find_many(Sample.increment > 2).sort(
        Sample.increment
    ).limit(
        2
    ):  # noqa
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_all(preset_documents):
    result = await Sample.find_all().to_list()
    assert len(result) == 10

    len_result = 0
    async for a in Sample.find_all():
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_find_one(preset_documents):
    a = await Sample.find_one(Sample.integer > 1)  # noqa
    assert a.integer > 1

    a = await Sample.find_one(Sample.integer > 100)  # noqa
    assert a is None


async def test_get(preset_documents):
    a = await Sample.find_one(Sample.integer > 1)  # noqa
    assert a.integer > 1

    new_a = await Sample.get(a.id)
    assert new_a == a

    # check for another type
    new_a = await Sample.get(str(a.id))
    assert new_a == a


async def test_sort(preset_documents):
    q = Sample.find_many(Sample.integer > 1, sort="-integer")
    assert q.sort_expressions == [("integer", SortDirection.DESCENDING)]

    q = Sample.find_many(Sample.integer > 1, sort="integer")
    assert q.sort_expressions == [("integer", SortDirection.ASCENDING)]

    q = Sample.find_many(Sample.integer > 1).sort("-integer")
    assert q.sort_expressions == [("integer", SortDirection.DESCENDING)]

    q = (
        Sample.find_many(Sample.integer > 1)
        .find_many(Sample.integer < 100)
        .sort("-integer")
    )
    assert q.sort_expressions == [("integer", SortDirection.DESCENDING)]

    result = await Sample.find_many(
        Sample.integer > 1, sort="-integer"
    ).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf >= a.integer
        i_buf = a.integer

    result = await Sample.find_many(
        Sample.integer > 1, sort="+integer"
    ).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf <= a.integer
        i_buf = a.integer

    result = await Sample.find_many(
        Sample.integer > 1, sort="integer"
    ).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf <= a.integer
        i_buf = a.integer

    result = await Sample.find_many(
        Sample.integer > 1, sort=-Sample.integer
    ).to_list()
    i_buf = None
    for a in result:
        if i_buf is None:
            i_buf = a.integer
        assert i_buf >= a.integer
        i_buf = a.integer

    with pytest.raises(TypeError):
        Sample.find_many(Sample.integer > 1, sort=1)


async def test_find_many_with_projection(preset_documents):
    class SampleProjection(BaseModel):
        string: str
        integer: int

    result = (
        await Sample.find_many(Sample.integer > 1)
        .project(projection_model=SampleProjection)
        .to_list()
    )
    assert len(result) == 4

    result = (
        await Sample.find_many(Sample.integer > 1)
        .find_many(projection_model=SampleProjection)
        .to_list()
    )
    assert isinstance(result[0], SampleProjection)


@pytest.mark.skip("Not supported")
async def test_find_many_with_custom_projection(preset_documents):
    class SampleProjection(BaseModel):
        string: str
        i: int

        class Settings:
            projection = {"string": 1, "i": "$nested.integer"}

    result = (
        await Sample.find_many(Sample.integer > 1)
        .project(projection_model=SampleProjection)
        .to_list()
    )
    assert result == [
        SampleProjection(string="test_2", i=3),
        SampleProjection(string="test_2", i=4),
    ]


async def test_find_many_with_session(preset_documents, session):
    q_1 = Sample.find_many(Sample.integer > 1).set_session(session)
    assert q_1.session == session

    q_2 = Sample.find_many(Sample.integer > 1)
    assert q_2.session == session

    result = await q_2.to_list()

    assert len(result) == 4
    for a in result:
        assert a.integer > 1

    len_result = 0
    async for a in Sample.find_many(Sample.integer > 1):
        assert a in result
        len_result += 1

    assert len_result == len(result)


async def test_bson_encoders_filed_types():
    custom = DocumentWithBsonEncodersFiledsTypes(
        color="7fffd4", timestamp=datetime.datetime.utcnow()
    )
    c = await custom.insert()
    c_fromdb = await DocumentWithBsonEncodersFiledsTypes.find_one(
        DocumentWithBsonEncodersFiledsTypes.color == Color("7fffd4")
    )
    assert c_fromdb.color.as_hex() == c.color.as_hex()


@pytest.mark.skip("Not supported")
async def test_find_by_datetime(preset_documents):
    datetime_1 = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    datetime_2 = datetime.datetime.utcnow() - datetime.timedelta(days=2)
    docs = await Sample.find(
        Sample.timestamp >= datetime_1,
        Sample.timestamp <= datetime_2,
    ).to_list()
    assert len(docs) == 5


async def test_find_first_or_none(preset_documents):
    doc = (
        await Sample.find(Sample.increment > 1)
        .sort(-Sample.increment)
        .first_or_none()
    )
    assert doc.increment == 9

    doc = (
        await Sample.find(Sample.increment > 9)
        .sort(-Sample.increment)
        .first_or_none()
    )
    assert doc is None


@pytest.mark.skip("Not supported")
async def test_find_pymongo_kwargs(preset_documents):
    with pytest.raises(TypeError):
        await Sample.find_many(Sample.increment > 1, wrong=100).to_list()

    await Sample.find_many(
        Sample.increment > 1, Sample.integer > 1, allow_disk_use=True
    ).to_list()

    await Sample.find_many(
        Sample.increment > 1, Sample.integer > 1, hint="integer_1"
    ).to_list()

    await House.find_many(
        House.height > 1, fetch_links=True, hint="height_1"
    ).to_list()

    await House.find_many(
        House.height > 1, fetch_links=True, allowDiskUse=True
    ).to_list()

    await Sample.find_one(
        Sample.increment > 1, Sample.integer > 1, hint="integer_1"
    )

    await House.find_one(House.height > 1, fetch_links=True, hint="height_1")
