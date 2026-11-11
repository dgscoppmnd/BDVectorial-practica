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
		--name aurum-bdv \
		--display-name "Python (Aurum BDV)"
	uv run python scriptss/validate_content.py --quick
	echo "Entorno preparado. Levanta Qdrant con 'make qdrant' y ejecuta 'make lab'."

qdrant:
	cd "$(PROJECT_ROOT)"
	docker compose up -d
	curl -s http://localhost:6333/readyz && echo " · Qdrant listo en http://localhost:6333"

lab:
	cd "$(PROJECT_ROOT)"
	uv run jupyter lab

test:
	cd "$(PROJECT_ROOT)"
	uv run python -m pytest tests -q

validate:
	cd "$(PROJECT_ROOT)"
	uv run python scriptss/validate_content.py

informe:
	cd "$(PROJECT_ROOT)"
	uv run python scriptss/generar_informe.py
