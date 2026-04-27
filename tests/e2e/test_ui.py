import time

from playwright.sync_api import expect
from uuid import uuid4

BASE_PAGE=  'http://localhost:8002'

def create_unique_user():

    unique_id = uuid4()
    return {
        'first_name': 'John',
        'last_name': 'Smith',
        'email': f'jsmith{unique_id}@example.com',
        'username': f'smith{unique_id}',
        'password': 'SecurePass123!',
    }

def test_ui_register(page, fastapi_server):

    user = create_unique_user()

    page.goto(f'{BASE_PAGE}/register')

    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#first_name', user['first_name'])
    page.fill('#last_name', user['last_name'])
    page.fill('#password', user['password'])
    page.fill('#confirm_password', user['password'])

    page.click('button:text("Register")')
    page.wait_for_timeout(500)

    assert page.inner_text('#errorMessage') == ''
    assert page.inner_text('#successMessage') == 'Registration successful! Redirecting to login...'

    # Redirect back to login
    time.sleep(3)
    expect(page).to_have_url(f'{BASE_PAGE}/login')
