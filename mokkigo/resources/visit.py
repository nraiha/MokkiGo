import json

from flask import request, Response
from flask_restful import Resource

from jsonschema import validate, ValidationError

from werkzeug.routing import BaseConverter
from werkzeus.exceptions import (NotFound)

from mokkigo import db, api
from mokkigo.module import Visit
from mokkigo.constants import JSON


class VisitCollection(Resource):
    def get(self):
        pass

    def post(self):
        pass


class VisitItem(Resource):
    def get(self, visit):
        pass

    def post(self, visit):
        pass

    def put(self, visit):
        pass

    def delete(self, visit):
        pass


class VisitConverter(BaseConverter):
    def to_url(self, visit):
        pass

    def to_python(self, visit_name):
        pass
