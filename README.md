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
days_until_season_change      # Days until season change
```

### Calendar Metrics
```
is_public_holiday             # 1 on public holidays
is_school_holiday             # 1 during school breaks
is_weekend                    # 1 on Saturday/Sunday
is_working_day                # 1 on working days
```
