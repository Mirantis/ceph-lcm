# -*- coding: utf-8 -*-
"""This module contains special property descriptors."""


import enum
import importlib


class Property:
    SENTINEL = object()


class ChoicesProperty(Property):

    def __init__(self, attr_name, choices):
        self.choices = choices
        self.attr_name = attr_name

    def __get__(self, instance, owner):
        value = getattr(instance, self.attr_name, self.SENTINEL)
        if value is self.SENTINEL:
            raise AttributeError()

        return value

    def __set__(self, instance, value):
        choices = self.choices
        if callable(choices) and type(choices) is not enum.EnumMeta:
            choices = choices()

        try:
            if value in choices:
                setattr(instance, self.attr_name, value)
                return
        except TypeError:
            pass

        raise ValueError("Unknown error")


class ModelProperty(Property):

    @classmethod
    def get_value_id(cls, value):
        if hasattr(value, "model_id"):
            return value.model_id
        if isinstance(value, dict):
            return value.get("_id", value.get("id"))
        if value is None:
            return None
        return str(value)

    @classmethod
    def get_model(cls, klass, model_id):
        return klass.find_by_model_id(model_id)

    def __init__(self, model_class_name, id_attribute):
        self.model_class_name = model_class_name
        self.id_attribute = id_attribute
        self.instance_attribute = id_attribute + "_instance"

    def __get__(self, instance, owner):
        value = instance.__dict__.get(self.instance_attribute, self.SENTINEL)
        if value is not self.SENTINEL:
            return value

        model_id = instance.__dict__.get(self.id_attribute)
        model = self.get_model(self.get_class(), model_id)
        instance.__dict__[self.instance_attribute] = model

        return model

    def __set__(self, instance, value):
        value_id = self.get_value_id(value)
        instance.__dict__[self.id_attribute] = value_id
        instance.__dict__[self.instance_attribute] = self.SENTINEL

    def get_class(self):
        module, obj_name = self.model_class_name.rsplit(".", 1)
        module = importlib.import_module(module)
        klass = getattr(module, obj_name)

        return klass


class ModelListProperty(ModelProperty):

    @classmethod
    def get_value_id(cls, value):
        return [super(ModelListProperty, cls).get_value_id(item)
                for item in value]

    @classmethod
    def get_model(cls, klass, model_id):
        query = {
            "model_id": {"$in": model_id},
            "is_latest": True
        }

        models = []
        for item in klass.list_raw(query):
            model = klass()
            model.update_from_db_document(item)
            models.append(model)

        return models
