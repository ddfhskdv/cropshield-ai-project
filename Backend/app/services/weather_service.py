from typing import Any, Dict

import httpx

from app.core.config import settings


class WeatherService:
    def __init__(self):
        self.base_url = settings.WEATHER_API_BASE

    def get_forecast(self, latitude: float, longitude: float, days: int = 3) -> Dict[str, Any]:
        try:
            resp = httpx.get(
                self.base_url,
                params={
                    'latitude': latitude,
                    'longitude': longitude,
                    'current': 'temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m',
                    'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
                    'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                    'forecast_days': days,
                    'timezone': 'auto',
                },
                timeout=15,
            )
            resp.raise_for_status()
            payload = resp.json()
            current = payload.get('current', {})
            daily = payload.get('daily', {})
            return {
                'source': 'open-meteo',
                'latitude': latitude,
                'longitude': longitude,
                'temperature': current.get('temperature_2m'),
                'humidity': current.get('relative_humidity_2m'),
                'rainfall': current.get('precipitation', current.get('rain', 0)),
                'wind_speed': current.get('wind_speed_10m'),
                'forecast': {
                    'highs': daily.get('temperature_2m_max', []),
                    'lows': daily.get('temperature_2m_min', []),
                    'rainfall': daily.get('precipitation_sum', []),
                },
                'risk': self._risk_from_weather(current),
            }
        except Exception:
            return {
                'source': 'fallback',
                'latitude': latitude,
                'longitude': longitude,
                'temperature': 28,
                'humidity': 70,
                'rainfall': 8,
                'wind_speed': 10,
                'forecast': {'highs': [31, 29, 30], 'lows': [23, 22, 24], 'rainfall': [6, 9, 4]},
                'risk': {'category': 'Moderate', 'score': 58, 'explanation': 'Weather conditions are moderately favorable for foliar disease pressure.', 'suggestions': ['Monitor leaf moisture', 'Avoid over-irrigation', 'Promote canopy airflow']},
            }

    @staticmethod
    def _risk_from_weather(current):
        humidity = current.get('relative_humidity_2m', 50)
        temp = current.get('temperature_2m', 25)
        rain = current.get('precipitation', 0)
        score = min(100, max(0, (humidity * 0.5) + (rain * 2.5) + (max(0, 30 - temp) * 1.2)))
        if score >= 70:
            category = 'High'
            suggestions = ['Reduce leaf wetness', 'Check affected plants', 'Avoid nighttime irrigation']
            explanation = 'High humidity and moisture increase disease pressure for many foliar diseases.'
        elif score >= 45:
            category = 'Moderate'
            suggestions = ['Monitor canopy moisture', 'Improve spacing', 'Check for early symptoms']
            explanation = 'Conditions are suitable for moderate disease risk when combined with susceptible crops.'
        else:
            category = 'Low'
            suggestions = ['Continue routine inspections', 'Maintain crop hygiene']
            explanation = 'Conditions presently favor lower disease pressure.'
        return {'category': category, 'score': round(score, 1), 'explanation': explanation, 'suggestions': suggestions}
