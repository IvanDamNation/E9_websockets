import os
from aiohttp import web
from aiohttp.web import run_app

WEBSOCKET_FILE = os.path.join(os.path.dirname(__file__), 'index.html')


routes = web.RouteTableDef()


@routes.post('/news')
async def post(request):
    if request.body_exists:
        for websocket in request.application["sockets"]:
            await websocket.send_str(await request.text())
    return web.Response(status=200)


@routes.get('/ws')
async def handler(request):

    response = web.WebSocketResponse(autoping=True, heartbeat=30)
    available = response.can_prepare(request)

    if not available:
        with open(WEBSOCKET_FILE, 'rb') as ws_file:
            return web.Response(body=ws_file.read(), content_type='text/html')

    await response.prepare(request)

    try:
        request.app["sockets"].append(response)

        async for message in response:
            if message.type == web.WSMsgType.TEXT:
                for web_socket in request.app['sockets']:
                    if web_socket is not response:
                        await web_socket.send_str(message.data)
            else:
                return response
        return response

    finally:
        request.app['sockets'].remove(response)


async def on_close(application: web.Application):
    for web_socket in application['sockets']:
        await web_socket.close()


def init():
    application = web.Application()
    application['sockets'] = []
    application.add_routes(routes)
    application.on_close.append(on_close)
    web.run_app(application)


run_app()
