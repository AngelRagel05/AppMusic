from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout, QWidget

from app.presentation.styles import applyComponentQss
from app.presentation.ui.ignoredTerms.ignoredTermsSection import IgnoredTermsSection
from app.presentation.ui.localLibraries.localLibrariesSection import LocalLibrariesSection
from app.presentation.ui.mainScreen.heroSection.heroSection import HeroSection


class MainWindowPage(QScrollArea):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("mainWindowPageRoot")
        self.heroSection = HeroSection()
        self.localLibrariesSection = LocalLibrariesSection()
        self.ignoredTermsSection = IgnoredTermsSection()

        pageLayout = QVBoxLayout()
        pageLayout.setContentsMargins(28, 24, 28, 28)
        pageLayout.setSpacing(20)
        pageLayout.addWidget(self.heroSection)
        pageLayout.addLayout(self._buildMainContent())
        pageLayout.addStretch()

        page = QWidget()
        page.setObjectName("mainWindowPageContent")
        page.setLayout(pageLayout)

        self.setWidgetResizable(True)
        self.setWidget(page)
        applyComponentQss(self, Path(__file__).with_suffix(".qss"))

    def _buildMainContent(self) -> QGridLayout:
        layout = QGridLayout()
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(20)
        layout.addWidget(self.localLibrariesSection, 0, 0)
        layout.addWidget(self.ignoredTermsSection, 0, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        return layout
