from injector import Binder, Injector, Module, singleton
from sqlalchemy import Engine

from src.configuration.logging import Logger
from src.configuration.settings import Settings
from src.domain.repositories.bottles_repository import BottleRepository
from src.domain.repositories.placements_repository import PlacementRepository
from src.domain.repositories.shelves_repository import ShelfRepository
from src.domain.repositories.tag_categories_repository import TagCategoryRepository
from src.domain.repositories.tags_repository import TagRepository
from src.domain.services.bottles_service import BottlesService
from src.domain.services.placements_service import PlacementsService
from src.domain.services.shelves_service import ShelvesService
from src.domain.services.tag_categories_service import TagCategoriesService
from src.domain.services.tags_service import TagsService
from src.infrastructure.dao.base_dao import BaseDAO
from src.infrastructure.database import build_engine
from src.infrastructure.mappers.bottle_details_entity_mapper import BottleDetailsEntityMapper
from src.infrastructure.mappers.bottle_entity_mapper import BottleEntityMapper
from src.infrastructure.mappers.placement_entity_mapper import PlacementEntityMapper
from src.infrastructure.mappers.shelf_entity_mapper import ShelfEntityMapper
from src.infrastructure.mappers.tag_category_entity_mapper import TagCategoryEntityMapper
from src.infrastructure.mappers.tag_entity_mapper import TagEntityMapper
from src.infrastructure.repositories.bottles_repository_impl import BottleRepositoryImpl
from src.infrastructure.repositories.placements_repository_impl import PlacementRepositoryImpl
from src.infrastructure.repositories.shelves_repository_impl import ShelfRepositoryImpl
from src.infrastructure.repositories.tag_categories_repository_impl import TagCategoryRepositoryImpl
from src.infrastructure.repositories.tags_repository_impl import TagRepositoryImpl

logger = Logger(child=True)


class ConfigurationModule(Module):
    def configure(self, binder: Binder) -> None:
        # Partie Settings
        settings = Settings()
        binder.bind(Settings, to=settings, scope=singleton)

        # Partie Infra
        ## Base de données
        engine = build_engine(settings)
        binder.bind(Engine, to=engine, scope=singleton)

        ## DAOs
        binder.bind(BaseDAO, scope=singleton)

        ## Mappers
        binder.bind(BottleEntityMapper, scope=singleton)
        binder.bind(ShelfEntityMapper, scope=singleton)
        binder.bind(TagCategoryEntityMapper, scope=singleton)
        binder.bind(TagEntityMapper, scope=singleton)
        binder.bind(PlacementEntityMapper, scope=singleton)
        binder.bind(BottleDetailsEntityMapper, scope=singleton)

        ## Repositories
        binder.bind(ShelfRepository, to=ShelfRepositoryImpl, scope=singleton)
        binder.bind(TagCategoryRepository, to=TagCategoryRepositoryImpl, scope=singleton)
        binder.bind(TagRepository, to=TagRepositoryImpl, scope=singleton)
        binder.bind(BottleRepository, to=BottleRepositoryImpl, scope=singleton)
        binder.bind(PlacementRepository, to=PlacementRepositoryImpl, scope=singleton)

        # Partie Domain
        ## Services
        binder.bind(ShelvesService, scope=singleton)
        binder.bind(TagCategoriesService, scope=singleton)
        binder.bind(TagsService, scope=singleton)
        binder.bind(BottlesService, scope=singleton)
        binder.bind(PlacementsService, scope=singleton)


def create_injector() -> Injector:
    logger.info("Démarrage de la création de l'injector global")
    injector = Injector([ConfigurationModule()])
    logger.info("Fin de la création de l'injector global")
    return injector


injector = create_injector()
