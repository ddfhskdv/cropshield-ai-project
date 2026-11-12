from fastapi import APIRouter, Depends

from app.core.database import fake_db
from app.core.security import get_current_user, require_role
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix='/knowledge', tags=['Knowledge'])
service = RecommendationService()


@router.get('/records')
def knowledge_records(user: dict = Depends(get_current_user)):
    return {'records': fake_db['knowledge']}


@router.get('/recommendation')
def recommendation(disease_name: str, crop_name: str = '', user: dict = Depends(get_current_user)):
    return service.get_recommendations(disease_name, crop_name)
