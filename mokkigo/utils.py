# Taken from the course material
# https://lovelace.oulu.fi/file-download/embedded/ohjelmoitava-web/ohjelmoitava-web/pwp-masonbuilder-py/
import json

from flask import url_for, request, Response

from mokkigo.models import Visit, Mokki, Participant, Item
from mokkigo.constants import ERROR_PROFILE, MASON


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class MokkigoBuilder(MasonBuilder):
    def add_control_add_visit(self):
        self.add_control(
                "mokkigo:add-visit",
                href=url_for("api.visitcollection"),
                method="POST",
                encoding="json",
                title="Add a new visit",
                schema=Visit.json_schema()
        )

    def add_control_delete_visit(self, visit):
        self.add_control(
                "mokkigo:delete-visit",
                href=url_for("api.visititem", visit=visit),
                method="DELETE",
                title="Delete this visit",
                schema=Visit.json_schema()
        )

    def add_control_edit_visit(self, visit):
        self.add_control(
                "mokkigo:edit-visit",
                href=url_for("api.visititem", visit=visit),
                method="PUT",
                encoding="json",
                title="Edit this visit",
                schema=Visit.json_schema()
        )

    def add_control_add_mokki(self):
        self.add_control(
                "mokkigo:add-mokki",
                href=url_for("api.mokkicollection"),
                method="POST",
                encoding="json",
                title="Add a new mokki",
                schema=Mokki.json_schema()
        )

    def add_control_delete_mokki(self, mokki):
        self.add_control(
                "mokkigo:delete-mokki",
                href=url_for("api.mokkiitem", mokki=mokki),
                method="DELETE",
                title="Delete this mokki",
                schema=Mokki.json_schema()
        )

    def add_control_edit_mokki(self, mokki):
        self.add_control(
                "mokkigo:edit-mokki",
                href=url_for("api.mokkiitem", mokki=mokki),
                method="PUT",
                encoding="json",
                title="Edit this mokki",
                schema=Mokki.json_schema()
        )

    def add_control_add_participant(self):
        self.add_control(
                "mokkigo:add-participant",
                href=url_for("api.participantcollection"),
                method="POST",
                encoding="json",
                title="Add a new participant",
                schema=Participant.json_schema()
        )

    def add_control_delete_participant(self, participant):
        self.add_control(
                "mokkigo:delete-participant",
                href=url_for("api.participantitem", participant=participant),
                method="DELETE",
                title="Delete this participant",
                schema=Participant.json_schema()
        )

    def add_control_edit_participant(self, participant):
        self.add_control(
                "mokkigo:editgparticipant",
                href=url_for("api.participantitem", participant=participant),
                method="PUT",
                encoding="json",
                title="Edit this participant",
                schema=Participant.json_schema()
        )

    def add_control_add_item(self, mokki):
        self.add_control(
                "mokkigo:add-item",
                href=url_for("api.itemcollection", mokki=mokki),
                method="POST",
                encoding="json",
                title="Add a new item",
                schema=Item.json_schema()
        )

    def add_control_delete_item(self, item):
        self.add_control(
                "mokkigo:delete-item",
                href=url_for("api.itemitem", item=item),
                method="DELETE",
                title="Delete this item",
                schema=Item.json_schema()
        )

    def add_control_edit_item(self, item):
        self.add_control(
                "mokkigo:edit-item",
                href=url_for("api.itemitem", item=item),
                method="PUT",
                encoding="json",
                title="Edit this item",
                schema=Item.json_schema()
        )


def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
