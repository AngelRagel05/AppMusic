from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self' http://127.0.0.1:*; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'"
)


def registerFrontendFiles(application: FastAPI, frontend_directory: Path) -> None:
    resolved_directory = frontend_directory.resolve(strict=False)
    index_path = resolved_directory / "index.html"
    if not index_path.is_file():
        raise RuntimeError(
            "No se encontro el build de React esperado en "
            f"{resolved_directory}. Ejecuta el build del frontend."
        )

    @application.get("/", include_in_schema=False)
    def serveFrontendIndex() -> FileResponse:
        return _frontendIndexResponse(index_path)

    @application.get("/{frontend_path:path}", include_in_schema=False)
    def serveFrontendPath(frontend_path: str) -> FileResponse:
        if frontend_path == "api" or frontend_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        requested_path = (resolved_directory / frontend_path).resolve(strict=False)
        try:
            requested_path.relative_to(resolved_directory)
        except ValueError as error:
            raise HTTPException(status_code=404, detail="Not Found") from error

        if requested_path.is_file():
            return FileResponse(requested_path)
        return _frontendIndexResponse(index_path)


def _frontendIndexResponse(index_path: Path) -> FileResponse:
    return FileResponse(
        index_path,
        headers={"Content-Security-Policy": CONTENT_SECURITY_POLICY},
    )
