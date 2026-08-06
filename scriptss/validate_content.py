#!/usr/bin/env python3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
required_paths = [
    "Aurum_Market_Practica.ipynb",
    "data",
    ".python-version",
    "pyproject.toml",
    ".env.example",
]
missing = [path for path in required_paths if not (PROJECT_ROOT / path).exists()]
if missing:
    raise SystemExit(
        "Validation failed. Missing required paths:\n" + "\n".join(f" - {path}" for path in missing)
    )
print("Validation completed successfully.")
