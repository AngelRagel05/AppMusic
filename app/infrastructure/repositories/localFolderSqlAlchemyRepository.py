from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.domain.entities.localFolder import LocalFolder
from app.domain.services.localFolderRepository import LocalFolderRepository
from app.infrastructure.database.models import LocalFolder as LocalFolderModel


class LocalFolderSqlAlchemyRepository(LocalFolderRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active(self) -> LocalFolder | None:
        statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).where(
            LocalFolderModel.is_active.is_(True)
        )
        model = self._session.scalar(statement)
        if model is None:
            return None

        return self._to_entity(model)

    def save_as_active(self, path: str, display_name: str) -> LocalFolder:
        self._session.query(LocalFolderModel).update({LocalFolderModel.is_active: False})

        statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).where(
            LocalFolderModel.path == path
        )
        model = self._session.scalar(statement)

        if model is None:
            model = LocalFolderModel(
                path=path,
                display_name=display_name,
                is_active=True,
            )
            self._session.add(model)
        else:
            model.display_name = display_name
            model.is_active = True

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: LocalFolderModel) -> LocalFolder:
        return LocalFolder(
            id=model.id,
            path=model.path,
            display_name=model.display_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
