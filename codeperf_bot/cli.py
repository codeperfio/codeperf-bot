import asyncio
import logging
import sys
import traceback
import aiohttp
from aiohttp import web
import cachetools
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing
from gidgethub import sansio
from gidgethub import apps
from gidgethub import BadRequest, ValidationFailure

from codeperf_bot.config import (
    GH_APP_ID,
    GH_PRIVATE_KEY,
    PORT,
    GH_SECRET,
    check_env_var,
)

router = routing.Router()
cache = cachetools.LRUCache(maxsize=500)

routes = web.RouteTableDef()


async def main(request):
    try:
        body = await request.read()
        event = sansio.Event.from_http(request.headers, body, secret=GH_SECRET)
        if event.event == "ping":
            return web.Response(status=200)
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(session, "demo", cache=cache)
            # Give GitHub some time to reach internal consistency.
            await asyncio.sleep(1)
            await router.dispatch(event, gh)
        try:
            logging.info("GH requests remaining:", gh.rate_limit.remaining)
        except AttributeError:
            pass
        return web.Response(status=200)
    except BadRequest:
        return web.Response(status=400)
    except ValidationFailure:
        return web.Response(status=401)
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=400)


@router.register("installation", action="created")
async def repo_installation_added(event, gh, *args, **kwargs):
    installation_id = event.data["installation"]["id"]

    installation_access_token = await apps.get_installation_access_token(
        gh,
        installation_id=installation_id,
        app_id=GH_APP_ID,
        private_key=GH_PRIVATE_KEY,
    )
    repo_name = event.data["repositories"][0]["full_name"]
    url = f"/repos/{repo_name}/issues"
    response = await gh.post(
        url,
        data={
            "title": "Thanks for installing my bot",
            "body": "Thanks!",
        },
        oauth_token=installation_access_token["token"],
    )
    logging.info(response)


def cli():
    if (check_env_var(GH_PRIVATE_KEY, "GH_PRIVATE_KEY") is False) or (
        check_env_var(GH_APP_ID, "GH_APP_ID") is False
    ):
        exit(1)
    app = web.Application()
    app.router.add_post("/", main)
    port = PORT
    if port is not None:
        port = int(port)
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, port=port)
