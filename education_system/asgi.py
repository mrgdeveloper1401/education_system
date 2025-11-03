"""
ASGI config for education_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from decouple import config

from django.core.asgi import get_asgi_application

debug_mode = config('DEBUG', cast=bool, default=False)
if debug_mode:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education_system.envs.development")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education_system.envs.production")

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