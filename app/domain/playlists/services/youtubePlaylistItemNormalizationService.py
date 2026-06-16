from __future__ import annotations

from dataclasses import dataclass
import re

from app.domain.metadata.services.musicComparisonNormalizationService import (
    IgnoredTermsByScope,
    normalizeMusicComparisonArtist,
    normalizeMusicComparisonMetadata,
    normalizeMusicComparisonText,
    normalizeMusicComparisonTitle,
    splitMusicComparisonSegments,
)
from app.domain.playlists.services.playlistItemMatchingRules import (
    TitleMatchEvidence,
    buildTextMatchEvidence,
)


@dataclass(frozen=True, slots=True)
class NormalizedYoutubePlaylistItemMetadata:
    normalized_title: str
    normalized_artist: str


@dataclass(frozen=True, slots=True)
class _SplitCandidate:
    normalized_artist: str
    normalized_title: str
    channel_rank: int
    artist_hint_score: int
    title_token_count: int
    artist_token_count: int


_TRACK_INDEX_PATTERN = re.compile(r"^\d{1,3}[a-z]?$", re.IGNORECASE)
_BRACKETED_FRAGMENT_PATTERN = re.compile(r"(\([^)]*\)|\[[^\]]*\]|\{[^}]*\})")
_COLLABORATION_SPLIT_PATTERN = re.compile(r"\s*(?:,|&|\+|\bx\b|/|\band\b|\by\b)\s*", re.IGNORECASE)
_ARTIST_HINT_PATTERN = re.compile(
    r"\b(feat|ft|featuring|x|and|y|with|prod|topic)\b",
    re.IGNORECASE,
)
_PROTECTED_BRACKET_TOKENS = {"remix", "live", "version"}


def normalizeYoutubePlaylistItemMetadata(
    raw_title: str,
    raw_channel_name: str,
    ignored_terms_by_scope: IgnoredTermsByScope | None = None,
) -> NormalizedYoutubePlaylistItemMetadata:
    artist_from_title, title_from_title = _splitArtistAndTitle(
        raw_title,
        raw_channel_name,
        ignored_terms_by_scope,
    )
    if artist_from_title and title_from_title:
        return NormalizedYoutubePlaylistItemMetadata(
            normalized_title=title_from_title,
            normalized_artist=artist_from_title,
        )

    normalized_metadata = normalizeMusicComparisonMetadata(
        title=raw_title,
        artist=raw_channel_name,
        ignored_terms_by_scope=ignored_terms_by_scope,
    )
    return NormalizedYoutubePlaylistItemMetadata(
        normalized_title=normalized_metadata.normalized_title,
        normalized_artist=normalized_metadata.normalized_artist,
    )


def _splitArtistAndTitle(
    value: str,
    raw_channel_name: str,
    ignored_terms_by_scope: IgnoredTermsByScope | None,
) -> tuple[str | None, str | None]:
    cleaned_value = _removeNonTitleBracketedContent(value)
    channel_prefixed_hashtag_split = _extractChannelPrefixedHashtagTitle(
        cleaned_value,
        raw_channel_name,
        ignored_terms_by_scope,
    )
    if channel_prefixed_hashtag_split != (None, None):
        return channel_prefixed_hashtag_split

    raw_parts = list(
        splitMusicComparisonSegments(
            cleaned_value,
            _resolveIgnoredTermsForScope(ignored_terms_by_scope, "title"),
        )
    )
    if len(raw_parts) < 2:
        return None, None

    if _looksLikeTrackIndex(raw_parts[0]):
        raw_parts = raw_parts[1:]
    if len(raw_parts) < 2:
        return None, None

    normalized_channel = normalizeMusicComparisonArtist(
        raw_channel_name,
        _resolveIgnoredTermsForScope(ignored_terms_by_scope, "artist"),
    )
    split_candidates = _buildSplitCandidates(
        raw_parts,
        normalized_channel,
        ignored_terms_by_scope,
    )
    if split_candidates:
        best_candidate = max(
            split_candidates,
            key=lambda candidate: (
                candidate.channel_rank,
                candidate.artist_hint_score,
                candidate.title_token_count,
                -candidate.artist_token_count,
            ),
        )
        if best_candidate.channel_rank >= 2:
            return (
                best_candidate.normalized_artist or None,
                best_candidate.normalized_title or None,
            )
        heuristic_candidate = _pickHeuristicCandidate(split_candidates)
        if heuristic_candidate is not None:
            return (
                heuristic_candidate.normalized_artist or None,
                heuristic_candidate.normalized_title or None,
            )

    default_artist = normalizeMusicComparisonArtist(
        raw_parts[0],
        _resolveIgnoredTermsForScope(ignored_terms_by_scope, "artist"),
    )
    default_title = normalizeMusicComparisonTitle(
        " ".join(raw_parts[1:]),
        _resolveIgnoredTermsForScope(ignored_terms_by_scope, "title"),
    )
    if default_artist and default_title:
        return default_artist, default_title
    return None, None


def _extractChannelPrefixedHashtagTitle(
    value: str,
    raw_channel_name: str,
    ignored_terms_by_scope: IgnoredTermsByScope | None,
) -> tuple[str | None, str | None]:
    raw_channel_tokens = [token for token in raw_channel_name.split() if token]
    if not raw_channel_tokens:
        return None, None

    channel_prefix_pattern = re.compile(
        r"^\s*"
        + r"\s+".join(re.escape(token) for token in raw_channel_tokens)
        + r"\s*#\s*(.+)$",
        re.IGNORECASE,
    )
    channel_prefixed_match = channel_prefix_pattern.match(value)
    if channel_prefixed_match is None:
        return None, None

    normalized_artist = normalizeMusicComparisonArtist(
        raw_channel_name,
        _resolveIgnoredTermsForScope(ignored_terms_by_scope, "artist"),
    )
    normalized_title = normalizeMusicComparisonTitle(
        channel_prefixed_match.group(1),
        _resolveIgnoredTermsForScope(ignored_terms_by_scope, "title"),
    )
    if normalized_artist and normalized_title:
        return normalized_artist, normalized_title
    return None, None


