from __future__ import annotations

import customtkinter as ctk

from app.presentation.features.comparison.comparisonResultDetailViewData import (
    ComparisonResultDetailViewData,
)
from app.presentation.styles import createFrame, createLabel


class ComparisonResultDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, theme, detail_view_data: ComparisonResultDetailViewData) -> None:
        super().__init__(parent)
        self.title("Detalle del resultado")
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.configure(fg_color=theme["bg"])
        self.geometry("760x520")
        self.minsize(680, 460)

        container = createFrame(self, theme=theme, fg_color=theme["bg"])
        container.pack(fill="both", expand=True, padx=16, pady=16)
        container.grid_columnconfigure(0, weight=1)

        createLabel(
            container,
            detail_view_data.title,
            theme=theme,
            font=("Segoe UI", 20, "bold"),
            wraplength=680,
        ).grid(row=0, column=0, sticky="w")
        createLabel(
            container,
            detail_view_data.subtitle,
            theme=theme,
            text_color=theme["text_secondary"],
            font=("Segoe UI", 13),
            wraplength=680,
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        summary_card = createFrame(
            container,
            theme=theme,
            fg_color=theme["panel"],
            border_width=1,
            border_color=theme["border"],
            corner_radius=int(theme["radius_md"]),
        )
        summary_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        summary_card.grid_columnconfigure(0, weight=1)
        createLabel(
            summary_card,
            (
                f"Estado: {detail_view_data.status_label}\n"
                f"Disponibilidad: {detail_view_data.availability_summary}\n"
                f"Score: {detail_view_data.score_label}"
            ),
            theme=theme,
            font=("Segoe UI", 12),
            wraplength=660,
        ).grid(row=0, column=0, sticky="w", padx=12, pady=12)

        linked_song_card = createFrame(
            container,
            theme=theme,
            fg_color=theme["surface"],
            border_width=1,
            border_color=theme["border"],
            corner_radius=int(theme["radius_md"]),
        )
        linked_song_card.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        linked_song_card.grid_columnconfigure(0, weight=1)
        createLabel(
            linked_song_card,
            detail_view_data.linked_song_title,
            theme=theme,
            font=("Segoe UI", 13, "bold"),
            wraplength=660,
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        createLabel(
            linked_song_card,
            detail_view_data.linked_song_detail,
            theme=theme,
            text_color=theme["text_secondary"],
            font=("Segoe UI", 11),
            wraplength=660,
        ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 12))

        reason_card = createFrame(
            container,
            theme=theme,
            fg_color=theme["surface"],
            border_width=1,
            border_color=theme["border"],
            corner_radius=int(theme["radius_md"]),
        )
        reason_card.grid(row=4, column=0, sticky="nsew")
        reason_card.grid_columnconfigure(0, weight=1)
        reason_card.grid_rowconfigure(1, weight=1)
        container.grid_rowconfigure(4, weight=1)
        createLabel(
            reason_card,
            "Motivo del resultado",
            theme=theme,
            font=("Segoe UI", 13, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        createLabel(
            reason_card,
            (
                f"Resumen: {detail_view_data.reason_summary}\n\n"
                f"Detalle: {detail_view_data.raw_reason}"
            ),
            theme=theme,
            text_color=theme["text_secondary"],
            font=("Segoe UI", 11),
            wraplength=660,
            justify="left",
        ).grid(row=1, column=0, sticky="nw", padx=12, pady=(0, 12))
