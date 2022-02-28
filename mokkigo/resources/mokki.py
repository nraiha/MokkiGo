import json

from flask import request, Response, url_for
from flask_restful import Resource

from sqlalchemy.exc import IntegrityError

from jsonschema import validate, ValidationError

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound

from mokkigo import db
from mokkigo.models import Mokki
from mokkigo.constants import JSON


class MokkiCollection(Resource):
    def get(self):
        """
        GET for MokkiCollection
        OpenAPI description below:
        ---
        description: Get the list of all Mokki
        responses:
          '200':
            description: List of mokkis
            content:
              application/json:
                example:
                  - name: Ii-mokki
                    location: Ii
                  - name: Kemi-mokki
                    location: Kemi
        """
        body = {"items": []}
        for db_m in Mokki.query.all():
            m = db_m.serialize()
            body["items"].append(m)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self):
        """
        POST method for MokkiCollection
        OpenAPI description below:
        ---
        description: create new mokki
        requestBody:
          description: JSON document that contains data for a new mokki
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Mokki'
              example:
                name: Ii-mokki
                location: Ii
        responses:
          '201':
            description: Mokki created successfully
            headers:
              Location:
                description: URI of the new mokki
                schema:
                  type: string
          '400':
            description: Request body invalid
          '409':
            description: Already exists
          '415':
            description: Wrong media type was used
        """
        content_type = request.mimetype
        if content_type != JSON:
            return Response("Unsupported Media Type", status=415)

        try:
            validate(request.json, Mokki.json_schema())
        except ValidationError as e:
            return Response(400, "Invalid JSON document", str(e))

        m = Mokki(name=request.json["name"], location=request.json["location"])
        href = url_for("api.mokkiitem", mokki=m)
        try:
            db.session.add(m)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Mokki '{}' already exists".format(m.name), 409

        return Response(status=201, headers={"Location": href})


class MokkiItem(Resource):
    def get(self, mokki):
        """
        GET method for MokkiItem
        OpenAPI description below:
        ---
        description: Get details of one mokki
        responses:
          '200':
            description: Data of the single mokki
            content:
              application/json:
                examples:
                  name: Ii-mokki
                  location: Ii
          '404':
            description: The mokki was not found
        """
        body = mokki.serialize()
        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, mokki):
        """
        PUT method for MokkiItem
        OpenAPI description below:
        ---
        description: Edit one mokki
        requestBody:
          description: JSON document that contains new data for mokki
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Mokki'
              example:
                name: Ii-mokki
                location: Kuivaniemi
        responses:
          '204':
            description: The mokki was updated successfully
          '400':
            description: The request body was not valid
          '404':
            description: The mokki was not found
          '409':
            description: A mokki with that name already exists
          '415':
            description: Wrong media type was used
        """
        if request.mimetype != JSON:
            return Response("Unsupported Media Type", status=415)
        try:
            validate(request.json, Mokki.json_schema())
        except ValidationError as e:
            return Response(400, "Invalid JSON document", str(e))

        mokki.deserialize(request.json)
        try:
            db.session.add(mokki)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Mokki '{}' already exists".format(mokki.name), 409

    def delete(self, mokki):
        """
        DELETE method for MokkiItem
        OpenAPI description below:
        ---
        description: Delete selected mokki
        responses:
          '204':
            description: Mokki deleted successfully
          '404':
            description: Mokki not found
        """
        db.session.delete(mokki)
        db.session.commit()
        return Response(status=204)


class MokkiConverter(BaseConverter):
    def to_url(self, mokki):
        return str(mokki.id)

    def to_python(self, mokki_name):
        db_mokki = Mokki.query.filter_by(name=mokki_name).first()
        if db_mokki is None:
            raise NotFound
        return db_mokki
