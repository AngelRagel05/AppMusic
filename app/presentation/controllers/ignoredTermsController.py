from __future__ import annotations

from collections.abc import Callable

from app.presentation.ui.mainScreen.mainWindow.mainWindow import MainWindow
from app.presentation.viewmodels.ignoredTermsViewModel import IgnoredTermsViewModel


class IgnoredTermsController:
    def __init__(
        self,
        view: MainWindow,
        view_model: IgnoredTermsViewModel,
        on_action_recorded: Callable[[str], None],
    ) -> None:
        self._view = view
        self._view_model = view_model
        self._on_action_recorded = on_action_recorded
        self._editing_term_id: int | None = None

    def bindEvents(self) -> None:
        section = self._view.page.ignoredTermsSection
        section.createButton.clicked.connect(self._handleSaveTerm)
        section.editRequested.connect(self._handleEditTermById)
        section.deleteRequested.connect(self._handleDeleteTermById)

    def load(self) -> None:
        ignored_terms = self._view_model.load_terms()
        self._view.page.ignoredTermsSection.showTerms(ignored_terms)

    def _handleSaveTerm(self) -> None:
        try:
            if self._editing_term_id is None:
                ignored_term = self._view_model.create_term(
                    self._view.page.ignoredTermsSection.termText(),
                    self._view.page.ignoredTermsSection.termScope(),
                    self._view.page.ignoredTermsSection.termLanguage(),
                )
                message = (
                    f'Termino "{ignored_term.term}" guardado para el scope "{ignored_term.scope}".'
                )
            else:
                ignored_term = self._view_model.update_term(
                    self._editing_term_id,
                    self._view.page.ignoredTermsSection.termText(),
                    self._view.page.ignoredTermsSection.termScope(),
                    self._view.page.ignoredTermsSection.termLanguage(),
                )
                message = (
                    f'Termino "{ignored_term.term}" actualizado para el scope "{ignored_term.scope}".'
                )
        except ValueError as exc:
            self._view.page.ignoredTermsSection.showStatusMessage(str(exc), tone="error")
            return

        self._editing_term_id = None
        self._view.page.ignoredTermsSection.clearTermInput()
        self.load()
        self._view.page.ignoredTermsSection.showStatusMessage(message, tone="success")
        self._on_action_recorded(message)

    def _handleEditTermById(self, ignored_term_id: int) -> None:
        selected_term = self._selectedTermById(ignored_term_id)
        if selected_term is None:
            self._view.page.ignoredTermsSection.showStatusMessage(
                "El termino seleccionado no existe.",
                tone="error",
            )
            return

        self._editing_term_id = selected_term.id
        self._view.page.ignoredTermsSection.setTermText(selected_term.term)
        self._view.page.ignoredTermsSection.setTermScope(selected_term.scope)
        self._view.page.ignoredTermsSection.setTermLanguage(selected_term.language)
        self._view.page.ignoredTermsSection.setSaveMode(True)
        self._view.page.showPage("filters", focus_input=True)
        self._view.page.ignoredTermsSection.showStatusMessage(
            f'Editando el termino "{selected_term.term}".',
            tone="info",
        )

    def _handleDeleteTermById(self, ignored_term_id: int) -> None:
        selected_term = self._selectedTermById(ignored_term_id)
        if selected_term is None:
            self._view.page.ignoredTermsSection.showStatusMessage(
                "El termino seleccionado no existe.",
                tone="error",
            )
            return

        try:
            self._view_model.delete_term(selected_term.id)
        except ValueError as exc:
            self._view.page.ignoredTermsSection.showStatusMessage(str(exc), tone="error")
            return

        if self._editing_term_id == selected_term.id:
            self._editing_term_id = None
            self._view.page.ignoredTermsSection.clearTermInput()
        self.load()
        self._view.page.ignoredTermsSection.showStatusMessage(
            f'Termino "{selected_term.term}" eliminado correctamente.',
            tone="success",
        )
        self._on_action_recorded(f'Termino "{selected_term.term}" eliminado.')

    def _selectedTermById(self, ignored_term_id: int):
        return next(
            (
                ignored_term
                for ignored_term in self._view_model.load_terms()
                if ignored_term.id == ignored_term_id
            ),
            None,
        )
