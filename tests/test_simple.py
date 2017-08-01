# -*- coding: utf-8 -*-
# Relative import flasksqla_apicrud
import sys;sys.path.append('..')
from flasksqla_apicrud import APIManager
import json

def test_db(Film):
    assert Film.query.count() == 1
    film = Film.query.first()
    assert film.name == 'Star Wars'
    assert film.id == 1


def test_clinet_get(app, client, api):
    resp = client.open('/films/', method='GET')
    assert resp.status_code == 200
    obj = json.loads(resp.data)
    assert len(obj) == 1
    assert obj[0]['name'] == 'Star Wars'


def test_client_get_item(app, client, api):
    resp = client.open('/films/1', method='GET')
    assert resp.status_code == 200
    obj = json.loads(resp.data)
    assert obj['name'] == 'Star Wars'


def test_client_update_item(app, client, api):
    resp = client.put('/films/1',
        data=json.dumps(dict(name='Star Wars: Episode I - The Phantom Menace')),
        headers={'Content-Type': 'application/json'})
    assert resp.status_code == 200
    obj = json.loads(resp.data)
    assert obj['name'] == 'Star Wars: Episode I - The Phantom Menace'


def test_client_delete_item(app, client, api):
    resp = client.delete('/films/1')
    assert resp.status_code == 200
    obj = json.loads(resp.data)
    assert obj['success'] == True
