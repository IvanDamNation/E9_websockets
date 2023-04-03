import os

from aiohttp import web

WS_FILE = os.path.join(os.path.dirname(__file__), "index.html")


def init():
    app = web.Application()
    app["sockets"] = []
    app.router.add_get("/", wshandler)
    app.router.add_post("/news", post_add_news)
    app.on_shutdown.append(on_shutdown)
    return app


async def post_add_news(request):
    t = request.query['text']
    for ws in request.app["sockets"]:
        await ws.send_str(t)
    return web.Response(text=t)


async def wshandler(request: web.Request):
    resp = web.WebSocketResponse(autoping=True, heartbeat=30)
    available = resp.can_prepare(request)
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)

    await resp.send_str("Welcome on news portal.")

    try:
        for ws in request.app["sockets"]:
            await ws.send_str("New user connected")
        request.app["sockets"].append(resp)

        async for msg in resp:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)
        for ws in request.app["sockets"]:
            await ws.send_str("User disconnected.")


async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close()


web.run_app(init())
