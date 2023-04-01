import os
from aiohttp import web
import asyncio
from asyncio import Queue
import time
import aiohttp


WEBSOCKET_FILE = os.path.join(os.path.dirname(__file__), 'index.html')


async def handler(request: web.Request):
    response = web.WebSocketResponse(heartbeat=5)
    available = response.can_prepare(request)

    if not available:
        with open(WEBSOCKET_FILE, 'rb') as ws_file:
            return web.Response(body=ws_file.read(), content_type='text/html')

    await response.prepare(request)
    await response.send_str('Hello!')

    try:
        print('New joiner.')
        for web_socket in request.app['sockets']:
            await web_socket.send_str('New joiner.')
        request.app["sockets"].append(response)

        async for message in response:
            if message.type == web.WSMsgType.TEXT:
                if message.data == "check":
                    await response.send_str('connection OK')
                else:
                    for web_socket in request.app['sockets']:
                        if web_socket is not response:
                            await web_socket.send_str(message.data)
            else:
                return response

        return response

    finally:
        request.app['sockets'].remove(response)
        print('Someone close connection.')
        for web_socket in request.app['sockets']:
            await web_socket.send_str('Someone close connection.')


async def on_close(application: web.Application):
    for web_socket in application['sockets']:
        await web_socket.close()


def init():
    application = web.Application()
    application['sockets'] = []
    application.router.add_get('/news', handler)
    application.on_close.append(on_close)
    return application


web.run_app(init())
