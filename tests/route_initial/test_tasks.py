import pytest
from app.routes.initial import tasks


@pytest.mark.asyncio
async def test_generate_data():
    data = await tasks.generate_data()
    assert len(data) == 4
    assert set(data.keys()) == {"id", "type", "create_date", "value"}


@pytest.mark.asyncio
async def test_generate_data_with_constant():
    data = await tasks.generate_data({
        "add": "foo",
    })
    assert len(data) == 5
    assert set(data.keys()) == {"id", "type", "create_date", "value", "add"}
