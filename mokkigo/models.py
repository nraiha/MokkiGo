import click

from flask.cli import with_appcontext
from . import db
from datetime import datetime


# Association table used to enable to map participants to multiple visits
visitors = db.Table(
    "visitors",
    db.Column("visit_id", db.Integer, db.ForeignKey("visit.id")),
    db.Column("participant_id", db.Integer, db.ForeignKey("participant.id"))
)


class Visit(db.Model):
    """
    Visit table
    time_start       String in format of date-time (ISO8601)
    time_end         String in format of date-time (ISO8601)
    mokki_name       String name reference to mokki where this visit occurred
    participants     table of Participant objects
    """
    __tablename__ = "visit"
    id = db.Column(db.Integer, primary_key=True)
    time_start = db.Column(db.String(128), nullable=False)
    time_end = db.Column(db.String(128), nullable=False)
    mokki_name = db.Column(db.String(128), nullable=False)
    participants = db.relationship("Participant", secondary=visitors)

    def json_schema():
        schema = {
                "type": "object",
                "required": ["mokki_name", "time_start", "time_end"]
        }
        props = schema["properties"] = {}
        props["mokki_name"] = {
                "description": "Name of the mokki",
                "type": "string"
        }
        props["time_start"] = {
                "description": "Start date of the visit w/ date-time format",
                "type": "string",
                "format": "date-time"
        }
        props["time_end"] = {
                "description": "End date of the visit w/ date-time format",
                "type": "string",
                "format": "date-time"
        }
        return schema

    def serialize(self):
        return {
                "mokki_name": self.mokki_name,
                "time_start": self.time_start.isoformat(),
                "time_end": self.time_end.isoformat()
        }

    def deserialize(self, doc):
        self.mokki_name = doc["mokki_name"]
        self.time_start = datetime.datefromisoformat(doc["time_start"])
        self.time_end = datetime.datefromisoformat(doc["time_end"])


class Mokki(db.Model):
    """
    Mokki table
    name            String, unique
    location        String
    shoppinglist    table of Items objects
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    location = db.Column(db.String(128), nullable=False)
    shoppinglist = db.relationship("Item",)

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
                "amount": self.amount
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
    name = db.Column(db.String(128), nullable=False)
    allergies = db.Column(db.String(128))
    visit_id = db.Column(db.Integer, db.ForeignKey("visit.id"), unique=True)

    def json_schema():
        schema = {
                "type": "object",
                "required": "name"
        }
        props = schema["properties"] = {}
        props["name"] = {
                "description": "Name of the participant",
                "type": "string",
        }
        return schema

    def serialize(self):
        return {
                "name": self.name,
                "allergies": self.allergies
        }

    def deserialize(self, doc):
        self.name = doc["name"]
        self.allergies = doc["allergies"]


class Item(db.Model):
    """
    name            String
    amount          String
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    mokki = db.relationship("Mokki", back_populates="shoppinglist")
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