def _buildSplitCandidates(
    raw_parts: list[str],
    normalized_channel: str,
    ignored_terms_by_scope: IgnoredTermsByScope | None,
) -> list[_SplitCandidate]:
    split_candidates: list[_SplitCandidate] = []
    for split_index in range(1, len(raw_parts)):
        left_raw_value = " ".join(raw_parts[:split_index])
        right_raw_value = " ".join(raw_parts[split_index:])
        left_artist = normalizeMusicComparisonArtist(
            left_raw_value,
            _resolveIgnoredTermsForScope(ignored_terms_by_scope, "artist"),
        )
        right_artist = normalizeMusicComparisonArtist(
            right_raw_value,
            _resolveIgnoredTermsForScope(ignored_terms_by_scope, "artist"),
        )
        left_title = normalizeMusicComparisonTitle(
            left_raw_value,
            _resolveIgnoredTermsForScope(ignored_terms_by_scope, "title"),
        )
        right_title = normalizeMusicComparisonTitle(
            right_raw_value,
            _resolveIgnoredTermsForScope(ignored_terms_by_scope, "title"),
        )

        if left_artist and right_title:
            split_candidates.append(
                _buildSplitCandidate(
                    normalized_artist=left_artist,
                    normalized_title=right_title,
                    normalized_channel=normalized_channel,
                    raw_artist_value=left_raw_value,
                )
            )
        if right_artist and left_title:
            split_candidates.append(
                _buildSplitCandidate(
                    normalized_artist=right_artist,
                    normalized_title=left_title,
                    normalized_channel=normalized_channel,
                    raw_artist_value=right_raw_value,
                )
            )
    return split_candidates


def _buildSplitCandidate(
    *,
    normalized_artist: str,
    normalized_title: str,
    normalized_channel: str,
    raw_artist_value: str,
) -> _SplitCandidate:
    return _SplitCandidate(
        normalized_artist=normalized_artist,
        normalized_title=normalized_title,
        channel_rank=_rankChannelMatch(normalized_channel, normalized_artist),
        artist_hint_score=_scoreArtistHint(raw_artist_value, normalized_artist),
        title_token_count=len([token for token in normalized_title.split(" ") if token]),
        artist_token_count=len([token for token in normalized_artist.split(" ") if token]),
    )


def _looksLikeTrackIndex(value: str) -> bool:
    normalized_value = normalizeMusicComparisonText(value)
    return bool(normalized_value and _TRACK_INDEX_PATTERN.fullmatch(normalized_value))


def _rankChannelMatch(normalized_channel: str, normalized_artist: str) -> int:
    if not normalized_channel or not normalized_artist:
        return 0

    evidence = buildTextMatchEvidence(normalized_channel, normalized_artist)
    return {
        TitleMatchEvidence.EXACT: 3,
        TitleMatchEvidence.NEAR_EXACT: 2,
        TitleMatchEvidence.CONTAINS: 1,
        TitleMatchEvidence.WEAK: 0,
        TitleMatchEvidence.NONE: 0,
    }[evidence]


def _pickHeuristicCandidate(
    split_candidates: list[_SplitCandidate],
) -> _SplitCandidate | None:
    if not split_candidates:
        return None

    best_candidate = max(
        split_candidates,
        key=lambda candidate: (
            candidate.artist_hint_score,
            candidate.title_token_count,
            -candidate.artist_token_count,
        ),
    )
    if best_candidate.artist_hint_score >= 2:
        return best_candidate
    return None


def _scoreArtistHint(raw_artist_value: str, normalized_artist: str) -> int:
    score = 0
    token_count = len([token for token in normalized_artist.split(" ") if token])
    if 2 <= token_count <= 6:
        score += 1
    elif token_count > 6:
        score -= 1

    if _ARTIST_HINT_PATTERN.search(raw_artist_value):
        score += 2

    collaborator_count = len(
        [
            segment
            for segment in _COLLABORATION_SPLIT_PATTERN.split(raw_artist_value)
            if normalizeMusicComparisonText(segment)
        ]
    )
    if collaborator_count >= 2:
        score += 2

    return score


def _removeNonTitleBracketedContent(value: str) -> str:
    cleaned_value = value
    for match in _BRACKETED_FRAGMENT_PATTERN.findall(value):
        normalized_fragment = normalizeMusicComparisonText(match[1:-1])
        fragment_tokens = {token for token in normalized_fragment.split(" ") if token}
        if not fragment_tokens:
            cleaned_value = cleaned_value.replace(match, " ")
            continue
        if fragment_tokens & _PROTECTED_BRACKET_TOKENS:
            continue
        cleaned_value = cleaned_value.replace(match, " ")
    return cleaned_value


def _resolveIgnoredTermsForScope(
    ignored_terms_by_scope: IgnoredTermsByScope | None,
    scope: str,
) -> tuple[str, ...]:
    if not ignored_terms_by_scope:
        return ()
    scoped_terms = tuple(ignored_terms_by_scope.get(scope, ()))
    global_terms = tuple(ignored_terms_by_scope.get("global", ()))
    return tuple(
        term
        for term in (*global_terms, *scoped_terms)
        if (term or "").strip()
    )
