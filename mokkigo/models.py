import click

from flask.cli import with_appcontext
from sqlalchemy.engine import Engine
from sqlalchemy import event

from dateutil import parser

from mokkigo import db


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Association table used to enable to map participants to multiple visits
visit_participant_mapping = db.Table(
    "visit_participant_mapping",
    db.Column("visit_id", db.ForeignKey("visit.id"), primary_key=True),
    db.Column("participant_id", db.ForeignKey("participant.id"),
              primary_key=True)
)


class Visit(db.Model):
    """
    Visit table
    visit_name       String
    time_start       String in format of date-time (ISO8601)
    time_end         String in format of date-time (ISO8601)
    mokki_name       String name reference to mokki where this visit occurred
    participants     table of Participant objects
    """
    __tablename__ = "visit"
    id = db.Column(db.Integer, primary_key=True)
    visit_name = db.Column(db.String(128), nullable=False, unique=True)
    mokki_name = db.Column(db.String(128), nullable=False)
    time_start = db.Column(db.DateTime, nullable=False)
    time_end = db.Column(db.DateTime, nullable=False)
    participants = db.relationship("Participant",
                                   secondary=visit_participant_mapping,
                                   back_populates="visits")

    def json_schema():
        schema = {
                "type": "object",
                "required": ["visit_name", "mokki_name",
                             "time_start", "time_end"
                             ]
        }
        props = schema["properties"] = {}
        props["visit_name"] = {
                "description": "Name of the visit",
                "type": "string"
        }
        props["mokki_name"] = {
                "description": "Name of the mokki",
                "type": "string"
        }
        props["time_start"] = {
                "description": "Start date of the visit with date-time format",
                "type": "string",
                "format": "date-time"
        }
        props["time_end"] = {
                "description": "End date of the visit with date-time format",
                "type": "string",
                "format": "date-time"
        }
        props["participants"] = {
                "description": "Names of visit participants",
                "type": "array",
                "items": {
                        "type": "string"
                }
        }
        return schema

    def serialize(self):
        return {
                "visit_name": self.visit_name,
                "mokki_name": self.mokki_name,
                "time_start": self.time_start.isoformat(),
                "time_end": self.time_end.isoformat()
        }

    def deserialize(self, doc):
        self.visit_name = doc["visit_name"]
        self.mokki_name = doc["mokki_name"]
        self.time_start = parser.parse(doc["time_start"])
        self.time_end = parser.parse(doc["time_end"])


class Mokki(db.Model):
    """
    Mokki table
    name            String, unique
    location        String
    items           table of Item objects
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    location = db.Column(db.String(128), nullable=False)
    items = db.relationship("Item")

    def json_schema():
        schema = {
                "type": "object",
                "required": ["name", "location"]
        }
        props = schema["properties"] = {}
        props["name"] = {
                "description": "Name of the mokki",
                "type": "string"
        }
        props["location"] = {
                "description": "Location of the mokki",
                "type": "string"
        }
        return schema

    def serialize(self):
        return {
                "name": self.name,
                "location": self.location
        }

    def deserialize(self, doc):
        self.name = doc["name"]
        self.location = doc["location"]


class Participant(db.Model):
    """
    Participant table
    name            String
    allergies       String, nullable
                    list of all the allergies in string format
                        - Needs some thinking
                            - parse json array?
                            - just str?
    """
    __tablename__ = "participant"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    allergies = db.Column(db.String(128))
    visits = db.relationship("Visit", secondary=visit_participant_mapping,
                             back_populates="participants")

    def json_schema():
        schema = {
                "type": "object",
                "required": ["name", "allergies", "visits"]
        }
        props = schema["properties"] = {}
        props["name"] = {
                "description": "Name of the participant",
                "type": "string"
        }
        props["allergies"] = {
                "description": "Possible allergies if any",
                "type": "string"
        }
        props["visits"] = {
                "description": "List of all the participant's visits",
                "type": "array",
                "items": {
                        "type": "string"
                }
        }
        return schema

    def serialize(self):
        return {
                "name": self.name,
                "allergies": self.allergies
        }

    def deserialize(self, doc):
        self.name = doc["name"]
        self.allergies = doc.get("allergies")


class Item(db.Model):
    """
    name            String
    amount          String
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    mokki = db.relationship("Mokki", back_populates="items")
    mokki_id = db.Column(db.Integer, db.ForeignKey("mokki.id"))
    amount = db.Column(db.String(64), nullable=False)

    def json_schema():
        schema = {
                "type": "object",
                "required": ["name", "amount"]
        }
        props = schema["properties"] = {}
        props["name"] = {
                "description": "Name of the item",
                "type": "string"
        }
        props["amount"] = {
                "description": "Needed amount of the item",
                "type": "string"
        }
        return schema

    def serialize(self):
        return {
                "name": self.name,
                "amount": self.amount
        }

    def deserialize(self, doc):
        self.name = doc["name"]
        self.amount = doc["amount"]


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()


@click.command("testgen")
@with_appcontext
def generate_test_data():
    v1 = Visit(
        time_start="2022-06-05T16:25:29+00:00",
        time_end="2022-06-05T16:25:29+00:00",
        visit_name="visit1"
    )

    m1 = Mokki(
            name="mokki",
            location="sijainti1"
    )

    p1 = Participant(
            name="participant",
            allergies="food"
    )

    v1.mokki_name = m1.name
    v1.participants.append(p1)

    db.session.add(p1)
    db.session.add(m1)
    db.session.add(v1)

    db.session.commit()
