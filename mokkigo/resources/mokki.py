import json

from flask import request, Response
from flask_restful import Resource

from jsonschema import validate, ValidationError

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound

from mokkigo.models import Mokki
from mokkigo.constants import JSON


class MokkiCollection(Resource):
    def get(self):
        pass

    def post(self):
        content_type = request.mimetype
        if content_type != JSON:
            return Response("Unsupported Media Type", status=415)


class MokkiItem(Resource):
    def get(self, mokki):
        pass

    def post(self, mokki):
        pass

    def put(self, mokki):
        pass

    def delete(self, mokki):
        pass


class MokkiConverter(BaseConverter):
    def to_url(self, mokki):
        return str(mokki.id)

    def to_python(self, mokki_name):
        db_mokki = Mokki.query.filter_by(name=mokki_name).first()
        if db_mokki is None:
            raise NotFound
        return db_mokki
