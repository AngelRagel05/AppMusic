from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


COMPARISON_IGNORED_TERMS = (
    "featuring",
    "feat",
    "ft",
    "official video",
    "video oficial",
    "videoclip oficial",
    "official audio",
    "official",
    "video",
    "visualizer",
    "videoclip",
    "lyrics",
    "lyric",
    "letra",
    "audio",
    "prod",
    "produced",
    "producido",
    "topic",
    "hd",
    "4k",
    "remastered",
)
_FEATURE_TERMS = ("featuring", "feat", "ft")
_SEPARATOR_SPLIT_PATTERN = re.compile(r"\s*(?:-{1,3}|[–—|·~:]+|/{1,3}|\\{1,3})\s*")
_BRACKETED_CONTENT_PATTERN = re.compile(r"(\([^)]*\)|\[[^\]]*\]|\{[^}]*\})")
_FEATURE_PATTERN = re.compile(r"\b(featuring|feat\.?|ft\.?)\b", re.IGNORECASE)
_LEADING_TRACK_NUMBER_PATTERN = re.compile(r"^\s*\d{1,3}[a-z]?[\s\.\-\)_]+", re.IGNORECASE)
_SYMBOL_PATTERN = re.compile(r"[^a-z0-9\s]")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_COMPARISON_IGNORED_PATTERN = re.compile(
    r"(?<!\w)("
    + "|".join(
        re.escape(term)
        for term in sorted(COMPARISON_IGNORED_TERMS, key=len, reverse=True)
    )
    + r")(?!\w)",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class NormalizedComparisonTextParts:
    primary_value: str
    collaborators: tuple[str, ...] = ()
    ignored_decorators: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class NormalizedMusicComparisonMetadata:
    normalized_title: str
    normalized_artist: str
    normalized_album: str = ""
    title_collaborators: tuple[str, ...] = ()
    artist_collaborators: tuple[str, ...] = ()
    ignored_title_decorators: tuple[str, ...] = ()
    ignored_artist_decorators: tuple[str, ...] = ()
    ignored_album_decorators: tuple[str, ...] = ()


def normalizeMusicComparisonText(value: str) -> str:
    return _normalizeComparableSegment(
        _removeIgnoredDecorators(
            _FEATURE_PATTERN.sub(
                " feat ",
                _removeIgnoredBracketedContent(value.strip().lower()),
            )
        ),
    )


def splitMusicComparisonSegments(value: str) -> tuple[str, ...]:
    cleaned_value = _removeIgnoredBracketedContent(value)
    return tuple(
        part.strip()
        for part in _SEPARATOR_SPLIT_PATTERN.split(cleaned_value)
        if part.strip()
    )


def normalizeMusicComparisonMetadata(
    title: str,
    artist: str,
    album: str = "",
) -> NormalizedMusicComparisonMetadata:
    normalized_title_parts = normalizeMusicComparisonTitleParts(title)
    normalized_artist_parts = normalizeMusicComparisonArtistParts(artist)
    normalized_album_parts = normalizeMusicComparisonAlbumParts(album)
    comparable_artist = " ".join(
        token
        for token in (
            normalized_artist_parts.primary_value,
            *normalized_artist_parts.collaborators,
        )
        if token
    ).strip()

    return NormalizedMusicComparisonMetadata(
        normalized_title=normalized_title_parts.primary_value,
        normalized_artist=comparable_artist,
        normalized_album=normalized_album_parts.primary_value,
        title_collaborators=normalized_title_parts.collaborators,
        artist_collaborators=normalized_artist_parts.collaborators,
        ignored_title_decorators=normalized_title_parts.ignored_decorators,
        ignored_artist_decorators=normalized_artist_parts.ignored_decorators,
        ignored_album_decorators=normalized_album_parts.ignored_decorators,
    )


def normalizeMusicComparisonTitle(value: str) -> str:
    return normalizeMusicComparisonTitleParts(value).primary_value


def normalizeMusicComparisonArtist(value: str) -> str:
    artist_parts = normalizeMusicComparisonArtistParts(value)
    return " ".join(
        token
        for token in (artist_parts.primary_value, *artist_parts.collaborators)
        if token
    ).strip()


def normalizeMusicComparisonAlbum(value: str) -> str:
    return normalizeMusicComparisonAlbumParts(value).primary_value


def normalizeMusicComparisonTitleParts(value: str) -> NormalizedComparisonTextParts:
    normalized_value = _prepareRawComparisonValue(value)
    normalized_value = _LEADING_TRACK_NUMBER_PATTERN.sub("", normalized_value)
    main_value, collaborator_segments = _splitFeatureSegments(normalized_value)
    ignored_decorators = _extractIgnoredDecorators(main_value)
    return NormalizedComparisonTextParts(
        primary_value=_normalizeComparableSegment(_removeIgnoredDecorators(main_value)),
        collaborators=_normalizeCollaboratorSegments(collaborator_segments),
        ignored_decorators=ignored_decorators,
    )


def normalizeMusicComparisonArtistParts(value: str) -> NormalizedComparisonTextParts:
    normalized_value = _prepareRawComparisonValue(value)
    normalized_value = _LEADING_TRACK_NUMBER_PATTERN.sub("", normalized_value)
    main_value, collaborator_segments = _splitFeatureSegments(normalized_value)
    ignored_decorators = _extractIgnoredDecorators(main_value)
    return NormalizedComparisonTextParts(
        primary_value=_normalizeComparableSegment(_removeIgnoredDecorators(main_value)),
        collaborators=_normalizeCollaboratorSegments(collaborator_segments),
        ignored_decorators=ignored_decorators,
    )


def normalizeMusicComparisonAlbumParts(value: str) -> NormalizedComparisonTextParts:
    normalized_value = _prepareRawComparisonValue(value)
    ignored_decorators = _extractIgnoredDecorators(normalized_value)
    return NormalizedComparisonTextParts(
        primary_value=_normalizeComparableSegment(_removeIgnoredDecorators(normalized_value)),
        ignored_decorators=ignored_decorators,
    )


def _prepareRawComparisonValue(value: str) -> str:
    normalized_value = _stripAccents(value.strip().lower())
    normalized_value = _removeIgnoredBracketedContent(normalized_value)
    return _FEATURE_PATTERN.sub(" feat ", normalized_value)


def _normalizeComparableSegment(value: str) -> str:
    normalized_value = _stripAccents(value)
    normalized_value = _SEPARATOR_SPLIT_PATTERN.sub(" ", normalized_value)
    normalized_value = _SYMBOL_PATTERN.sub(" ", normalized_value)
    normalized_value = _WHITESPACE_PATTERN.sub(" ", normalized_value)
    return normalized_value.strip()


def _normalizeCollaboratorSegments(values: tuple[str, ...]) -> tuple[str, ...]:
    normalized_values: list[str] = []
    for value in values:
        normalized_value = _normalizeComparableSegment(_removeIgnoredDecorators(value))
        if normalized_value and normalized_value not in normalized_values:
            normalized_values.append(normalized_value)
    return tuple(normalized_values)


def _splitFeatureSegments(value: str) -> tuple[str, tuple[str, ...]]:
    feature_match = re.search(r"\bfeat\b", value)
    if feature_match is None:
        return value, ()

    primary_value = value[: feature_match.start()].strip()
    collaborator_value = value[feature_match.end() :].strip()
    if not collaborator_value:
        return primary_value, ()

    collaborator_segments = tuple(
        segment
        for segment in re.split(r"\s*(?:,|&|\+|\bx\b|/|\band\b)\s*", collaborator_value)
        if segment.strip()
    )
    return primary_value, collaborator_segments


def _extractIgnoredDecorators(value: str) -> tuple[str, ...]:
    decorators: list[str] = []
    for match in _COMPARISON_IGNORED_PATTERN.finditer(value):
        normalized_match = _normalizeComparableSegment(match.group(1))
        if normalized_match and normalized_match not in decorators:
            decorators.append(normalized_match)
    return tuple(decorators)


def _removeIgnoredDecorators(value: str) -> str:
    return _COMPARISON_IGNORED_PATTERN.sub(" ", value)


def _stripAccents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(character for character in normalized if not unicodedata.combining(character))


def _removeIgnoredBracketedContent(value: str) -> str:
    result = value
    for match in _BRACKETED_CONTENT_PATTERN.findall(value):
        normalized_content = _normalizeComparableSegment(_stripAccents(match[1:-1].lower()))
        if not normalized_content:
            result = result.replace(match, " ")
            continue
        content_tokens = tuple(token for token in normalized_content.split(" ") if token)
        if content_tokens and all(_isIgnoredComparisonToken(token) for token in content_tokens):
            result = result.replace(match, " ")
    return result


def _isIgnoredComparisonToken(token: str) -> bool:
    if token in _FEATURE_TERMS:
        return True
    return any(
        token == ignored_term or token in ignored_term.split(" ")
        for ignored_term in COMPARISON_IGNORED_TERMS
    )
