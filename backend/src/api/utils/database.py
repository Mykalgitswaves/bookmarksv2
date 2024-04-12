import typing

import fastapi
from src.api.utils.driver import get_driver
from src.api.utils.session import get_session
from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.database.sql.crud.base import BaseCRUDRepositoryMySQL

def get_repository(repo_type: typing.Type[BaseCRUDRepositoryGraph]):
    def _get_repo(
        driver = fastapi.Depends(get_driver),
    ) -> BaseCRUDRepositoryGraph:
        return repo_type(driver=driver)

    return _get_repo

def get_sql_repository(repo_type: typing.Type[BaseCRUDRepositoryMySQL]):
    def _get_repo(
        session = fastapi.Depends(get_session),
    ) -> BaseCRUDRepositoryMySQL:
        return repo_type(session=session)

    return _get_repo