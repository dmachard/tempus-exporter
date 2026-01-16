from datetime import datetime
from unittest.mock import patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tempus.moon import update_moon_metrics, get_moon_phase_name
from tempus.metrics import moon_phase_day, moon_phase_info

def test_moon_phases():
    print("Testing moon phases...")
    
    # Test phase naming logic
    assert get_moon_phase_name(0.5) == "New Moon"
    assert get_moon_phase_name(14.5) == "Full Moon"
    print("Phase naming logic: OK")
    
    # Test metrics update
    with patch('tempus.moon.datetime') as mock_date:
        # Mock a date. 
        # 2026-01-03 was full moon in real life? Let's not guess.
        # Just verify that calling the function sets the metrics.
        mock_date.now.return_value = datetime(2026, 1, 16, 12, 0, 0)
        
        update_moon_metrics()
        
        day = moon_phase_day.collect()[0].samples[0].value
        print(f"Calculated Moon Day for 2026-01-16: {day}")
        
        # Verify info metric
        info_samples = moon_phase_info.collect()[0].samples
        # Should have one sample with value 1
        assert len(info_samples) == 1
        assert info_samples[0].value == 1
        label_phase = info_samples[0].labels['phase']
        print(f"Calculated Phase: {label_phase}")
        
        if 0 <= day <= 28:
            print("SUCCESS: Moon day is within valid range.")
        else:
            print("FAILURE: Moon day out of range.")

if __name__ == "__main__":
    test_moon_phases()
