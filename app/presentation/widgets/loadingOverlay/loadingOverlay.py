from __future__ import annotations

import customtkinter as ctk

from app.presentation.styles import createFrame, createLabel


class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, parent, theme) -> None:
        self._theme = theme
        super().__init__(parent, fg_color=self._theme["bg"], corner_radius=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        panel = createFrame(
            self,
            theme=self._theme,
            fg_color=self._theme["panel"],
            border_width=1,
            border_color=self._theme["border"],
            corner_radius=int(self._theme["radius_lg"]),
        )
        panel.grid(row=0, column=0)

        self._title_label = createLabel(
            panel,
            "Cargando",
            theme=self._theme,
            font=("Segoe UI", 22, "bold"),
            anchor="center",
            justify="center",
        )
        self._title_label.pack(padx=32, pady=(28, 10))

        self._message_label = createLabel(
            panel,
            "",
            theme=self._theme,
            text_color=self._theme["text_secondary"],
            font=("Segoe UI", 13),
            anchor="center",
            justify="center",
            wraplength=360,
        )
        self._message_label.pack(padx=32, pady=(0, 18))

        self._progress_bar = ctk.CTkProgressBar(
            panel,
            mode="indeterminate",
            width=220,
            height=14,
            corner_radius=int(self._theme["radius_sm"]),
            progress_color=self._theme["accent"],
            fg_color=self._theme["surface"],
        )
        self._progress_bar.pack(padx=32, pady=(0, 28))
        self._progress_bar.start()

    def show(self, title: str, message: str) -> None:
        self._title_label.configure(text=title)
        self._message_label.configure(text=message)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self.update_idletasks()
        self._progress_bar.start()

    def hide(self) -> None:
        self._progress_bar.stop()
        self.place_forget()
