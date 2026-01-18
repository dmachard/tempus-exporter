import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock config
with patch('tempus.config.config') as mock_config:
    mock_config.country_code = 'FR'
    from tempus.holidays import update_holiday_metrics
    from tempus.metrics import is_public_holiday, is_weekend, is_working_day

def test_holiday_logic():
    print("Testing Holiday and Calendar Logic...")
    
    # 1. Test a weekend (Jan 18, 2026 is Sunday)
    with patch('tempus.holidays.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2026, 1, 18)
        update_holiday_metrics()
        
        assert is_weekend._value.get() == 1
        assert is_working_day._value.get() == 0
        
    # 2. Test a working day (Jan 19, 2026 is Monday)
    with patch('tempus.holidays.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2026, 1, 19)
        update_holiday_metrics()
        
        assert is_weekend._value.get() == 0
        assert is_working_day._value.get() == 1
        assert is_public_holiday._value.get() == 0

    # 3. Test a public holiday (Jan 1, 2026 in France)
    with patch('tempus.holidays.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2026, 1, 1)
        update_holiday_metrics()
        
        assert is_public_holiday._value.get() == 1
        assert is_working_day._value.get() == 0

    print("SUCCESS: Holiday logic verified.")

if __name__ == "__main__":
    test_holiday_logic()
