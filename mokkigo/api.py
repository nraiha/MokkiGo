from flask import Blueprint
from flask_restful import Api, Resource

from mokkigo.resources.mokki import MokkiCollection, MokkiItem
from mokkigo.resources.item import ItemCollection, ItemItem
from mokkigo.resources.visit import VisitCollection, VisitItem
from mokkigo.resources.participant import (ParticipantCollection,
                                           ParticipantItem)

abi_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(abi_bp)

api.add_resource(MokkiCollection, "mokkis/")
api.add_resource(MokkiItem, "mokkis/<mokki:mokki>/")

api.add_resource(ItemCollection, "mokkis/<mokki:mokki>/items/")
api.add_resource(ItemItem, "mokkis/<mokki:mokki>/items/<item:item>/")

api.add_resource(ParticipantCollection, "participants/")
api.add_resource(ParticipantItem, "participants/<participant:participant>/")

api.add_resource(VisitCollection, "visits/")
api.add_resource(VisitItem, "visits/<visit:visit>/")
