from __future__ import annotations

from app.domain.playlists.services.persistedComparisonModels import (
    ComparableLocalSong,
    ComparableYoutubePlaylistItem,
)
from app.domain.playlists.services.playlistItemMatchingRules import (
    ArtistMatchEvidence,
    buildArtistMatchEvidence,
)


def classifyComparableArtistMatchForSelection(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    local_song: ComparableLocalSong,
) -> ArtistMatchEvidence:
    primary_to_primary_evidence = buildArtistMatchEvidence(
        youtube_playlist_item.comparable_artist_primary,
        local_song.comparable_artist_primary,
    )
    if primary_to_primary_evidence is ArtistMatchEvidence.STRONG:
        return ArtistMatchEvidence.STRONG

    primary_to_full_evidence = buildArtistMatchEvidence(
        youtube_playlist_item.comparable_artist_primary,
        local_song.comparable_artist_full,
    )
    if primary_to_full_evidence in (
        ArtistMatchEvidence.STRONG,
        ArtistMatchEvidence.MEDIUM,
    ):
        return ArtistMatchEvidence.MEDIUM

    return _buildCollaboratorDiagnosticEvidence(
        youtube_playlist_item,
        local_song,
    )


def _artistEvidenceRank(evidence: ArtistMatchEvidence) -> int:
    return {
        ArtistMatchEvidence.STRONG: 3,
        ArtistMatchEvidence.MEDIUM: 2,
        ArtistMatchEvidence.WEAK: 1,
        ArtistMatchEvidence.NONE: 0,
    }[evidence]


def _buildCollaboratorDiagnosticEvidence(
    youtube_playlist_item: ComparableYoutubePlaylistItem,
    local_song: ComparableLocalSong,
) -> ArtistMatchEvidence:
    youtube_values = (
        youtube_playlist_item.comparable_artist_primary,
        *youtube_playlist_item.comparable_artist_collaborators,
    )
    local_values = (
        local_song.comparable_artist_primary,
        *local_song.comparable_artist_collaborators,
    )

    best_evidence = ArtistMatchEvidence.NONE
    for youtube_value in youtube_values:
        for local_value in local_values:
            if not youtube_value or not local_value:
                continue
            evidence = buildArtistMatchEvidence(youtube_value, local_value)
            downgraded_evidence = _downgradeSecondaryEvidence(evidence)
            if _artistEvidenceRank(downgraded_evidence) > _artistEvidenceRank(best_evidence):
                best_evidence = downgraded_evidence

    if best_evidence is ArtistMatchEvidence.WEAK:
        return ArtistMatchEvidence.NONE
    return best_evidence


def _downgradeSecondaryEvidence(evidence: ArtistMatchEvidence) -> ArtistMatchEvidence:
    return {
        ArtistMatchEvidence.STRONG: ArtistMatchEvidence.MEDIUM,
        ArtistMatchEvidence.MEDIUM: ArtistMatchEvidence.WEAK,
        ArtistMatchEvidence.WEAK: ArtistMatchEvidence.WEAK,
        ArtistMatchEvidence.NONE: ArtistMatchEvidence.NONE,
    }[evidence]
