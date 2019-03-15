import json
import datetime
import logging
import requests

from flask import abort
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from zou.app.services import (
    contacts_service
)
from zou.app.utils import auth, permissions, csv_utils
from zou.app.services.exception import WrongDateFormatException

gunicorn_logger = logging.getLogger('gunicorn.error')

class UpdateSevDeskContacts(Resource):
    @jwt_required
    def post(self):
        data = self.get_arguments()
        url = 'https://my.sevdesk.de/api/v1/Contact?limit=1000&embed=parent%2CcommunicationWays%2Caddresses%2Caddresses.country%2Ccategory&depth=1&token=' + data['token']
        request = requests.get(url)
        request.encoding = 'utf-8'
        if request.status_code != 200:
            abort(404)
        response = request.json()

        for person in response['objects']:
            if person['surename'] != None:
                person_sevdesk_id = person['id']
                person_street = ""
                person_zip = ""
                person_city = ""
                person_address = ""
                person_company = ""
                person_mail = ""
                person_phone = ""
                person_mobile = ""
                person_role = ""

                role_dic = {'Kunde': 'client', 'Lieferant': 'supplier'}

                address_dic = person['addresses'][0]
                if address_dic['street'] != None:
                  person_street = address_dic['street']
                if address_dic['zip'] != None:
                  person_zip = address_dic['zip']
                if address_dic['city'] != None:
                  person_city = address_dic['city']
                person_address = "%s %s %s" % (person_street, person_zip, person_city)

                for comm in person['communicationWays']:
                    if comm['type'] == 'PHONE':
                        person_phone = comm['value']
                    elif comm['type'] == 'EMAIL':
                        person_mail = comm['value']
                    elif comm['type'] == 'MOBILE':
                        person_mobile = comm['value']

                if 'parent' in person:
                    person_company = person['parent']['name']

                if 'category' in person:
                    person_role = role_dic[person['category']['name']]

                person_exists = contacts_service.get_contact_by_sevdesk_id(person_sevdesk_id)

                if not person_exists:
                    new_person = contacts_service.create_contact(email=person_mail, first_name=person['surename'], last_name=person['familyname'], sevdesk_id=person_sevdesk_id)
                    contacts_service.update_contact(new_person['id'], {'phone': person_phone, 'address': person_address, 'company': person_company, 'mobile': person_mobile, 'role': person_role})

                else:
                    contacts_service.update_contact(person_exists['id'], {'phone': person_phone, 'address': person_address, 'company': person_company, 'mobile': person_mobile, 'role': person_role})

        return True, 201

    def get_arguments(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "token",
            help="The token is required",
            required=True
        )
        args = parser.parse_args()
        return args

class NewContactResource(Resource):
    """
    Create a new user in the database. Set "default" as password.
    User role can be set but only admins can create admin users.
    """

    @jwt_required
    def post(self):
        permissions.check_admin_permissions()
        data = self.get_arguments()
        contact = contacts_service.create_contact(
            data["email"],
            data["first_name"],
            data["last_name"],
            data["phone"],
            data["mobile"],
            data["company"],
            data["address"],
            role=data["role"]
        )
        return contact, 201

    def get_arguments(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "email",
            help="The email is required.",
            required=True
        )
        parser.add_argument(
            "first_name",
            help="The first name is required.",
            required=True
        )
        parser.add_argument(
            "last_name",
            help="The last name is required.",
            required=True
        )
        parser.add_argument("phone", default="")
        parser.add_argument("mobile", default="")
        parser.add_argument("company", default="")
        parser.add_argument("address", default="")
        parser.add_argument("role", default="client")
        args = parser.parse_args()
        return args
