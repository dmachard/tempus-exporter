"""
Trash collection tracking
"""
from datetime import datetime
from loguru import logger
from tempus.metrics import (
    trash_collection_today,
    trash_next_days,
    current_context
)


# Example trash schedule (customize this)
# Days: 0=Monday, 1=Tuesday, ..., 6=Sunday
TRASH_SCHEDULE = {
    'yellow': [1],      # Tuesday
    'black': [4],       # Friday
    'green': [0, 3]     # Monday and Thursday
}


def update_trash_metrics():
    """Update trash collection metrics"""
    try:
        now = datetime.now()
        today_weekday = now.weekday()
        
        trash_info = {}
        
        for trash_type, collection_days in TRASH_SCHEDULE.items():
            # Is collection today?
            is_today = today_weekday in collection_days
            trash_collection_today.labels(type=trash_type).set(1 if is_today else 0)
            
            # Days until next collection
            days_ahead = []
            for day in collection_days:
                diff = (day - today_weekday) % 7
                if diff == 0 and not is_today:
                    diff = 7
                days_ahead.append(diff)
            
            next_days = min(days_ahead) if days_ahead else 0
            trash_next_days.labels(type=trash_type).set(next_days)
            
            trash_info[trash_type] = {
                'today': is_today,
                'next_in_days': next_days
            }
        
        # Update context for JSON API
        current_context['trash'] = trash_info
        
        logger.debug("Trash metrics updated")
        
    except Exception as e:
        logger.error(f"Error updating trash metrics: {e}")