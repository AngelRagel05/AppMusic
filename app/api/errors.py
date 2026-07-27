from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class ApiError(RuntimeError):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details=None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def registerErrorHandlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handleApiError(_request: Request, error: ApiError) -> JSONResponse:
        return _errorResponse(
            error.status_code,
            error.code,
            error.message,
            error.details,
        )

    @app.exception_handler(RequestValidationError)
    async def handleValidationError(
        _request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        return _errorResponse(
            422,
            "validation_error",
            "La solicitud contiene datos no validos.",
            error.errors(),
        )

    @app.exception_handler(IntegrityError)
    async def handleIntegrityError(
        _request: Request,
        _error: IntegrityError,
    ) -> JSONResponse:
        return _errorResponse(
            409,
            "integrity_conflict",
            "La operacion entra en conflicto con datos relacionados.",
        )

    @app.exception_handler(ValueError)
    async def handleValueError(_request: Request, error: ValueError) -> JSONResponse:
        return _errorResponse(
            400,
            "business_rule_violation",
            str(error),
        )


def _errorResponse(
    status_code: int,
    code: str,
    message: str,
    details=None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            {
                "error": {
                    "code": code,
                    "message": message,
                    "details": details,
                }
            },
            custom_encoder={Exception: str},
        ),
    )
