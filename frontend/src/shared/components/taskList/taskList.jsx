import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../../api/apiClient";
import ui from "../../styles/ui.module.css";

const activeStatuses = new Set(["queued", "running", "cancelling"]);

export function TaskList({ kind, emptyMessage = "No hay tareas recientes." }) {
  const queryClient = useQueryClient();
  const tasksQuery = useQuery({
    queryKey: ["tasks", kind],
    queryFn: () => api.tasks(kind),
    refetchInterval: (query) =>
      query.state.data?.some((task) => activeStatuses.has(task.status))
        ? 1000
        : false,
  });
  const cancelMutation = useMutation({
    mutationFn: api.cancelTask,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks"] }),
  });
  const tasks = tasksQuery.data || [];

  if (tasksQuery.isError) {
    return <div className={ui.alertError}>{tasksQuery.error.message}</div>;
  }
  if (!tasks.length) {
    return <p className={ui.muted}>{emptyMessage}</p>;
  }
  return (
    <div className={ui.taskList} aria-live="polite">
      {tasks.slice(0, 8).map((task) => (
        <div className={ui.taskItem} key={task.id}>
          <div className={ui.taskTop}>
            <div>
              <strong>{task.message || task.kind}</strong>
              <span> · {task.status}</span>
            </div>
            {activeStatuses.has(task.status) && (
              <button
                className={ui.buttonSecondary}
                disabled={task.status === "cancelling"}
                onClick={() => cancelMutation.mutate(task.id)}
                type="button"
              >
                Cancelar
              </button>
            )}
          </div>
          <div
            aria-label={`Progreso: ${Math.round(task.progressPercent)} %`}
            aria-valuemax="100"
            aria-valuemin="0"
            aria-valuenow={Math.round(task.progressPercent)}
            className={ui.progressTrack}
            role="progressbar"
          >
            <div
              className={ui.progressBar}
              style={{ width: `${task.progressPercent}%` }}
            />
          </div>
          {task.error && <div className={ui.alertError}>{task.error}</div>}
        </div>
      ))}
    </div>
  );
}
