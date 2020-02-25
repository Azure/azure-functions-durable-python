from typing import Any

import aiohttp


@staticmethod
async def post_async_request(url: str, data: Any = None) -> [int, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url,
                                json=data) as response:
            data = await response.json()
            return [response.status, data]


@staticmethod
async def get_async_request(url: str) -> [int, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return [response.status, data]
