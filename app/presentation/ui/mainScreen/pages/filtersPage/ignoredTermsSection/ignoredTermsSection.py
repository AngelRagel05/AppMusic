from __future__ import annotations

import tkinter as tk

from app.application.dto.ignored_term_dto import IgnoredTermDto
from app.presentation.uiTheme import (
    ActionButton,
    clearChildren,
    createEntry,
    createLabel,
    createOptionMenu,
    setStatusLabelTone,
)
from app.presentation.uiTheme.themePalette import ThemeTokens

SCOPE_OPTIONS = ("title", "artist", "album")
LANGUAGE_OPTIONS = ("global", "es", "en")


class _IgnoredTermRow(tk.Frame):
    def __init__(self, parent: tk.Misc, ignored_term: IgnoredTermDto, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["surface"], padx=16, pady=10)
        self._theme = theme

        createLabel(
            self,
            ignored_term.term,
            theme=self._theme,
            bg=self._theme["surface"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w")
        self._badge(ignored_term.scope).grid(row=0, column=1, sticky="w", padx=(12, 0))
        self._badge(ignored_term.language).grid(row=0, column=2, sticky="w", padx=(12, 0))
        self._badge("Activo" if ignored_term.is_active else "Inactivo").grid(
            row=0, column=3, sticky="w", padx=(12, 0)
        )
        action_button = tk.Button(
            self,
            text="...",
            state="disabled",
            relief="flat",
            bd=0,
            bg=self._theme["surface_alt"],
            fg=self._theme["text_muted"],
            disabledforeground=self._theme["text_muted"],
        )
        action_button.grid(row=0, column=4, sticky="e", padx=(12, 0))
        self.grid_columnconfigure(0, weight=1)

    def _badge(self, text: str) -> tk.Label:
        return createLabel(
            self,
            text,
            theme=self._theme,
            bg=self._theme["surface_alt"],
            fg=self._theme["text_secondary"],
            font=("Segoe UI", 9, "bold"),
        )


class IgnoredTermsSection(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeTokens) -> None:
        super().__init__(parent, bg=theme["bg"])
        self._theme = theme

        self.termInput = createEntry(self, theme=self._theme, width=32)
        self.scopeVar = tk.StringVar(value=SCOPE_OPTIONS[0])
        self.scopeInput = createOptionMenu(self, self.scopeVar, SCOPE_OPTIONS, theme=self._theme)
        self.languageVar = tk.StringVar(value=LANGUAGE_OPTIONS[0])
        self.languageInput = createOptionMenu(
            self,
            self.languageVar,
            LANGUAGE_OPTIONS,
            theme=self._theme,
        )
        self.createButton = ActionButton(self, "Guardar termino", theme=self._theme)
        self.statusLabel = createLabel(
            self,
            "Configura filtros ligeros para mejorar el matching.",
            theme=self._theme,
            fg=self._theme["accent"],
            wraplength=720,
        )
        self.listCaption = createLabel(
            self,
            "Terminos ignorados",
            theme=self._theme,
            font=("Segoe UI", 11, "bold"),
        )

        self._rowsHost = tk.Frame(self, bg=self._theme["bg"])

        self._buildLeadBand().pack(anchor="w")
        self._buildComposer().pack(fill="x", pady=(14, 0))
        self.statusLabel.pack(anchor="w", pady=(14, 0))
        self.listCaption.pack(anchor="w", pady=(16, 8))
        self._buildTableHeader().pack(fill="x")
        self._rowsHost.pack(fill="both", expand=True)

    def showTerms(self, ignored_terms: list[IgnoredTermDto]) -> None:
        clearChildren(self._rowsHost)
        if not ignored_terms:
            self._buildEmptyState(self._rowsHost).pack(fill="x")
            return

        for ignored_term in ignored_terms:
            _IgnoredTermRow(self._rowsHost, ignored_term, self._theme).pack(fill="x", pady=(0, 1))

    def termText(self) -> str:
        return self.termInput.get()

    def termScope(self) -> str:
        return self.scopeVar.get()

    def termLanguage(self) -> str:
        return self.languageVar.get()

    def clearTermInput(self) -> None:
        self.termInput.delete(0, tk.END)

    def showStatusMessage(self, message: str, tone: str = "info") -> None:
        self.statusLabel.configure(text=message)
        setStatusLabelTone(self.statusLabel, tone, theme=self._theme)

    def focusPrimaryInput(self) -> None:
        self.termInput.focus_set()

    def _buildLeadBand(self) -> tk.Frame:
        band = tk.Frame(self, bg=self._theme["bg"])
        createLabel(
            band,
            "Filtros base",
            theme=self._theme,
            fg=self._theme["accent"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")
        createLabel(
            band,
            "Terminos ignorados",
            theme=self._theme,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", pady=(3, 0))
        createLabel(
            band,
            "Limpia ruido comun en titulos y artistas antes de comparar tu musica.",
            theme=self._theme,
            fg=self._theme["text_secondary"],
            wraplength=720,
        ).pack(anchor="w", pady=(3, 0))
        return band

    def _buildComposer(self) -> tk.Frame:
        inputs = tk.Frame(self, bg=self._theme["bg"])
        self.termInput.pack(in_=inputs, side="left", fill="x", expand=True)
        self.scopeInput.pack(in_=inputs, side="left", padx=(10, 10))
        self.languageInput.pack(in_=inputs, side="left", padx=(0, 10))
        self.createButton.widget.pack(in_=inputs, side="left")
        return inputs

    def _buildTableHeader(self) -> tk.Frame:
        header = tk.Frame(self, bg=self._theme["surface_alt"], padx=16, pady=8)
        labels = ("Termino", "Campo", "Ambito", "Estado", "Acciones")
        for index, text in enumerate(labels):
            createLabel(
                header,
                text,
                theme=self._theme,
                bg=self._theme["surface_alt"],
                fg=self._theme["text_secondary"],
                font=("Segoe UI", 9, "bold"),
            ).grid(row=0, column=index, sticky="w", padx=(0, 12))
        header.grid_columnconfigure(0, weight=1)
        return header

    def _buildEmptyState(self, parent: tk.Misc) -> tk.Frame:
        card = tk.Frame(parent, bg=self._theme["surface"], padx=18, pady=18)
        createLabel(
            card,
            "Todavia no hay terminos ignorados",
            theme=self._theme,
            bg=self._theme["surface"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        createLabel(
            card,
            "Anade palabras frecuentes para mejorar la limpieza de nombres antes de comparar.",
            theme=self._theme,
            bg=self._theme["surface"],
            fg=self._theme["text_secondary"],
            wraplength=700,
        ).pack(anchor="w", pady=(6, 0))
        return card
