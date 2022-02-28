import json

from flask import request, Response, url_for
from flask_restful import Resource

from sqlalchemy.exc import IntegrityError

from jsonschema import validate, ValidationError

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound

from mokkigo import db
from mokkigo.models import Participant
from mokkigo.constants import JSON


class ParticipantCollection(Resource):
    def get(self):
        """
        GET for ParticipantCollection
        OpenAPI description below:
        ---
        description: Get the list of participants
        responses:
          '200':
            description: List of participants
            content:
              application/json:
                example:
                - name: John Doe
                  allergies: Carrots
                - name: Jane Doe

        """
        body = {"items": []}
        for db_p in Participant.query.all():
            p = db_p.serialize()
            body["items"].append(p)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self):
        """
        POST for ParticipantCollection
        OpenAPI description below:
        ---
        description: create new participant
        requestBody:
          description: JSON document that contains data for a new participant
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Participant'
              example:
                name: Jane Doe
                allergies: Carrots
        responses:
          '201':
            description: Participant was created successfully
            headers:
              Location:
                description: URI of the new participant
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
                Participant.json_schema()
            )
        except ValidationError as e:
            return Response(400, "Invalid JSON document", str(e))

        p = Participant(
            name=request.json["name"],
            allergies=request.json.get("allergies")
        )

        href = url_for("api.participantitem", participant=p)

        try:
            db.session.add(p)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Participant '{}' already exists".format(p.name), 409

        return Response(status=201, headers={"Location": href})


class ParticipantItem(Resource):
    def get(self, participant):
        """
        GET method for ParticipantItem
        OpenAPI description below:
        ---
        description: Get details of one participant
        responses:
          '200':
            description: Data of the single participant
            content:
              application/json:
                examples:
                  name: "Jane Doe"
          '404':
            description: The participant was not found
        """
        body = participant.serialize()
        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, participant):
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
            validate(request.json, Participant.json_schema())
        except ValidationError as e:
            return Response(400, "Invalid JSON document", str(e))

        participant.deserialize(request.json)
        try:
            db.session.add(participant)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Participant '{}' already exists".format(
                    participant.name), 409

    def delete(self, participant):
        """
        DELETE method for ParticipantItem
        OpenAPI description below:
        ---
        description: Delete selected participant
        responses:
          '204':
            description: Participant deleted successfully
          '404':
            description: Participant not found
        """
        db.session.delete(participant)
        db.session.commit()
        return Response(status=204)


class ParticipantConverter(BaseConverter):
    def to_url(self, participant):
        return participant.name

    def to_python(self, participant_name):
        db_p = Participant.query.filter_by(name=participant_name).first()
        if db_p is None:
            raise NotFound
        return db_p
