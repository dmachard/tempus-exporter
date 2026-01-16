"""
Solar calculations and metrics
"""
from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
from loguru import logger
import pytz
from tempus.config import config
from tempus.metrics import (
    sun_sunrise_minutes,
    sun_sunset_minutes,
    sun_day_length_minutes,
    sun_day_gain_minutes,
    sun_is_growing_day,
    current_context
)

def update_sun_metrics():
    """Update all solar metrics"""
    try:
        # Get timezone
        tz = pytz.timezone(config.timezone)
        now = datetime.now(tz)
        
        location = LocationInfo(
            name="Location",
            region="Region",
            timezone=config.timezone,
            latitude=config.latitude,
            longitude=config.longitude
        )
        
        # Calculate sun times - astral handles timezone correctly via LocationInfo
        today_sun = sun(location.observer, date=now.date(), tzinfo=location.timezone)
        yesterday_sun = sun(location.observer, date=(now - timedelta(days=1)).date(), tzinfo=location.timezone)
        
        sunrise_local = today_sun['sunrise']
        sunset_local = today_sun['sunset']
        yesterday_sunrise = yesterday_sun['sunrise']
        yesterday_sunset = yesterday_sun['sunset']
        
        sunrise_minutes = sunrise_local.hour * 60 + sunrise_local.minute
        sunset_minutes = sunset_local.hour * 60 + sunset_local.minute
        day_length = sunset_minutes - sunrise_minutes
        
        yesterday_length = (
            (yesterday_sunset.hour * 60 + yesterday_sunset.minute) -
            (yesterday_sunrise.hour * 60 + yesterday_sunrise.minute)
        )
        
        day_gain = day_length - yesterday_length
        is_growing = 1 if day_gain > 0 else 0

        sun_sunrise_minutes.set(sunrise_minutes)
        sun_sunset_minutes.set(sunset_minutes)
        sun_day_length_minutes.set(day_length)
        sun_day_gain_minutes.set(day_gain)
        sun_is_growing_day.set(is_growing)

        # Update context for JSON API
        current_context['timestamp'] = now.isoformat()
        current_context['sun'] = {
            'sunrise': sunrise_local.strftime('%H:%M'),
            'sunset': sunset_local.strftime('%H:%M'),
            'day_length': f"{day_length // 60}h{day_length % 60:02d}m",
            'daily_change': f"{'+' if day_gain >= 0 else ''}{day_gain}min",
        }
        
        logger.debug(
            f"Sun: rise={sunrise_local.strftime('%H:%M')} set={sunset_local.strftime('%H:%M')} "
            f"length={day_length}min change={day_gain:+d}min"
        )
        
    except Exception as e:
        logger.error(f"Error updating sun metrics: {e}")