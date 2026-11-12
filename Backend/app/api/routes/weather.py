from fastapi import APIRouter, Depends, Query

from app.core.database import fake_db
from app.core.security import get_current_user
from app.services.weather_service import WeatherService

router = APIRouter(prefix='/weather', tags=['Weather'])
service = WeatherService()


@router.get('/current')
def current_weather(
    latitude: float = Query(25.61),
    longitude: float = Query(85.13),
    user: dict = Depends(get_current_user),
):
    return service.get_forecast(latitude, longitude)
