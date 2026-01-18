"""
Seasonal metrics and calculations
"""
from datetime import datetime
from loguru import logger
from tempus.config import config
from tempus.metrics import (
    season_id,
    season_progress_percent,
    days_until_spring,
    days_until_summer,
    days_until_fall,
    days_until_winter,
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


def get_days_until_seasons(date: datetime) -> dict:
    """Calculate days until each season start
    
    Args:
        date: Current date
        
    Returns:
        Dictionary with days until each season
    """
    year = date.year
    
    # Season start dates (Northern hemisphere dates - used as reference)
    spring_start = datetime(year, 3, 20)
    summer_start = datetime(year, 6, 21)
    fall_start = datetime(year, 9, 22)
    winter_start = datetime(year, 12, 21)
    
    # Calculate days until each season
    days_to_spring = (spring_start - date).days
    days_to_summer = (summer_start - date).days
    days_to_fall = (fall_start - date).days
    days_to_winter = (winter_start - date).days
    
    # If a season has passed this year, calculate for next year
    if days_to_spring < 0:
        days_to_spring = (datetime(year + 1, 3, 20) - date).days
    if days_to_summer < 0:
        days_to_summer = (datetime(year + 1, 6, 21) - date).days
    if days_to_fall < 0:
        days_to_fall = (datetime(year + 1, 9, 22) - date).days
    if days_to_winter < 0:
        days_to_winter = (datetime(year + 1, 12, 21) - date).days
    
    return {
        'spring': days_to_spring,
        'summer': days_to_summer,
        'fall': days_to_fall,
        'winter': days_to_winter
    }


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
        
        # Calculate and set days until each season
        days_until_seasons = get_days_until_seasons(now)
        days_until_spring.set(days_until_seasons['spring'])
        days_until_summer.set(days_until_seasons['summer'])
        days_until_fall.set(days_until_seasons['fall'])
        days_until_winter.set(days_until_seasons['winter'])
        
        # Update context for JSON API
        current_context['season'] = {
            'name': season_name,
            'progress': round(progress, 1),
            'days_until_spring': days_until_seasons['spring'],
            'days_until_summer': days_until_seasons['summer'],
            'days_until_fall': days_until_seasons['fall'],
            'days_until_winter': days_until_seasons['winter'],
            'hemisphere': config.hemisphere
        }
        
        logger.debug(
            f"Season metrics updated ({config.hemisphere}): {season_name} at {progress:.1f}%, "
            f"spring:{days_until_seasons['spring']}d, summer:{days_until_seasons['summer']}d, "
            f"fall:{days_until_seasons['fall']}d, winter:{days_until_seasons['winter']}d"
        )
        
    except Exception as e:
        logger.error(f"Error updating season metrics: {e}")