from __future__ import annotations

from collections.abc import Callable

from app.presentation.features.ignoredTerms.ui.ignoredTermsPage.ignoredTermsPage import (
    IgnoredTermsPage,
)
from app.presentation.features.ignoredTerms.viewmodel.ignoredTermsViewModel import (
    IgnoredTermsViewModel,
)


class IgnoredTermsController:
    def __init__(
        self,
        page: IgnoredTermsPage,
        view_model: IgnoredTermsViewModel,
        show_page: Callable[[str, bool], None],
        on_action_recorded: Callable[[str], None],
    ) -> None:
        self._page = page
        self._view_model = view_model
        self._show_page = show_page
        self._on_action_recorded = on_action_recorded
        self._editing_term_id: int | None = None

    def bindEvents(self) -> None:
        self._page.onSaveTermRequested(self._handleSaveTerm)
        self._page.onEditTermRequested(self._handleEditTermById)
        self._page.onDeleteTermRequested(self._handleDeleteTermById)

    def load(self) -> None:
        self._page.showTerms(self._view_model.refreshState())

    def _handleSaveTerm(self) -> None:
        try:
            if self._editing_term_id is None:
                ignored_term = self._view_model.create_term(
                    self._page.termText(),
                    self._page.termScope(),
                    self._page.termLanguage(),
                )
                message = (
                    f'Termino "{ignored_term.term}" guardado para el scope "{ignored_term.scope}".'
                )
            else:
                ignored_term = self._view_model.update_term(
                    self._editing_term_id,
                    self._page.termText(),
                    self._page.termScope(),
                    self._page.termLanguage(),
                )
                message = (
                    f'Termino "{ignored_term.term}" actualizado para el scope "{ignored_term.scope}".'
                )
        except ValueError as exc:
            self._page.showStatusMessage(str(exc), tone="error")
            return

        self._editing_term_id = None
        self._page.clearTermInput()
        self._renderState()
        self._page.showStatusMessage(message, tone="success")
        self._on_action_recorded(message)

    def _handleEditTermById(self, ignored_term_id: int) -> None:
        selected_term = self._view_model.find_term_by_id(ignored_term_id)
        if selected_term is None:
            self._page.showStatusMessage(
                "El termino seleccionado no existe.",
                tone="error",
            )
            return

        self._editing_term_id = selected_term.id
        self._page.setTermText(selected_term.term)
        self._page.setTermScope(selected_term.scope)
        self._page.setTermLanguage(selected_term.language)
        self._page.setSaveMode(True)
        self._show_page("ignoredTerms", True)
        self._page.showStatusMessage(
            f'Editando el termino "{selected_term.term}".',
            tone="info",
        )

    def _handleDeleteTermById(self, ignored_term_id: int) -> None:
        selected_term = self._view_model.find_term_by_id(ignored_term_id)
        if selected_term is None:
            self._page.showStatusMessage(
                "El termino seleccionado no existe.",
                tone="error",
            )
            return

        try:
            self._view_model.delete_term(selected_term.id)
        except ValueError as exc:
            self._page.showStatusMessage(str(exc), tone="error")
            return

        if self._editing_term_id == selected_term.id:
            self._editing_term_id = None
            self._page.clearTermInput()
        self._renderState()
        self._page.showStatusMessage(
            f'Termino "{selected_term.term}" eliminado correctamente.',
            tone="success",
        )
        self._on_action_recorded(f'Termino "{selected_term.term}" eliminado.')

    def _renderState(self) -> None:
        self._page.showTerms(self._view_model.load_terms())
