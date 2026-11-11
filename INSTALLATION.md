# Instrucciones de instalación y ejecución

## Requisitos previos

- **Python** ≥ 3.14, < 3.15
- **Docker** (recomendado) para el servidor Qdrant. Sin Docker, el notebook usa el modo
  local persistente del SDK de Qdrant de forma automática.
- Linux, macOS o Windows.

## 1. Levantar la base de datos vectorial (Qdrant)

```bash
docker compose up -d
curl http://localhost:6333/readyz   # debe responder "all shards are ready"
```

El almacenamiento es persistente en `./qdrant_storage` (volumen Docker): la colección
sobrevive a reinicios del contenedor. La URL se configura con `QDRANT_URL` en `.env`
(por defecto `http://localhost:6333`).

## 2. Preparar el entorno Python

### Opción A: Makefile (automatizado)

```bash
make setup
```

### Opción B: uv (manual)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.14
uv sync --all-extras --python 3.14
cp .env.example .env
uv run python -m ipykernel install --user \
    --name aurum-bdv --display-name "Python (Aurum BDV)"
uv run python scriptss/validate_content.py --quick
```

### Opción C: pip + requirements.txt

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate   |   Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
python -m ipykernel install --user --name aurum-bdv --display-name "Python (Aurum BDV)"
python scriptss/validate_content.py --quick
```

## 3. Ejecutar el notebook

```bash
make lab        # o: uv run jupyter lab
```

Abrir `notebook/Aurum_Market_Practica.ipynb`, seleccionar el kernel **Python (Aurum BDV)**
y ejecutar todas las celdas. La primera ejecución descarga los dos modelos de embeddings
(~600 MB) y codifica el catálogo completo (~10 min en CPU); los embeddings se cachean en
`.cache_embeddings/` para reejecuciones.

**Modo humo** (validación rápida del recorrido completo, ~3 min): exportar `AURUM_SMOKE=1`
antes de lanzar Jupyter. Usa la muestra de 1.500 productos y una colección separada
(`aurum_catalogo_smoke`).

## 4. Pruebas y validación

```bash
make test       # pytest: métricas, preparación de texto, contrato Qdrant, artefactos
make validate   # estructura del proyecto + esquema de los artefactos de results/
make informe    # regenera informe/INFORME.pdf a partir de results/
```

Las pruebas del contrato con Qdrant usan el modo en memoria del SDK: no necesitan Docker
ni modelos descargados.

## Dependencias principales

- `sentence-transformers` (≥3): modelos de embeddings (incluye `torch`)
- `qdrant-client` (≥1.12): SDK nativo de la base de datos vectorial
- `scikit-learn`: baseline léxico TF-IDF
- `plotly`: figuras del notebook
- `pandas`, `numpy`, `python-dotenv`, `jupyterlab`, `ipykernel`, `pytest`

## Solución de problemas

| Problema | Solución |
|---|---|
| `command not found: uv` | `export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"` |
| El kernel no aparece en Jupyter | reinstalar: `uv run python -m ipykernel install --user --force --name aurum-bdv --display-name "Python (Aurum BDV)"` |
| Qdrant no responde | `docker compose up -d` y comprobar `docker ps`; sin Docker, el notebook usa el modo local del SDK automáticamente |
| Descarga lenta de modelos | definir `HF_TOKEN` en `.env` (opcional) |
| Reejecución lenta | los embeddings se reutilizan de `.cache_embeddings/`; borrar esa carpeta fuerza el recálculo |

## Limpieza

- Las colecciones se borran solo desde la celda final del notebook (bandera `LIMPIAR=True`).
- `docker compose down` detiene el servidor; añadir `-v` **no** borra `./qdrant_storage`
  (es un bind mount: eliminarlo manualmente si se quiere empezar de cero).
