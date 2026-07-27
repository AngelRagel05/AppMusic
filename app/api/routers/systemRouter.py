from __future__ import annotations

from fastapi import APIRouter, Request
from yt_dlp import version as yt_dlp_version

from app.api.apiSchemas import CapabilitiesResponse, HealthResponse
from app.infrastructure.downloads.youtube import YtDlpAudioDownloader

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def getHealth(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
    )


@router.get("/capabilities", response_model=CapabilitiesResponse)
def getCapabilities(request: Request) -> CapabilitiesResponse:
    settings = request.app.state.settings
    return CapabilitiesResponse(
        ffmpeg_available=YtDlpAudioDownloader(
            settings.ffmpeg_path,
            socket_timeout_seconds=settings.yt_dlp_timeout_seconds,
            temporary_folder=str(settings.temporaryFolderPath),
        ).isAvailable(),
        yt_dlp_available=bool(getattr(yt_dlp_version, "__version__", "")),
        task_poll_interval_ms=settings.task_poll_interval_ms,
    )
