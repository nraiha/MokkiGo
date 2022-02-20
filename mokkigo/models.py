import click
from flask.cli import with_appcontext
from . import db
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

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


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

