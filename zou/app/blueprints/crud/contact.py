from flask import abort

from zou.app.models.contact import Contact
from zou.app.services import contacts_service
from zou.app.utils import permissions

from .base import (
    BaseModelsResource,
    BaseModelResource
)


class ContactsResource(BaseModelsResource):

    def __init__(self):
        BaseModelsResource.__init__(self, Contact)

    def all_entries(self, query=None):
        if query is None:
            query = self.model.query

        return [person.serialize_safe() for person in query.all()]

    def post(self):
        abort(405)

    def check_read_permissions(self):
        return True


class ContactResource(BaseModelResource):

    def __init__(self):
        BaseModelResource.__init__(self, Contact)

    def check_read_permissions(self, instance):
        return True

    def check_update_permissions(self, instance, data):
        self.check_escalation_permissions(instance, data)

    def check_delete_permissions(self, instance):
        self.check_escalation_permissions(instance)

    def check_escalation_permissions(self, instance, data=None):
        if permissions.admin_permission.can():
            return True
        else:
            raise permissions.PermissionDenied

    def serialize_instance(self, instance):
        if permissions.has_manager_permissions():
            return instance.serialize_safe()
        else:
            return instance.serialize_without_info()

    def post_update(self, instance_dict):
        contacts_service.clear_contact_cache()
        return instance_dict

    def pre_delete(self, instance_dict):
        return instance_dict

    def post_delete(self, instance_dict):
        contacts_service.clear_contact_cache()
        return instance_dict

    def update_data(self, data, instance_id):
        return data
