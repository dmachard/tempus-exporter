"""
Clock and Daylight Saving Time (DST) metrics
"""
import pytz
from datetime import datetime, timedelta
from loguru import logger
from tempus.config import config
from tempus.metrics import (
    clock_is_summer_time,
    clock_days_until_dst_change,
    clock_dst_change_offset,
    current_context
)


def get_dst_info(tz_name: str) -> tuple:
    """Get current DST status and next transition info
    
    Returns:
        tuple: (is_summer_time, days_until_change, next_change_date, next_change_offset)
    """
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.UTC
        
    now = datetime.now(tz)
    
    # is_dst() returns True if currently in DST for the given timezone
    is_summer = now.dst() != timedelta(0)
    
    # Find next transition by checking day by day
    current_dst = now.dst()
    next_change_dt = None
    
    # Check up to 366 days ahead
    for i in range(1, 367):
        future_date = tz.normalize(now + timedelta(days=i))
        if future_date.dst() != current_dst:
            # Found the day of change
            next_change_dt = future_date.replace(hour=0, minute=0, second=0, microsecond=0)
            break
            
    # Next offset: 
    # If summer -> winter: we do -1 (e.g. 3:00 becomes 2:00)
    # If winter -> summer: we do +1 (e.g. 2:00 becomes 3:00)
    next_offset = -1 if is_summer else 1
    
    days_until = (next_change_dt - now).days if next_change_dt else 0
    
    return is_summer, days_until, next_change_dt, next_offset


def update_clock_metrics():
    """Update clock and DST metrics"""
    try:
        is_summer, days_until, next_date, next_offset = get_dst_info(config.timezone)
        
        # Update Prometheus metrics
        clock_is_summer_time.set(1 if is_summer else 0)
        clock_days_until_dst_change.set(days_until)
        clock_dst_change_offset.set(next_offset)
        
        # Update JSON context
        current_context['clock'] = {
            'is_summer_time': is_summer,
            'days_until_change': days_until,
            'next_change_date': next_date.strftime('%Y-%m-%d') if next_date else 'Unknown',
            'next_change_offset': next_offset,
            'timezone': config.timezone
        }
        
        status = "Summer Time (+1)" if is_summer else "Winter Time (0)"
        logger.debug(
            f"Clock metrics updated: {status}, "
            f"next change in {days_until} days ({next_offset:+1}h)"
        )
        
    except Exception as e:
        logger.error(f"Error updating clock metrics: {e}")
