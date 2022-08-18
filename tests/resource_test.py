# Code edited from
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/testing-flask-applications-part-2/ # noqa

import json
import os
import pytest
import tempfile
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event

from mokkigo import create_app, db
from mokkigo.models import Visit, Mokki, Item, Participant

from tests.utils import (get_mokki, get_item, get_participant, get_visit)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)


def _populate_db():
    ps = []
    items = []
    ms = []
    vs = []
    for i in range(4):
        ps.append(Participant(name="participant-{}".format(i+1),
                              allergies="food-{}".format(i+1)))

        items.append(Item(name="item-{}".format(i+1),
                          amount="{}".format(i+1)))

        ms.append(Mokki(name="mokki-{}".format(i+1),
                        location="location-{}".format(i+1)))

        db.session.add(ps[i])
        db.session.add(items[i])
        db.session.add(ms[i])
        db.session.commit()

    for i in range(4):
        visit_parts = []
        visit_parts.append(ps[i])
        visit_parts.append(ps[i-1])
        vs.append(Visit(visit_name="visit-{}".format(i+1),
                        mokki_name=ms[i].name,
                        time_start=datetime.now(),
                        time_end=datetime.now(),
                        participants=visit_parts))
        db.session.add(vs[i])
        db.session.commit()


def _check_namespace(client, body):
    """ Checks that the namespace (mokkigo) is in response body."""
    href = body["@namespaces"]["mokkigo"]["name"]
    r = client.get(href)
    assert r.status_code == 200


def _check_control_get(ctrl, client, body):
    """ Check GET control from JSON object. Control's URL must be accessed."""
    href = body['@controls'][ctrl]['href']
    r = client.get(href)
    assert r.status_code == 200


def _check_control_post_mokki(ctrl, client, body):
    """ Checks POST method"""
    ctrl = body['@controls'][ctrl]
    href = ctrl['href']
    method = ctrl['method'].lower()
    encoding = ctrl['encoding'].lower()
    schema = ctrl['schema']
    assert method == 'post'
    assert encoding == 'json'
    mokki = get_mokki()
    validate(schema, mokki)
    r = client.post(href, json=mokki)
    assert r.status_code == 201


class TestMokki(object):
    COLLECTION = '/api/mokkis/'
    ITEM = '/api/mokkis/mokki-1/'
    ITEM2 = '/api/mokkis/mokki-2/'
    INVALID = '/api/mokkis/mokki-10/'
    MODIFIED = '/api/mokkis/mokki-x/'

    def test_mokki(self, client):
        mokkijson = get_mokki()
        mokkijson2 = get_mokki(2)
        # Test empty
        r = client.get(self.COLLECTION)
        assert r.status_code == 404

        r = client.get(self.ITEM)
        assert r.status_code == 404

        r = client.post(self.COLLECTION, data=json.dumps(mokkijson))
        assert r.status_code == 415

        r = client.post(self.COLLECTION, json=mokkijson)
        assert r.status_code == 201

        r = client.post(self.COLLECTION, json=mokkijson)
        assert r.status_code == 409

        invalid = {"asd": "asd", "loc": "loc"}
        r = client.post(self.COLLECTION, json=invalid)
        assert r.status_code == 400

        r = client.get(self.COLLECTION)
        assert r.status_code == 200

        r = client.get(self.ITEM)
        assert r.status_code == 200

        r = client.get(self.INVALID)
        assert r.status_code == 404

        r = client.put(self.ITEM, data=json.dumps(mokkijson))
        assert r.status_code == 415

        r = client.put(self.INVALID, json=mokkijson)
        assert r.status_code == 404

        invalidjson = {'neim': 'mpoe', 'location': 'loc'}
        r = client.put(self.ITEM, json=invalidjson)
        assert r.status_code == 400

        r = client.post(self.COLLECTION, json=mokkijson2)
        assert r.status_code == 201

        r = client.put(self.ITEM2, json=mokkijson)
        assert r.status_code == 409

        mokkijson['name'] = 'mokki-x'
        r = client.put(self.ITEM, json=mokkijson)
        assert r.status_code == 204

        r = client.delete(self.MODIFIED)
        assert r.status_code == 204

        r = client.get(self.MODIFIED)
        assert r.status_code == 404

        r = client.delete(self.MODIFIED)
        assert r.status_code == 404

        r = client.delete(self.INVALID)
        assert r.status_code == 404

        r = client.delete(self.ITEM2)
        assert r.status_code == 204

        r = client.delete(self.ITEM2)
        assert r.status_code == 404


