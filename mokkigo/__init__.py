import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from

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
    """
    app.config["SWAGGER"] = {
            "title": "MokkiGo",
            "openapi": "3.0.3",
            "uiversion": 3,
    }
    swagger = Swagger(app, template_file="doc/mokkigo.yml")
    """

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

    return app
