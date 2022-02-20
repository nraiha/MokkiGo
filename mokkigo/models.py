from enum import unique
import click
from flask.cli import with_appcontext
from . import db


# Used to enable to map participants to multiple visits
visitor_table = db.Table
(
    db.Column("visit_id", db.Integer, db.ForeignKey("visit.id")),
    db.Column("participant_id", db.Integer, db.ForeignKey("participant.id"))
)

class Visit(db.Model):
    """
    Visit table
    timeperiod       String (Datetime?)
    mokki_name       String name reference to mokki where this visit occurred
    participants     table of Participant objects
    """
    __tablename__= "visit"
    id = db.Column(db.Integer, primary_key=True)
    timeperiod = db.Column(db.String(128), nullable=False)
    mokki_name = db.Column(db.String(128), nullable=False)
    participants = db.relationship("Participant", secondary=visitor_table)

class Mokki(db.Model):
    """
    Mokki table
    name            String
    location        String
    shoppinglist    table of Items objects
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    location = db.Column(db.String(128), nullable=False)
    shoppinglist = db.relationship("Item")

class Participant(db.Model):
    """
    Participant table
    name            String
    allergies       String list of all the allergies in string format (Needs some thinking)
    """
    __tablename__= "participant"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    allergies = db.Column(db.String(128))

class Item(db.Model):
    """
    name            String

    TBD If amount is wanted maybe need to create new item instance every time when new amount is picked for the item
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    mokki = db.relationship("Mokki", back_populates="shoppinglist")

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()

