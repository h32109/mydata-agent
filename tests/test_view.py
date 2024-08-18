import pytest
from starlette import status


@pytest.mark.asyncio
async def test_get_page(client):
    response = await client.get(
        "/agent"
    )
    assert response.status_code == status.HTTP_200_OK