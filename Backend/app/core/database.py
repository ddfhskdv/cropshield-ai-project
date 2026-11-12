import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

TESTING = 'pytest' in sys.modules or os.getenv('PYTEST_CURRENT_TEST') is not None or os.getenv('CROPSHIELD_TEST_MODE') == '1'
DATABASE_URL = os.getenv('DATABASE_URL') or ('sqlite:///:memory:' if TESTING else 'sqlite:///./cropshield.db')
engine_kwargs = {'connect_args': {'check_same_thread': False}} if DATABASE_URL.startswith('sqlite') else {}
if TESTING and DATABASE_URL.startswith('sqlite:///:memory:'):
    engine_kwargs['poolclass'] = StaticPool
engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class UserORM(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default='FARMER')
    location = Column(String, default='')
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DiagnosisORM(Base):
    __tablename__ = 'diagnoses'

    id = Column(String, primary_key=True, index=True)
    farmer_id = Column(String, nullable=False)
    farmer_name = Column(String, nullable=False)
    crop_name = Column(String, nullable=False)
    disease_name = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    result_status = Column(String, default='model_unavailable')
    location = Column(String, default='')
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    symptoms = Column(JSON, default=list)
    causes = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    model_message = Column(String, default='')


class KnowledgeRecordORM(Base):
    __tablename__ = 'knowledge_records'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disease = Column(String, nullable=False)
    crop = Column(String, nullable=False)
    symptoms = Column(JSON, default=list)
    causes = Column(JSON, default=list)
    prevention = Column(JSON, default=list)
    management = Column(JSON, default=list)
    next_steps = Column(JSON, default=list)


class HotspotORM(Base):
    __tablename__ = 'hotspots'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    region = Column(String, nullable=False)
    disease = Column(String, nullable=False)
    risk_score = Column(Integer, default=0)
    trend = Column(String, default='Watchlist')
    affected_fields = Column(Integer, default=0)
    note = Column(String, default='')


class ValidationORM(Base):
    __tablename__ = 'validations'

    id = Column(String, primary_key=True, index=True)
    farmer_name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    disease_name = Column(String, nullable=False)
    priority = Column(String, default='Medium')
    status = Column(String, default='Pending review')
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)

fake_db: Dict[str, List[Dict[str, Any]]] = {
    'users': [],
    'diagnoses': [],
    'knowledge': [],
    'validations': [],
    'hotspots': [],
}


def sync_fake_db() -> Dict[str, List[Dict[str, Any]]]:
    db = SessionLocal()
    try:
        fake_db['users'] = [
            {
                'id': item.id,
                'name': item.name,
                'email': item.email,
                'password': item.password,
                'role': item.role,
                'location': item.location,
                'created_at': item.created_at.isoformat() if item.created_at else None,
            }
            for item in db.query(UserORM).order_by(UserORM.created_at.asc()).all()
        ]
        fake_db['diagnoses'] = [
            {
                'id': item.id,
                'farmer_id': item.farmer_id,
                'farmer_name': item.farmer_name,
                'crop_name': item.crop_name,
                'disease_name': item.disease_name,
                'confidence': item.confidence,
                'result_status': item.result_status,
                'location': item.location,
                'date': item.date.isoformat() if item.date else None,
                'symptoms': item.symptoms or [],
                'causes': item.causes or [],
                'recommendations': item.recommendations or [],
                'model_message': item.model_message,
            }
            for item in db.query(DiagnosisORM).order_by(DiagnosisORM.date.asc()).all()
        ]
        fake_db['knowledge'] = [
            {
                'id': item.id,
                'disease': item.disease,
                'crop': item.crop,
                'symptoms': item.symptoms or [],
                'causes': item.causes or [],
                'prevention': item.prevention or [],
                'management': item.management or [],
                'next_steps': item.next_steps or [],
            }
            for item in db.query(KnowledgeRecordORM).all()
        ]
        fake_db['hotspots'] = [
            {
                'id': item.id,
                'region': item.region,
                'disease': item.disease,
                'risk_score': item.risk_score,
                'trend': item.trend,
                'affected_fields': item.affected_fields,
                'note': item.note,
            }
            for item in db.query(HotspotORM).all()
        ]
        fake_db['validations'] = [
            {
                'id': item.id,
                'farmer_name': item.farmer_name,
                'region': item.region,
                'disease_name': item.disease_name,
                'priority': item.priority,
                'status': item.status,
                'submitted_at': item.submitted_at.isoformat() if item.submitted_at else None,
            }
            for item in db.query(ValidationORM).all()
        ]
        return fake_db
    finally:
        db.close()


