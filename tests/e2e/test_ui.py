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

    with page.expect_response('**/register') as response:
        page.click('button:text("Register")')

    assert response.value.status == 201

    page.wait_for_timeout(500)
    assert page.inner_text('#errorMessage') == ''
    assert page.inner_text('#successMessage') == 'Registration successful! Redirecting to login...'

    # Redirect back to login
    time.sleep(3)
    expect(page).to_have_url(f'{BASE_PAGE}/login')

def test_ui_login(page, fastapi_server):

    user = create_unique_user()

    # Register new user

    page.goto(f'{BASE_PAGE}/register')

    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#first_name', user['first_name'])
    page.fill('#last_name', user['last_name'])
    page.fill('#password', user['password'])
    page.fill('#confirm_password', user['password'])

    with page.expect_response('**/register') as response:
        page.click('button:text("Register")')

    assert response.value.status == 201

    page.wait_for_timeout(500)
    assert page.inner_text('#errorMessage') == ''
    assert page.inner_text('#successMessage') == 'Registration successful! Redirecting to login...'

    # Redirect back to login

    time.sleep(3)
    expect(page).to_have_url(f'{BASE_PAGE}/login')

    # Do login

    page.fill('#username', user['username'])
    page.fill('#password', user['password'])

    with page.expect_response('**/login') as response:
        page.click('button:text("Sign in")')

    assert response.value.status == 200

    page.wait_for_timeout(500)
    assert page.inner_text('#errorMessage') == ''
    assert page.inner_text('#successMessage') == 'Login successful! Redirecting...'

    # Redirect to Dashboard

    time.sleep(3)
    expect(page).to_have_url(f'{BASE_PAGE}/dashboard')

def test_ui_register_short_password(page, fastapi_server):

    user = create_unique_user()

    page.goto(f'{BASE_PAGE}/register')

    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#first_name', user['first_name'])
    page.fill('#last_name', user['last_name'])
    page.fill('#password', 'short')
    page.fill('#confirm_password', 'short')

    page.click('button:text("Register")')

    page.wait_for_timeout(500)
    assert page.inner_text('#successMessage') == ''
    assert page.inner_text('#errorMessage') == 'Password must be at least 8 characters long and contain uppercase, lowercase, and numbers'

def test_ui_login_wrong_password(page, fastapi_server):

    user = create_unique_user()

    # Register new user

    page.goto(f'{BASE_PAGE}/register')

    page.fill('#username', user['username'])
    page.fill('#email', user['email'])
    page.fill('#first_name', user['first_name'])
    page.fill('#last_name', user['last_name'])
    page.fill('#password', user['password'])
    page.fill('#confirm_password', user['password'])

    with page.expect_response('**/register') as response:
        page.click('button:text("Register")')

    assert response.value.status == 201

    page.wait_for_timeout(500)
    assert page.inner_text('#errorMessage') == ''
    assert page.inner_text('#successMessage') == 'Registration successful! Redirecting to login...'

    # Redirect back to login

    time.sleep(3)
    expect(page).to_have_url(f'{BASE_PAGE}/login')

    # Do login with wrong password

    page.fill('#username', user['username'])
    page.fill('#password', user['password'] + 'wrong')

    with page.expect_response('**/login') as response:
        page.click('button:text("Sign in")')

    assert response.value.status == 401

    page.wait_for_timeout(500)
    assert page.inner_text('#successMessage') == ''
    assert page.inner_text('#errorMessage') == 'Invalid username or password'
