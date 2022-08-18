import json

from flask import request, Response, url_for
from flask_restful import Resource

from sqlalchemy.exc import IntegrityError

from jsonschema import validate, ValidationError

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound

from mokkigo import db
from mokkigo.models import Participant
from mokkigo.constants import (JSON, MASON, LINK_RELATIONS_URL,
                               PARTICIPANT_PROFILE)
from mokkigo.utils import create_error_response, MokkigoBuilder


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
        participants = Participant.query.all()
        if not participants:
            return create_error_response(
                title="Not found",
                status_code=404,
                message="Database is empty"
            )

        body = MokkigoBuilder(items=[])
        body.add_namespace("mokkigo", LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.participantcollection"))
        body.add_control_add_participant()

        for participant in participants:
            p = MokkigoBuilder(
                name=participant.name,
                allergies=participant.allergies,
            )

            p.add_control("self", url_for("api.participantitem",
                                          participant=participant))
            p.add_control("profile", PARTICIPANT_PROFILE)
            body["items"].append(p)

        return Response(json.dumps(body), 200, mimetype=MASON)

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
        if request.mimetype != JSON:
            return create_error_response(
                    status_code=415,
                    title="Unsupported Media Type",
                    message="Content type must be JSON"
            )

        try:
            validate(request.json, Participant.json_schema())

        except ValidationError as e:
            return create_error_response(
                    status_code=400,
                    title="Invalid JSON document",
                    message=str(e)
            )

        p = Participant(
            name=request.json["name"],
            allergies=request.json.get("allergies")
        )

        # names = request.json["visits"]
        # for name in names:
        #     visit = Visit.query.filter_by(visit_name=name).first()
        #     if visit is None:
        #         return create_error_response(
        #             status_code=404,
        #             title="Not found",
        #             message="No visit with name {} found".format(name)
        #         )

        #     p.visits.append(visit)

        href = url_for("api.participantitem", participant=p)

        try:
            db.session.add(p)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return create_error_response(
                    status_code=409,
                    title="Participant already exists"
            )

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
        p = Participant.query.filter_by(name=participant.name).first()

        body = MokkigoBuilder(
                name=p.name,
                allergies=p.allergies,
        )

        body.add_namespace("mokkigo", LINK_RELATIONS_URL)

        body.add_control("self", url_for("api.participantitem", participant=p))
        body.add_control("profile", PARTICIPANT_PROFILE)
        body.add_control("collection", url_for("api.participantcollection"))

        body.add_control_delete_participant(participant=p)
        body.add_control_edit_participant(participant=p)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, participant):
        """
        PUT method for ParticipantItem
        OpenAPI description below:
        ---
        description: Edit one participant
        requestBody:
          description: JSON document that contains new data for participant
          content:
            application/json: schema:
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
        if request.mimetype != JSON:
            return create_error_response(
                    status_code=415,
                    title="Content type error",
                    message="Content type must be JSON"
            )

        try:
            validate(request.json, Participant.json_schema())
        except ValidationError as e:
            return create_error_response(
                    status_code=400,
                    title="Invalid JSON document",
                    message=str(e)
            )

        participant.deserialize(request.json)
        try:
            db.session.add(participant)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return create_error_response(
                    status_code=409,
                    title="Participant already exists"
            )

        href = url_for("api.participantitem", participant=participant)
        return Response(status=204, headers={"Location": href})

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
