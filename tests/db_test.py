# Code edited from
# https://lovelace.oulu.fi/file-download/embedded/ohjelmoitava-web/ohjelmoitava-web/pwp-sensorhub-db-test-py/ # noqa

import os
import pytest
import tempfile

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


def _get_visit():
    return Visit(
            time_start="1990-01-01",
            time_end="1990-01-08"
    )


def _get_mokki():
    return Mokki(
            name="mokki",
            location="Oulu"
    )


def _get_participant():
    return Participant(
            name="Erkki Esimerkki"
    )


def _get_item():
    return Item(
            name="test_item"
        )


def test_create_instances(app):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that
    everything can be found from database, and that all relationships have been
    saved correctly.
    """
    with app.app_context():
        p1 = _get_participant()
        p2 = _get_participant()

        i1 = _get_item()
        i2 = _get_item()

        m1 = _get_mokki()

        v1 = _get_visit()

        v1.mokki_name = m1.name
        v1.participants.append(p1)
        v1.participants.append(p2)

        i1.mokki = m1
        i2.mokki = m1

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