class TestParticipant(object):
    COLLECTION = '/api/participants/'
    ITEM = '/api/participants/part1/'
    ITEM2 = '/api/participants/part2/'
    INVALID = '/api/participants/mokki-10/'
    MODIFIED = '/api/participants/partx/'

    def test_participant(self, client):
        pjson = get_participant()
        pjson2 = get_participant(2)

        # Test empty
        r = client.get(self.COLLECTION)
        assert r.status_code == 404

        r = client.get(self.ITEM)
        assert r.status_code == 404

        r = client.post(self.COLLECTION, data=json.dumps(pjson))
        assert r.status_code == 415

        r = client.post(self.COLLECTION, json=pjson)
        assert r.status_code == 201

        r = client.post(self.COLLECTION, json=pjson)
        assert r.status_code == 409

        invalid = {"asd": "asd", "loc": "loc"}
        r = client.post(self.COLLECTION, json=invalid)
        assert r.status_code == 400

        r = client.get(self.COLLECTION)
        assert r.status_code == 200

        r = client.get(self.ITEM)
        assert r.status_code == 200

        r = client.get(self.INVALID)
        assert r.status_code == 404

        r = client.put(self.ITEM, data=json.dumps(pjson))
        assert r.status_code == 415

        r = client.put(self.INVALID, json=pjson)
        assert r.status_code == 404

        invalidjson = {'neim': 'mpoe', 'location': 'loc'}
        r = client.put(self.ITEM, json=invalidjson)
        assert r.status_code == 400

        r = client.post(self.COLLECTION, json=pjson2)
        assert r.status_code == 201

        r = client.put(self.ITEM2, json=pjson)
        assert r.status_code == 409

        pjson['name'] = 'partx'
        r = client.put(self.ITEM, json=pjson)
        assert r.status_code == 204

        r = client.delete(self.MODIFIED)
        assert r.status_code == 204

        r = client.get(self.MODIFIED)
        assert r.status_code == 404

        r = client.delete(self.MODIFIED)
        assert r.status_code == 404

        r = client.delete(self.INVALID)
        assert r.status_code == 404

        r = client.delete(self.ITEM2)
        assert r.status_code == 204

        r = client.delete(self.ITEM2)
        assert r.status_code == 404


class TestItem(object):
    MOKKI = '/api/mokkis/'
    COLLECTION = '/api/mokkis/mokki-1/items/'
    ITEM = '/api/mokkis/mokki-1/items/item1/'
    ITEM2 = '/api/mokkis/mokki-1/items/item2/'
    INVALID = '/api/mokkis/mokki-1/items/mokki-10/'
    MODIFIED = '/api/mokkis/mokki-1/items/itemx/'

    def test_item(self, client):
        ijson = get_item()
        ijson2 = get_item(2)

        mjson = get_mokki()
        r = client.post(self.MOKKI, json=mjson)
        assert r.status_code == 201

        # Test empty
        r = client.get(self.COLLECTION)
        assert r.status_code == 404

        r = client.get(self.ITEM)
        assert r.status_code == 404

        r = client.post(self.COLLECTION, data=json.dumps(ijson))
        assert r.status_code == 415

        r = client.post(self.COLLECTION, json=ijson)
        assert r.status_code == 201

        r = client.post(self.COLLECTION, json=ijson)
        assert r.status_code == 409

        invalid = {"asd": "asd", "loc": "loc"}
        r = client.post(self.COLLECTION, json=invalid)
        assert r.status_code == 400

        r = client.get(self.COLLECTION)
        assert r.status_code == 200

        r = client.get(self.ITEM)
        assert r.status_code == 200

        r = client.get(self.INVALID)
        assert r.status_code == 404

        r = client.put(self.ITEM, data=json.dumps(ijson))
        assert r.status_code == 415

        r = client.put(self.INVALID, json=ijson)
        assert r.status_code == 404

        invalidjson = {'neim': 'mpoe', 'location': 'loc'}
        r = client.put(self.ITEM, json=invalidjson)
        assert r.status_code == 400

        r = client.post(self.COLLECTION, json=ijson2)
        assert r.status_code == 201

        r = client.put(self.ITEM2, json=ijson)
        assert r.status_code == 409

        ijson['name'] = 'itemx'
        r = client.put(self.ITEM, json=ijson)
        assert r.status_code == 204

        r = client.delete(self.MODIFIED)
        assert r.status_code == 204

        r = client.get(self.MODIFIED)
        assert r.status_code == 404

        r = client.delete(self.MODIFIED)
        assert r.status_code == 404

        r = client.delete(self.INVALID)
        assert r.status_code == 404

        r = client.delete(self.ITEM2)
        assert r.status_code == 204

        r = client.delete(self.ITEM2)
        assert r.status_code == 404


