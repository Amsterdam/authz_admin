import json
import pytest
import re

from authz_admin.main import build_application
from .helpers import follow_path
from .test_fixtures import access_token


@pytest.fixture
def client(loop, test_client):
    """An aiohttp test_client initialized for our app."""
    return loop.run_until_complete(test_client(build_application()))


@pytest.fixture(scope="session")
def base_path():
    app = build_application()
    swagger = follow_path(app, 'swagger')
    return swagger.base_path


async def test_get_base_path(client, base_path, access_token):
    authz_headers = {'Authorization', 'Bearer ' + access_token}
    resp = await client.head(base_path + '/', headers=authz_headers)
    assert resp.status == 200
    resp = await client.get(base_path + '/', headers=authz_headers)
    assert resp.status == 200
    body = json.loads(await resp.text())
    for child_resource_name in ('accounts', 'datasets', 'profiles', 'roles'):
        assert body['_links'][child_resource_name]['href'] == base_path + '/' + child_resource_name
    resp = await client.get(
        base_path + '/?embed=accounts(item),datasets(item),profiles(item),roles(item)',
        headers=authz_headers
    )
    assert resp.status == 200
    body = json.loads(await resp.text())
    for child_resource_name in ('accounts', 'datasets', 'profiles', 'roles'):
        items = follow_path(body, '_embedded', child_resource_name, '_embedded', 'item')
        assert len(items) > 0




async def test_accounts(client, base_path):
    resp = await client.get(base_path + '/accounts?roles=DPB')
    assert resp.status == 200
    body = json.loads(await resp.text())
    items = follow_path(body, '_links', 'item')
    assert len(items) > 0
    account_url = follow_path(items[0], 'href')
    resp = await client.get(account_url + '?roles=DPB&embed=role(profile(scope))')
    assert resp.status == 200
    body = json.loads(await resp.text())
    roles = follow_path(body, '_embedded', 'role')
    assert len(roles) > 0
    profiles = follow_path(roles[0], '_embedded', 'profile')
    assert len(profiles) > 0
    scopes = follow_path(profiles[0], '_embedded', 'scope')
    assert len(scopes) > 0
    follow_path(scopes[0], '_links', 'self', 'name')


async def test_scopes(client, base_path):
    resp = await client.get(base_path + '/datasets?embed=item(item)')
    assert resp.status == 200
    body = json.loads(await resp.text())
    etag = follow_path(resp.headers, 'ETag')
    resp = await client.get(
        base_path + '/datasets?embed=item(item)',
        headers={'If-None-Match': etag}
    )
    assert resp.status == 304
    datasets = follow_path(body, '_embedded', 'item')
    assert len(datasets) > 0
    scopes = follow_path(datasets[0], '_embedded', 'item')
    assert len(scopes) > 0

    resp = await client.get(base_path + '/datasets/AUR/W?embed=profile(role(account))')
    assert resp.status == 200
    body = json.loads(await resp.text())
    print(body)
    profiles = follow_path(body, '_embedded', 'profile')
    assert len(profiles) > 0
    roles = follow_path(profiles[0], '_embedded', 'role')
    assert len(roles) > 0
    accounts = follow_path(roles[0], '_embedded', 'account')
    assert len(accounts) > 0


async def test_account_methods(client, base_path):
    url = base_path + '/accounts/pytest_test_account@amsterdam.nl'
    data = {
        '_links': {
            'role': [
                {'href': '/roles/CDE'},
                {'href': '/roles/CDE_PLUS'}
            ]
        }
    }
    resp = await client.get(url)
    if resp.status == 200:
        etag = follow_path(resp.headers, 'ETag')
        resp = await client.delete(url, headers={
            'If-Match': etag
        })
        assert resp.status == 204
    else:
        assert resp.status == 404
    resp = await client.put(url, json=data)
    assert resp.status == 428
    resp = await client.put(url, json=data, headers={
        'If-Match': '"foobar"'
    })
    assert resp.status == 404
    resp = await client.put(url, json=data, headers={
        'If-None-Match': '*'
    })
    assert resp.status == 201
    location = follow_path(resp.headers, 'Location')
    assert location == url
    etag = follow_path(resp.headers, 'ETag')
    resp = await client.get(url)
    body = json.loads(await resp.text())
    roles = follow_path(body, '_links', 'role')
    assert len(roles) == 2
    assert etag == follow_path(resp.headers, 'ETag')
    data = {
        '_links': {
            'role': [
                {'href': '/roles/CDE'}
            ]
        }
    }
    resp = await client.put(url, json=data, headers={
        'If-Match': etag
    })
    assert resp.status == 204
    new_etag = follow_path(resp.headers, 'ETag')
    assert new_etag != etag
    resp = await client.delete(url, headers={
        'If-Match': etag
    })
    assert resp.status == 412
    resp = await client.delete(url, headers={
        'If-Match': new_etag
    })
    assert resp.status == 204


async def test_maximum_query_depth(client, base_path):
    url = base_path + '/?embed=datasets(item(item(profile(role))))'
    resp = await client.get(url)
    assert resp.status == 200

    url = base_path + '/?embed=datasets(item(item(profile(role(account)))))'
    resp = await client.get(url)
    assert resp.status == 400
    text = await client.text()
    assert re.search('query depth', text) is not None
