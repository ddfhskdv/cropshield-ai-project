from fastapi import APIRouter, Depends

from app.core.database import fake_db, sync_fake_db
from app.core.security import get_current_user, require_role

router = APIRouter(prefix='/admin', tags=['Admin'])


@router.get('/dashboard')
def dashboard(user: dict = Depends(require_role('ADMIN'))):
    sync_fake_db()
    total_farmers = len([u for u in fake_db['users'] if u.get('role') == 'FARMER'])
    total_diagnoses = len(fake_db['diagnoses'])
    disease_counts = {}
    crop_counts = {}
    for item in fake_db['diagnoses']:
        disease_counts[item.get('disease_name', 'Unknown')] = disease_counts.get(item.get('disease_name', 'Unknown'), 0) + 1
        crop_counts[item.get('crop_name', 'Unknown')] = crop_counts.get(item.get('crop_name', 'Unknown'), 0) + 1
    return {
        'summary': {
            'total_farmers': total_farmers,
            'total_diagnoses': total_diagnoses,
            'disease_stats': disease_counts,
            'crop_stats': crop_counts,
        },
        'recent_activity': list(reversed(fake_db['diagnoses']))[:5],
        'farmers': [u for u in fake_db['users'] if u.get('role') == 'FARMER'],
        'hotspots': fake_db.get('hotspots', []),
        'expert_queue': fake_db.get('validations', []),
    }


@router.get('/farmers')
def list_farmers(user: dict = Depends(require_role('ADMIN'))):
    sync_fake_db()
    return {'farmers': [u for u in fake_db['users'] if u.get('role') == 'FARMER']}


@router.get('/hotspots')
def list_hotspots(user: dict = Depends(require_role('ADMIN'))):
    sync_fake_db()
    return {'hotspots': fake_db.get('hotspots', [])}


@router.get('/validations')
def list_validations(user: dict = Depends(require_role('ADMIN'))):
    sync_fake_db()
    return {'expert_queue': fake_db.get('validations', [])}


@router.get('/diagnoses')
def list_diagnoses(user: dict = Depends(require_role('ADMIN'))):
    sync_fake_db()
    return {'diagnoses': fake_db['diagnoses']}
