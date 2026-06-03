from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from app.application.dto.ignoredTermDto import IgnoredTermDto
from app.shared.constants.ignoredTerms import LANGUAGE_OPTIONS, SCOPE_OPTIONS
from app.presentation.styles import (
    ActionButton,
    Signal,
    clearChildren,
    createEntry,
    createFrame,
    createLabel,
    createOptionMenu,
    createScrollableFrame,
    setStatusLabelTone,
)
from app.presentation.widgets.statusBadge.statusBadge import StatusBadge


class _IgnoredTermRow(ctk.CTkFrame):
    def __init__(self, parent, ignored_term: IgnoredTermDto, theme) -> None:
        self._theme = theme
        super().__init__(
            parent,
            fg_color=self._theme["panel"],
            corner_radius=int(self._theme["radius_lg"]),
            border_width=1,
            border_color=self._theme["border"],
        )
        self.editRequested = Signal()
        self.deleteRequested = Signal()
        self._ignored_term_id = ignored_term.id

        content = createFrame(self, theme=self._theme, fg_color="transparent")
        content.pack(fill="x", padx=18, pady=16)
        content.grid_columnconfigure(0, weight=1)

        createLabel(
            content,
            ignored_term.term,
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")

        badges = createFrame(content, theme=self._theme, fg_color="transparent")
        badges.grid(row=1, column=0, sticky="w", pady=(10, 0))
        StatusBadge(badges, ignored_term.scope, "info", self._theme).pack(side="left", padx=(0, 10))
        StatusBadge(badges, ignored_term.language, "idle", self._theme).pack(side="left", padx=(0, 10))
        StatusBadge(
            badges,
            "Activo" if ignored_term.is_active else "Inactivo",
            "success" if ignored_term.is_active else "idle",
            self._theme,
        ).pack(side="left")

        actions = createFrame(content, theme=self._theme, fg_color="transparent")
        actions.grid(row=0, column=1, rowspan=2, sticky="e")
        editButton = ActionButton(actions, "Editar", variant="secondary", theme=self._theme)
        editButton.clicked.connect(lambda: self.editRequested.emit(self._ignored_term_id))
        editButton.widget.pack(side="left", padx=(0, 10))
        deleteButton = ActionButton(actions, "Eliminar", variant="danger", theme=self._theme)
        deleteButton.clicked.connect(lambda: self.deleteRequested.emit(self._ignored_term_id))
        deleteButton.widget.pack(side="left")


class IgnoredTermsSection(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.editRequested = Signal()
        self.deleteRequested = Signal()

        topCard = createFrame(
            self,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        topCard.pack(fill="x")

        createLabel(
            topCard,
            "Configurar términos ignorados",
            theme=self._theme,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 8))
        createLabel(
            topCard,
            "Añade palabras frecuentes para limpiar ruido en títulos y artistas antes de comparar.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=860,
        ).pack(anchor="w", padx=20, pady=(0, 16))

        inputs = createFrame(topCard, theme=self._theme, fg_color="transparent")
        inputs.pack(fill="x", padx=20, pady=(0, 16))

        self.termInput = createEntry(
            inputs,
            theme=self._theme,
            width=280,
            placeholder_text="Ejemplo: live, official, remastered",
        )
        self.termInput.pack(side="left", fill="x", expand=True)
        self.scopeVar = tk.StringVar(value=SCOPE_OPTIONS[0])
        self.scopeInput = createOptionMenu(
            inputs,
            self.scopeVar,
            SCOPE_OPTIONS,
            theme=self._theme,
            width=160,
        )
        self.scopeInput.pack(side="left", padx=(12, 12))
        self.languageVar = tk.StringVar(value=LANGUAGE_OPTIONS[0])
        self.languageInput = createOptionMenu(
            inputs,
            self.languageVar,
            LANGUAGE_OPTIONS,
            theme=self._theme,
            width=140,
        )
        self.languageInput.pack(side="left", padx=(0, 12))
        self.createButton = ActionButton(inputs, "Guardar término", theme=self._theme)
        self.createButton.widget.pack(side="left")
        self.formHelper = createLabel(
            topCard,
            "Define el término, su campo y el ámbito de aplicación.",
            theme=self._theme,
            text_color=self._theme["text_muted"],
            font=("Segoe UI", 12),
            wraplength=860,
        )
        self.formHelper.pack(anchor="w", padx=20, pady=(0, 18))

        self.statusLabel = createLabel(
            self,
            "Los términos guardados aparecerán aquí como filtros activos.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
        )
        self.statusLabel.pack(anchor="w", pady=(18, 12))

        header = createFrame(self, theme=self._theme, fg_color="transparent")
        header.pack(fill="x", pady=(4, 12))
        createLabel(
            header,
            "Términos ignorados",
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")

        self._rowsHost = createScrollableFrame(self, theme=self._theme, fg_color="transparent")
        self._rowsHost.pack(fill="both", expand=True)

    def showTerms(self, ignored_terms: list[IgnoredTermDto]) -> None:
        clearChildren(self._rowsHost)
        if not ignored_terms:
            self._buildEmptyState(self._rowsHost).pack(fill="x")
            return

        for ignored_term in ignored_terms:
            row = _IgnoredTermRow(self._rowsHost, ignored_term, self._theme)
            row.editRequested.connect(self.editRequested.emit)
            row.deleteRequested.connect(self.deleteRequested.emit)
            row.pack(fill="x", pady=(0, 14))

    def termText(self) -> str:
        return self.termInput.get()

    def termScope(self) -> str:
        return self.scopeVar.get()

    def termLanguage(self) -> str:
        return self.languageVar.get()

    def clearTermInput(self) -> None:
        self.termInput.delete(0, "end")
        self.setTermScope(SCOPE_OPTIONS[0])
        self.setTermLanguage(LANGUAGE_OPTIONS[0])
        self.setSaveMode(False)

    def setTermText(self, value: str) -> None:
        self.termInput.delete(0, "end")
        self.termInput.insert(0, value)

    def setTermScope(self, value: str) -> None:
        self.scopeVar.set(value)

    def setTermLanguage(self, value: str) -> None:
        self.languageVar.set(value)

    def setSaveMode(self, is_editing: bool) -> None:
        if is_editing:
            self.createButton.setText("Guardar cambios")
            self.formHelper.configure(
                text="Estás editando un término guardado. Ajusta los campos y guarda para actualizarlo."
            )
            return

        self.createButton.setText("Guardar término")
        self.formHelper.configure(
            text="Define el término, su campo y el ámbito de aplicación."
        )

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.statusLabel.configure(text=message)
        setStatusLabelTone(self.statusLabel, tone, theme=self._theme)

    def focusPrimaryInput(self) -> None:
        self.termInput.focus_set()

    def _buildEmptyState(self, parent):
        card = createFrame(
            parent,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        createLabel(
            card,
            "Todavía no hay términos ignorados",
            theme=self._theme,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 8))
        createLabel(
            card,
            "Añade palabras recurrentes para limpiar ruido habitual antes de comparar canciones, artistas y álbumes.",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=760,
        ).pack(anchor="w", padx=20, pady=(0, 18))
        return card
