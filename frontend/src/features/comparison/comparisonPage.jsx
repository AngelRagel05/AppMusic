import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { api } from "../../shared/api/apiClient";
import { TaskList } from "../../shared/components/taskList/taskList";
import { useTaskCompletionRefresh } from "../../shared/hooks/useTaskCompletionRefresh";
import ui from "../../shared/styles/ui.module.css";

const comparisonRefreshKeys = [
  ["comparison"],
  ["comparisonHistory"],
  ["playlists"],
  ["libraries"],
];
const scanRefreshKeys = [["libraries"], ["songs"], ["comparison"]];
const importRefreshKeys = [["playlists"], ["comparison"]];

function statusClass(status) {
  if (status === "found" || status === "completed") {
    return ui.badgeSuccess;
  }
  if (status === "possible_match") {
    return ui.badgeWarning;
  }
  if (status === "missing" || status === "failed") {
    return ui.badgeDanger;
  }
  return ui.badgeNeutral;
}

function statusLabel(status) {
  return {
    found: "Encontrada",
    missing: "Faltante",
    possible_match: "Posible",
  }[status] || status;
}

export function ComparisonPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedHistoryId, setSelectedHistoryId] = useState(null);
  const [editingLibraryId, setEditingLibraryId] = useState(null);
  const [editingPlaylistId, setEditingPlaylistId] = useState(null);
  const [editingTermId, setEditingTermId] = useState(null);
  const [libraryForm, setLibraryForm] = useState({ path: "", displayName: "" });
  const [playlistForm, setPlaylistForm] = useState({
    playlistUrl: "",
    title: "",
  });
  const [termForm, setTermForm] = useState({
    term: "",
    scope: "title",
    language: "global",
  });

  useTaskCompletionRefresh("library_comparison", comparisonRefreshKeys);
  useTaskCompletionRefresh("library_scan", scanRefreshKeys);
  useTaskCompletionRefresh("playlist_import", importRefreshKeys);

  const librariesQuery = useQuery({
    queryKey: ["libraries"],
    queryFn: api.libraries,
  });
  const playlistsQuery = useQuery({
    queryKey: ["playlists"],
    queryFn: api.playlists,
  });
  const ignoredTermsQuery = useQuery({
    queryKey: ["ignoredTerms"],
    queryFn: api.ignoredTerms,
  });
  const historyQuery = useQuery({
    queryKey: ["comparisonHistory"],
    queryFn: api.comparisonHistory,
    retry: false,
  });
  const activeLibrary = librariesQuery.data?.find((library) => library.isActive);
  const activePlaylist = playlistsQuery.data?.find((playlist) => playlist.isActive);
  const songsQuery = useQuery({
    queryKey: ["songs", activeLibrary?.id, "comparisonCandidates"],
    queryFn: () =>
      api.songs({
        libraryId: activeLibrary.id,
        availability: "available",
        pageSize: 100,
      }),
    enabled: Boolean(activeLibrary),
  });
  const comparisonQuery = useQuery({
    queryKey: [
      "comparison",
      selectedHistoryId,
      search,
      statusFilter,
      page,
    ],
    queryFn: () => {
      const filters = {
        search,
        status: statusFilter,
        page,
        pageSize: 25,
      };
      return selectedHistoryId
        ? api.comparisonById(selectedHistoryId, filters)
        : api.comparison(filters);
    },
    retry: false,
    enabled: Boolean(activeLibrary && activePlaylist),
  });

  function invalidatingMutation(mutationFn, queryKeys) {
    return {
      mutationFn,
      onSuccess: () => {
        queryKeys.forEach((queryKey) => {
          queryClient.invalidateQueries({ queryKey });
        });
      },
    };
  }

  const createLibraryMutation = useMutation(
    invalidatingMutation(api.createLibrary, [["libraries"]]),
  );
  const updateLibraryMutation = useMutation(
    invalidatingMutation(
      ({ libraryId, payload }) => api.updateLibrary(libraryId, payload),
      [["libraries"]],
    ),
  );
  const deleteLibraryMutation = useMutation(
    invalidatingMutation(api.deleteLibrary, [
      ["libraries"],
      ["songs"],
      ["comparison"],
      ["comparisonHistory"],
    ]),
  );
  const activateLibraryMutation = useMutation(
    invalidatingMutation(api.activateLibrary, [
      ["libraries"],
      ["songs"],
      ["comparison"],
    ]),
  );
  const scanMutation = useMutation(
    invalidatingMutation(api.scanLibrary, [["tasks"]]),
  );
  const createPlaylistMutation = useMutation(
    invalidatingMutation(api.createPlaylist, [["playlists"]]),
  );
  const updatePlaylistMutation = useMutation(
    invalidatingMutation(
      ({ playlistId, payload }) => api.updatePlaylist(playlistId, payload),
      [["playlists"]],
    ),
  );
  const deletePlaylistMutation = useMutation(
    invalidatingMutation(api.deletePlaylist, [
      ["playlists"],
      ["comparison"],
      ["comparisonHistory"],
    ]),
  );
  const activatePlaylistMutation = useMutation(
    invalidatingMutation(api.activatePlaylist, [
      ["playlists"],
      ["comparison"],
    ]),
  );
  const importMutation = useMutation(
    invalidatingMutation(api.importPlaylist, [["tasks"]]),
  );
  const compareMutation = useMutation(
    invalidatingMutation(api.runComparison, [["tasks"]]),
  );
  const updateItemMutation = useMutation(
    invalidatingMutation(
      ({ comparisonId, itemId, payload }) =>
        api.updateComparisonItem(comparisonId, itemId, payload),
      [["comparison"]],
    ),
  );
  const createTermMutation = useMutation(
    invalidatingMutation(api.createIgnoredTerm, [["ignoredTerms"]]),
  );
  const updateTermMutation = useMutation(
    invalidatingMutation(
      ({ termId, payload }) => api.updateIgnoredTerm(termId, payload),
      [["ignoredTerms"], ["comparison"]],
    ),
  );
  const stateTermMutation = useMutation(
    invalidatingMutation(
      ({ termId, isActive }) => api.setIgnoredTermState(termId, isActive),
      [["ignoredTerms"]],
    ),
  );
  const deleteTermMutation = useMutation(
    invalidatingMutation(api.deleteIgnoredTerm, [["ignoredTerms"]]),
  );
  const mutationError = [
    createLibraryMutation,
    updateLibraryMutation,
    deleteLibraryMutation,
    activateLibraryMutation,
    scanMutation,
    createPlaylistMutation,
    updatePlaylistMutation,
    deletePlaylistMutation,
    activatePlaylistMutation,
    importMutation,
    compareMutation,
    updateItemMutation,
    createTermMutation,
    updateTermMutation,
    stateTermMutation,
    deleteTermMutation,
  ].find((mutation) => mutation.isError)?.error;

  const selectedComparisonItem = useMemo(() => {
    if (!selectedItem) {
      return null;
    }
    return (
      comparisonQuery.data?.items.find(
        (item) =>
          item.youtubePlaylistItemId === selectedItem.youtubePlaylistItemId,
      ) || selectedItem
    );
  }, [comparisonQuery.data, selectedItem]);
  const summary = comparisonQuery.data?.summary;

  function submitLibrary(event) {
    event.preventDefault();
    const resetForm = () => {
      setEditingLibraryId(null);
      setLibraryForm({ path: "", displayName: "" });
    };
    if (editingLibraryId) {
      updateLibraryMutation.mutate(
        { libraryId: editingLibraryId, payload: libraryForm },
        { onSuccess: resetForm },
      );
      return;
    }
    createLibraryMutation.mutate(libraryForm, { onSuccess: resetForm });
  }

  function submitPlaylist(event) {
    event.preventDefault();
    const resetForm = () => {
      setEditingPlaylistId(null);
      setPlaylistForm({ playlistUrl: "", title: "" });
    };
    if (editingPlaylistId) {
      updatePlaylistMutation.mutate(
        { playlistId: editingPlaylistId, payload: playlistForm },
        { onSuccess: resetForm },
      );
      return;
    }
    createPlaylistMutation.mutate(playlistForm, { onSuccess: resetForm });
  }

  function submitTerm(event) {
    event.preventDefault();
    const resetForm = () => {
      setEditingTermId(null);
      setTermForm({ term: "", scope: "title", language: "global" });
    };
    if (editingTermId) {
      updateTermMutation.mutate(
        { termId: editingTermId, payload: termForm },
        { onSuccess: resetForm },
      );
      return;
    }
    createTermMutation.mutate(termForm, { onSuccess: resetForm });
  }

  function editActiveLibrary() {
    if (!activeLibrary) {
      return;
    }
    setEditingLibraryId(activeLibrary.id);
    setLibraryForm({
      path: activeLibrary.path,
      displayName: activeLibrary.displayName,
    });
  }

  function deleteActiveLibrary() {
    if (
      !activeLibrary ||
      !window.confirm(
        `¿Eliminar la biblioteca "${activeLibrary.displayName}"?`,
      )
    ) {
      return;
    }
    deleteLibraryMutation.mutate(activeLibrary.id, {
      onSuccess: () => {
        setEditingLibraryId(null);
        setLibraryForm({ path: "", displayName: "" });
      },
    });
  }

  function editActivePlaylist() {
    if (!activePlaylist) {
      return;
    }
    setEditingPlaylistId(activePlaylist.id);
    setPlaylistForm({
      playlistUrl: activePlaylist.playlistUrl,
      title: activePlaylist.title,
    });
  }

  function deleteActivePlaylist() {
    if (
      !activePlaylist ||
      !window.confirm(`¿Eliminar la playlist "${activePlaylist.title}"?`)
    ) {
      return;
    }
    deletePlaylistMutation.mutate(activePlaylist.id, {
      onSuccess: () => {
        setEditingPlaylistId(null);
        setPlaylistForm({ playlistUrl: "", title: "" });
      },
    });
  }

  function deleteTerm(term) {
    if (!window.confirm(`¿Eliminar el término ignorado "${term.term}"?`)) {
      return;
    }
    deleteTermMutation.mutate(term.id, {
      onSuccess: () => {
        if (editingTermId === term.id) {
          setEditingTermId(null);
          setTermForm({ term: "", scope: "title", language: "global" });
        }
      },
    });
  }

  function saveManualDecision(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const localSongValue = formData.get("localSongId");
    updateItemMutation.mutate({
      comparisonId: comparisonQuery.data.playlistComparisonId,
      itemId: selectedComparisonItem.youtubePlaylistItemId,
      payload: {
        matchStatus: formData.get("matchStatus"),
        localSongId: localSongValue ? Number(localSongValue) : null,
      },
    });
  }

  return (
    <div className={ui.page}>
      <header className={ui.pageHeader}>
        <div>
          <span className={ui.eyebrow}>Herramienta 01</span>
          <h1>Comparación de biblioteca</h1>
          <p>
            Contrasta el snapshot de una playlist de YouTube con tus MP3 locales,
            revisa ambigüedades y conserva un histórico verificable.
          </p>
        </div>
        <div className={ui.headerActions}>
          <button
            className={ui.buttonSecondary}
            disabled={!activeLibrary || !activePlaylist || compareMutation.isPending}
            onClick={() => compareMutation.mutate(true)}
            type="button"
          >
            Recalcular todo
          </button>
          <button
            className={ui.button}
            disabled={!activeLibrary || !activePlaylist || compareMutation.isPending}
            onClick={() => compareMutation.mutate(false)}
            type="button"
          >
            Ejecutar comparación
          </button>
        </div>
      </header>

      {mutationError && <div className={ui.alertError}>{mutationError.message}</div>}

      <section className={ui.panel}>
        <div className={ui.panelHeader}>
          <div>
            <h2>Contexto de trabajo</h2>
            <p>Selecciona las dos fuentes que formarán el snapshot.</p>
          </div>
          <span className={activeLibrary && activePlaylist ? ui.badgeSuccess : ui.badgeWarning}>
            {activeLibrary && activePlaylist ? "Contexto listo" : "Configuración pendiente"}
          </span>
        </div>
        <div className={ui.panelBody}>
          <div className={ui.gridTwo}>
            <div className={ui.contextCard}>
              <div className={ui.contextTitle}>
                <div>
                  <h3>Biblioteca local</h3>
                  <p>{activeLibrary?.path || "Ninguna biblioteca activa"}</p>
                </div>
                <span className={activeLibrary ? ui.badgeSuccess : ui.badgeNeutral}>
                  {activeLibrary ? "Activa" : "Vacía"}
                </span>
              </div>
              <label className={ui.field}>
                <span>Biblioteca guardada</span>
                <select
                  className={ui.select}
                  onChange={(event) =>
                    event.target.value &&
                    activateLibraryMutation.mutate(Number(event.target.value))
                  }
                  value={activeLibrary?.id || ""}
                >
                  <option value="">Selecciona una biblioteca</option>
                  {(librariesQuery.data || []).map((library) => (
                    <option key={library.id} value={library.id}>
                      {library.displayName}
                    </option>
                  ))}
                </select>
              </label>
              <div className={ui.inlineActions}>
                <button
                  className={ui.buttonSecondary}
                  disabled={!activeLibrary}
                  onClick={editActiveLibrary}
                  type="button"
                >
                  Editar activa
                </button>
                <button
                  className={ui.buttonDanger}
                  disabled={!activeLibrary || deleteLibraryMutation.isPending}
                  onClick={deleteActiveLibrary}
                  type="button"
                >
                  Eliminar activa
                </button>
              </div>
              <form className={ui.formGrid} onSubmit={submitLibrary}>
                <label className={`${ui.field} ${ui.fieldFull}`}>
                  <span>Ruta de carpeta</span>
                  <input
                    className={ui.input}
                    onChange={(event) =>
                      setLibraryForm((current) => ({
                        ...current,
                        path: event.target.value,
                      }))
                    }
                    placeholder="C:\Música\Biblioteca"
                    required
                    value={libraryForm.path}
                  />
                </label>
                <label className={ui.field}>
                  <span>Nombre visible</span>
                  <input
                    className={ui.input}
                    onChange={(event) =>
                      setLibraryForm((current) => ({
                        ...current,
                        displayName: event.target.value,
                      }))
                    }
                    placeholder="Biblioteca principal"
                    value={libraryForm.displayName}
                  />
                </label>
                <div className={`${ui.inlineActions} ${ui.field}`}>
                  <button className={ui.buttonSecondary} type="submit">
                    {editingLibraryId ? "Actualizar" : "Guardar"}
                  </button>
                  {editingLibraryId && (
                    <button
                      className={ui.buttonSecondary}
                      onClick={() => {
                        setEditingLibraryId(null);
                        setLibraryForm({ path: "", displayName: "" });
                      }}
                      type="button"
                    >
                      Cancelar edición
                    </button>
                  )}
                  <button
                    className={ui.button}
                    disabled={!activeLibrary}
                    onClick={() => scanMutation.mutate(activeLibrary.id)}
                    type="button"
                  >
                    Escanear
                  </button>
                </div>
              </form>
            </div>

            <div className={ui.contextCard}>
              <div className={ui.contextTitle}>
                <div>
                  <h3>Playlist de YouTube</h3>
                  <p>
                    {activePlaylist
                      ? `${activePlaylist.itemCount} items importados`
                      : "Ninguna playlist activa"}
                  </p>
                </div>
                <span className={activePlaylist ? ui.badgeSuccess : ui.badgeNeutral}>
                  {activePlaylist ? "Activa" : "Vacía"}
                </span>
              </div>
              <label className={ui.field}>
                <span>Playlist guardada</span>
                <select
                  className={ui.select}
                  onChange={(event) =>
                    event.target.value &&
                    activatePlaylistMutation.mutate(Number(event.target.value))
                  }
                  value={activePlaylist?.id || ""}
                >
                  <option value="">Selecciona una playlist</option>
                  {(playlistsQuery.data || []).map((playlist) => (
                    <option key={playlist.id} value={playlist.id}>
                      {playlist.title}
                    </option>
                  ))}
                </select>
              </label>
              <div className={ui.inlineActions}>
                <button
                  className={ui.buttonSecondary}
                  disabled={!activePlaylist}
                  onClick={editActivePlaylist}
                  type="button"
                >
                  Editar activa
                </button>
                <button
                  className={ui.buttonDanger}
                  disabled={!activePlaylist || deletePlaylistMutation.isPending}
                  onClick={deleteActivePlaylist}
                  type="button"
                >
                  Eliminar activa
                </button>
              </div>
              <form className={ui.formGrid} onSubmit={submitPlaylist}>
                <label className={`${ui.field} ${ui.fieldFull}`}>
                  <span>URL de playlist</span>
                  <input
                    className={ui.input}
                    onChange={(event) =>
                      setPlaylistForm((current) => ({
                        ...current,
                        playlistUrl: event.target.value,
                      }))
                    }
                    placeholder="https://www.youtube.com/playlist?list=…"
                    required
                    type="url"
                    value={playlistForm.playlistUrl}
                  />
                </label>
                <label className={ui.field}>
                  <span>Nombre visible</span>
                  <input
                    className={ui.input}
                    onChange={(event) =>
                      setPlaylistForm((current) => ({
                        ...current,
                        title: event.target.value,
                      }))
                    }
                    placeholder="Favoritas"
                    required
                    value={playlistForm.title}
                  />
                </label>
                <div className={`${ui.inlineActions} ${ui.field}`}>
                  <button className={ui.buttonSecondary} type="submit">
                    {editingPlaylistId ? "Actualizar" : "Guardar"}
                  </button>
                  {editingPlaylistId && (
                    <button
                      className={ui.buttonSecondary}
                      onClick={() => {
                        setEditingPlaylistId(null);
                        setPlaylistForm({ playlistUrl: "", title: "" });
                      }}
                      type="button"
                    >
                      Cancelar edición
                    </button>
                  )}
                  <button
                    className={ui.button}
                    disabled={!activePlaylist}
                    onClick={() => importMutation.mutate(activePlaylist.id)}
                    type="button"
                  >
                    Importar
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>

      <section aria-label="Resumen de comparación" className={ui.statGrid}>
        <div className={ui.stat}>
          <span>Total comparado</span>
          <strong>{summary?.totalCompared ?? "—"}</strong>
        </div>
        <div className={ui.stat}>
          <span>Encontradas</span>
          <strong>{summary?.foundCount ?? "—"}</strong>
        </div>
        <div className={ui.stat}>
          <span>Posibles</span>
          <strong>{summary?.possibleMatchCount ?? "—"}</strong>
        </div>
        <div className={ui.stat}>
          <span>Faltantes</span>
          <strong>{summary?.missingCount ?? "—"}</strong>
        </div>
      </section>

      <section className={ui.panel}>
        <div className={ui.panelHeader}>
          <div>
            <h2>Resultados</h2>
            <p>
              {selectedHistoryId
                ? `Snapshot histórico #${selectedHistoryId}`
                : "Último snapshot del contexto activo"}
            </p>
          </div>
          <div className={ui.filters}>
            <input
              aria-label="Buscar resultados"
              className={ui.input}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
              placeholder="Buscar título o artista"
              value={search}
            />
            <select
              aria-label="Filtrar por estado"
              className={ui.select}
              onChange={(event) => {
                setStatusFilter(event.target.value);
                setPage(1);
              }}
              value={statusFilter}
            >
              <option value="">Todos los estados</option>
              <option value="found">Encontradas</option>
              <option value="possible_match">Posibles</option>
              <option value="missing">Faltantes</option>
            </select>
            {selectedHistoryId && (
              <button
                className={ui.buttonSecondary}
                onClick={() => setSelectedHistoryId(null)}
                type="button"
              >
                Volver al último
              </button>
            )}
          </div>
        </div>
        <div className={ui.detailGrid}>
          <div className={ui.tableWrap}>
            {comparisonQuery.isLoading && (
              <div className={ui.empty}>Cargando comparación…</div>
            )}
            {comparisonQuery.isError && (
              <div className={ui.empty}>
                <div>
                  <strong>Aún no hay resultados</strong>
                  <span>{comparisonQuery.error.message}</span>
                </div>
              </div>
            )}
            {comparisonQuery.data && (
              <table className={ui.table}>
                <thead>
                  <tr>
                    <th>Estado</th>
                    <th>YouTube</th>
                    <th>Coincidencia local</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonQuery.data.items.map((item) => (
                    <tr
                      className={`${ui.clickableRow} ${
                        selectedComparisonItem?.youtubePlaylistItemId ===
                        item.youtubePlaylistItemId
                          ? ui.selectedRow
                          : ""
                      }`}
                      key={item.youtubePlaylistItemId}
                      onClick={() => setSelectedItem(item)}
                    >
                      <td>
                        <span className={statusClass(item.comparisonStatus)}>
                          {statusLabel(item.comparisonStatus)}
                        </span>
                      </td>
                      <td>
                        <span className={ui.primaryCell}>{item.youtubeTitle}</span>
                        <span className={ui.secondaryCell}>{item.youtubeArtist}</span>
                      </td>
                      <td>
                        <span className={ui.primaryCell}>
                          {item.localTitle || "Sin enlace"}
                        </span>
                        <span className={ui.secondaryCell}>
                          {item.localArtist || item.reason}
                        </span>
                      </td>
                      <td>{item.score.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <aside className={ui.detailPanel} aria-label="Detalle del resultado">
            {selectedComparisonItem ? (
              <>
                <div>
                  <span className={statusClass(selectedComparisonItem.comparisonStatus)}>
                    {statusLabel(selectedComparisonItem.comparisonStatus)}
                  </span>
                </div>
                <h3>{selectedComparisonItem.youtubeTitle}</h3>
                <dl className={ui.definitionList}>
                  <div>
                    <dt>Artista de YouTube</dt>
                    <dd>{selectedComparisonItem.youtubeArtist}</dd>
                  </div>
                  <div>
                    <dt>Decisión</dt>
                    <dd>{selectedComparisonItem.reason}</dd>
                  </div>
                  <div>
                    <dt>Origen de decisión</dt>
                    <dd>{selectedComparisonItem.matchedBy || "Motor automático"}</dd>
                  </div>
                </dl>
                <form className={ui.formGrid} onSubmit={saveManualDecision}>
                  <label className={`${ui.field} ${ui.fieldFull}`}>
                    <span>Estado manual</span>
                    <select
                      className={ui.select}
                      defaultValue={selectedComparisonItem.comparisonStatus}
                      key={`${selectedComparisonItem.youtubePlaylistItemId}:status`}
                      name="matchStatus"
                    >
                      <option value="found">Encontrada</option>
                      <option value="possible_match">Posible</option>
                      <option value="missing">Faltante</option>
                    </select>
                  </label>
                  <label className={`${ui.field} ${ui.fieldFull}`}>
                    <span>Canción local</span>
                    <select
                      className={ui.select}
                      defaultValue={selectedComparisonItem.localSongId || ""}
                      key={`${selectedComparisonItem.youtubePlaylistItemId}:song`}
                      name="localSongId"
                    >
                      <option value="">Sin enlace local</option>
                      {(songsQuery.data?.items || []).map((song) => (
                        <option key={song.id} value={song.id}>
                          {song.artist} — {song.title}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button className={`${ui.button} ${ui.fieldFull}`} type="submit">
                    Guardar decisión
                  </button>
                </form>
                {selectedComparisonItem.comparisonStatus !== "found" && activeLibrary && (
                  <button
                    className={ui.buttonSecondary}
                    disabled={!comparisonQuery.data?.playlistComparisonId}
                    onClick={() =>
                      navigate(
                        "/downloads?comparisonId="
                          + comparisonQuery.data.playlistComparisonId,
                      )
                    }
                    type="button"
                  >
                    Revisar faltantes en Descargas
                  </button>
                )}
              </>
            ) : (
              <div className={ui.empty}>
                Selecciona una fila para revisar el razonamiento y corregirla.
              </div>
            )}
          </aside>
        </div>
        {comparisonQuery.data && (
          <div className={ui.pagination}>
            <span>
              Página {comparisonQuery.data.page} · {comparisonQuery.data.total} resultados
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
              disabled={page * 25 >= comparisonQuery.data.total}
              onClick={() => setPage((current) => current + 1)}
              type="button"
            >
              Siguiente
            </button>
          </div>
        )}
      </section>

      <div className={ui.gridTwo}>
        <section className={ui.panel}>
          <div className={ui.panelHeader}>
            <div>
              <h2>Términos ignorados</h2>
              <p>Ajusta la normalización del matching.</p>
            </div>
          </div>
          <div className={ui.panelBody}>
            <form className={ui.formGrid} onSubmit={submitTerm}>
              <label className={ui.field}>
                <span>Término</span>
                <input
                  className={ui.input}
                  onChange={(event) =>
                    setTermForm((current) => ({
                      ...current,
                      term: event.target.value,
                    }))
                  }
                  required
                  value={termForm.term}
                />
              </label>
              <label className={ui.field}>
                <span>Ámbito</span>
                <select
                  className={ui.select}
                  onChange={(event) =>
                    setTermForm((current) => ({
                      ...current,
                      scope: event.target.value,
                    }))
                  }
                  value={termForm.scope}
                >
                  <option value="title">Título</option>
                  <option value="artist">Artista</option>
                  <option value="all">Todo</option>
                </select>
              </label>
              <button className={`${ui.button} ${ui.fieldFull}`} type="submit">
                {editingTermId ? "Actualizar término" : "Añadir término"}
              </button>
              {editingTermId && (
                <button
                  className={`${ui.buttonSecondary} ${ui.fieldFull}`}
                  onClick={() => {
                    setEditingTermId(null);
                    setTermForm({
                      term: "",
                      scope: "title",
                      language: "global",
                    });
                  }}
                  type="button"
                >
                  Cancelar edición
                </button>
              )}
            </form>
            <div className={ui.tableWrap}>
              <table className={ui.table}>
                <thead>
                  <tr>
                    <th>Término</th>
                    <th>Ámbito</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {(ignoredTermsQuery.data || []).map((term) => (
                    <tr key={term.id}>
                      <td>
                        <span className={ui.primaryCell}>{term.term}</span>
                        <span className={ui.secondaryCell}>{term.language}</span>
                      </td>
                      <td>{term.scope}</td>
                      <td>
                        <div className={ui.inlineActions}>
                          <button
                            className={ui.buttonSecondary}
                            onClick={() => {
                              setEditingTermId(term.id);
                              setTermForm({
                                term: term.term,
                                scope: term.scope,
                                language: term.language,
                              });
                            }}
                            type="button"
                          >
                            Editar
                          </button>
                          <button
                            className={ui.buttonSecondary}
                            onClick={() =>
                              stateTermMutation.mutate({
                                termId: term.id,
                                isActive: !term.isActive,
                              })
                            }
                            type="button"
                          >
                            {term.isActive ? "Desactivar" : "Activar"}
                          </button>
                          <button
                            className={ui.buttonDanger}
                            onClick={() => deleteTerm(term)}
                            type="button"
                          >
                            Eliminar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section className={ui.panel}>
          <div className={ui.panelHeader}>
            <div>
              <h2>Histórico</h2>
              <p>Últimos snapshots del contexto activo.</p>
            </div>
          </div>
          <div className={ui.panelBody}>
            <div className={ui.taskList}>
              {(historyQuery.data || []).map((entry) => (
                <button
                  className={ui.taskItem}
                  key={entry.comparisonId}
                  onClick={() => {
                    setSelectedHistoryId(entry.comparisonId);
                    setPage(1);
                  }}
                  type="button"
                >
                  <div className={ui.taskTop}>
                    <strong>Snapshot #{entry.comparisonId}</strong>
                    <span>
                      {new Date(entry.comparedAt).toLocaleString("es-ES")}
                    </span>
                  </div>
                  <span className={ui.muted}>
                    {entry.foundCount} encontradas · {entry.possibleMatchCount} posibles ·{" "}
                    {entry.missingCount} faltantes
                  </span>
                </button>
              ))}
              {!historyQuery.data?.length && (
                <p className={ui.muted}>No hay snapshots guardados todavía.</p>
              )}
            </div>
          </div>
        </section>
      </div>

      <section className={ui.panel}>
        <div className={ui.panelHeader}>
          <div>
            <h2>Operaciones en segundo plano</h2>
            <p>El estado se actualiza mediante polling local.</p>
          </div>
        </div>
        <div className={ui.panelBody}>
          <TaskList kind="library_comparison" />
          <br />
          <TaskList kind="library_scan" />
          <br />
          <TaskList kind="playlist_import" />
        </div>
      </section>
    </div>
  );
}
