"""
Birthday tracking logic
"""
import yaml
import os
from datetime import datetime, date as dt_date
from loguru import logger
from tempus.config import config
from tempus.metrics import (
    birthday_this_month,
    birthday_days_until,
    birthday_today,
    current_context
)

def load_birthdays():
    """Load birthdays from YAML file"""
    try:
        if not os.path.exists(config.schedule_file):
            logger.warning(f"Schedule file {config.schedule_file} not found")
            return []
            
        with open(config.schedule_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('birthdays', [])
    except Exception as e:
        logger.error(f"Error loading birthdays: {e}")
        return []

def get_days_until_birthday(current_date, birthday_str):
    """
    Calculate days until birthday.
    Format of birthday_str: MM-DD
    """
    try:
        month, day = map(int, birthday_str.split('-'))
        
        # Birthday this year
        b_date = datetime(current_date.year, month, day)
        
        # If already passed this year, look at next year
        if b_date.date() < current_date.date():
            b_date = datetime(current_date.year + 1, month, day)
            
        return (b_date.date() - current_date.date()).days
    except Exception as e:
        logger.error(f"Error calculating days until birthday {birthday_str}: {e}")
        return 999

def update_birthday_metrics():
    """Update birthday metrics"""
    try:
        birthdays = load_birthdays()
        now = datetime.now()
        current_month = now.month
        
        this_month_list = []
        
        # Clear/Reset existing label-based metrics is tricky with Gauge.
        # Ideally we'd wish to clear them, but prometheus_client doesn't make it easy
        # for labels that might have disappeared. 
        # For now, we update what we find.
        
        for b in birthdays:
            name = b.get('name')
            b_date_str = b.get('date')
            
            if not name or not b_date_str:
                continue
                
            days_until = get_days_until_birthday(now, b_date_str)
            is_today = (days_until == 0)
            
            # Check if it's this month
            b_month = int(b_date_str.split('-')[0])
            b_day = int(b_date_str.split('-')[1])
            
            if b_month == current_month:
                birthday_this_month.labels(name=name, day=b_day).set(1)
                this_month_list.append({
                    'name': name,
                    'day': b_day,
                    'days_until': days_until,
                    'is_today': is_today
                })
            else:
                # We could set it to 0 if it was previously set, 
                # but we don't know the previous labels easily here.
                pass
                
            birthday_days_until.labels(name=name).set(days_until)
            birthday_today.labels(name=name).set(1 if is_today else 0)
            
        # Update context for JSON API
        current_context['birthdays'] = {
            'this_month': this_month_list
        }
        
        logger.debug(f"Birthday metrics updated. Found {len(this_month_list)} this month.")
        
    except Exception as e:
        logger.error(f"Error updating birthday metrics: {e}")
