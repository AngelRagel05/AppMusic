from __future__ import annotations

from app.presentation.features.comparison.comparisonPaginationState import (
    ComparisonPaginationState,
)


def test_comparison_pagination_state_returns_first_page_with_default_size() -> None:
    state = ComparisonPaginationState[int]()
    state.setItems(list(range(1, 41)))

    assert state.pageSize == 25
    assert state.currentPage == 1
    assert state.totalPages == 2
    assert state.visibleRange == (1, 25)
    assert state.currentItems() == list(range(1, 26))


def test_comparison_pagination_state_keeps_visible_offset_when_page_size_changes() -> None:
    state = ComparisonPaginationState[int]()
    state.setItems(list(range(1, 91)))
    state.nextPage()
    state.nextPage()

    state.setPageSize(10)

    assert state.pageSize == 10
    assert state.currentPage == 6
    assert state.visibleRange == (51, 60)
    assert state.currentItems() == list(range(51, 61))


def test_comparison_pagination_state_stops_at_list_boundaries() -> None:
    state = ComparisonPaginationState[int](page_size=25)
    state.setItems(list(range(1, 31)))

    state.previousPage()
    state.nextPage()
    state.nextPage()
    state.nextPage()

    assert state.currentPage == 2
    assert state.hasPreviousPage is True
    assert state.hasNextPage is False
    assert state.visibleRange == (26, 30)
