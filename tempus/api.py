"""
JSON API endpoint for human-readable context
"""
from aiohttp import web
from datetime import datetime
from loguru import logger
from tempus.metrics import current_context

async def handle_context(request):
    """Return current context as JSON"""
    return web.json_response(current_context)

async def start_api_server(port: int):
    """Start the JSON API server"""
    app = web.Application()
    app.router.add_get('/context', handle_context)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    try:
        # Keep running until cancelled
        import asyncio
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("API server shutting down...")
    finally:
        await runner.cleanup()