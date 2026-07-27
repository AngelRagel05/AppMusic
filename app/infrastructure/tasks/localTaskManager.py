from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import UTC, datetime
from enum import StrEnum
from threading import Event, RLock
from typing import Any
from uuid import uuid4

from app.shared.exceptions import OperationCancelledError


class TaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    CANCELLING = "cancelling"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class TaskSnapshot:
    id: str
    kind: str
    status: TaskStatus
    progress_percent: float
    message: str | None
    result: Any
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


@dataclass(slots=True)
class _TaskRecord:
    id: str
    kind: str
    status: TaskStatus = TaskStatus.QUEUED
    progress_percent: float = 0.0
    message: str | None = None
    result: Any = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None
    cancellation: Event = field(default_factory=Event)
    future: Future | None = None


class TaskContext:
    def __init__(
        self,
        task_id: str,
        cancellation: Event,
        progress_reporter: Callable[[float, str | None], None],
    ) -> None:
        self.task_id = task_id
        self._cancellation = cancellation
        self._progress_reporter = progress_reporter

    @property
    def isCancelled(self) -> bool:
        return self._cancellation.is_set()

    def raiseIfCancelled(self) -> None:
        if self.isCancelled:
            raise OperationCancelledError("La tarea fue cancelada por el usuario.")

    def reportProgress(
        self,
        progress_percent: float,
        message: str | None = None,
    ) -> None:
        self.raiseIfCancelled()
        self._progress_reporter(progress_percent, message)


TaskOperation = Callable[[TaskContext], Any]


class LocalTaskManager:
    def __init__(self, worker_count: int = 3) -> None:
        self._executor = ThreadPoolExecutor(
            max_workers=worker_count,
            thread_name_prefix="soundshelf-task",
        )
        self._records: dict[str, _TaskRecord] = {}
        self._lock = RLock()
        self._is_shutdown = False

    def submit(self, kind: str, operation: TaskOperation) -> TaskSnapshot:
        normalized_kind = kind.strip()
        if not normalized_kind:
            raise ValueError("El tipo de tarea es obligatorio.")

        with self._lock:
            if self._is_shutdown:
                raise RuntimeError("El gestor de tareas ya esta detenido.")
            task_id = uuid4().hex
            record = _TaskRecord(id=task_id, kind=normalized_kind)
            self._records[task_id] = record
            record.future = self._executor.submit(
                self._runOperation,
                record,
                operation,
            )
            return self._snapshot(record)

    def list(self, *, kind: str | None = None) -> list[TaskSnapshot]:
        with self._lock:
            records = list(self._records.values())
            if kind:
                records = [record for record in records if record.kind == kind]
            records.sort(key=lambda record: record.created_at, reverse=True)
            return [self._snapshot(record) for record in records]

    def get(self, task_id: str) -> TaskSnapshot | None:
        with self._lock:
            record = self._records.get(task_id)
            return self._snapshot(record) if record is not None else None

    def cancel(self, task_id: str) -> TaskSnapshot | None:
        with self._lock:
            record = self._records.get(task_id)
            if record is None:
                return None
            if record.status in {
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            }:
                return self._snapshot(record)

            record.cancellation.set()
            if record.future is not None and record.future.cancel():
                record.status = TaskStatus.CANCELLED
                record.message = "Tarea cancelada antes de comenzar."
                record.finished_at = datetime.now(UTC)
            else:
                record.status = TaskStatus.CANCELLING
                record.message = "Cancelacion solicitada."
            return self._snapshot(record)

    def shutdown(self, *, wait: bool = False) -> None:
        with self._lock:
            if self._is_shutdown:
                return
            self._is_shutdown = True
            for record in self._records.values():
                if record.status in {TaskStatus.QUEUED, TaskStatus.RUNNING}:
                    record.cancellation.set()
                    record.status = TaskStatus.CANCELLING
        self._executor.shutdown(wait=wait, cancel_futures=True)

    def _runOperation(
        self,
        record: _TaskRecord,
        operation: TaskOperation,
    ) -> None:
        with self._lock:
            if record.cancellation.is_set():
                record.status = TaskStatus.CANCELLED
                record.finished_at = datetime.now(UTC)
                return
            record.status = TaskStatus.RUNNING
            record.started_at = datetime.now(UTC)
            record.message = "Tarea iniciada."

        context = TaskContext(
            record.id,
            record.cancellation,
            lambda progress, message: self._updateProgress(
                record.id,
                progress,
                message,
            ),
        )
        try:
            result = operation(context)
            context.raiseIfCancelled()
        except OperationCancelledError as error:
            with self._lock:
                record.status = TaskStatus.CANCELLED
                record.error = None
                record.message = str(error)
                record.finished_at = datetime.now(UTC)
            return
        except Exception as error:
            with self._lock:
                record.status = TaskStatus.FAILED
                record.error = str(error) or error.__class__.__name__
                record.message = "La tarea ha fallado."
                record.finished_at = datetime.now(UTC)
            return

        with self._lock:
            record.status = TaskStatus.COMPLETED
            record.progress_percent = 100.0
            record.message = "Tarea completada."
            record.result = self._serializeResult(result)
            record.finished_at = datetime.now(UTC)

    def _updateProgress(
        self,
        task_id: str,
        progress_percent: float,
        message: str | None,
    ) -> None:
        with self._lock:
            record = self._records.get(task_id)
            if record is None:
                return
            record.progress_percent = min(100.0, max(0.0, float(progress_percent)))
            if message is not None:
                record.message = message

    def _snapshot(self, record: _TaskRecord) -> TaskSnapshot:
        return TaskSnapshot(
            id=record.id,
            kind=record.kind,
            status=record.status,
            progress_percent=record.progress_percent,
            message=record.message,
            result=record.result,
            error=record.error,
            created_at=record.created_at,
            started_at=record.started_at,
            finished_at=record.finished_at,
        )

    def _serializeResult(self, result: Any) -> Any:
        if is_dataclass(result) and not isinstance(result, type):
            return asdict(result)
        if isinstance(result, list):
            return [self._serializeResult(item) for item in result]
        if isinstance(result, tuple):
            return [self._serializeResult(item) for item in result]
        if isinstance(result, dict):
            return {
                str(key): self._serializeResult(value)
                for key, value in result.items()
            }
        if isinstance(result, StrEnum):
            return result.value
        return result
