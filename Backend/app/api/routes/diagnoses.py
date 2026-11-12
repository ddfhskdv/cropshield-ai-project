from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.database import add_diagnosis, fake_db, sync_fake_db
from app.core.security import get_current_user, require_role
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix='/diagnoses', tags=['Diagnoses'])


@router.post('/detect')
async def detect_disease(
    crop_name: str = Form(...),
    location: str = Form(''),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    from app.services.model_service import DiseaseModelService

    content = await file.read()
    service = DiseaseModelService()
    try:
        service.validate_image(content, file.filename or 'image.jpg')
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    prediction = service.predict(content, crop_name)
    if prediction.get('prediction_status') == 'predicted':
        advice = RecommendationService().get_recommendations(
            prediction.get('label', ''),
            crop_name,
        )
        prediction.update({
            'symptoms': advice['symptoms'],
            'causes': advice['causes'],
            'recommendations': advice['recommendations'],
            'action_plan': advice['action_plan'],
            'safety_note': advice['safety_note'],
            'follow_up': advice['follow_up'],
        })

    diagnosis = {
        'id': f'dx-{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}-{len(fake_db["diagnoses"]) + 1}',
        'farmer_id': user['id'],
        'farmer_name': user['name'],
        'crop_name': crop_name,
        'disease_name': prediction.get('label', 'Unavailable'),
        'confidence': prediction.get('confidence', 0.0),
        'result_status': prediction.get('prediction_status', 'model_unavailable'),
        'location': location,
        'date': datetime.now(timezone.utc),
        'symptoms': prediction.get('symptoms', []),
        'causes': prediction.get('causes', []),
        'recommendations': prediction.get('recommendations', []),
        'model_message': prediction.get('message', 'No model result'),
    }
    add_diagnosis(diagnosis)
    sync_fake_db()
    return {'diagnosis': {**diagnosis, 'date': diagnosis['date'].isoformat()}, 'prediction': prediction}


@router.post('/pest-detect')
async def detect_pest(
    crop_name: str = Form(...),
    location: str = Form(''),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    from app.services.model_service import DiseaseModelService

    content = await file.read()
    service = DiseaseModelService()
    try:
        service.validate_image(content, file.filename or 'pest.jpg')
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    prediction = {
        'prediction_status': 'model_unavailable',
        'label': 'Pest scan unavailable',
        'confidence': 0.0,
        'message': 'Pest detection model is not configured in this deployment. Field scouting remains recommended.',
        'crop': crop_name,
        'symptoms': ['Look for chewing holes, webbing, pests beneath leaves, and sudden wilting.', 'Inspect stress points across the field edge and mid-canopy.'],
        'causes': ['Late-season moisture and dense crop cover favor pest pressure.', 'Movement of infestation from adjacent plots.'],
        'recommendations': ['Scout the field weekly and inspect leaf undersides.', 'Use targeted agronomic controls only after expert verification.', 'Prioritize likely hotspots near field edges and dense canopy areas.'],
    }

    diagnosis = {
        'id': f'pest-{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}-{len(fake_db["diagnoses"]) + 1}',
        'farmer_id': user['id'],
        'farmer_name': user['name'],
        'crop_name': crop_name,
        'disease_name': 'Pest pressure',
        'confidence': 0.0,
        'result_status': 'model_unavailable',
        'location': location,
        'date': datetime.now(timezone.utc),
        'symptoms': prediction['symptoms'],
        'causes': prediction['causes'],
        'recommendations': prediction['recommendations'],
        'model_message': prediction['message'],
    }
    add_diagnosis(diagnosis)
    sync_fake_db()
    return {'diagnosis': {**diagnosis, 'date': diagnosis['date'].isoformat()}, 'prediction': prediction}


@router.get('/history')
def diagnosis_history(user: dict = Depends(get_current_user)):
    sync_fake_db()
    diagnoses = [item for item in fake_db['diagnoses'] if item['farmer_id'] == user['id']]
    return {'diagnoses': diagnoses}


@router.get('/all')
def all_diagnoses(user: dict = Depends(require_role('ADMIN'))):
    sync_fake_db()
    return {'diagnoses': fake_db['diagnoses']}
