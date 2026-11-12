from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.database import add_user, fake_db, get_user_by_email, sync_fake_db
from app.core.security import get_current_user

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/register')
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    location: str = Form(''),
):
    sync_fake_db()
    if any(item['email'].lower() == email.lower() for item in fake_db['users']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    from app.core.security import hash_password
    from uuid import uuid4

    user = {
        'id': str(uuid4()),
        'name': name,
        'email': email,
        'password': hash_password(password),
        'role': 'FARMER',
        'location': location,
    }
    add_user(user)
    sync_fake_db()
    return {'message': 'Farmer registered successfully', 'user': {'id': user['id'], 'name': user['name'], 'email': user['email'], 'role': user['role']}}


@router.post('/login')
def login(email: str = Form(...), password: str = Form(...)):
    sync_fake_db()
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    from app.core.security import verify_password, create_access_token
    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return {
        'access_token': create_access_token(user.id),
        'token_type': 'bearer',
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role},
    }


@router.get('/me')
def me(user: dict = Depends(get_current_user)):
    return {'user': {'id': user['id'], 'name': user['name'], 'email': user['email'], 'role': user['role'], 'location': user.get('location', '')}}
