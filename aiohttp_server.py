import os

from aiohttp import web

WS_FILE = os.path.join(os.path.dirname(__file__), "/index.html")

routes = web.RouteTableDef()


@routes.post('/news')
async def post_news(request):
    if request.body_exists:
        for web_socket in request.application["sockets"]:
            await web_socket.send_str(await request.text())
    return web.Response(status=200)


@routes.get('/ws')
async def websocket_handler(request):

    response = web.WebSocketResponse(autoping=True, heartbeat=30)
    available = response.can_prepare(request)
    if not available:
        with open(WS_FILE, "rb") as ws_file:
            return web.Response(body=ws_file.read(), content_type="text/html")

    await response.prepare(request)

    try:
        request.application["sockets"].append(response)

        async for msg in response:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.application["sockets"]:
                    if ws is not response:
                        await ws.send_str(msg.data)
            else:
                return response
        return response

    finally:
        request.application["sockets"].remove(response)


async def on_shutdown(application: web.Application):
    for web_socket in application["sockets"]:
        await web_socket.close()


def init():
    application = web.Application()
    application["sockets"] = []
    application.add_routes(routes)
    application.on_shutdown.append(on_shutdown)
    web.run_app(application)


init()
