from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.presentation.viewmodels import (
    IgnoredTermsViewModel,
    LocalFolderViewModel,
    YoutubePlaylistViewModel,
)


@dataclass(frozen=True)
class ServiceRegistry:
    session: Session
    ignoredTermsViewModel: IgnoredTermsViewModel
    localFolderViewModel: LocalFolderViewModel
    youtubePlaylistViewModel: YoutubePlaylistViewModel