class TestVisit(object):
    MOKKI = '/api/mokkis/'
    PARTICIPANT = '/api/participants/'
    ITEMITEM = '/api/mokkis/mokki-1/items/'

    COLLECTION = '/api/visits/'
    ITEM = '/api/visits/visit1/'
    ITEM2 = '/api/visits/visit2/'
    INVALID = '/api/visits/visit10/'
    MODIFIED = '/api/visits/visitx/'

    def test_visit(self, client):
        mjson = get_mokki()
        mjson2 = get_mokki(2)
        pjson = get_participant()
        pjson2 = get_participant(2)
        pjson3 = get_participant(3)
        ijson = get_item()
        vjson = get_visit()
        vjson2 = get_visit(2)

        r = client.post(self.MOKKI, json=mjson)
        assert r.status_code == 201
        r = client.post(self.MOKKI, json=mjson2)
        assert r.status_code == 201
        r = client.post(self.PARTICIPANT, json=pjson)
        assert r.status_code == 201
        r = client.post(self.PARTICIPANT, json=pjson2)
        assert r.status_code == 201
        r = client.post(self.PARTICIPANT, json=pjson3)
        assert r.status_code == 201
        r = client.post(self.ITEMITEM, json=ijson)
        assert r.status_code == 201

        # Test empty
        r = client.get(self.COLLECTION)
        assert r.status_code == 404

        r = client.get(self.ITEM)
        assert r.status_code == 404

        r = client.post(self.COLLECTION, data=json.dumps(vjson))
        assert r.status_code == 415

        r = client.post(self.COLLECTION, json=vjson)
        assert r.status_code == 201

        r = client.post(self.COLLECTION, json=vjson)
        assert r.status_code == 409

        invalid = {"asd": "asd", "loc": "loc"}
        r = client.post(self.COLLECTION, json=invalid)
        assert r.status_code == 400

        r = client.get(self.COLLECTION)
        assert r.status_code == 200

        r = client.get(self.ITEM)
        assert r.status_code == 200

        r = client.get(self.INVALID)
        assert r.status_code == 404

        r = client.put(self.ITEM, data=json.dumps(vjson))
        assert r.status_code == 415

        r = client.put(self.INVALID, json=vjson)
        assert r.status_code == 404

        invalidjson = {'neim': 'mpoe', 'location': 'loc'}
        r = client.put(self.ITEM, json=invalidjson)
        assert r.status_code == 400

        print(vjson2)
        r = client.post(self.COLLECTION, json=vjson2)
        assert r.status_code == 201

        r = client.put(self.ITEM2, json=vjson)
        assert r.status_code == 409

        vjson['visit_name'] = 'visitx'
        r = client.put(self.ITEM, json=vjson)
        assert r.status_code == 204

        r = client.delete(self.MODIFIED)
        assert r.status_code == 204

        r = client.get(self.MODIFIED)
        assert r.status_code == 404

        r = client.delete(self.MODIFIED)
        assert r.status_code == 404

        r = client.delete(self.INVALID)
        assert r.status_code == 404

        r = client.delete(self.ITEM2)
        assert r.status_code == 204

        r = client.delete(self.ITEM2)
        assert r.status_code == 404


class TestOther(object):
    def test(self, client):
        r = client.get('/api/')
        assert r.status_code == 200
