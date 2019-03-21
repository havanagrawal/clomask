"""Defines the interface that all Model implementations need to adhere to

This allows us to swap out model implementations easily
"""
from abc import ABC, abstractmethod

class Model(ABC):
    def __init__(self, name=None, *args, **kwargs):
        self.name = name
        super().__init__()

    @abstractmethod
    def load(self, filepath=None):
        pass

    @abstractmethod
    def create_mask(self, filepath, output_dir):
        """Create an object mask for the input image

        Arguments
        ---------
        filepath: str
            A relative/absolute filepath to the image

        output_dir: str
            The directory to which the result should be persisted

        Return
        -------
        The filepath of the output masked image
        or the directory with a specific structure (TODO)
        """
        pass
