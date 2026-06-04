from __future__ import annotations

from math import ceil
from typing import Generic, Sequence, TypeVar


TItem = TypeVar("TItem")


class ComparisonPaginationState(Generic[TItem]):
    def __init__(self, page_size: int = 25) -> None:
        self._items: tuple[TItem, ...] = ()
        self._page_size = max(1, page_size)
        self._current_page = 1

    @property
    def totalItems(self) -> int:
        return len(self._items)

    @property
    def pageSize(self) -> int:
        return self._page_size

    @property
    def totalPages(self) -> int:
        if self.totalItems == 0:
            return 0
        return ceil(self.totalItems / self._page_size)

    @property
    def currentPage(self) -> int:
        if self.totalItems == 0:
            return 0
        return self._current_page

    @property
    def hasPreviousPage(self) -> bool:
        return self.currentPage > 1

    @property
    def hasNextPage(self) -> bool:
        return self.currentPage < self.totalPages

    @property
    def visibleRange(self) -> tuple[int, int]:
        if self.totalItems == 0:
            return (0, 0)
        start = ((self._current_page - 1) * self._page_size) + 1
        end = min(start + self._page_size - 1, self.totalItems)
        return (start, end)

    def setItems(self, items: Sequence[TItem]) -> None:
        self._items = tuple(items)
        if self.totalItems == 0:
            self._current_page = 1
            return
        self._current_page = min(max(1, self._current_page), self.totalPages)

    def setPageSize(self, page_size: int) -> None:
        normalized_page_size = max(1, page_size)
        first_visible_item_index = max(0, (self._current_page - 1) * self._page_size)
        self._page_size = normalized_page_size
        if self.totalItems == 0:
            self._current_page = 1
            return
        self._current_page = min((first_visible_item_index // self._page_size) + 1, self.totalPages)

    def nextPage(self) -> None:
        if self.hasNextPage:
            self._current_page += 1

    def previousPage(self) -> None:
        if self.hasPreviousPage:
            self._current_page -= 1

    def currentItems(self) -> list[TItem]:
        if self.totalItems == 0:
            return []
        start_index = (self._current_page - 1) * self._page_size
        end_index = start_index + self._page_size
        return list(self._items[start_index:end_index])
