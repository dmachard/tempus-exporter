# tempus-exporter

**Temporal, solar and calendar context exporter for Prometheus**

Export meaningful time context metrics to understand your monitoring data in relation to natural cycles, seasons, holidays, and custom events.

## Features

- ☀️ **Solar metrics**: Sunrise, sunset, day length
- 🍂 **Seasonal context**: Current season, seasonal progression, solstice countdowns
- 📅 **Calendar awareness**: Weekends, holidays, working days
- 🚮 **Custom scrapers**: Trash collection, local events
- 📊 **Prometheus format**: Ready for Grafana dashboards

## Quick Start

### Docker (recommended)

```bash
docker run -d \
  --name tempus \
  -p 8000:8000 \
  -e LATITUDE=49.2297 \
  -e LONGITUDE=-0.4458 \
  -e TIMEZONE=Europe/Paris \
  dmachard/tempus:latest
```

### Python

```bash
git clone https://github.com/dmachard/tempus-exporter.git
cd tempus
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp example.env .env
python -m tempus
```

## Docker build

Build docker image

```bash
sudo docker build . --file Dockerfile -t tempos-exporter
```

## 📦 Exposed Metrics

### Solar Metrics
```
sun_sunrise_minutes           # Minutes since midnight for sunrise
sun_sunset_minutes            # Minutes since midnight for sunset
sun_day_length_minutes        # Total daylight in minutes
sun_day_gain_minutes          # Daily change in daylight
sun_is_growing_day            # 1 if days are getting longer
```

### Seasonal Metrics
```
season_id{season="winter"}    # Current season indicator
season_progress_percent       # Progress through current season
days_until_spring             # Days until spring
days_until_summer             # Days until summer
days_until_fall               # Days until fall
days_until_winter             # Days until winter
```

### Calendar Metrics
```
is_public_holiday             # 1 on public holidays
is_school_holiday             # 1 during school breaks
is_weekend                    # 1 on Saturday/Sunday
is_working_day                # 1 on working days
```

### Moon Metrics
```
moon_phase_day                # Current day of lunar cycle (0-28)
moon_phase_info{phase=""}     # Current phase description (e.g. "Full Moon")
```

### Trash Metrics
```
trash_collection_today{type="black"} # 1 if collection is today
trash_next_days{type="black"}        # Days until next collection
```

### Birthday Metrics
```
birthday_this_month{name="Alice", day="15"} # 1 if birthday is this month
birthday_days_until{name="Alice"}           # Days until next birthday
birthday_today{name="Alice"}                # 1 if birthday is today
```

## ⚙️ Configuration

### Schedule
You can configure trash collection and birthdays in `schedule.yaml`:

```yaml
trash:
  black:
    frequency: biweekly
    day: Friday
    reference_date: 2026-01-16
  yellow:
    frequency: weekly
    day: Tuesday

birthdays:
  - name: "Alice"
    date: "01-15"
  - name: "Bob"
    date: "01-18"
```

