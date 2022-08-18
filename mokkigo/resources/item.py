import json

from flask import request, Response, url_for
from flask_restful import Resource

from jsonschema import validate, ValidationError

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import (NotFound)

from mokkigo import db
from mokkigo.models import Item, Mokki
from mokkigo.constants import JSON, LINK_RELATIONS_URL, ITEM_PROFILE
from mokkigo.utils import create_error_response, MokkigoBuilder


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
        db_mokki = Mokki.query.filter_by(name=mokki.name).first()

        is_items = Item.query.filter_by(mokki=db_mokki).first()
        if not is_items:
            return create_error_response(
                    title="Not found",
                    status_code=404,
                    message="Database is empty"
            )

        mokki_items = Item.query.filter_by(mokki=db_mokki)

        body = MokkigoBuilder(items=[])

        body.add_namespace("mokkigo", LINK_RELATIONS_URL)
        body.add_namespace("self", url_for("api.itemcollection",
                                           mokki=db_mokki))
        body.add_control_add_item(mokki)

        for item in mokki_items:
            i = MokkigoBuilder(
                    name=item.name,
                    amount=item.amount
            )

            i.add_control("self", url_for("api.itemitem",
                                          mokki=mokki, item=item))
            i.add_control("profile", ITEM_PROFILE)
            body["items"].append(i)

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
        if request.mimetype != JSON:
            return create_error_response(
                    status_code=415,
                    title="Unsupported Media Type",
                    message="Content type must be JSON"
            )

        try:
            validate(request.json, Item.json_schema())
        except ValidationError as e:
            return create_error_response(
                    status_code=400,
                    title="Invalid JSON document",
                    message=str(e)
            )

        try:
            if Item.query.filter_by(name=request.json["name"]).first():
                raise Exception

            item = Item(
                    name=request.json["name"],
                    amount=request.json["amount"],
                    mokki=mokki
            )

            href = url_for("api.itemitem", mokki=mokki, item=item)

            db.session.add(item)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return create_error_response(
                    status_code=409,
                    title="Item already exists"
            )

        return Response(status=201, headers={"Location": href})


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
        m, i = find_mokki_item(mokki, item)

        body = MokkigoBuilder(
                name=i.name,
                amount=i.amount
        )

        body.add_namespace("mokkigo", LINK_RELATIONS_URL)

        body.add_control("self", url_for("api.itemitem", mokki=mokki, item=i))
        body.add_control("profile", ITEM_PROFILE)
        body.add_control("collection", url_for("api.itemcollection",
                                               mokki=mokki))

        body.add_control_delete_item(mokki=mokki, item=i)
        body.add_control_edit_item(mokki=mokki, item=i)

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
        if request.mimetype != JSON:
            return create_error_response(
                    status_code=415,
                    title="Content type error",
                    message="Content type must be JSON"
            )

        find_mokki_item(mokki, item)
        try:
            validate(request.json, Item.json_schema())
        except ValidationError as e:
            return create_error_response(
                    status_code=400,
                    title="Invalid JSON document",
                    message=str(e)
            )

        try:
            if Item.query.filter_by(name=request.json["name"]).first():
                raise Exception

            item.deserialize(request.json)
            db.session.add(item)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return create_error_response(
                    status_code=409,
                    title="Item already exists"
            )

        return Response(status=204)

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
        find_mokki_item(mokki, item)

        db.session.delete(item)
        db.session.commit()
        return Response(status=204)


class ItemConverter(BaseConverter):
    def to_url(self, item):
        return str(item.name)

    def to_python(self, item_name):
        db_i = Item.query.filter_by(name=item_name).first()
        if db_i is None:
            raise NotFound
        return db_i


def find_mokki_item(mokki, item):
    """
    Checks if there is specified mokki found and if it has specified item
    """
    m = Mokki.query.filter_by(name=mokki.name).first()

    i = Item.query.filter_by(mokki=mokki, name=item.name).first()

    return m, i
