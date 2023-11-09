from dependency_injector import containers, providers

from application.logger.services.logger_service import LoggerService
from domain.services.contract.abstract_logger_service import AbstractLoggerService
from domain.services.contract.abstract_path_service import AbstractPathService
from application.paths.services.path_service import PathService

class Services(containers.DeclarativeContainer):

    path_provider = providers.Singleton(AbstractPathService.register(PathService))

    logger_provider = providers.Singleton(AbstractLoggerService.register(LoggerService),path=path_provider)

class Application(containers.DeclarativeContainer):

    services = providers.Container(Services)

