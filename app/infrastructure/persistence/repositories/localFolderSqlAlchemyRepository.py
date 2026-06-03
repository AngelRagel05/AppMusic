from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.domain.library.entities.localFolder import LocalFolder
from app.domain.library.repositories.localFolderRepository import LocalFolderRepository
from app.infrastructure.persistence.database.models import LocalFolder as LocalFolderModel


class LocalFolderSqlAlchemyRepository(LocalFolderRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[LocalFolder]:
        statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).order_by(
            LocalFolderModel.display_name.asc(),
            LocalFolderModel.path.asc(),
        )
        return [self._to_entity(model) for model in self._session.scalars(statement).all()]

    def get_active(self) -> LocalFolder | None:
        statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).where(
            LocalFolderModel.is_active.is_(True)
        )
        model = self._session.scalar(statement)
        if model is None:
            return None

        return self._to_entity(model)

    def save_as_active(self, path: str, display_name: str) -> LocalFolder:
        statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).where(
            LocalFolderModel.path == path
        )
        model = self._session.scalar(statement)

        if model is not None:
            msg = "Esta carpeta ya esta guardada."
            raise ValueError(msg)

        self._session.query(LocalFolderModel).update({LocalFolderModel.is_active: False})
        model = LocalFolderModel(
            path=path,
            display_name=display_name,
            is_active=True,
        )
        self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def activate(self, local_folder_id: int) -> LocalFolder:
        statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).where(
            LocalFolderModel.id == local_folder_id
        )
        model = self._session.scalar(statement)
        if model is None:
            msg = "La biblioteca seleccionada no existe."
            raise ValueError(msg)

        self._session.query(LocalFolderModel).update({LocalFolderModel.is_active: False})
        model.is_active = True
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def update(self, local_folder_id: int, path: str, display_name: str) -> LocalFolder:
        statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).where(
            LocalFolderModel.id == local_folder_id
        )
        model = self._session.scalar(statement)
        if model is None:
            msg = "La biblioteca seleccionada no existe."
            raise ValueError(msg)

        duplicate_statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).where(
            LocalFolderModel.path == path,
            LocalFolderModel.id != local_folder_id,
        )
        duplicate_model = self._session.scalar(duplicate_statement)
        if duplicate_model is not None:
            msg = "Esta carpeta ya esta guardada."
            raise ValueError(msg)

        model.path = path
        model.display_name = display_name
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, local_folder_id: int) -> None:
        statement: Select[tuple[LocalFolderModel]] = select(LocalFolderModel).where(
            LocalFolderModel.id == local_folder_id
        )
        model = self._session.scalar(statement)
        if model is None:
            msg = "La biblioteca seleccionada no existe."
            raise ValueError(msg)

        self._session.delete(model)
        self._session.commit()

    def _to_entity(self, model: LocalFolderModel) -> LocalFolder:
        return LocalFolder(
            id=model.id,
            path=model.path,
            display_name=model.display_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
