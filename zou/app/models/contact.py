import sys

from zou.app import db
from zou.app.models.serializer import SerializerMixin
from zou.app.models.base import BaseMixin

from sqlalchemy_utils import UUIDType, EmailType, LocaleType, TimezoneType
from sqlalchemy.dialects.postgresql import JSONB

from pytz import timezone as pytz_timezone
from babel import Locale


#department_link = db.Table(
#    "department_link",
#    db.Column(
#        "person_id",
#        UUIDType(binary=False),
#        db.ForeignKey("person.id")
#    ),
#    db.Column(
#        "department_id",
#        UUIDType(binary=False),
#        db.ForeignKey("department.id")
#    )
#)


class Contact(db.Model, BaseMixin, SerializerMixin):
    """
    Describe a member of the studio (and an API user).
    """
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(EmailType, unique=True)
    phone = db.Column(db.String(30))
    mobile = db.Column(db.String(30))
    company = db.Column(db.String(80))
    address = db.Column(db.String(80))

    sevdesk_id = db.Column(db.Integer, unique=True)

    data = db.Column(JSONB)
    role = db.Column(db.String(30), default="Kunde")

    def __repr__(self):
        if sys.version_info[0] < 3:
            return "<Contact %s>" % self.full_name().encode("utf-8")
        else:
            return "<Contact %s>" % self.full_name()

    def full_name(self):
        return "%s %s" % (
            self.first_name,
            self.last_name
        )

    def serialize(self, obj_type="Contact"):
        data = SerializerMixin.serialize(self, "Contact")
        data["full_name"] = self.full_name()
        return data

    def serialize_safe(self):
        data = SerializerMixin.serialize(self, "Contact")
        data["full_name"] = self.full_name()
        return data

    def serialize_without_info(self):
        data = self.serialize_safe()
        del data["phone"]
        del data["email"]
        return data
