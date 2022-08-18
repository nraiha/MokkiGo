# Some of the code taken from
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/flask-api-project-layout/
import os
import json

from flask import Flask, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

from mokkigo.constants import LINK_RELATIONS_URL, MASON

db = SQLAlchemy()


# Based on
# http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    app = Flask(__name__,
                instance_relative_config=True,
                static_folder="static")
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path,
                                                            "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    app.config["SWAGGER"] = {
            "title": "MokkiGo",
            "openapi": "3.0.3",
            "uiversion": 3,
    }
    Swagger(app, template_file="doc/mokkigo.yml")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from mokkigo.resources.item import ItemConverter
    from mokkigo.resources.visit import VisitConverter
    from mokkigo.resources.mokki import MokkiConverter
    from mokkigo.resources.participant import ParticipantConverter

    app.url_map.converters["item"] = ItemConverter
    app.url_map.converters["mokki"] = MokkiConverter
    app.url_map.converters["visit"] = VisitConverter
    app.url_map.converters["participant"] = ParticipantConverter

    from . import api
    app.register_blueprint(api.api_bp)

    from . import models
    app.cli.add_command(models.init_db_command)

    @app.route("/profiles/<profile>/")
    def send_profile(profile):
        # TODO: meaningful function
        return "Request profile {}".format(profile)

    @app.route(LINK_RELATIONS_URL)
    def send_link_relations():
        return "link relations"

    @app.route("/api/")
    def index():
        from mokkigo.utils import MasonBuilder
        body = MasonBuilder()
        body.add_namespace("mokkigo", LINK_RELATIONS_URL)
        body.add_control("mokkigo:participants-all",
                         url_for("api.participantcollection"))
        body.add_control("mokkigo:visits-all",
                         url_for("api.visitcollection"))
        body.add_control("mokkigo:mokkis-all",
                         url_for("api.mokkicollection"))
        body.add_control("mokkigo:items-all",
                         url_for("api.itemcollection"))

        return Response(json.dumps(body), status=200, mimetype=MASON)

    return app
