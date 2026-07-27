from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class ErrorDetail(ApiModel):
    code: str
    message: str
    details: Any = None


class ErrorResponse(ApiModel):
    error: ErrorDetail


class HealthResponse(ApiModel):
    status: Literal["ok"]
    app_name: str
    environment: str


class CapabilitiesResponse(ApiModel):
    ffmpeg_available: bool
    yt_dlp_available: bool
    metadata_editing_available: bool = True
    task_poll_interval_ms: int


class TaskResponse(ApiModel):
    id: str
    kind: str
    status: Literal[
        "queued",
        "running",
        "cancelling",
        "completed",
        "failed",
        "cancelled",
    ]
    progress_percent: float
    message: str | None
    result: Any = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class LocalFolderRequest(ApiModel):
    path: str = Field(min_length=1, max_length=1024)
    display_name: str = Field(default="", max_length=255)


class LocalFolderResponse(ApiModel):
    id: int
    path: str
    display_name: str
    is_active: bool


class YoutubePlaylistRequest(ApiModel):
    playlist_url: HttpUrl
    title: str = Field(min_length=1, max_length=255)


class YoutubePlaylistResponse(ApiModel):
    id: int
    playlist_url: str
    external_playlist_id: str
    title: str
    is_active: bool
    item_count: int = 0


class YoutubePlaylistItemResponse(ApiModel):
    id: int
    youtube_playlist_id: int
    external_video_id: str
    position: int
    raw_title: str
    raw_channel_name: str
    duration_seconds: float | None
    published_at: datetime | None


class IgnoredTermRequest(ApiModel):
    term: str = Field(min_length=1, max_length=255)
    scope: str = Field(default="title", min_length=1, max_length=64)
    language: str = Field(default="global", min_length=1, max_length=16)


class IgnoredTermStateRequest(ApiModel):
    is_active: bool


class IgnoredTermResponse(ApiModel):
    id: int
    term: str
    scope: str
    language: str
    is_active: bool


class LocalSongResponse(ApiModel):
    id: int
    local_folder_id: int
    file_path: str
    file_name: str
    is_available: bool
    title: str
    artist: str
    album: str
    release_year: int
    track_number_album: int
    duration_seconds: float


class LocalSongPageResponse(ApiModel):
    items: list[LocalSongResponse]
    total: int
    page: int
    page_size: int


class LocalSongMetadataRequest(ApiModel):
    title: str = Field(min_length=1, max_length=255)
    artist: str = Field(default="", max_length=255)
    album: str = Field(default="", max_length=255)
    release_year: int = Field(default=0, ge=0, le=9999)
    track_number_album: int = Field(default=0, ge=0)


class ComparisonSummaryResponse(ApiModel):
    found_count: int
    missing_count: int
    possible_match_count: int
    total_compared: int


class ComparisonItemResponse(ApiModel):
    youtube_playlist_item_id: int
    local_song_id: int | None
    comparison_status: Literal["found", "missing", "possible_match"]
    youtube_title: str
    youtube_artist: str
    local_title: str | None
    local_artist: str | None
    score: float
    reason: str
    matched_by: str | None


class ComparisonResponse(ApiModel):
    summary: ComparisonSummaryResponse
    items: list[ComparisonItemResponse]
    playlist_comparison_id: int | None
    last_compared_at: datetime | None
    total: int
    page: int
    page_size: int


class ComparisonHistoryResponse(ApiModel):
    comparison_id: int
    compared_at: datetime
    found_count: int
    missing_count: int
    possible_match_count: int
    total_compared: int


class ComparisonUpdateRequest(ApiModel):
    match_status: Literal["found", "missing", "possible_match"]
    local_song_id: int | None = None


class DownloadBatchRequest(ApiModel):
    local_folder_id: int = Field(gt=0)
    source_urls: list[HttpUrl] = Field(default_factory=list, max_length=50)
    youtube_playlist_item_ids: list[int] = Field(
        default_factory=list,
        max_length=50,
    )

    @model_validator(mode="after")
    def validateSources(self) -> DownloadBatchRequest:
        if not self.source_urls and not self.youtube_playlist_item_ids:
            raise ValueError(
                "Debes indicar al menos una URL o un item de comparacion."
            )
        return self


class DownloadResponse(ApiModel):
    id: int
    youtube_playlist_item_id: int | None
    local_folder_id: int
    task_id: str
    source_url: str
    source_title: str | None
    source_artist: str | None
    status: Literal[
        "pending",
        "in_progress",
        "completed",
        "failed",
        "cancelled",
    ]
    progress_percent: float
    target_file_path: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None


class DownloadBatchResponse(ApiModel):
    tasks: list[TaskResponse]
