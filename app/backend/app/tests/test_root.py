import pytest
from httpx import AsyncClient
from requests import Response


@pytest.mark.asyncio
async def test_root(async_client: AsyncClient):
    res: Response = await async_client.get("/")
    print(res.json())
    assert res.status_code == 200
    assert res.json().get("detail") == "Hello World!"
