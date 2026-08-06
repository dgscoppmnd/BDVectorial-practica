SHELL := /usr/bin/env bash
.ONESHELL:

PROJECT_ROOT := $(shell cd "$(dir $(realpath $(lastword $(MAKEFILE_LIST))))" && pwd)
PYTHON_VERSION := $(shell tr -d '[:space:]' < $(PROJECT_ROOT)/.python-version)

setup:
	cd "$(PROJECT_ROOT)"
	if ! command -v uv >/dev/null 2>&1; then
		curl -LsSf https://astral.sh/uv/install.sh | sh
		export PATH="$(HOME)/.local/bin:$(HOME)/.cargo/bin:$$PATH"
	fi
	uv python install "$(PYTHON_VERSION)"
	uv sync --all-extras --python "$(PYTHON_VERSION)"
	if [[ ! -f .env ]]; then
		cp .env.example .env
	fi
	uv run python -m ipykernel install --user \
		--name faiss-ann-search \
		--display-name "Python (BBDD Vectoriales · Sesión 2)"
	uv run python scriptss/validate_content.py --quick
	echo "Entorno preparado. Ejecuta 'make lab'."

lab:
	cd "$(PROJECT_ROOT)"
	uv run jupyter lab
