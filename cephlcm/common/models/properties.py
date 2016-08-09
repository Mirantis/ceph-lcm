# -*- coding: utf-8 -*-
"""This module contains special property descriptors."""


import importlib


class ModelProperty:

    SENTINEL = object()

    def __init__(self, model_class_name, id_attribute):
        self.model_class_name = model_class_name
        self.id_attribute = id_attribute
        self.instance_attribute = id_attribute + "_instance"

    def __get__(self, instance, owner):
        value = instance.__dict__.get(self.instance_attribute, self.SENTINEL)
        if value is not self.SENTINEL:
            return value

        model_class = self.get_class()
        model_id = instance.__dict__.get(self.id_attribute)
        model = model_class.find_by_model_id(model_id)
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

    def get_value_id(self, value):
        if hasattr(value, "model_id"):
            return value.model_id
        if isinstance(value, dict):
            return value.get("_id", value.get("id"))
        if value is None:
            return None
        return str(value)
