"""
Prometheus metrics definitions
"""
from prometheus_client import Gauge, start_http_server as prom_start_http
from datetime import datetime

# Solar metrics
sun_sunrise_minutes = Gauge('sun_sunrise_minutes', 'Minutes since midnight for sunrise')
sun_sunset_minutes = Gauge('sun_sunset_minutes', 'Minutes since midnight for sunset')
sun_day_length_minutes = Gauge('sun_day_length_minutes', 'Total daylight in minutes')
sun_day_gain_minutes = Gauge('sun_day_gain_minutes', 'Daily change in daylight')
sun_is_growing_day = Gauge('sun_is_growing_day', 'Whether days are getting longer')

# Seasonal metrics
season_id = Gauge('season_id', 'Current season indicator', ['season'])
season_progress_percent = Gauge('season_progress_percent', 'Progress through season')
days_until_spring = Gauge('days_until_spring', 'Days until spring')
days_until_summer = Gauge('days_until_summer', 'Days until summer')
days_until_fall = Gauge('days_until_fall', 'Days until fall')
days_until_winter = Gauge('days_until_winter', 'Days until winter')

# Calendar metrics
is_public_holiday = Gauge('is_public_holiday', 'Is public holiday')
is_weekend = Gauge('is_weekend', 'Is weekend')
is_working_day = Gauge('is_working_day', 'Is working day')

# Trash metrics
trash_collection_today = Gauge('trash_collection_today', 'Trash today', ['type'])
trash_next_days = Gauge('trash_next_days', 'Days until next', ['type'])

# Moon metrics
moon_phase_day = Gauge('moon_phase_day', 'Current moon phase day (0-27)')
moon_phase_info = Gauge('moon_phase_info', 'Current moon phase description', ['phase'])

# Store current context for JSON API
current_context = {
    'timestamp': datetime.now().isoformat(),
    'sun': {},
    'season': {},
    'calendar': {},
    'trash': {},
    'moon': {}
}

def start_http_server(port: int):
    """Start Prometheus HTTP server"""
    prom_start_http(port)