from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.presentation.features.ignoredTerms.viewmodel import IgnoredTermsViewModel
from app.presentation.features.localLibrary.viewmodel import LocalFolderViewModel
from app.presentation.features.youtubePlaylists.viewmodel import YoutubePlaylistViewModel


@dataclass(frozen=True)
class ServiceRegistry:
    session: Session
    ignoredTermsViewModel: IgnoredTermsViewModel
    localFolderViewModel: LocalFolderViewModel
    youtubePlaylistViewModel: YoutubePlaylistViewModel
