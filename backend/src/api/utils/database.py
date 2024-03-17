import typing

import fastapi
from src.api.utils.driver import get_driver
from src.database.graph.crud.base import BaseCRUDRepositoryGraph

def get_repository(repo_type: typing.Type[BaseCRUDRepositoryGraph]):
    def _get_repo(
        driver = fastapi.Depends(get_driver),
    ) -> BaseCRUDRepositoryGraph:
        return repo_type(driver=driver)

    return _get_repo