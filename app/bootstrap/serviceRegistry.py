from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.application.use_cases import ScanLocalFolderUseCase
from app.presentation.viewmodels import (
    IgnoredTermsViewModel,
    LibraryComparisonViewModel,
    LocalFolderViewModel,
    LocalLibraryScanViewModel,
    YoutubePlaylistImportViewModel,
    YoutubePlaylistViewModel,
)


@dataclass(frozen=True)
class ServiceRegistry:
    session: Session
    ignoredTermsViewModel: IgnoredTermsViewModel
    libraryComparisonViewModel: LibraryComparisonViewModel
    localFolderViewModel: LocalFolderViewModel
    localLibraryScanViewModel: LocalLibraryScanViewModel
    youtubePlaylistImportViewModel: YoutubePlaylistImportViewModel
    youtubePlaylistViewModel: YoutubePlaylistViewModel
