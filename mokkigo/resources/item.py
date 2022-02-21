import json

from flask import request, Response
from flask_restful import Resource

from jsonschema import validate, ValidationError

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import (NotFound)

from mokkigo import db
from mokkigo.models import Item, Mokki
from mokkigo.constants import JSON


class ItemCollection(Resource):
    def get(self, mokki):
        db_mokki = Mokki.query.filter_by(name=mokki).first()
        if db_mokki is None:
            raise NotFound

        remaining = Item.query.filter_by(mokki=db_mokki)
        body = {
                "mokki": db_mokki.name,
                "items": []
        }

        for item in remaining:
            body["items"].append(
                    {
                        "name": item.name,
                        "amount": item.amount
                    }
            )
        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self, mokki):
        content_type = request.mimetype
        if content_type != JSON:
            return Response("Unsupported Media Type", status=415)

        try:
            validate(request.json, Item.json_schema())
        except ValidationError as e:
            return Response(str(e), status=400)

        item = Item(
                name=request.json["name"],
                amount=request.json["amount"],
                mokki=mokki
        )
        db.session.add(item)
        db.session.commit()

        from mokkigo import api

        return Response(status=201,
                        headers={
                            "Location": api.url_for(ItemItem,
                                                    mokki=mokki,
                                                    item=item)
                        })


class ItemItem(Resource):
    def get(self, mokki, item):
        pass

    def put(self, mokki, item):
        pass

    def delete(self, mokki, item):
        pass


class ItemConverter(BaseConverter):
    def to_url(self, item):
        return str(item.id)
