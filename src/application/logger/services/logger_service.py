import logging
import os
import sys
from datetime import datetime

from application.logger.handlers.rotating_log_handler import RotatingLogHandler
from application.logger.formatters.logging_level_formatter import LoggingLevelFormatter
from domain.services.contract.abstract_logger_service import AbstractLoggerService
from domain.services.contract.abstract_path_service import AbstractPathService
from domain.models.paths import Paths


class LoggerService(AbstractLoggerService):
    """
            A class used to create and configure custom logger
            ...

            Attributes
            ----------
            _logger: logging
                Logger instance for custom logs
            _file_handler: logging.Handler
                File log handler
            _stream_handler: logging.Handler
                Console log handler

            Methods
            -------
            _create_file_handler() -> logging.Handler
                Creates a rotation log handler

            _create_stream_handler() -> logging.Handler
                Creates a console log handler

            _customize_uvicorn_logger() -> None
                Replace uvicorn logger with custom rotation and console handlers

            get_logger() -> logging
                Returns custom logger
    """

    def __init__(self,path: AbstractPathService):
        self.path: Paths = path.get_paths()
        # creating base logger
        self._logger = logging.getLogger("CV_API")
        self._logger.propagate = False
        self._logger.setLevel(logging.DEBUG)
        # creating handlers
        self._file_handler: logging.Handler = self._create_file_handler()
        self._stream_handler: logging.Handler = self._create_stream_handler()
        # adding handlers to logger
        self._logger.addHandler(self._file_handler)
        self._logger.addHandler(self._stream_handler)
        # adding handlers to uvicorn logger
        self._customize_uvicorn_logger()

    def _create_file_handler(self) -> logging.Handler:
        # Get the current working directory, which is typically the directory where your script is located.
        #current_directory = os.getcwd()

        # Access the root directory by navigating up the directory tree.
        #root_directory = os.path.abspath(os.path.join(current_directory, '..'))
        logs_directory=os.path.join(self.path.log_dir,"logs")
        # Setting log path
        date_str: str = datetime.now().strftime("%Y_%m_%d")
        log_dir: str = os.path.join(logs_directory,date_str)

        os.makedirs(log_dir,exist_ok=True)
        log_path: str = os.path.join(log_dir,"CV_API.log")
        # Create Custom Formatter
        file_message_format: LoggingLevelFormatter = LoggingLevelFormatter({
            logging.DEBUG: '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s',
            logging.INFO: '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            logging.WARN: '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            logging.ERROR: '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s'
        })
        # Create File Handler
        file_handler = RotatingLogHandler(log_path, when="d", interval=1, backupCount=10, maxBytes=10000000)
        file_handler.setFormatter(file_message_format)
        try:
            file_handler.setLevel(logging.getLevelName(os.environ.get('FILE_LOG_LEVEL')))
        except Exception:
            # Set level to INFO if env variable FILE_LOG_LEVEL is not found
            file_handler.setLevel(logging.DEBUG)
            logging.getLogger().warning("Environment FILE_LOG_LEVEL not found. File Handler Logger set to INFO")
        return file_handler

    def _create_stream_handler(self) -> logging.Handler:
        # Create Custom Formatter
        stream_message_format: LoggingLevelFormatter = LoggingLevelFormatter({
            logging.DEBUG: '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s',
            logging.INFO: '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            logging.WARN: '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            logging.ERROR: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        })
        # Create Console Handler
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(stream_message_format)
        try:
            stream_handler.setLevel(logging.getLevelName(os.environ.get('CONSOLE_LOG_LEVEL')))
        except Exception:
            # Set level to INFO if env variable CONSOLE_LOG_LEVEL is not found
            stream_handler.setLevel(logging.DEBUG)
            logging.getLogger().warning("Environment CONSOLE_LOG_LEVEL not found. Console Handler Logger set to INFO")
        return stream_handler

    def _customize_uvicorn_logger(self) -> None:

        # Adding our handlers to uvicorn logger
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.addHandler(self._file_handler)
        uvicorn_logger.addHandler(self._stream_handler)
        uvicorn_logger.removeHandler(uvicorn_logger.handlers[0])  


    def get_logger(self) -> logging:
        return self._logger
