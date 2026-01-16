import sys
import os
import yaml
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock config before importing trash
with patch('tempus.config.config') as mock_config:
    mock_config.schedule_file = "test_schedule.yaml"
    from tempus.trash import get_next_collection_days, update_trash_metrics, load_schedule

def test_trash_schedule():
    print("Testing Trash Schedule...")
    
    # 1. Create a test schedule
    test_schedule_content = {
        'trash': {
            'black': {
                'frequency': 'biweekly',
                'day': 'Friday',
                'reference_date': '2026-01-16' # Today!
            },
            'yellow': {
                'frequency': 'biweekly',
                'day': 'Friday',
                'reference_date': '2026-01-23' # Next Friday
            }
        }
    }
    
    with open('test_schedule.yaml', 'w') as f:
        yaml.dump(test_schedule_content, f)
        
    try:
        # Load config manually to test our helper
        # But we need to patch config in trash.py context
        # We already patched config import above, but we need to ensure load_schedule sees the right file
        # We mocked config.schedule_file above globally for the module.
        
        # Test Case 1: Today (2026-01-16, Friday)
        # Black should be TODAY (0 days)
        # Yellow should be NEXT WEEK (7 days)
        
        current_date = datetime(2026, 1, 16, 10, 0, 0) # Friday
        
        schedule = load_schedule()
        
        # Check Black
        black_days = get_next_collection_days(current_date, schedule['black'])
        print(f"2026-01-16 (Black Ref): Black In {black_days} days (Expected 0)")
        assert black_days == 0
        
        # Check Yellow
        yellow_days = get_next_collection_days(current_date, schedule['yellow'])
        print(f"2026-01-16: Yellow In {yellow_days} days (Expected 7)")
        assert yellow_days == 7
        
        # Test Case 2: Tomorrow (Saturday)
        # Black should be in 13 days
        # Yellow should be in 6 days
        current_date_sat = datetime(2026, 1, 17, 10, 0, 0)
        
        black_days_sat = get_next_collection_days(current_date_sat, schedule['black'])
        print(f"2026-01-17: Black In {black_days_sat} days (Expected 13)")
        assert black_days_sat == 13
        
        yellow_days_sat = get_next_collection_days(current_date_sat, schedule['yellow'])
        print(f"2026-01-17: Yellow In {yellow_days_sat} days (Expected 6)")
        assert yellow_days_sat == 6
        
        print("SUCCESS: Trash schedule logic verified.")
        
    finally:
        if os.path.exists('test_schedule.yaml'):
            os.remove('test_schedule.yaml')

if __name__ == "__main__":
    test_trash_schedule()
