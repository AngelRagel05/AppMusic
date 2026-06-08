from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

FRONT_LINT_TARGETS = [
    "app/presentation",
    "app/workers",
    "app/bootstrap/presentationFactory.py",
]

FRONT_TEST_TARGETS = [
    "tests/unit/testFeatureControllers.py",
    "tests/unit/testFeatureViewmodels.py",
    "tests/unit/testYoutubePlaylistImportViewModel.py",
    "tests/unit/testLocalLibraryScanViewModel.py",
    "tests/unit/testLoadLibraryComparisonWorker.py",
    "tests/unit/testScanLocalFolderWorker.py",
    "tests/unit/testImportYoutubePlaylistItemsWorker.py",
    "tests/unit/testComparisonAvailabilitySummary.py",
    "tests/unit/testComparisonDtos.py",
    "tests/unit/testComparisonPaginationState.py",
    "tests/unit/testComparisonReasonSummary.py",
    "tests/unit/testComparisonResultFilter.py",
    "tests/unit/testComparisonSearch.py",
    "tests/unit/testDependencyRules.py",
]


def run_command(title: str, command: list[str]) -> int:
    print(f"\n== {title} ==")
    print(" ".join(command))
    completed = subprocess.run(command, cwd=PROJECT_ROOT)
    return completed.returncode


def main() -> int:
    compile_exit_code = run_command(
        "Compile Front",
        [
            sys.executable,
            "-m",
            "compileall",
            "app/presentation",
            "app/workers",
            "app/bootstrap/presentationFactory.py",
        ],
    )
    if compile_exit_code != 0:
        return compile_exit_code

    lint_exit_code = run_command(
        "Ruff Front Severe",
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--select",
            "E9,F63,F7,F82",
            *FRONT_LINT_TARGETS,
        ],
    )
    if lint_exit_code != 0:
        return lint_exit_code

    test_exit_code = run_command(
        "Pytest Front",
        [sys.executable, "-m", "pytest", *FRONT_TEST_TARGETS],
    )
    if test_exit_code != 0:
        return test_exit_code

    print("\nFront verificado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
