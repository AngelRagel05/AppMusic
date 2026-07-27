from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.apiSchemas import (
    IgnoredTermRequest,
    IgnoredTermResponse,
    IgnoredTermStateRequest,
)
from app.api.dependencies import createApiRepositoryRegistry, getSession
from app.application.dto.createIgnoredTermInputDto import CreateIgnoredTermInputDto
from app.application.dto.deleteIgnoredTermInputDto import DeleteIgnoredTermInputDto
from app.application.dto.setIgnoredTermActiveStateInputDto import (
    SetIgnoredTermActiveStateInputDto,
)
from app.application.dto.updateIgnoredTermInputDto import UpdateIgnoredTermInputDto
from app.application.use_cases.filters.createIgnoredTermUseCase import (
    CreateIgnoredTermUseCase,
)
from app.application.use_cases.filters.deleteIgnoredTermUseCase import (
    DeleteIgnoredTermUseCase,
)
from app.application.use_cases.filters.listIgnoredTermsUseCase import (
    ListIgnoredTermsUseCase,
)
from app.application.use_cases.filters.setIgnoredTermActiveStateUseCase import (
    SetIgnoredTermActiveStateUseCase,
)
from app.application.use_cases.filters.updateIgnoredTermUseCase import (
    UpdateIgnoredTermUseCase,
)

router = APIRouter(prefix="/ignored-terms", tags=["ignored terms"])


@router.get("", response_model=list[IgnoredTermResponse])
def listIgnoredTerms(session: Session = Depends(getSession)) -> list:
    registry = createApiRepositoryRegistry(session)
    return ListIgnoredTermsUseCase(registry.ignoredTermRepository).execute()


@router.post(
    "",
    response_model=IgnoredTermResponse,
    status_code=status.HTTP_201_CREATED,
)
def createIgnoredTerm(
    payload: IgnoredTermRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return CreateIgnoredTermUseCase(registry.ignoredTermRepository).execute(
        CreateIgnoredTermInputDto(
            term=payload.term,
            scope=payload.scope,
            language=payload.language,
        )
    )


@router.put("/{term_id}", response_model=IgnoredTermResponse)
def updateIgnoredTerm(
    term_id: int,
    payload: IgnoredTermRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return UpdateIgnoredTermUseCase(registry.ignoredTermRepository).execute(
        UpdateIgnoredTermInputDto(
            term_id=term_id,
            term=payload.term,
            scope=payload.scope,
            language=payload.language,
        )
    )


@router.patch("/{term_id}/state", response_model=IgnoredTermResponse)
def setIgnoredTermState(
    term_id: int,
    payload: IgnoredTermStateRequest,
    session: Session = Depends(getSession),
):
    registry = createApiRepositoryRegistry(session)
    return SetIgnoredTermActiveStateUseCase(
        registry.ignoredTermRepository
    ).execute(
        SetIgnoredTermActiveStateInputDto(
            term_id=term_id,
            is_active=payload.is_active,
        )
    )


@router.delete("/{term_id}", status_code=status.HTTP_204_NO_CONTENT)
def deleteIgnoredTerm(
    term_id: int,
    session: Session = Depends(getSession),
) -> Response:
    registry = createApiRepositoryRegistry(session)
    DeleteIgnoredTermUseCase(registry.ignoredTermRepository).execute(
        DeleteIgnoredTermInputDto(term_id=term_id)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
