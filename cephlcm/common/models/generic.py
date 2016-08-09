# -*- coding: utf-8 -*-
"""This module contains a generic model.

Basically, all stuff, related to the database is expressed in models.
Model is an abstraction for the row in RDBS or documents in some NoSQL
solutions. They are providers between API responses (JSON ones) and DB
internal presentation.

DB and API presentations are different: as a rule, DB presentation is
a bit richer because it stores some additional information which is
not required for the API users (or even it should be hidden, like any
password related informaton).

Every model has a set of fields which are common for any model:
  - `id` is an ID of the **certain** model version.
  - `model_id` is an ID of the model (common for all versions).
  - `version` is the monotonic sequence for the version models.
  - `time_created` is the UNIX timestamp when **version** of the
     model was created.
  - `time_deleted` is the UNIX timestamp when **model** was deleted.
    Basically, only latest version has this field not 0.
  - `initiator_id` - ID of User who initiated creation of this version.
  - `data` is a model specific data.

These are API fields. DB has those fields and some additional
information as well.
"""


import abc
import copy
import uuid

import bson.objectid
import pymongo
import pymongo.errors

from cephlcm.common import exceptions
from cephlcm.common import log
from cephlcm.common import timeutils
from cephlcm.common import wrappers


MODEL_DB_STRUCTURE = {
    "_id": None,  # Unique ID of the instance. Usually MongoDB ObjectID
    "model_id": None,  # ID of the model set. Usually UUID4
    "version": 0,  # Version number of the model within a model set
    "time_created": 0,  # UNIX timestamp of the time when model was created
    "time_deleted": 0,  # UNIX timestamp of the time when model was deleted
    "initiator_id": None,  # User ID of the used who created this model
    "is_latest": True  # A sign that the model is the latest in the model list
}
"""The set of common fields for the structure of model in DB."""

MODEL_API_STRUCTURE = {
    "data": {},
    "model": "",
    "id": "",
    "version": "",
    "time_updated": 0,
    "time_deleted": 0,
    "initiator_id": None
}
"""The set of common fields for the API response.

Basically, it is JSON boilerplate.
"""

SORT_ASC = pymongo.ASCENDING
SORT_DESC = pymongo.DESCENDING

LOG = log.getLogger(__name__)
"""Logger."""


class Base:

    COLLECTION_NAME = None
    """The name of the collection where model documents are stored."""

    CONNECTION = None
    """The connection to the MongoDB."""

    @classmethod
    def database(cls):
        """This method returns a connection to the MongoDB database."""

        return cls.CONNECTION.db

    @classmethod
    def collection(cls):
        """This method returns a connection to the collection."""

        return cls.database()[cls.COLLECTION_NAME]

    @classmethod
    def ensure_index(cls):
        pass


