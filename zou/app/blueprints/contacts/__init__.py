from flask import Blueprint
from zou.app.utils.api import configure_api_from_blueprint

from .resources import (
    NewContactResource,
    UpdateSevDeskContacts
)

routes = [
    ("/data/contacts/new", NewContactResource),
    ("/data/contacts/update-sevdesk", UpdateSevDeskContacts)
]

blueprint = Blueprint("contacts", "contacts")
api = configure_api_from_blueprint(blueprint, routes)
