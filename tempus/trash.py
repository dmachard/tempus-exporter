"""
Trash collection tracking
"""
import yaml
import os
from datetime import datetime, timedelta
from loguru import logger
from tempus.config import config
from tempus.metrics import (
    trash_collection_today,
    trash_next_days,
    current_context
)

DAYS_MAP = {
    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
    'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
}

def load_schedule():
    """Load schedule from YAML file"""
    try:
        if not os.path.exists(config.schedule_file):
            logger.warning(f"Schedule file {config.schedule_file} not found")
            return {}
            
        with open(config.schedule_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('trash', {})
    except Exception as e:
        logger.error(f"Error loading schedule: {e}")
        return {}

def get_next_collection_days(today, trash_config):
    """
    Calculate days until next collection.
    Returns 0 if today is collection day.
    """
    frequency = trash_config.get('frequency', 'weekly')
    day_name = trash_config.get('day', 'Monday')
    target_weekday = DAYS_MAP.get(day_name, 0)
    
    today_weekday = today.weekday()
    
    # Calculate days until next occurrence of the weekday
    days_until_weekday = (target_weekday - today_weekday) % 7
    next_weekday_date = today + timedelta(days=days_until_weekday)
    
    if frequency == 'weekly':
        return days_until_weekday
        
    elif frequency == 'biweekly':
        ref_date_str = trash_config.get('reference_date')
        if not ref_date_str:
            logger.warning("No reference_date for biweekly schedule")
            return 999
            
        ref_date = datetime.strptime(str(ref_date_str), "%Y-%m-%d").date()
        
        # Check if next_weekday_date aligns with reference week
        # (next_weekday_date - ref_date) should be multiple of 14 days
        
        diff_days = (next_weekday_date.date() - ref_date).days
        
        if diff_days % 14 == 0:
            return days_until_weekday
        else:
            # It's the week after
            return days_until_weekday + 7
            
    return 999

def update_trash_metrics():
    """Update trash collection metrics"""
    try:
        schedule = load_schedule()
        if not schedule:
            return

        now = datetime.now()
        trash_info = {}
        
        # Reset metrics? Current implementation of prometheus_client keeps old labels.
        # Ideally we might want to clear them if config changes drastically, 
        # but for now we just update/set them.
        
        for trash_type, trash_config in schedule.items():
            days_until = get_next_collection_days(now, trash_config)
            
            is_today = (days_until == 0)
            
            trash_collection_today.labels(type=trash_type).set(1 if is_today else 0)
            trash_next_days.labels(type=trash_type).set(days_until)
            
            trash_info[trash_type] = {
                'today': is_today,
                'next_in_days': days_until
            }
            
            logger.debug(f"Trash {trash_type}: today={is_today} next_in={days_until}")
        
        # Update context for JSON API
        current_context['trash'] = trash_info
        
        logger.debug("Trash metrics updated")
        
    except Exception as e:
        logger.error(f"Error updating trash metrics: {e}")