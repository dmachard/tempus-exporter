"""
Holiday and calendar metrics
"""
from datetime import datetime
import holidays
from loguru import logger
from tempus.config import config
from tempus.metrics import (
    is_public_holiday,
    is_weekend,
    is_working_day,
    current_context
)


def update_holiday_metrics():
    """Update holiday and calendar metrics"""
    try:
        now = datetime.now()
        
        # Get holidays for the country
        country_holidays = holidays.country_holidays(
            config.country_code,
            years=now.year
        )
        
        # Check if today is a holiday
        is_holiday = now.date() in country_holidays
        holiday_name = country_holidays.get(now.date(), None)
        
        # Check if weekend
        is_wknd = now.weekday() >= 5
        
        # Check if working day (not weekend and not holiday)
        is_work = not is_wknd and not is_holiday
        
        # Update metrics
        is_public_holiday.set(1 if is_holiday else 0)
        is_weekend.set(1 if is_wknd else 0)
        is_working_day.set(1 if is_work else 0)
        
        # Update context for JSON API
        current_context['calendar'] = {
            'is_weekend': is_wknd,
            'is_holiday': is_holiday,
            'holiday_name': holiday_name,
            'is_working_day': is_work,
            'day_of_week': now.strftime('%A')
        }
        
        logger.debug(
            f"Calendar metrics updated: holiday={is_holiday}, "
            f"weekend={is_wknd}, working={is_work}"
        )
        
    except Exception as e:
        logger.error(f"Error updating holiday metrics: {e}")