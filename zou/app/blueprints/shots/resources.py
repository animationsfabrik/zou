from flask import request, abort
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from zou.app.models.entity import Entity

from zou.app.services import (
    shots_service,
    tasks_service,
    projects_service
)
from zou.app.utils import query

from zou.app.services.exception import (
    EpisodeNotFoundException,
    SequenceNotFoundException,
    ShotNotFoundException,
    ProjectNotFoundException
)


class ShotResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, instance_id):
        """
        Retrieve given shot.
        """
        try:
            shot = shots_service.get_shot(instance_id)
        except ShotNotFoundException:
            abort(404)
        return shot.serialize(obj_type="Shot")


class ShotsResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self):
        """
        Retrieve all shot entries. Filters can be specified in the query string.
        """
        criterions = query.get_query_criterions_from_request(request)
        return shots_service.get_shots(criterions)


class ShotAssetsResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, instance_id):
        """
        Retrieve all assets for a given shot.
        """
        try:
            shot = shots_service.get_shot(instance_id)
        except ShotNotFoundException:
            abort(404)

        return Entity.serialize_list(shot.entities_out, obj_type="Asset")


class ShotTaskTypesResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, shot_id):
        """
        Retrieve all task types related to a given shot.
        """
        try:
            shot = shots_service.get_shot(shot_id)
            task_types = tasks_service.get_task_types_for_shot(shot)
        except ShotNotFoundException:
            abort(404)

        return task_types


class ShotTasksResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, instance_id):
        """
        Retrieve all tasks related to a given shot.
        """
        try:
            return tasks_service.get_task_dicts_for_shot(instance_id)
        except ShotNotFoundException:
            abort(404)


class ShotsAndTasksResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self):
        """
        Retrieve all shots, adds project name and asset type name and all
        related tasks.
        """
        criterions = query.get_query_criterions_from_request(request)
        return shots_service.get_shots_and_tasks(criterions)


class ProjectShotsResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, project_id):
        """
        Retrieve all shots related to a given project.
        """
        try:
            project = projects_service.get_project(project_id)
            return Entity.serialize_list(
                shots_service.get_shots_for_project(project),
                obj_type="Shot"
            )
        except ProjectNotFoundException:
            abort(404)


class ProjectSequencesResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, project_id):
        """
        Retrieve all sequences related to a given project.
        """
        try:
            project = projects_service.get_project(project_id)
            return Entity.serialize_list(
                shots_service.get_sequences_for_project(project),
                obj_type="Sequence"
            )
        except ProjectNotFoundException:
            abort(404)


class ProjectEpisodesResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, project_id):
        """
        Retrieve all episodes related to a given project.
        """
        try:
            project = projects_service.get_project(project_id)
            return Entity.serialize_list(
                shots_service.get_episodes_for_project(project),
                obj_type="Episode"
            )
        except ProjectNotFoundException:
            abort(404)


class EpisodeResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, instance_id):
        """
        Retrieve given episode.
        """
        try:
            episode = shots_service.get_episode(instance_id)
        except EpisodeNotFoundException:
            abort(404)
        return episode.serialize(obj_type="Episode")


class EpisodesResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self):
        """
        Retrieve all episode entries. Filters can be specified in the query
        string.
        """
        criterions = query.get_query_criterions_from_request(request)
        episodes = shots_service.get_episodes(criterions)
        return Entity.serialize_list(episodes, obj_type="Episode")


class EpisodeSequencesResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, instance_id):
        """
        Retrieve all sequence entries for a given episode.
        Filters can be specified in the query string.
        """
        criterions = query.get_query_criterions_from_request(request)
        criterions["parent_id"] = instance_id
        sequences = shots_service.get_sequences(criterions)
        return Entity.serialize_list(sequences, obj_type="Sequence")


class SequenceResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, instance_id):
        """
        Retrieve given sequence.
        """
        try:
            sequence = shots_service.get_sequence(instance_id)
        except SequenceNotFoundException:
            abort(404)
        return sequence.serialize(obj_type="Sequence")


class SequencesResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self):
        """
        Retrieve all sequence entries. Filters can be specified in the query
        string.
        """
        criterions = query.get_query_criterions_from_request(request)
        sequences = shots_service.get_sequences(criterions)
        return Entity.serialize_list(sequences, obj_type="Sequence")


class SequenceShotsResource(Resource):

    def __init__(self):
        Resource.__init__(self)

    @jwt_required
    def get(self, instance_id):
        """
        Retrieve all shot entries for a given sequence.
        Filters can be specified in the query string.
        """
        criterions = query.get_query_criterions_from_request(request)
        criterions["parent_id"] = instance_id
        return shots_service.get_shots(criterions)
