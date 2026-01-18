import sys
import os
import yaml
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock config before importing birthdays
with patch('tempus.config.config') as mock_config:
    mock_config.schedule_file = "test_birthdays_schedule.yaml"
    from tempus.birthdays import get_days_until_birthday, load_birthdays, update_birthday_metrics

def test_birthday_logic():
    print("Testing Birthday Logic...")
    
    # 1. Setup test schedule
    test_schedule = {
        'birthdays': [
            {'name': 'Alice', 'date': '01-15'},
            {'name': 'Bob', 'date': '01-18'},
            {'name': 'Charlie', 'date': '03-10'}
        ]
    }
    
    with open('test_birthdays_schedule.yaml', 'w') as f:
        yaml.dump(test_schedule, f)
        
    try:
        # Today is Jan 18
        current_date = datetime(2026, 1, 18, 12, 0, 0)
        
        # Bob is today
        bob_days = get_days_until_birthday(current_date, '01-18')
        print(f"Bob (01-18): {bob_days} days (Expected 0)")
        assert bob_days == 0
        
        # Alice was Jan 15 (passed, so next year)
        alice_days = get_days_until_birthday(current_date, '01-15')
        print(f"Alice (01-15): {alice_days} days (Expected ~362)")
        assert alice_days > 360
        
        # Charlie is March 10
        # Jan 18 to Mar 10: 13 (jan) + 28 (feb) + 10 (mar) = 51 days
        charlie_days = get_days_until_birthday(current_date, '03-10')
        print(f"Charlie (03-10): {charlie_days} days (Expected 51)")
        assert charlie_days == 51
        
        # Test loading
        loaded = load_birthdays()
        assert len(loaded) == 3
        assert loaded[0]['name'] == 'Alice'
        
        print("SUCCESS: Birthday logic verified.")
        
    finally:
        if os.path.exists('test_birthdays_schedule.yaml'):
            os.remove('test_birthdays_schedule.yaml')

if __name__ == "__main__":
    test_birthday_logic()
