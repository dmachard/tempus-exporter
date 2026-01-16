"""
Moon phase monitoring
"""
from datetime import datetime
from astral import moon
from loguru import logger
from tempus.metrics import moon_phase_day, moon_phase_info, current_context

def get_moon_phase_name(phase_day):
    """
    Return the name of the moon phase based on the day (0-28).
    Broad categorization.
    """
    if phase_day < 1:
        return "New Moon"
    elif phase_day < 7:
        return "Waxing Crescent"
    elif phase_day < 8:
        return "First Quarter"
    elif phase_day < 14:
        return "Waxing Gibbous"
    elif phase_day < 15:
        return "Full Moon"
    elif phase_day < 21:
        return "Waning Gibbous"
    elif phase_day < 22:
        return "Last Quarter"
    else:
        return "Waning Crescent"

def update_moon_metrics():
    """Update moon metrics"""
    try:
        now = datetime.now()
        
        # astral.moon.phase returns 0..27.99
        # 0 = New Moon, 7 = First Quarter, 14 = Full Moon, 21 = Last Quarter
        phase = moon.phase(now)
        
        phase_name = get_moon_phase_name(phase)
        
        logger.debug(f"Moon: day={phase:.1f} phase={phase_name}")
        
        moon_phase_day.set(phase)
        
        # Reset info metric
        moon_phase_info.clear()
        moon_phase_info.labels(phase=phase_name).set(1)
        
        # Update context
        current_context['moon'] = {
            'day': round(phase, 2),
            'phase': phase_name
        }
        
    except Exception as e:
        logger.error(f"Error updating moon metrics: {e}")
