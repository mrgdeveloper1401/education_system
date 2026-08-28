import os


from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")

django_application = get_asgi_application()

async def application(scope, receive, send):
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                # print("✅ Django ASGI startup event received")
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                # print("❌ Django ASGI shutdown event received")
                await send({'type': 'lifespan.shutdown.complete'})
                return
    else:
        await django_application(scope, receive, send)