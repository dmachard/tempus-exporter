import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tempus.seasons import get_season_info, get_days_until_seasons

def test_seasons_north():
    print("Testing Northern Hemisphere Seasons...")
    
    # Spring start
    season, progress, days = get_season_info(datetime(2026, 3, 20), 'north')
    assert season == 'spring'
    assert progress == 0
    assert days == 93 # March 20 to June 21
    
    # Summer start
    season, progress, days = get_season_info(datetime(2026, 6, 21), 'north')
    assert season == 'summer'
    assert progress == 0
    
    # Fall start
    season, progress, days = get_season_info(datetime(2026, 9, 22), 'north')
    assert season == 'fall'
    
    # Winter start
    season, progress, days = get_season_info(datetime(2026, 12, 21), 'north')
    assert season == 'winter'
    
    # Mid-winter (Jan 1)
    season, progress, days = get_season_info(datetime(2026, 1, 1), 'north')
    assert season == 'winter'
    assert 0 < progress < 100
    
    print("SUCCESS: Northern seasons verified.")

def test_seasons_south():
    print("Testing Southern Hemisphere Seasons...")
    
    # Spring start in South (Sep 22)
    season, progress, days = get_season_info(datetime(2026, 9, 22), 'south')
    assert season == 'spring'
    
    # Summer start in South (Dec 21)
    season, progress, days = get_season_info(datetime(2026, 12, 21), 'south')
    assert season == 'summer'
    
    # Winter start in South (Jun 21)
    season, progress, days = get_season_info(datetime(2026, 6, 21), 'south')
    assert season == 'winter'
    
    print("SUCCESS: Southern seasons verified.")

def test_days_until_seasons():
    print("Testing Days Until Seasons...")
    
    today = datetime(2026, 1, 1)
    days = get_days_until_seasons(today)
    
    # Jan 1 to Mar 20 is ~78 days
    assert days['spring'] == 78
    assert days['summer'] > days['spring']
    assert days['fall'] > days['summer']
    assert days['winter'] > days['fall']
    
    # After March 20
    later = datetime(2026, 4, 1)
    days_later = get_days_until_seasons(later)
    assert days_later['spring'] > 300 # Should be next year
    
    print("SUCCESS: Days until seasons verified.")

if __name__ == "__main__":
    test_seasons_north()
    test_seasons_south()
    test_days_until_seasons()
