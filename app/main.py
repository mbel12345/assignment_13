from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.database import get_engine
from app.database.database_init import init_db
from app.models.user import User
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate
from app.schemas.user import UserLogin
from app.schemas.user import UserResponse


@asynccontextmanager
async def lifespan(app: FastAPI):

    print('Creating tables...')
    engine = get_engine()
    init_db(engine=engine)
    print('Tables created successfully')
    yield

app = FastAPI(
    title='JWT Secure App',
    description='App to demonstrate JWT integrated with a Front-End',
    version='1.0.0',
    lifespan=lifespan,
)

# Mount the static files directory
app.mount('/static', StaticFiles(directory='static'), name='static')

# Set up Jinja2 templates directory
templates = Jinja2Templates(directory='templates')

# Home page route
@app.get('/', response_class=HTMLResponse, tags=['web'])
def read_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

# Login page route
@app.get('/login', response_class=HTMLResponse, tags=['web'])
def login_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})

# Registration page route
@app.get('/register', response_class=HTMLResponse, tags=['web'])
def register_page(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})

# Health endpoint
@app.get('/health', tags=['health'])
def read_health():
    return {'status': 'ok'}

# User registration route
@app.post(
    '/auth/register',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=['auth'],
)
def register(user_create: UserCreate, db: Session = Depends(get_db)):

    # Register new user

    print('/auth/register')

    user_data = dict(user_create)
    del(user_data['confirm_password'])
    try:
        user = User.register(db, user_data)
        db.commit()
        db.refresh(user)
        print('Registration succeeded')
        return user
    except ValueError as e:
        print(f'Register failed: {e}')
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# User login route
@app.post('/auth/login', response_model=TokenResponse, tags=['auth'])
def login_json(user_login: UserLogin, db: Session = Depends(get_db)):

    # Login with JSON payload

    print('/auth/login')

    auth_result = User.authenticate(db, user_login.username, user_login.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user = auth_result['user']
    db.commit()

    expires_at = auth_result.get('expires_at')
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    return TokenResponse(
        access_token=auth_result['access_token'],
        refresh_token=auth_result['refresh_token'],
        token_type='bearer',
        expires_at=expires_at,
        user_id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )

@app.post('/auth/token', tags=['auth'])
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # Login with form data for Swagger UI

    print('/auth/token')

    auth_result = User.authenticate(db, form_data.username, form_data.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {
        'access_token': auth_result['access_token'],
        'token_type': 'bearer',
    }

if __name__ == '__main__':

    # Main method should not be included in test cases
    import uvicorn # pragma: no cover
    uvicorn.run('app.main:app', host='127.0.0.1', port=8001, log_level='info') # pragma: no cover
