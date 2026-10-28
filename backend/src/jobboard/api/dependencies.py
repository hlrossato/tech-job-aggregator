from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from jobboard.application.services import SearchJobsService
from jobboard.infrastructure.db.session import get_session
from jobboard.infrastructure.repositories.sqlalchemy import SQLAlchemyJobRepository

SessionDependency = Annotated[Session, Depends(get_session)]


def get_search_service(session: SessionDependency) -> SearchJobsService:
    return SearchJobsService(SQLAlchemyJobRepository(session))


SearchServiceDependency = Annotated[SearchJobsService, Depends(get_search_service)]
