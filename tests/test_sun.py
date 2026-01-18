import sys
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock config
with patch('tempus.config.config') as mock_config:
    mock_config.latitude = 49.2
    mock_config.longitude = -0.4
    mock_config.timezone = 'Europe/Paris'
    from tempus.sun import update_sun_metrics
    from tempus.metrics import sun_sunrise_minutes, sun_sunset_minutes, sun_day_length_minutes

def test_sun_metrics():
    print("Testing Sun Metrics...")
    
    # Mock astral's sun function to return fixed values
    mock_sun_data = {
        'sunrise': datetime(2026, 1, 1, 8, 0, tzinfo=timezone.utc),
        'sunset': datetime(2026, 1, 1, 17, 0, tzinfo=timezone.utc)
    }
    
    # Mock yesterday too
    mock_yesterday_sun = {
        'sunrise': datetime(2026, 1, 1, 8, 1, tzinfo=timezone.utc),
        'sunset': datetime(2026, 1, 1, 16, 59, tzinfo=timezone.utc)
    }

    with patch('tempus.sun.sun') as mock_astral_sun:
        # First call for today, second for yesterday
        mock_astral_sun.side_effect = [mock_sun_data, mock_yesterday_sun]
        
        # We also need to mock datetime.now(tz) to be predictable
        with patch('tempus.sun.datetime') as mock_datetime:
            mock_now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            update_sun_metrics()
            
            # 8:00 AM is 480 minutes
            assert sun_sunrise_minutes._value.get() == 480
            # 5:00 PM is 1020 minutes
            assert sun_sunset_minutes._value.get() == 1020
            # 1020 - 480 = 540
            assert sun_day_length_minutes._value.get() == 540
            
    print("SUCCESS: Sun metrics verified.")

if __name__ == "__main__":
    test_sun_metrics()