def get_user_by_id(user_id: str):
    db = SessionLocal()
    try:
        return db.query(UserORM).filter(UserORM.id == user_id).first()
    finally:
        db.close()


def get_user_by_email(email: str):
    db = SessionLocal()
    try:
        return db.query(UserORM).filter(UserORM.email.ilike(email)).first()
    finally:
        db.close()


def add_user(user_data: Dict[str, Any]):
    db = SessionLocal()
    try:
        user = UserORM(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def add_diagnosis(diagnosis_data: Dict[str, Any]):
    db = SessionLocal()
    try:
        item = DiagnosisORM(**diagnosis_data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()


def seed_demo_data():
    db = SessionLocal()
    try:
        if db.query(UserORM).count() == 0:
            from app.core.security import hash_password

            db.add_all([
                UserORM(
                    id='admin-1',
                    name='CropShield Admin',
                    email='admin@cropshield.ai',
                    password=hash_password('admin123'),
                    role='ADMIN',
                    location='New Delhi, India',
                    created_at=datetime.now(timezone.utc),
                ),
                UserORM(
                    id='farmer-1',
                    name='Demo Farmer',
                    email='farmer@demo.com',
                    password=hash_password('password123'),
                    role='FARMER',
                    location='Patna, Bihar',
                    created_at=datetime.now(timezone.utc),
                ),
            ])
        if db.query(KnowledgeRecordORM).count() == 0:
            db.add_all([
                KnowledgeRecordORM(
                    disease='Leaf Spot',
                    crop='Tomato',
                    symptoms=['Small circular spots on leaves', 'Yellow halos around lesions'],
                    causes=['High humidity', 'Water splashing between plants'],
                    prevention=['Remove infected leaves', 'Use resistant varieties', 'Avoid overhead irrigation'],
                    management=['Apply copper-based fungicide only if needed', 'Practice crop rotation'],
                    next_steps=['Inspect the lower canopy first', 'Monitor daily for spread'],
                ),
                KnowledgeRecordORM(
                    disease='Early Blight',
                    crop='Potato',
                    symptoms=['Dark concentric lesions', 'Leaf yellowing'],
                    causes=['Warm wet weather', 'Leaf-to-leaf spread'],
                    prevention=['Mulch to reduce soil splash', 'Maintain spacing'],
                    management=['Remove infected debris', 'Fungicide sprays under advisement'],
                    next_steps=['Assess severity and prune lower affected leaves'],
                ),
                KnowledgeRecordORM(
                    disease='Rust',
                    crop='Wheat',
                    symptoms=['Orange pustules on leaves', 'Reduced vigor'],
                    causes=['Cool nights', 'Moisture'],
                    prevention=['Use resistant seed', 'Timed sowing'],
                    management=['Avoid dense canopy', 'Apply registered fungicides only when recommended'],
                    next_steps=['Check nearby fields for spread'],
                ),
            ])
        if db.query(HotspotORM).count() == 0:
            db.add_all([
                HotspotORM(
                    region='Patna, Bihar',
                    disease='Leaf Spot',
                    risk_score=82,
                    trend='Rising',
                    affected_fields=14,
                    note='High humidity and evening fog are increasing spore pressure in low-lying plots.',
                ),
                HotspotORM(
                    region='Muzaffarpur, Bihar',
                    disease='Rust',
                    risk_score=71,
                    trend='Stable',
                    affected_fields=9,
                    note='Early season infection remains moderate; target the upper canopy in susceptible blocks.',
                ),
                HotspotORM(
                    region='Gaya, Bihar',
                    disease='Early Blight',
                    risk_score=68,
                    trend='Watchlist',
                    affected_fields=6,
                    note='Moisture retention after irrigation has elevated disease pressure during the last week.',
                ),
            ])
        if db.query(ValidationORM).count() == 0:
            db.add_all([
                ValidationORM(
                    id='val-101',
                    farmer_name='Demo Farmer',
                    region='Patna, Bihar',
                    disease_name='Leaf Spot',
                    priority='High',
                    status='Pending expert review',
                    submitted_at=datetime.now(timezone.utc),
                ),
                ValidationORM(
                    id='val-102',
                    farmer_name='Rakesh Kumar',
                    region='Muzaffarpur, Bihar',
                    disease_name='Rust',
                    priority='Medium',
                    status='Awaiting field confirm',
                    submitted_at=datetime.now(timezone.utc),
                ),
            ])
        db.commit()
    finally:
        db.close()

    sync_fake_db()
    return fake_db
