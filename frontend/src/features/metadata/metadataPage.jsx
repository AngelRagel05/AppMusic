import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../../shared/api/apiClient";
import { TaskList } from "../../shared/components/taskList/taskList";
import { useTaskCompletionRefresh } from "../../shared/hooks/useTaskCompletionRefresh";
import ui from "../../shared/styles/ui.module.css";

const metadataScanRefreshKeys = [["songs"], ["libraries"]];

const emptyMetadata = {
  title: "",
  artist: "",
  album: "",
  releaseYear: 0,
  trackNumberAlbum: 0,
};

export function MetadataPage() {
  const queryClient = useQueryClient();
  const [libraryId, setLibraryId] = useState("");
  const [search, setSearch] = useState("");
  const [availability, setAvailability] = useState("all");
  const [sortBy, setSortBy] = useState("title");
  const [sortDirection, setSortDirection] = useState("asc");
  const [page, setPage] = useState(1);
  const [selectedSongId, setSelectedSongId] = useState(null);
  const [metadata, setMetadata] = useState(emptyMetadata);
  const [successMessage, setSuccessMessage] = useState("");

  useTaskCompletionRefresh("library_scan", metadataScanRefreshKeys);

  const librariesQuery = useQuery({
    queryKey: ["libraries"],
    queryFn: api.libraries,
  });
  const activeLibrary = librariesQuery.data?.find((library) => library.isActive);

  useEffect(() => {
    if (!libraryId && activeLibrary) {
      setLibraryId(String(activeLibrary.id));
    }
  }, [activeLibrary, libraryId]);

  const songsQuery = useQuery({
    queryKey: [
      "songs",
      libraryId,
      search,
      availability,
      sortBy,
      sortDirection,
      page,
    ],
    queryFn: () =>
      api.songs({
        libraryId,
        search,
        availability,
        sortBy,
        sortDirection,
        page,
        pageSize: 25,
      }),
    enabled: Boolean(libraryId),
  });

  const selectedSong =
    songsQuery.data?.items.find((song) => song.id === selectedSongId) || null;

  useEffect(() => {
    if (!selectedSong) {
      return;
    }
    setMetadata({
      title: selectedSong.title,
      artist: selectedSong.artist,
      album: selectedSong.album,
      releaseYear: selectedSong.releaseYear,
      trackNumberAlbum: selectedSong.trackNumberAlbum,
    });
    setSuccessMessage("");
  }, [selectedSong]);

  const updateMutation = useMutation({
    mutationFn: ({ songId, payload }) => api.updateSongMetadata(songId, payload),
    onSuccess: (song) => {
      queryClient.invalidateQueries({ queryKey: ["songs"] });
      setMetadata({
        title: song.title,
        artist: song.artist,
        album: song.album,
        releaseYear: song.releaseYear,
        trackNumberAlbum: song.trackNumberAlbum,
      });
      setSuccessMessage("Los tags se escribieron y verificaron en el archivo MP3.");
    },
  });
  const refreshMutation = useMutation({
    mutationFn: api.refreshSongMetadata,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["songs"] });
      setSuccessMessage("La metadata se ha vuelto a leer desde el MP3.");
    },
  });
  const activateMutation = useMutation({
    mutationFn: api.activateLibrary,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["libraries"] }),
  });
  const scanMutation = useMutation({
    mutationFn: api.scanLibrary,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks"] }),
  });

  function saveMetadata(event) {
    event.preventDefault();
    if (!selectedSongId) {
      return;
    }
    setSuccessMessage("");
    updateMutation.mutate({
      songId: selectedSongId,
      payload: {
        ...metadata,
        releaseYear: Number(metadata.releaseYear) || 0,
        trackNumberAlbum: Number(metadata.trackNumberAlbum) || 0,
      },
    });
  }

  const error =
    updateMutation.error ||
    refreshMutation.error ||
    activateMutation.error ||
    scanMutation.error ||
    songsQuery.error;

  return (
    <div className={ui.page}>
      <header className={ui.pageHeader}>
        <div>
          <span className={ui.eyebrow}>Herramienta 02</span>
          <h1>Editor de metadata</h1>
          <p>
            Trabaja sobre un MP3 cada vez. SoundShelf escribe los tags, vuelve a
            leer el archivo y solo entonces actualiza el índice local.
          </p>
        </div>
        <div className={ui.headerActions}>
          <button
            className={ui.buttonSecondary}
            disabled={!libraryId}
            onClick={() => {
              activateMutation.mutate(Number(libraryId), {
                onSuccess: () => scanMutation.mutate(Number(libraryId)),
              });
            }}
            type="button"
          >
            Escanear biblioteca
          </button>
        </div>
      </header>

      {error && <div className={ui.alertError}>{error.message}</div>}
      {successMessage && <div className={ui.alertSuccess}>{successMessage}</div>}

      <section className={ui.panel}>
        <div className={ui.panelHeader}>
          <div>
            <h2>Explorar canciones</h2>
            <p>Filtra el índice sin tocar los archivos.</p>
          </div>
          <span className={ui.badgeNeutral}>{songsQuery.data?.total || 0} canciones</span>
        </div>
        <div className={ui.panelBody}>
          <div className={ui.filters}>
            <label className={ui.field}>
              <span>Biblioteca</span>
              <select
                className={ui.select}
                onChange={(event) => {
                  setLibraryId(event.target.value);
                  setSelectedSongId(null);
                  setPage(1);
                }}
                value={libraryId}
              >
                <option value="">Selecciona una biblioteca</option>
                {(librariesQuery.data || []).map((library) => (
                  <option key={library.id} value={library.id}>
                    {library.displayName}
                  </option>
                ))}
              </select>
            </label>
            <label className={ui.field}>
              <span>Buscar</span>
              <input
                className={ui.input}
                onChange={(event) => {
                  setSearch(event.target.value);
                  setPage(1);
                }}
                placeholder="Título, artista, álbum o archivo"
                value={search}
              />
            </label>
            <label className={ui.field}>
              <span>Disponibilidad</span>
              <select
                className={ui.select}
                onChange={(event) => {
                  setAvailability(event.target.value);
                  setPage(1);
                }}
                value={availability}
              >
                <option value="all">Todas</option>
                <option value="available">Disponibles</option>
                <option value="missing">No disponibles</option>
              </select>
            </label>
            <label className={ui.field}>
              <span>Orden</span>
              <select
                className={ui.select}
                onChange={(event) => setSortBy(event.target.value)}
                value={sortBy}
              >
                <option value="title">Título</option>
                <option value="artist">Artista</option>
                <option value="album">Álbum</option>
                <option value="year">Año</option>
                <option value="fileName">Archivo</option>
              </select>
            </label>
            <button
              aria-label="Invertir orden"
              className={ui.iconButton}
              onClick={() =>
                setSortDirection((current) => (current === "asc" ? "desc" : "asc"))
              }
              type="button"
            >
              {sortDirection === "asc" ? "↑" : "↓"}
            </button>
          </div>
        </div>
        <div className={ui.detailGrid}>
          <div className={ui.tableWrap}>
            {!libraryId && (
              <div className={ui.empty}>Selecciona una biblioteca para comenzar.</div>
            )}
            {libraryId && songsQuery.isLoading && (
              <div className={ui.empty}>Leyendo el índice local…</div>
            )}
            {songsQuery.data && !songsQuery.data.items.length && (
              <div className={ui.empty}>
                <div>
                  <strong>No hay canciones para estos filtros</strong>
                  <span>Escanea la biblioteca o cambia la búsqueda.</span>
                </div>
              </div>
            )}
            {songsQuery.data?.items.length > 0 && (
              <table className={ui.table}>
                <thead>
                  <tr>
                    <th>Disponibilidad</th>
                    <th>Canción</th>
                    <th>Álbum</th>
                    <th>Año</th>
                  </tr>
                </thead>
                <tbody>
                  {songsQuery.data.items.map((song) => (
                    <tr
                      className={`${ui.clickableRow} ${
                        selectedSongId === song.id ? ui.selectedRow : ""
                      }`}
                      key={song.id}
                      onClick={() => setSelectedSongId(song.id)}
                    >
                      <td>
                        <span
                          className={
                            song.isAvailable ? ui.badgeSuccess : ui.badgeDanger
                          }
                        >
                          {song.isAvailable ? "Disponible" : "Ausente"}
                        </span>
                      </td>
                      <td>
                        <span className={ui.primaryCell}>{song.title}</span>
                        <span className={ui.secondaryCell}>
                          {song.artist || "Sin artista"} · {song.fileName}
                        </span>
                      </td>
                      <td>{song.album || "—"}</td>
                      <td>{song.releaseYear || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <aside className={ui.detailPanel} aria-label="Editor de tags">
            {selectedSong ? (
              <>
                <div>
                  <span className={selectedSong.isAvailable ? ui.badgeSuccess : ui.badgeDanger}>
                    {selectedSong.isAvailable ? "Archivo listo" : "Archivo ausente"}
                  </span>
                </div>
                <h3>{selectedSong.fileName}</h3>
                <p className={ui.muted}>{selectedSong.filePath}</p>
                <form className={ui.formGrid} onSubmit={saveMetadata}>
                  <label className={`${ui.field} ${ui.fieldFull}`}>
                    <span>Título</span>
                    <input
                      className={ui.input}
                      disabled={!selectedSong.isAvailable}
                      onChange={(event) =>
                        setMetadata((current) => ({
                          ...current,
                          title: event.target.value,
                        }))
                      }
                      required
                      value={metadata.title}
                    />
                  </label>
                  <label className={`${ui.field} ${ui.fieldFull}`}>
                    <span>Artista</span>
                    <input
                      className={ui.input}
                      disabled={!selectedSong.isAvailable}
                      onChange={(event) =>
                        setMetadata((current) => ({
                          ...current,
                          artist: event.target.value,
                        }))
                      }
                      value={metadata.artist}
                    />
                  </label>
                  <label className={`${ui.field} ${ui.fieldFull}`}>
                    <span>Álbum</span>
                    <input
                      className={ui.input}
                      disabled={!selectedSong.isAvailable}
                      onChange={(event) =>
                        setMetadata((current) => ({
                          ...current,
                          album: event.target.value,
                        }))
                      }
                      value={metadata.album}
                    />
                  </label>
                  <label className={ui.field}>
                    <span>Año</span>
                    <input
                      className={ui.input}
                      disabled={!selectedSong.isAvailable}
                      max="9999"
                      min="0"
                      onChange={(event) =>
                        setMetadata((current) => ({
                          ...current,
                          releaseYear: event.target.value,
                        }))
                      }
                      type="number"
                      value={metadata.releaseYear}
                    />
                  </label>
                  <label className={ui.field}>
                    <span>Pista</span>
                    <input
                      className={ui.input}
                      disabled={!selectedSong.isAvailable}
                      min="0"
                      onChange={(event) =>
                        setMetadata((current) => ({
                          ...current,
                          trackNumberAlbum: event.target.value,
                        }))
                      }
                      type="number"
                      value={metadata.trackNumberAlbum}
                    />
                  </label>
                  <button
                    className={`${ui.button} ${ui.fieldFull}`}
                    disabled={!selectedSong.isAvailable || updateMutation.isPending}
                    type="submit"
                  >
                    Escribir y verificar tags
                  </button>
                </form>
                <button
                  className={ui.buttonSecondary}
                  disabled={!selectedSong.isAvailable || refreshMutation.isPending}
                  onClick={() => refreshMutation.mutate(selectedSong.id)}
                  type="button"
                >
                  Releer desde el MP3
                </button>
              </>
            ) : (
              <div className={ui.empty}>
                Selecciona una canción para abrir el editor.
              </div>
            )}
          </aside>
        </div>
        {songsQuery.data && (
          <div className={ui.pagination}>
            <span>
              Página {songsQuery.data.page} · {songsQuery.data.total} canciones
            </span>
            <button
              className={ui.buttonSecondary}
              disabled={page <= 1}
              onClick={() => setPage((current) => current - 1)}
              type="button"
            >
              Anterior
            </button>
            <button
              className={ui.buttonSecondary}
              disabled={page * 25 >= songsQuery.data.total}
              onClick={() => setPage((current) => current + 1)}
              type="button"
            >
              Siguiente
            </button>
          </div>
        )}
      </section>

      <section className={ui.panel}>
        <div className={ui.panelHeader}>
          <div>
            <h2>Escaneos</h2>
            <p>La interfaz sigue disponible mientras se procesa la carpeta.</p>
          </div>
        </div>
        <div className={ui.panelBody}>
          <TaskList kind="library_scan" />
        </div>
      </section>
    </div>
  );
}
