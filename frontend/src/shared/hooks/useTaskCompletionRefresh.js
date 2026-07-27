import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../api/apiClient";

const activeStatuses = new Set(["queued", "running", "cancelling"]);

export function useTaskCompletionRefresh(kind, queryKeys) {
  const queryClient = useQueryClient();
  const tasksQuery = useQuery({
    queryKey: ["taskRefresh", kind],
    queryFn: () => api.tasks(kind),
    refetchInterval: (query) =>
      query.state.data?.some((task) => activeStatuses.has(task.status))
        ? 1000
        : false,
  });
  const completionFingerprint = (tasksQuery.data || [])
    .filter((task) => task.finishedAt)
    .map((task) => `${task.id}:${task.finishedAt}`)
    .join("|");

  useEffect(() => {
    if (!completionFingerprint) {
      return;
    }
    queryKeys.forEach((queryKey) => {
      queryClient.invalidateQueries({ queryKey });
    });
  }, [completionFingerprint, queryClient, queryKeys]);

  return tasksQuery.data || [];
}
