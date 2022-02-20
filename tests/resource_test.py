# Code edited from
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/testing-flask-applications-part-2/ # noqa

import json
import os
import pytest
import tempfile
import time
from datetime import date
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from mokkigo import create_app, db
from mokkigo.models import Visit, Mokki, Item, Participant


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
        _populate_db()

    yield app.test_client()

    os.close(db_fd)
    os.unlink(db_fname)


def _populate_db():
    for i in range(1, 4):
        p = []
        for j in range(1, 4):
            p.append(Participant(name="participant-{}".format(i),
                                 allergies="food-{}".format(i)))
        m = Mokki(
                name="Mokki-{}".format(i),
                location="Area-{}".format(i)
        )
        v = Visit(
                time_start="2022-01-0{}".format(i),
                time_end="2022-01-0{}".format(i+5),
                visit_name="visit-{}".format(i)
        )
        item = []
        for j in range(1, 2):
            item.append(Item(name="item-{}".format(i),
                             amount="{}".format(i+10)))

        v.mokki_name = m.name
        v.participants.append(p[0])
        v.participants.append(p[1])
        v.participants.append(p[2])
        v.participants.append(p[3])

        item[0].mokki = m
        item[1].mokki = m

        db.session.add(p[0])
        db.session.add(p[1])
        db.session.add(p[2])
        db.session.add(p[3])
        db.session.add(item[0])
        db.session.add(item[1])
        db.session.add(m)
        db.session.add(v)

    db.session.commit()


class TestVisitCollection(object):
    RESOURCE_URL = "/api/visits/"


class TestVisitItem(object):
    RESOURCE_URL = "/api/visits/visit-1/"
    INVALID_URL = "/api/visits/visit-10/"


class TestMokkiCollection(object):
    RESOURCE_URL = "/api/mokkis/"


class TestMokkiItem(object):
    RESOURCE_URL = "/api/mokkis/Mokki-1/"
    INVALID_URL = "/api/visits/Mokki-10/"


class TestItemCollection(object):
    RESOURCE_URL = "/api/mokkis/Mokki-1/items/"


class TestItemItem(object):
    RESOURCE_URL = "/api/mokkis/Mokki-1/items/item-1"
    INVALID_URL = "/api/visits/Mokki-10/items/item-10"


class TestParticipantCollection(object):
    RESOURCE_URL = "/api/participants/"


class TestParticipantItem(object):
    RESOURCE_URL = "/api/participants/participant-1"
    INVALID_URL = "/api/participants/participant-10"

