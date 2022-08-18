# Code edited from
# https://lovelace.oulu.fi/file-download/embedded/ohjelmoitava-web/ohjelmoitava-web/pwp-sensorhub-db-test-py/ # noqa

import os
import pytest
import tempfile

from datetime import datetime

from sqlalchemy.engine import Engine
from sqlalchemy import event

from mokkigo import create_app, db
from mokkigo.models import Visit, Mokki, Participant, Item


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
            "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
            "TESTING": "TRUE",
    }
    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app
    os.close(db_fd)
    os.unlink(db_fname)


def _get_visit(num, mokki, parts):
    name = "Visit {}".format(num)
    time = datetime.now()
    return Visit(visit_name=name,
                 mokki_name=mokki,
                 time_start=time,
                 time_end=time,
                 participants=parts)


def _get_mokki(num):
    name = "Mokki {}".format(num)
    location = "Location {}".format(num)
    return Mokki(name=name, location=location)


def _get_participant(num):
    name = "Participant {}".format(num)
    allergies = "Food {}".format(num)
    return Participant(name=name, allergies=allergies)


def _get_item(num):
    name = "Item {}".format(num)
    amount = "{}".format(num)
    return Item(name=name, amount=amount)


def test_create_item(app):
    with app.app_context():
        i = _get_item(1)
        db.session.add(i)
        db.session.commit()
        assert Item.query.count() == 1


def test_create_mokki(app):
    with app.app_context():
        m = _get_mokki(1)
        db.session.add(m)
        db.session.commit()
        assert Mokki.query.count()


def test_create_participant(app):
    with app.app_context():
        p = _get_participant(1)
        db.session.add(p)
        db.session.commit()
        assert Participant.query.count()


def test_create_visit(app):
    with app.app_context():
        participants = []
        m = _get_mokki(1)
        p1 = _get_participant(1)
        participants.append(p1)
        v = _get_visit(2, m.name, participants)

        db.session.add(m)
        db.session.add(p1)
        db.session.add(v)
        db.session.commit()


def test_create_instances(app):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that
    everything can be found from database, and that all relationships have been
    saved correctly.
    """
    with app.app_context():
        p1 = _get_participant(num=1)
        p2 = _get_participant(num=2)

        i1 = _get_item(num=1)
        i2 = _get_item(num=2)

        m1 = _get_mokki(num=1)

        parts = []
        parts.append(p1)
        parts.append(p2)

        v1 = _get_visit(num=1, mokki=m1.name, parts=parts)

        db.session.add(p1)
        db.session.add(p2)
        db.session.add(i1)
        db.session.add(i2)
        db.session.add(m1)
        db.session.add(v1)
        db.session.commit()

        assert Visit.query.count() == 1
        assert Mokki.query.count() == 1
        assert Participant.query.count() == 2
        assert Item.query.count() == 2
