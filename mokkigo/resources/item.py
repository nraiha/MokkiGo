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
        """
        Get for ItemCollection
        OpenAPI Description below:
        ---
        description: Get the list of items
        responses:
          '200':
            description: List of items
            content:
              application/json:
                example:
                - name: item1
                  amount: 3
                - name: item2
                  amount: 5
        """

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
        """
        Post method for the ItemCollection
        OpenAPI description below:
        ---
        description: create new item
        requestBody:
          description: JSON document that contains basic data for a new item
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Item'
              example:
                name: item1
                amount: 1.0
          responses:
            '200':
              description:
            '400':
              description:
            '415':
              description:
        """
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
        """
        PUT for ItemItem
        OpenAPI description below:
        ---
        description: JSON document that contains new data for Item
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Item'
            example:
              'todo'
        responses:
          '204':
            description: The item's attributes were updated successfully
          '400':
            description: The request body was invalid
          '404':
            description: The item was not found
          '409':
            description: The item the same name already exists
          '415':
            description: Wrong media type was used
        """
        pass

    def delete(self, mokki, item):
        pass


class ItemConverter(BaseConverter):
    def to_url(self, item):
        return str(item.id)
