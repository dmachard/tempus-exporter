"""
Main monitoring loop
"""
import asyncio
import signal
from datetime import datetime
from loguru import logger
from tempus.config import config
from tempus.sun import update_sun_metrics
from tempus.seasons import update_season_metrics
from tempus.holidays import update_holiday_metrics
from tempus.trash import update_trash_metrics
from tempus.metrics import start_http_server
from tempus.api import start_api_server


def run_all_updates():
    """Run all metric updates"""
    update_sun_metrics()
    update_season_metrics()
    update_holiday_metrics()
    update_trash_metrics()


async def daily_updates(start_shutdown):
    """Run daily updates at midnight"""
    last_date = None
    
    while not start_shutdown.is_set():
        now = datetime.now()
        
        if last_date != now.date():
            logger.info(f"Running daily updates for {now.date()}")
            try:
                run_all_updates()
                last_date = now.date()
            except Exception as e:
                logger.error(f"Error in daily updates: {e}")
        
        # Calculate seconds until the next minute
        sleep_seconds = 60 - datetime.now().second
        
        try:
            await asyncio.wait_for(start_shutdown.wait(), timeout=sleep_seconds)
        except asyncio.TimeoutError:
            pass

async def run_monitor(start_shutdown):
    """Run the monitor with both update loop and API server"""
    # Start API server task
    api_task = asyncio.create_task(start_api_server(config.api_port))
    
    # Start daily updates task
    updates_task = asyncio.create_task(daily_updates(start_shutdown))
    
    # Wait for shutdown signal
    await start_shutdown.wait()
    
    # Cancel tasks
    logger.info("Cancelling tasks...")
    api_task.cancel()
    updates_task.cancel()
    
    # Wait for tasks to finish
    await asyncio.gather(api_task, updates_task, return_exceptions=True)


def start_monitor():
    """Start the monitoring service"""
    logger.info("Starting Tempus Exporter")
    logger.info(f"Location: {config.latitude}, {config.longitude}")
    
    start_http_server(config.port)
    logger.info(f"Metrics available at http://0.0.0.0:{config.port}/metrics")
    logger.info(f"JSON API available at http://0.0.0.0:{config.api_port}/context")
    
    start_shutdown = asyncio.Event()
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        start_shutdown.set()
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Running initial updates...")
    run_all_updates()
    
    try:
        asyncio.run(run_monitor(start_shutdown))
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    
    logger.info("Tempus Exporter stopped")