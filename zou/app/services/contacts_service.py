import slugify
import datetime
import logging

from calendar import monthrange
from dateutil import relativedelta

from sqlalchemy.exc import StatementError

from flask_jwt_extended import get_jwt_identity

from zou.app.models.contact import Contact

from zou.app.utils import fields, events, cache

from zou.app.services.exception import (
    PersonNotFoundException
)

gunicorn_logger = logging.getLogger('gunicorn.error')

def clear_contact_cache():
    cache.cache.delete_memoized(get_contact)
    cache.cache.delete_memoized(get_contact_by_email)
    cache.cache.delete_memoized(get_contact_by_email_username)
    cache.cache.delete_memoized(get_contact_by_sevdesk_id)


def get_contacts():
    """
    Return all person stored in database.
    """
    return fields.serialize_models(Contact.query.all())


def get_contact_raw(contact_id):
    """
    Return given person as an active record.
    """
    if contact_id is None:
        raise PersonNotFoundException()

    try:
        contact = Contact.get(contact_id)
    except StatementError:
        raise PersonNotFoundException()

    if contact is None:
        raise PersonNotFoundException()
    return contact


@cache.memoize_function(120)
def get_contact(contact_id):
    """
    Return given person as a dictionary.
    """
    contact = get_contact_raw(contact_id)
    return contact.serialize()


@cache.memoize_function(120)
def get_contact_by_email_username(email):
    """
    Return person that matches given email as a dictionary.
    """
    username = email.split("@")[0]

    for contact in get_contacts():
        first_name = slugify.slugify(contact["first_name"])
        last_name = slugify.slugify(contact["last_name"])
        contact_username = "%s.%s" % (first_name, last_name)
        if contact_username == username:
            return contact

    raise PersonNotFoundException


def get_contact_by_email_raw(email):
    """
    Return person that matches given email as an active record.
    """
    contact = Contact.get_by(email=email)

    if contact is None:
        raise PersonNotFoundException()
    return contact


@cache.memoize_function(120)
def get_contact_by_email(email):
    """
    Return person that matches given email as a dictionary.
    """
    contact = get_contact_by_email_raw(email)
    return contact.serialize()


@cache.memoize_function(120)
def get_contact_by_sevdesk_id(sevdesk_id):
    try:
        contact = Contact.get_by(sevdesk_id=sevdesk_id)
    except StatementError:
        return False
    if contact is None:
        return False
    else:
        return contact.serialize()


def create_contact(
    email,
    first_name,
    last_name,
    phone="",
    mobile="",
    company="",
    address="",
    role="client",
    sevdesk_id=None
):
    """
    Create a new person entry in the database. No operation are performed on
    password, so encrypted password is expected.
    """
    if email is not None:
        email = email.strip()
    contact = Contact.create(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        mobile=mobile,
        company=company,
        address=address,
        role=role,
        sevdesk_id=sevdesk_id
    )
    events.emit("contact:new", {
        "contact_id": contact.id
    })
    clear_contact_cache()
    return contact.serialize()


def update_contact(contact_id, data):
    """
    Update person entry with data given in parameter.
    """
    contact = Contact.get(contact_id)
    if "email" in data and data["email"] is not None:
        data["email"] = data["email"].strip()
    contact.update(data)
    events.emit("contact:update", {
        "contact_id": contact_id
    })
    clear_contact_cache()
    return contact.serialize()


def delete_contact(contact_id):
    """
    Delete person entry from database.
    """
    contact = Contact.get(contact_id)
    contact_dict = contact.serialize()
    contact.delete()
    events.emit("contact:delete", {
        "contact_id": contact_id
    })
    clear_contact_cache()
    return contact_dict
