"""
Seasonal metrics and calculations
"""
from datetime import datetime
from loguru import logger
from tempus.config import config
from tempus.metrics import (
    season_id,
    season_progress_percent,
    days_until_season_change,
    current_context
)


def get_season_info(date: datetime, hemisphere: str = 'north') -> tuple:
    """Get season name, progress, and days until next event
    
    Args:
        date: Current date
        hemisphere: 'north' or 'south'
    """
    month = date.month
    day = date.day
    
    # Season boundaries for Northern hemisphere
    if hemisphere == 'north':
        if (month == 3 and day >= 20) or (month > 3 and month < 6) or (month == 6 and day < 21):
            current_season = 'spring'
            season_start = datetime(date.year, 3, 20)
            season_end = datetime(date.year, 6, 21)
        elif (month == 6 and day >= 21) or (month > 6 and month < 9) or (month == 9 and day < 22):
            current_season = 'summer'
            season_start = datetime(date.year, 6, 21)
            season_end = datetime(date.year, 9, 22)
        elif (month == 9 and day >= 22) or (month > 9 and month < 12) or (month == 12 and day < 21):
            current_season = 'fall'
            season_start = datetime(date.year, 9, 22)
            season_end = datetime(date.year, 12, 21)
        else:
            current_season = 'winter'
            if month == 12:
                season_start = datetime(date.year, 12, 21)
                season_end = datetime(date.year + 1, 3, 20)
            else:
                season_start = datetime(date.year - 1, 12, 21)
                season_end = datetime(date.year, 3, 20)
    else:  # Southern hemisphere - seasons are reversed
        if (month == 9 and day >= 22) or (month > 9 and month < 12) or (month == 12 and day < 21):
            current_season = 'spring'
            season_start = datetime(date.year, 9, 22)
            season_end = datetime(date.year, 12, 21)
        elif (month == 12 and day >= 21) or (month > 12) or (month < 3) or (month == 3 and day < 20):
            current_season = 'summer'
            if month == 12:
                season_start = datetime(date.year, 12, 21)
                season_end = datetime(date.year + 1, 3, 20)
            else:
                season_start = datetime(date.year - 1, 12, 21)
                season_end = datetime(date.year, 3, 20)
        elif (month == 3 and day >= 20) or (month > 3 and month < 6) or (month == 6 and day < 21):
            current_season = 'fall'
            season_start = datetime(date.year, 3, 20)
            season_end = datetime(date.year, 6, 21)
        else:
            current_season = 'winter'
            season_start = datetime(date.year, 6, 21)
            season_end = datetime(date.year, 9, 22)
    
    # Calculate progress
    total_days = (season_end - season_start).days
    elapsed_days = (date - season_start).days
    progress = min(100, max(0, (elapsed_days / total_days) * 100))
    days_to_next = (season_end - date).days
    
    return current_season, progress, max(0, days_to_next)


def update_season_metrics():
    """Update seasonal metrics"""
    try:
        now = datetime.now()
        season_name, progress, days_to_event = get_season_info(now, config.hemisphere)
        
        # Reset all season indicators
        for season in ['winter', 'spring', 'summer', 'fall']:
            season_id.labels(season=season).set(0)
        
        # Set current season
        season_id.labels(season=season_name).set(1)
        season_progress_percent.set(progress)
        days_until_season_change.set(days_to_event)
        
        # Update context for JSON API
        current_context['season'] = {
            'name': season_name,
            'progress': round(progress, 1),
            'days_to_next': days_to_event,
            'hemisphere': config.hemisphere
        }
        
        logger.debug(
            f"Season metrics updated ({config.hemisphere}): {season_name} at {progress:.1f}%, "
            f"{days_to_event} days to next event"
        )
        
    except Exception as e:
        logger.error(f"Error updating season metrics: {e}")