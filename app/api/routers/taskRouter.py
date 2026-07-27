from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.api.apiSchemas import TaskResponse
from app.api.dependencies import getTaskManager
from app.api.errors import ApiError
from app.infrastructure.tasks import LocalTaskManager

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
def listTasks(
    kind: str | None = Query(default=None, max_length=64),
    task_manager: LocalTaskManager = Depends(getTaskManager),
) -> list:
    return task_manager.list(kind=kind)


@router.get("/{task_id}", response_model=TaskResponse)
def getTask(
    task_id: str,
    task_manager: LocalTaskManager = Depends(getTaskManager),
):
    task = task_manager.get(task_id)
    if task is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            "task_not_found",
            "La tarea solicitada no existe.",
        )
    return task


@router.post("/{task_id}/cancel", response_model=TaskResponse)
def cancelTask(
    task_id: str,
    task_manager: LocalTaskManager = Depends(getTaskManager),
):
    task = task_manager.cancel(task_id)
    if task is None:
        raise ApiError(
            status.HTTP_404_NOT_FOUND,
            "task_not_found",
            "La tarea solicitada no existe.",
        )
    return task
