from __future__ import annotations

from threading import Event
from time import monotonic, sleep

from app.infrastructure.tasks import LocalTaskManager, TaskStatus


def waitForTerminalTask(manager: LocalTaskManager, task_id: str):
    deadline = monotonic() + 3
    while monotonic() < deadline:
        snapshot = manager.get(task_id)
        if snapshot is not None and snapshot.status in {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        }:
            return snapshot
        sleep(0.01)
    raise AssertionError("La tarea no alcanzo un estado terminal.")


def test_task_manager_reports_progress_and_serializes_result() -> None:
    manager = LocalTaskManager(worker_count=1)
    try:
        task = manager.submit(
            "test",
            lambda context: (
                context.reportProgress(42, "Procesando…"),
                {"ok": True},
            )[1],
        )

        completed = waitForTerminalTask(manager, task.id)

        assert completed.status is TaskStatus.COMPLETED
        assert completed.progress_percent == 100
        assert completed.result == {"ok": True}
        assert completed.error is None
    finally:
        manager.shutdown(wait=True)


def test_task_manager_cancels_running_operation_cooperatively() -> None:
    manager = LocalTaskManager(worker_count=1)
    started = Event()

    def operation(context):
        started.set()
        while not context.isCancelled:
            sleep(0.01)
        context.raiseIfCancelled()

    try:
        task = manager.submit("test", operation)
        assert started.wait(timeout=1)

        cancelling = manager.cancel(task.id)
        cancelled = waitForTerminalTask(manager, task.id)

        assert cancelling is not None
        assert cancelling.status is TaskStatus.CANCELLING
        assert cancelled.status is TaskStatus.CANCELLED
        assert cancelled.error is None
    finally:
        manager.shutdown(wait=True)


def test_task_manager_shutdown_cancels_running_operations() -> None:
    manager = LocalTaskManager(worker_count=1)
    started = Event()

    def operation(context):
        started.set()
        while not context.isCancelled:
            sleep(0.01)
        context.raiseIfCancelled()

    task = manager.submit("download", operation)
    assert started.wait(timeout=1)

    manager.shutdown(wait=False)
    cancelled = waitForTerminalTask(manager, task.id)

    assert cancelled.status is TaskStatus.CANCELLED
