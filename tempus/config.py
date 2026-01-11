"""
Configuration management
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration"""
    
    latitude: float = float(os.getenv("LATITUDE", "49.2297"))
    longitude: float = float(os.getenv("LONGITUDE", "-0.4458"))
    timezone: str = os.getenv("TIMEZONE", "Europe/Paris")
    port: int = int(os.getenv("PORT", "8000"))
    api_port: int = int(os.getenv("API_PORT", "8001"))
    country_code: str = os.getenv("COUNTRY_CODE", "FR")
    hemisphere: str = os.getenv("HEMISPHERE", "north").lower()  # 'north' or 'south'


config = Config()