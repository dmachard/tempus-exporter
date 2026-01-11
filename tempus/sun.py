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
    sun_season,
    current_context
)


def get_season(date: datetime, hemisphere: str = 'north') -> int:
    """Get season: 0=winter, 1=spring, 2=summer, 3=fall
    
    Args:
        date: Current date
        hemisphere: 'north' or 'south'
    """
    month = date.month
    day = date.day
    
    # Northern hemisphere
    if hemisphere == 'north':
        if (month == 3 and day >= 20) or (month > 3 and month < 6) or (month == 6 and day < 21):
            return 1  # spring
        elif (month == 6 and day >= 21) or (month > 6 and month < 9) or (month == 9 and day < 22):
            return 2  # summer
        elif (month == 9 and day >= 22) or (month > 9 and month < 12) or (month == 12 and day < 21):
            return 3  # fall
        else:
            return 0  # winter
    else:  # Southern hemisphere - reversed
        if (month == 9 and day >= 22) or (month > 9 and month < 12) or (month == 12 and day < 21):
            return 1  # spring
        elif (month == 12 and day >= 21) or (month > 12) or (month < 3) or (month == 3 and day < 20):
            return 2  # summer
        elif (month == 3 and day >= 20) or (month > 3 and month < 6) or (month == 6 and day < 21):
            return 3  # fall
        else:
            return 0  # winter


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
        season = get_season(now, config.hemisphere)
        
        sun_sunrise_minutes.set(sunrise_minutes)
        sun_sunset_minutes.set(sunset_minutes)
        sun_day_length_minutes.set(day_length)
        sun_day_gain_minutes.set(day_gain)
        sun_is_growing_day.set(is_growing)
        sun_season.set(season)
        
        # Update context for JSON API
        current_context['timestamp'] = now.isoformat()
        current_context['sun'] = {
            'sunrise': sunrise_local.strftime('%H:%M'),
            'sunset': sunset_local.strftime('%H:%M'),
            'day_length': f"{day_length // 60}h{day_length % 60:02d}m",
            'daily_change': f"{'+' if day_gain >= 0 else ''}{day_gain}min",
            'season': ['winter', 'spring', 'summer', 'fall'][season]
        }
        
        logger.debug(
            f"Sun: rise={sunrise_local.strftime('%H:%M')} set={sunset_local.strftime('%H:%M')} "
            f"length={day_length}min change={day_gain:+d}min"
        )
        
    except Exception as e:
        logger.error(f"Error updating sun metrics: {e}")