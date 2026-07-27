import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";

import { api } from "../../shared/api/apiClient";
import { TaskList } from "../../shared/components/taskList/taskList";
import { useTaskCompletionRefresh } from "../../shared/hooks/useTaskCompletionRefresh";
import ui from "../../shared/styles/ui.module.css";

const downloadRefreshKeys = [["downloads"], ["songs"]];

function statusClass(status) {
  if (status === "completed") {
    return ui.badgeSuccess;
  }
  if (status === "in_progress" || status === "pending") {
    return ui.badgeWarning;
  }
  if (status === "failed" || status === "cancelled") {
    return ui.badgeDanger;
  }
  return ui.badgeNeutral;
}

function statusLabel(status) {
  return {
    pending: "Pendiente",
    in_progress: "En curso",
    completed: "Completada",
    failed: "Fallida",
    cancelled: "Cancelada",
  }[status] || status;
}

export function DownloadsPage() {
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const [libraryId, setLibraryId] = useState("");
  const [sourceText, setSourceText] = useState("");
  const [selectedItemIds, setSelectedItemIds] = useState([]);
  const [successMessage, setSuccessMessage] = useState("");
  const requestedComparisonId = Number(searchParams.get("comparisonId"));
  const comparisonId =
    Number.isInteger(requestedComparisonId) && requestedComparisonId > 0
      ? requestedComparisonId
      : null;

  useTaskCompletionRefresh("audio_download", downloadRefreshKeys);

  const capabilitiesQuery = useQuery({
    queryKey: ["capabilities"],
    queryFn: api.capabilities,
  });
  const librariesQuery = useQuery({
    queryKey: ["libraries"],
    queryFn: api.libraries,
  });
  const downloadsQuery = useQuery({
    queryKey: ["downloads"],
    queryFn: api.downloads,
    refetchInterval: 2500,
  });
  const comparisonCandidatesQuery = useQuery({
    queryKey: ["downloadCandidates", comparisonId],
    queryFn: () =>
      api.comparisonById(comparisonId, {
        status: "missing",
        page: 1,
        pageSize: 50,
      }),
    enabled: Boolean(comparisonId),
    retry: false,
  });
  const activeLibrary = librariesQuery.data?.find((library) => library.isActive);
  const comparisonCandidates = comparisonCandidatesQuery.data?.items || [];
  const candidateFingerprint = comparisonCandidates
    .map((item) => item.youtubePlaylistItemId)
    .join(",");

  useEffect(() => {
    if (!libraryId && activeLibrary) {
      setLibraryId(String(activeLibrary.id));
    }
  }, [activeLibrary, libraryId]);

  useEffect(() => {
    setSelectedItemIds(
      candidateFingerprint
        ? candidateFingerprint.split(",").map((itemId) => Number(itemId))
        : [],
    );
  }, [candidateFingerprint, comparisonId]);

  const createMutation = useMutation({
    mutationFn: api.createDownloads,
    onSuccess: (result) => {
      setSourceText("");
      setSelectedItemIds([]);
      setSuccessMessage(
        `${result.tasks.length} descarga${
          result.tasks.length === 1 ? "" : "s"
        } añadida${result.tasks.length === 1 ? "" : "s"} a la cola.`,
      );
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["downloads"] });
    },
  });
  const retryMutation = useMutation({
    mutationFn: api.retryDownload,
    onSuccess: () => {
      setSuccessMessage("Se ha creado un nuevo intento de descarga.");
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  function submitDownloads(event) {
    event.preventDefault();
    setSuccessMessage("");
    const sourceUrls = sourceText
      .split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean);
    createMutation.mutate({
      localFolderId: Number(libraryId),
      sourceUrls,
      youtubePlaylistItemIds: selectedItemIds,
    });
  }

  const ffmpegAvailable = capabilitiesQuery.data?.ffmpegAvailable;
  const error =
    createMutation.error ||
    retryMutation.error ||
    downloadsQuery.error ||
    comparisonCandidatesQuery.error ||
    capabilitiesQuery.error;
  const downloads = downloadsQuery.data || [];
  const completedCount = downloads.filter(
    (download) => download.status === "completed",
  ).length;
  const failedCount = downloads.filter((download) =>
    ["failed", "cancelled"].includes(download.status),
  ).length;
  const activeCount = downloads.filter((download) =>
    ["pending", "in_progress"].includes(download.status),
  ).length;

  return (
    <div className={ui.page}>
      <header className={ui.pageHeader}>
        <div>
          <span className={ui.eyebrow}>Herramienta 03</span>
          <h1>Descargas de audio</h1>
          <p>
            Descarga con yt-dlp, convierte con FFmpeg e indexa el MP3 resultante
            dentro de una biblioteca registrada.
          </p>
        </div>
        <span className={ffmpegAvailable ? ui.badgeSuccess : ui.badgeDanger}>
          {ffmpegAvailable ? "FFmpeg disponible" : "FFmpeg no disponible"}
        </span>
      </header>

      {error && <div className={ui.alertError}>{error.message}</div>}
      {successMessage && <div className={ui.alertSuccess}>{successMessage}</div>}
      {capabilitiesQuery.data && !ffmpegAvailable && (
        <div className={ui.alertError}>
          Configura <strong>FFMPEG_PATH</strong> con el ejecutable de FFmpeg.
          La cola queda deshabilitada hasta que la capacidad esté disponible.
        </div>
      )}

      {comparisonId && (
        <section className={ui.panel}>
          <div className={ui.panelHeader}>
            <div>
              <h2>Faltantes de la comparación #{comparisonId}</h2>
              <p>
                Selecciona qué items se añadirán a la cola. El módulo recibe solo
                el ID del snapshot persistido.
              </p>
            </div>
            <span className={ui.badgeNeutral}>
              {selectedItemIds.length} seleccionados
            </span>
          </div>
          <div className={ui.panelBody}>
            {comparisonCandidatesQuery.isLoading && (
              <div className={ui.empty}>Cargando faltantes…</div>
            )}
            {!comparisonCandidatesQuery.isLoading &&
              comparisonCandidates.length === 0 && (
                <div className={ui.empty}>
                  Esta comparación no tiene canciones faltantes.
                </div>
              )}
            {comparisonCandidates.length > 0 && (
              <>
                <div className={ui.inlineActions}>
                  <button
                    className={ui.buttonSecondary}
                    onClick={() =>
                      setSelectedItemIds(
                        comparisonCandidates.map(
                          (item) => item.youtubePlaylistItemId,
                        ),
                      )
                    }
                    type="button"
                  >
                    Seleccionar todo
                  </button>
                  <button
                    className={ui.buttonSecondary}
                    onClick={() => setSelectedItemIds([])}
                    type="button"
                  >
                    Limpiar selección
                  </button>
                </div>
                <div className={ui.taskList}>
                  {comparisonCandidates.map((item) => (
                    <label className={ui.taskItem} key={item.youtubePlaylistItemId}>
                      <div className={ui.taskTop}>
                        <span>
                          <input
                            checked={selectedItemIds.includes(
                              item.youtubePlaylistItemId,
                            )}
                            onChange={(event) =>
                              setSelectedItemIds((current) =>
                                event.target.checked
                                  ? [...current, item.youtubePlaylistItemId]
                                  : current.filter(
                                      (itemId) =>
                                        itemId !== item.youtubePlaylistItemId,
                                    ),
                              )
                            }
                            type="checkbox"
                          />{" "}
                          <strong>{item.youtubeTitle}</strong>
                        </span>
                        <span>{item.youtubeArtist}</span>
                      </div>
                    </label>
                  ))}
                </div>
                {comparisonCandidatesQuery.data.total >
                  comparisonCandidates.length && (
                    <p className={ui.helpText}>
                      Se muestran los primeros {comparisonCandidates.length} de{" "}
                      {comparisonCandidatesQuery.data.total} faltantes.
                    </p>
                  )}
              </>
            )}
          </div>
        </section>
      )}

      <div className={ui.gridTwo}>
        <section className={ui.panel}>
          <div className={ui.panelHeader}>
            <div>
              <h2>Nueva descarga</h2>
              <p>Una URL por línea; no se aceptan rutas de destino arbitrarias.</p>
            </div>
          </div>
          <div className={ui.panelBody}>
            <form className={ui.formGrid} onSubmit={submitDownloads}>
              <label className={`${ui.field} ${ui.fieldFull}`}>
                <span>Biblioteca de destino</span>
                <select
                  className={ui.select}
                  onChange={(event) => setLibraryId(event.target.value)}
                  required
                  value={libraryId}
                >
                  <option value="">Selecciona una biblioteca</option>
                  {(librariesQuery.data || []).map((library) => (
                    <option key={library.id} value={library.id}>
                      {library.displayName} — {library.path}
                    </option>
                  ))}
                </select>
              </label>
              <label className={`${ui.field} ${ui.fieldFull}`}>
                <span>URLs de YouTube</span>
                <textarea
                  className={ui.textarea}
                  onChange={(event) => setSourceText(event.target.value)}
                  placeholder={
                    "https://www.youtube.com/watch?v=…\nhttps://youtu.be/…"
                  }
                  required={selectedItemIds.length === 0}
                  value={sourceText}
                />
              </label>
              <p className={`${ui.helpText} ${ui.fieldFull}`}>
                Cada origen crea una tarea independiente, por lo que puedes
                cancelar o reintentar sin afectar al resto del lote.
              </p>
              <button
                className={`${ui.button} ${ui.fieldFull}`}
                disabled={
                  !ffmpegAvailable ||
                  !libraryId ||
                  createMutation.isPending ||
                  (!sourceText.trim() && selectedItemIds.length === 0)
                }
                type="submit"
              >
                Añadir a la cola
              </button>
            </form>
          </div>
        </section>

        <section className={ui.panel}>
          <div className={ui.panelHeader}>
            <div>
              <h2>Estado de la cola</h2>
              <p>Actividad persistida y tareas del proceso actual.</p>
            </div>
          </div>
          <div className={ui.panelBody}>
            <div className={ui.gridThree}>
              <div className={ui.stat}>
                <span>En curso</span>
                <strong>{activeCount}</strong>
              </div>
              <div className={ui.stat}>
                <span>Completadas</span>
                <strong>{completedCount}</strong>
              </div>
              <div className={ui.stat}>
                <span>Con incidencias</span>
                <strong>{failedCount}</strong>
              </div>
            </div>
            <br />
            <TaskList
              emptyMessage="No hay descargas activas en este proceso."
              kind="audio_download"
            />
          </div>
        </section>
      </div>

      <section className={ui.panel}>
        <div className={ui.panelHeader}>
          <div>
            <h2>Historial de descargas</h2>
            <p>Los reintentos se guardan como intentos independientes.</p>
          </div>
          <button
            className={ui.buttonSecondary}
            onClick={() => downloadsQuery.refetch()}
            type="button"
          >
            Actualizar
          </button>
        </div>
        <div className={ui.tableWrap}>
          {downloadsQuery.isLoading && (
            <div className={ui.empty}>Cargando descargas…</div>
          )}
          {!downloadsQuery.isLoading && !downloads.length && (
            <div className={ui.empty}>
              <div>
                <strong>La cola está vacía</strong>
                <span>Pega una URL o envía un faltante desde Comparación.</span>
              </div>
            </div>
          )}
          {downloads.length > 0 && (
            <table className={ui.table}>
              <thead>
                <tr>
                  <th>Estado</th>
                  <th>Origen</th>
                  <th>Progreso</th>
                  <th>Archivo generado</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {downloads.map((download) => (
                  <tr key={download.id}>
                    <td>
                      <span className={statusClass(download.status)}>
                        {statusLabel(download.status)}
                      </span>
                    </td>
                    <td>
                      <span className={ui.primaryCell}>
                        {download.sourceTitle || "Origen de YouTube"}
                      </span>
                      <span className={ui.secondaryCell}>
                        {download.sourceArtist || download.sourceUrl}
                      </span>
                    </td>
                    <td>
                      <div className={ui.taskList}>
                        <span>{Math.round(download.progressPercent)} %</span>
                        <div className={ui.progressTrack}>
                          <div
                            className={ui.progressBar}
                            style={{ width: `${download.progressPercent}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={ui.secondaryCell}>
                        {download.targetFilePath || download.errorMessage || "—"}
                      </span>
                    </td>
                    <td>
                      {["failed", "cancelled"].includes(download.status) && (
                        <button
                          className={ui.buttonSecondary}
                          disabled={retryMutation.isPending || !ffmpegAvailable}
                          onClick={() => retryMutation.mutate(download.id)}
                          type="button"
                        >
                          Reintentar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}
