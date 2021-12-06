from aiohttp import web

from codeperf_bot import cli
from codeperf_bot.config import GH_SECRET


async def test_ping(aiohttp_client):
    app = web.Application()
    app.router.add_post("/", cli.main)
    client = await aiohttp_client(app)
    headers = {"x-github-event": "ping", "x-github-delivery": "1234"}
    data = {"zen": "testing is good"}
    response = await client.post("/", headers=headers, json=data)
    assert response.status == 200
