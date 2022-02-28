import json

from flask import request, Response, url_for
from flask_restful import Resource

from sqlalchemy.exc import IntegrityError

from jsonschema import validate, ValidationError, draft7_format_checker

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import (NotFound)

from dateutil import parser

from mokkigo import db
from mokkigo.models import Visit
from mokkigo.constants import JSON


class VisitCollection(Resource):
    def get(self):
        """
        GET method for VisitCollection
        OpenAPI description below:
        ---
        description: Get the list of visits
        responses:
          '200':
            description: List of visits
            content:
              application/json:
                example:
                - visit_name: Trip to Ii
                  time_start: 2020-02-01T00:01:01.003+1:00
                  time_end: 2020-02-03T00:02:02.003+1:00
                  mokki_name: Ii-mokki
                - visit_name: Weekend in the Ii-mokki
                  time_start: 2020-01-03T00:02:02.003+1:00
                  time_end:   2020-01-04T00:02:02.003+1:00
                  mokki_name: Ii-mokki
        """
        body = {"items": []}
        for db_v in Visit.query.all():
            v = db_v.serialize()
            body["items"].append(v)
        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self):
        """
        POST for VisitCollection
        OpenAPI description below:
        ---
        description: create new visit
        requestBody:
          description: JSON document that contains data for a new visit
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Visit'
              example:
                name: Weekend in the Ii
                time_start: 1990-01-01T00:02:02.003+1:00
                time_end: 1990-01-05T00:02:02.003+1:00
                mokki_name: Ii-mokki
        responses:
          '201':
            description: Visit was created successfully
            headers:
              Location:
                description: URI of the new visit
                schema:
                  type: string
          '400':
            description: The request body was not valid
          '409':
            description: Already exists
          '415':
            description: Wrong media type was used
        """
        content_type = request.mimetype
        if content_type != JSON:
            return Response("Unsupported Media Type", status=415)

        try:
            validate(
                request.json,
                Visit.json_schema(),
                format_checker=draft7_format_checker
            )
        except ValidationError as e:
            return "Invalid JSON document, {}".format(str(e)), 400

        v = Visit(
            visit_name=request.json["visit_name"],
            mokki_name=request.json["mokki_name"],
            time_start=parser.parse(request.json["time_start"]),
            time_end=parser.parse(request.json["time_end"])
        )

        href = url_for("api.visititem", visit=v)

        try:
            db.session.add(v)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Participant '{}' already exists".format(v.visit_name), 409

        return Response(status=201, headers={"Location": href})


class VisitItem(Resource):
    def get(self, visit):
        """
        GET method for VisitItem
        OpenAPI description below:
        ---
        description: Get details of one visit
        responses:
          '200':
            description: Data of the single visit
            content:
              application/json:
                examples:
                  visit_name: Weekend in the Ii
                  time_start: 1990-01-01T00:02:02.003+1:00
                  time_end: 1990-01-03T00:02:02.003+1:00
                  mokki_name: Ii-mokki
          '404':
            description: The participant was not found
        """
        body = visit.serialize()
        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, visit):
        """
        PUT method for ParticipantItem
        OpenAPI description below:
        ---
        description: Edit one participant
        requestBody:
          description: JSON document that contains new data for participant
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Participant'
              example:
                name: jugioh
                allergies: plants
        responses:
          '204':
            description: The participant was updated successfully
          '400':
            description: The request body was not valid
          '404':
            description: The participant was not found
          '409':
            description: A participant with that name already exists
          '415':
            description: Wrong media type was used
        """
        content_type = request.mimetype
        if content_type != JSON:
            return Response("Unsupported Media Type", status=415)

        try:
            validate(request.json, Visit.json_schema())
        except ValidationError as e:
            return Response(400, "Invalid JSON document", str(e))

        visit.deserialize(request.json)
        try:
            db.session.add(visit)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Participant '{}' already exists".format(
                    visit.visit_name), 409

    def delete(self, visit):
        """
        DELETE method for VisitItem
        OpenAPI description below:
        ---
        description: Delete selected visit
        responses:
          '204':
            description: visit deleted successfully
          '404':
            description: visit not found
        """
        db.session.delete(visit)
        db.session.commit()
        return Response(status=204)


class VisitConverter(BaseConverter):
    def to_url(self, visit):
        return visit.visit_name

    def to_python(self, visit_name):
        db_v = Visit.query.filter_by(visit_name=visit_name).first()
        if db_v is None:
            raise NotFound
        return db_v
