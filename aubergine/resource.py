"""Implementation of Resource suitable for use with the Falcon Framework."""
from aubergine.common import Loggable
from functools import partial
import logging




class ResourceBuilder:
    """Class for building Resource objects."""


    def __init__(self, extractor_builder):
        self.extractor_builder = extractor_builder

    def build_handler(self, handler_spec):
        pass

    def build_resource(self, path_spec):
        passg
