import logging
from abc import ABC, abstractmethod


class AbstractLoggerService(ABC):

    @abstractmethod
    def get_logger(self) -> logging: raise NotImplementedError
