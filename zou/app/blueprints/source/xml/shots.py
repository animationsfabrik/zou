import os
import uuid
import logging

import xml.etree.ElementTree as ET

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from zou.app import app
from zou.app.utils import permissions
from zou.app.services import user_service
from zou.app.services import shots_service
from zou.app.models.entity import Entity

from sqlalchemy.exc import IntegrityError

gunicorn_logger = logging.getLogger('gunicorn.error')

class ShotsXmlImportResource(Resource):
    def __init__(self):
        Resource.__init__(self)

    def prepare_import(self):
        self.episodes = {}
        self.sequences = {}

    @jwt_required
    def post(self, project_id):
        uploaded_file = request.files["file"]
        file_name = "%s.xml" % uuid.uuid4()
        file_path = os.path.join(app.config["TMP_DIR"], file_name)
        uploaded_file.save(file_path)

        try:
           result = self.run_import(file_path, project_id)
           return result, 201
        except Exception as e:
           gunicorn_logger.log(logging.ERROR, e)
           return { "error": True, "message": e}, 400

    def run_import(self, file_path, project_id):
        result = []
        self.check_permissions()
        self.prepare_import()
        xml_file = ET.parse(file_path)
        root = xml_file.getroot()
        sequence = xml_file.find('sequence').find('name').text
        episode = shots_service.get_or_create_first_episode(project_id)
        self.sequences[sequence] = shots_service.get_or_create_sequence(project_id, episode['id'], sequence)

        sequence_id = self.get_id_from_cache(self.sequences, sequence)
        shot_type = shots_service.get_shot_type()
        clips = root.iter('clipitem')
        for clip in clips:
           try:
               entity = Entity.create(
                   name=clip.find('name').text,
                   project_id=project_id,
                   parent_id=sequence_id,
                   entity_type_id=shot_type["id"],
                   nb_frames=clip.find('duration').text
               )
           except IntegrityError:
                entity = Entity.get_by(
                    name=clip.find('name').text,
                    project_id=project_id,
                    parent_id=sequence_id,
                    entity_type_id=shot_type["id"]
                )
           result.append(entity.serialize())

        return result

    def add_to_cache_if_absent(self, cache, retrieve_function, name):
        if name not in cache:
            cache[name] = retrieve_function(name)
        return cache[name]

    def get_id_from_cache(self, cache, name):
        cached_object = cache[name]
        if type(cached_object) is dict:
            return cached_object["id"]
        else:
            return cached_object.id

    def check_permissions(self):
        return permissions.check_manager_permissions()
