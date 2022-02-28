import json

from flask import request, Response, url_for
from flask_restful import Resource

from sqlalchemy.exc import IntegrityError

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
              description: Item was created successfully
              headers:
                Location:
                  description: URI of the new Item
                  schema:
                    type: string
            '400':
              description: The request body was not valid
            '404:
              description: Mokki was not found
            '409':
              description: A item with the same name already exists
            '415':
              description: Wrong media type was used
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

        href = url_for("api.itemitem", mokki=mokki, item=item)

        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Item '{}' already exists".format(item.name), 409

        return Response(status=201,
                        headers={
                            "Location": href
                        })


class ItemItem(Resource):
    def get(self, mokki, item):
        """
        GET method for ItemItem
        OpenAPI description below:
        ---
        description: Get details of one item
        responses:
          '200':
            description: Data of a single item
            content:
              application/json:
                examples:
                  name: carrot
                  amount: 3
          '404':
            description: Item not found
        """
        body = item.serialize()
        return Response(json.dumps(body), 200, mimetype=JSON)

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
              name: Pear
              amount: 0
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
        content_type = request.mimetype
        if content_type != JSON:
            return Response("Unsupported Media Type", status=415)

        try:
            validate(request.json, Item.json_schema())
        except ValidationError as e:
            return Response(400, "Invalid JSON document", str(e))

        item.deserialize(request.json)
        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Item '{}' already exists".format(item.name), 409

    def delete(self, mokki, item):
        """
        DELETE method for ItemItem
        OpenAPI description below:
        ---
        description: Delete selected item
        responses:
          '204':
            description: Item deleted successfully
          '404':
            description: Item not found
        """
        db.session.delete(item)
        db.session.commit()
        return Response(status=204)


class ItemConverter(BaseConverter):
    def to_url(self, item):
        return str(item.id)

    def to_python(self, item_name):
        db_i = Item.query.filter_by(name=item_name).first()
        if db_i is None:
            raise NotFound
        return db_i
