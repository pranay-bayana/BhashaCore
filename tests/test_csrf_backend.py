import re

from src.app import app, limiter
from src.auth import db


def _csrf_token(response):
    match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.get_data(as_text=True))
    assert match
    return match.group(1)


def test_rendered_csrf_token_protects_signup_and_authenticated_chat():
    old = {key: app.config.get(key) for key in ('TESTING', 'WTF_CSRF_ENABLED', 'ALLOW_ANONYMOUS_CHAT')}
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=True, ALLOW_ANONYMOUS_CHAT=False)
    try:
        with app.app_context():
            limiter.reset()
            db.drop_all(); db.create_all()
        with app.test_client() as client:
            signup = client.get('/signup')
            token = _csrf_token(signup)
            registered = client.post('/signup', data={
                'name': 'CSRF User', 'email': 'csrf-flow@example.test',
                'password': 'long-secret-passphrase', 'confirm_password': 'long-secret-passphrase',
                'consent': 'on', 'csrf_token': token,
            })
            assert registered.status_code == 302
            chat = client.get('/chat')
            chat_token = _csrf_token(chat)
            assert client.post('/api/new-chat', json={'session_id': 'csrf-flow'}).status_code == 400
            assert client.post('/api/new-chat', json={'session_id': 'csrf-flow'},
                               headers={'X-CSRFToken': chat_token}).status_code == 200
    finally:
        app.config.update(old)


def test_authenticated_mutations_accept_current_rendered_token():
    old = {key: app.config.get(key) for key in ('TESTING', 'WTF_CSRF_ENABLED', 'ALLOW_ANONYMOUS_CHAT')}
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=True, ALLOW_ANONYMOUS_CHAT=False)
    try:
        with app.app_context():
            limiter.reset()
            db.drop_all(); db.create_all()
        with app.test_client() as client:
            token = _csrf_token(client.get('/signup'))
            assert client.post('/signup', data={
                'name': 'CSRF Owner', 'email': 'csrf-owner@example.test',
                'password': 'long-secret-passphrase', 'confirm_password': 'long-secret-passphrase',
                'consent': 'on', 'csrf_token': token,
            }).status_code == 302
            token = _csrf_token(client.get('/chat'))
            headers = {'X-CSRFToken': token}
            assert client.post('/api/new-chat', json={'session_id': 'csrf-mutation'}, headers=headers).status_code == 200
            assert client.patch('/api/conversations/csrf-mutation', json={'title': 'Renamed'}, headers=headers).status_code == 200
            assert client.delete('/api/conversations/csrf-mutation', headers=headers).status_code == 200
            assert client.post('/settings/delete-account', data={
                'password': 'long-secret-passphrase', 'csrf_token': token,
            }).status_code == 302
    finally:
        app.config.update(old)
