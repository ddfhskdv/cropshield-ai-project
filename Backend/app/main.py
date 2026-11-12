from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import seed_demo_data
from app.api.routes.auth import router as auth_router
from app.api.routes.diagnoses import router as diagnoses_router
from app.api.routes.weather import router as weather_router
from app.api.routes.admin import router as admin_router
from app.api.routes.knowledge import router as knowledge_router

app = FastAPI(
    title=settings.APP_NAME,
    version='1.0.0',
    description='Crop disease detection and advisory platform for farmers and admins.'
)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(',') if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ['http://localhost:5173'],
    allow_origin_regex=r'https?://(localhost|127\.0\.0\.1):\d+',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

for router in [
    auth_router,
    diagnoses_router,
    weather_router,
    admin_router,
    knowledge_router,
]:
    app.include_router(router, prefix=settings.API_V1_STR)

seed_demo_data()

@app.on_event('startup')
def startup_event():
    seed_demo_data()

@app.get('/')
def root():
    return RedirectResponse(url='/docs')

@app.get('/health')
def health():
    return {'status': 'ok', 'app': settings.APP_NAME}
