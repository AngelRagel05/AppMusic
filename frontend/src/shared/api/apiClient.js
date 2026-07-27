const defaultHeaders = {
  Accept: "application/json",
  "Content-Type": "application/json",
};

export function resolveApiBaseUrl(locationValue = window.location) {
  const configuredUrl = new URLSearchParams(locationValue.search).get(
    "apiBaseUrl",
  );
  if (!configuredUrl) {
    return "";
  }

  try {
    const parsedUrl = new URL(configuredUrl);
    const isSafeLoopback =
      parsedUrl.protocol === "http:" &&
      parsedUrl.hostname === "127.0.0.1" &&
      !parsedUrl.username &&
      !parsedUrl.password;
    return isSafeLoopback ? parsedUrl.origin : "";
  } catch {
    return "";
  }
}

export function buildApiUrl(path, locationValue = window.location) {
  return `${resolveApiBaseUrl(locationValue)}/api${path}`;
}

const runtimeApiBaseUrl = resolveApiBaseUrl();

export class ApiClientError extends Error {
  constructor(message, status, code, details) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${runtimeApiBaseUrl}/api${path}`, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });
  if (response.status === 204) {
    return null;
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = body?.error;
    throw new ApiClientError(
      error?.message || `La solicitud ha fallado (${response.status}).`,
      response.status,
      error?.code || "request_failed",
      error?.details,
    );
  }
  return body;
}

function queryString(values) {
  const params = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  });
  const serialized = params.toString();
  return serialized ? `?${serialized}` : "";
}

export const api = {
  health: () => request("/health"),
  capabilities: () => request("/capabilities"),
  tasks: (kind) => request(`/tasks${queryString({ kind })}`),
  task: (taskId) => request(`/tasks/${taskId}`),
  cancelTask: (taskId) =>
    request(`/tasks/${taskId}/cancel`, { method: "POST" }),

  libraries: () => request("/libraries"),
  createLibrary: (payload) =>
    request("/libraries", { method: "POST", body: JSON.stringify(payload) }),
  updateLibrary: (libraryId, payload) =>
    request(`/libraries/${libraryId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  activateLibrary: (libraryId) =>
    request(`/libraries/${libraryId}/activate`, { method: "POST" }),
  deleteLibrary: (libraryId) =>
    request(`/libraries/${libraryId}`, { method: "DELETE" }),
  scanLibrary: (libraryId) =>
    request(`/libraries/${libraryId}/scan`, { method: "POST" }),

  playlists: () => request("/playlists"),
  createPlaylist: (payload) =>
    request("/playlists", { method: "POST", body: JSON.stringify(payload) }),
  updatePlaylist: (playlistId, payload) =>
    request(`/playlists/${playlistId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  activatePlaylist: (playlistId) =>
    request(`/playlists/${playlistId}/activate`, { method: "POST" }),
  deletePlaylist: (playlistId) =>
    request(`/playlists/${playlistId}`, { method: "DELETE" }),
  playlistItems: (playlistId) => request(`/playlists/${playlistId}/items`),
  importPlaylist: (playlistId) =>
    request(`/playlists/${playlistId}/import`, { method: "POST" }),

  comparison: (filters = {}) =>
    request(`/comparisons/current${queryString(filters)}`),
  comparisonById: (comparisonId, filters = {}) =>
    request(`/comparisons/${comparisonId}${queryString(filters)}`),
  comparisonHistory: () => request("/comparisons/history"),
  runComparison: (forceFullRecompute = false) =>
    request(
      `/comparisons/run${queryString({ forceFullRecompute })}`,
      { method: "POST" },
    ),
  updateComparisonItem: (comparisonId, itemId, payload) =>
    request(`/comparisons/${comparisonId}/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  ignoredTerms: () => request("/ignored-terms"),
  createIgnoredTerm: (payload) =>
    request("/ignored-terms", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateIgnoredTerm: (termId, payload) =>
    request(`/ignored-terms/${termId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  setIgnoredTermState: (termId, isActive) =>
    request(`/ignored-terms/${termId}/state`, {
      method: "PATCH",
      body: JSON.stringify({ isActive }),
    }),
  deleteIgnoredTerm: (termId) =>
    request(`/ignored-terms/${termId}`, { method: "DELETE" }),

  songs: (filters = {}) => request(`/songs${queryString(filters)}`),
  song: (songId) => request(`/songs/${songId}`),
  updateSongMetadata: (songId, payload) =>
    request(`/songs/${songId}/metadata`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  refreshSongMetadata: (songId) =>
    request(`/songs/${songId}/refresh`, { method: "POST" }),

  downloads: () => request("/downloads"),
  createDownloads: (payload) =>
    request("/downloads", { method: "POST", body: JSON.stringify(payload) }),
  retryDownload: (downloadId) =>
    request(`/downloads/${downloadId}/retry`, { method: "POST" }),
};