class Model(Base, metaclass=abc.ABCMeta):
    """A common class for the model.

    All models, which are working with DB, should be subclasses.
    """

    MODEL_NAME = None
    """The name of the model."""

    DEFAULT_SORT_BY = [("id", SORT_ASC)]

    @classmethod
    def find_by_model_id(cls, item_id):
        """Returns a latest not deleted model version for the model."""

        if not item_id:
            return None

        query = {"model_id": item_id, "is_latest": True}
        document = cls.collection().find_one(query)
        if not document:
            return None

        model = cls()
        model.update_from_db_document(document)

        return model

    @classmethod
    def find_by_id(cls, item_id):
        """Returns a model by the given **version** ID."""

        if not item_id:
            return None

        item_id = bson.objectid.ObjectId(item_id)
        document = cls.collection().find_one({"_id": item_id})
        if not document:
            return None

        model = cls()
        model.update_from_db_document(document)

        return model

    @classmethod
    def list_raw(cls, query, filter_fields=None, sort_by=None):
        assert query

        cursor = cls.collection().find(query, filter_fields)
        if sort_by is not None:
            cursor = cursor.sort(sort_by)

        return cursor

    @classmethod
    def list_paginated(cls, query, pagination,
                       filter_fields=None, sort_by=None):
        cursor = cls.list_raw(query, filter_fields, sort_by)
        total = cursor.count()

        page_items_before = pagination["per_page"] * (pagination["page"] - 1)
        if page_items_before:
            cursor = cursor.skip(page_items_before)
        cursor = cursor.limit(pagination["per_page"])

        paginated_result = wrappers.PaginationResult(
            cls, cursor, pagination, total
        )

        return paginated_result

    @classmethod
    def list_models(cls, pagination):
        query = {"time_deleted": 0, "is_latest": True}
        query.update(pagination["filter"])

        if pagination["sort_by"]:
            sort_by = pagination["sort_by"]
        else:
            sort_by = cls.DEFAULT_SORT_BY

        result = cls.list_paginated(query, pagination, sort_by=sort_by)

        return result

    @classmethod
    def list_versions(cls, item_id, pagination):
        query = {"model_id": item_id}
        sort_by = [("version", SORT_DESC)]
        result = cls.list_paginated(query, pagination, sort_by=sort_by)

        return result

    @classmethod
    def find_version(cls, model_id, version):
        """Returns a specific version of model."""

        query = {"model_id": model_id, "version": version}
        document = cls.collection().find_one(query)

        if not document:
            return None

        model = cls()
        model.update_from_db_document(document)

        return model

    def __init__(self):
        self.initiator_id = None
        self.model_id = None
        self.time_created = 0
        self.time_deleted = 0
        self.version = 0
        self._id = None

    def get_initiator(self):
        """This method returns a model of initiator."""

        # It looks like a dirty hack but I refer specific model
        # from the generic one.
        #
        # It is an isolated controlled hack. If no initiator model is
        # required, then remove it.
        from cephlcm.common.models import user

        return user.UserModel.find_by_model_id(self.initiator_id)

    def save(self, structure=None):
        """This method dumps model data to the database.

        Important here is that new version will be created on saving.
        So it is OK to update a field and save, new version will be
        created.

        Since model data is immutable in some sense, this is a reason
        why we do not have `update` method here.
        """

        self.check_constraints()

        if not structure:
            structure = self.make_db_document_structure()

        structure["version"] = self.version + 1
        if structure["model_id"] is None:
            structure["model_id"] = self.model_id or str(uuid.uuid4())
        structure["is_latest"] = True
        structure["time_created"] = timeutils.current_unix_timestamp()

        result = self.insert_document(structure)
        self.update_from_db_document(structure)
        self.collection().update_many(
            {
                "model_id": self.model_id,
                "_id": {"$ne": self._id},
                "is_latest": True
            },
            {"$set": {"is_latest": False}}
        )

        return result

    def delete(self):
        """This method marks model as deleted."""

        structure = self.make_db_document_structure()
        structure["time_deleted"] = timeutils.current_unix_timestamp()

        result = self.save(structure)

        return result

    def insert_document(self, db_document):
        """Inserts DB structure into the MongoDB."""

        try:
            return self.collection().insert(db_document)
        except pymongo.errors.DuplicateKeyError as exc:
            raise exceptions.UniqueConstraintViolationError() from exc

    def update_from_db_document(self, db_document):
        """Updates model fields with document from database.

        Basically, if you create a document, you build an empty
        instance, fetch DB and use this method.

        This separation is done intentionally to simplify testing.
        """

        self.initiator_id = db_document["initiator_id"]
        self.time_created = db_document["time_created"]
        self.time_deleted = db_document["time_deleted"]
        self.version = db_document["version"]
        self.model_id = db_document["model_id"]
        self._id = db_document["_id"]

    def make_db_document_structure(self):
        """Makes a structure for database from the model."""

        structure = copy.deepcopy(MODEL_DB_STRUCTURE)
        structure["_id"] = bson.objectid.ObjectId()

        structure.update(self.make_db_document_specific_fields())

        return structure

    @abc.abstractmethod
    def make_db_document_specific_fields(self):
        """This build a fieldset, specific to the certain model."""

        raise NotImplementedError

    def make_api_structure(self, *args, **kwargs):
        """This method build a structure, suitable for API."""

        structure = copy.deepcopy(MODEL_API_STRUCTURE)

        structure["version"] = self.version
        structure["id"] = str(self.model_id)
        structure["model"] = self.MODEL_NAME
        structure["time_updated"] = self.time_created
        structure["time_deleted"] = self.time_deleted
        structure["initiator_id"] = self.initiator_id
        structure["data"] = self.make_api_specific_fields(*args, **kwargs)

        return structure

    @abc.abstractmethod
    def make_api_specific_fields(self):
        """This builds a set of fields, specific for API response."""

        raise NotImplementedError

    def check_constraints(self):
        if self.time_deleted:
            raise exceptions.CannotUpdateDeletedModel()

    @classmethod
    def ensure_index(cls):
        # super().ensure_index()
        super(Model, cls).ensure_index()

        if not cls.COLLECTION_NAME:
            return

        collection = cls.collection()
        collection.create_index(
            [
                ("is_latest", pymongo.DESCENDING)
            ],
            name="index_latest",
            partialFilterExpression={"is_latest": True}
        )
        collection.create_index(
            [
                ("model_id", pymongo.ASCENDING),
                ("version", pymongo.ASCENDING)
            ],
            name="index_unique_version",
            unique=True
        )


def configure_models(connection):
    """This configures models to use database.

    Basically, all configuration of DB connection is done externally,
    models are configured with DB client only.
    """

    Base.CONNECTION = connection


def ensure_indexes(root=Base):
    for mdl in root.__subclasses__():
        mdl.ensure_index()
        ensure_indexes(mdl)
