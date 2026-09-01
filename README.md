# Instrucciones de Instalación y Ejecución

## Requisitos Previos

- **Python**: Versión 3.14 o superior (inferior a 3.15)
- **Sistema Operativo**: Linux, macOS o Windows (con WSL2 recomendado)

## Instalación

### Opción 1: Instalación Automatizada con Makefile (No probado)

Esta es la forma más simple y automatizada para configurar el entorno completo.

```bash
# Desde la raíz del proyecto
make setup
```

### Opción 2: Instalación Manual con uv

Instalación paso a paso:

```bash
# 1. Instalar uv (si no está instalado)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# 2. Instalar Python 3.14
uv python install 3.14

# 3. Sincronizar dependencias
uv sync --all-extras --python 3.14

# 4. Configurar variables de entorno (crear .env)
cp .env.example .env

# 5. Instalar el kernel de Jupyter
uv run python -m ipykernel install --user \
    --name faiss-ann-search \
    --display-name "Python (BBDD Vectoriales · Sesión 2)"

# 6. Validar la instalación
uv run python scriptss/validate_content.py --quick
```

### Opción 3: Instalación con pip y requirements.txt

Si prefieres usar `pip` directamente:

```bash
# 1. Crear un entorno virtual
python -m venv venv

# 2. Activar el entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env

# 5. Instalar el kernel de Jupyter
python -m ipykernel install --user \
    --name faiss-ann-search \
    --display-name "Python (BBDD Vectoriales · Sesión 2)"
```

## Ejecución

### Opción 1: Ejecutar JupyterLab

```bash
make lab
```

O manualmente:

```bash
uv run jupyter lab
```
- Abrir el notebook principal: `notebook/Aurum_Market_Practica.ipynb`


## Estructura del Proyecto

```
.
├── data/                          # Datos del proyecto
│   ├── altas_*.csv               # Datasets de altas (desarrollo/evaluación)
│   ├── consultas_*.csv           # Datasets de consultas
│   ├── catalogo_*.csv            # Catálogos de productos
│   ├── eventos_catalogo.csv      # Eventos del catálogo
│   └── relevancias_*.csv         # Datos de relevancia
├── notebook/                      # Notebooks principales
│   └── Aurum_Market_Practica.ipynb
├── results/                       # Resultados de ejecuciones
│   ├── metricas_desarrollo.json
│   ├── resultados_busqueda.csv
│   └── resultados_duplicados.csv
├── scriptss/                      # Scripts Python utilitarios
│   ├── setup.sh
│   └── validate_content.py
├── pyproject.toml                # Configuración del proyecto
├── requirements.txt              # Dependencias (alternativa a uv)
├── Makefile                      # Automatización
├── README.md                     # Documentación principal
├── INSTALLATION.md               # Este archivo
└── .env                          # Variables de entorno (generado)
```

## Dependencias Principales

- **numpy** (≥2.4): Computación numérica
- **pandas** (≥3.0): Manipulación de datos
- **scikit-learn** (≥1.8): Machine Learning
- **sentence-transformers** (≥2.0): Embeddings de texto
- **faiss-cpu** (≥1.7.4): Búsqueda de vecinos más cercanos
- **jupyter-lab** (≥4.0): Entorno interactivo de notebooks
- **python-dotenv** (≥1.0): Gestión de variables de entorno

## Solución de Problemas

### Problema: `command not found: uv`

**Solución**: Asegurar que el directorio de instalación de `uv` está en tu `PATH`:
```bash
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
```

### Problema: `Python 3.14 not found`

**Solución**: Instala manualmente con:
```bash
uv python install 3.14
```

### Problema: El kernel de Jupyter no aparece

**Solución**: Reinstala el kernel:
```bash
uv run python -m ipykernel install --user --force \
    --name faiss-ann-search \
    --display-name "Python (BBDD Vectoriales)"
```

### Problema: Errores de dependencias con pip

**Solución**: Usa `uv` en su lugar, que maneja las dependencias de forma más robusta:
```bash
uv sync --all-extras
```

## Variables de Entorno

El proyecto usa un archivo `.env` para configurar variables de entorno. Crea este archivo basándote en `.env.example`:

```bash
cp .env.example .env
```

## Verificación de la Instalación

Para verificar que todo está correctamente instalado, ejecuta:

```bash
# Validación
uv run python scriptss/validate_content.py
```

## Próximos Pasos

1. Ejecuta `make lab` para abrir JupyterLab
2. Abre `notebook/Aurum_Market_Practica.ipynb` para comenzar
3. Consulta `README.md` para más información sobre el proyecto















# Análisis y decisiones tomadas

## Objetivo de la solución

El notebook busca cubrir el flujo completo de un ejercicio de bases de datos vectoriales para catálogo de productos:

- Definir un baseline interpretable.
- Construir una representación densa de producto.
- Implementar búsqueda semántica local.
- Agregar filtros de metadatos.
- Controlar cambios de catálogo con eventos.
- Detectar duplicados con una regla calibrada.
- Generar artefactos de salida para evaluación.

## Decisiones tomadas

### 1. Estructura de datos

- Se usan los archivos de `data/` suministrados en la práctica.
- `catalogo_muestra.csv` se utiliza como catálogo de referencia para desarrollar y validar la lógica (No se usa el catalogo completo por restricciones de memoria).
- Las consultas de desarrollo y evaluación se separan en `consultas_desarrollo.csv` y `consultas_evaluacion.csv`.
- Las relevancias se usan para construir métricas sobre el conjunto de desarrollo.

### 2. Baseline léxico

- Se construyó un baseline TF-IDF sobre la concatenación de `title + text`.
- El modelo usa `TfidfVectorizer(max_features=20000, ngram_range=(1,2), stop_words=None)` para ser compatible con la versión local de scikit-learn.
- La búsqueda léxica se realiza con similitud de coseno (`linear_kernel`).

### 3. Representación densa

- El texto para embeddings combina `title`, `brand`, `color` y `text` en un solo campo enriquecido.
- Si `sentence-transformers` está disponible, se emplea `all-MiniLM-L6-v2`.
- Si no está disponible, el notebook usa un fallback local con TF-IDF para generar vectores de características.
- Los vectores se normalizan para interpretar la similitud coseno directamente.

### 4. Búsqueda y filtrado

- La función `search_dense()` calcula la similitud entre consulta y catálogo.
- Cuando `faiss` está disponible, se usa `IndexFlatIP` para eficiencia.
- Si no está disponible, se recurre a dot product con NumPy.
- El filtro por `brand` se aplica durante el bucle de resultados, no como post-procesado independiente.

### 5. Eventos de catálogo e idempotencia

- La ingesta de `eventos_catalogo.csv` se procesa en orden de `sequence`.
- El notebook actualiza el catálogo con `UPSERT` y elimina con `DELETE`.
- Se añade validación de idempotencia repitiendo el mismo conjunto de eventos y comparando el catálogo resultante.

### 6. Detección de duplicados

- Se usa la información de `altas_desarrollo.csv` que calibrar umbrales.
- La regla considera el score del candidato principal y la diferencia (`margin`) respecto al segundo mejor.
- La calibración busca maximizar F1 sobre el conjunto de desarrollo.

### 7. Exportación de resultados

- El notebook genera `results/resultados_busqueda.csv` para el conjunto de evaluación.
- Genera `results/resultados_duplicados.csv` si el fichero `altas_evaluacion.csv` está presente.
- Genera `results/metricas_desarrollo.json` con métricas agregadas y latencia aproximada.

### Aspectos a verificar manualmente

- Que el dataset completo requerido por el enunciado esté disponible en `data/` si la práctica lo solicita explícitamente.
- Que `altas_evaluacion.csv` exista si se desea generar `resultados_duplicados.csv` en evaluación.
- Que las versiones de paquetes instaladas coincidan con las dependencias reales del entorno.

## Documentación de decisiones operativas

### 1. Elección de representación

Se toma una aproximación híbrida, siguiendo el patrón de la práctica y de los notebooks de clase:

- baseline léxico con TF-IDF para ofrecer una primera referencia interpretable;
- representación densa con embeddings semánticos usando `all-MiniLM-L6-v2` cuando está disponible;
- normalización L2 antes de la comparación para que la métrica de similitud sea consistente;
- uso de producto escalar o similitud coseno como métrica nativa del índice, manteniendo la misma semántica en la búsqueda.

### 2. Índice y estructura ANN

A partir de los notebooks de clase, la decisión de diseño es:

- construir un índice exacto (`IndexFlatIP`) como oráculo;
- añadir un índice aproximado tipo HNSW (`IndexHNSWFlat`) para reproducir el patrón de clases en la parte de escala;
- mantener explícitos los hiperparámetros principales (`M`, `efConstruction`, `efSearch`), porque estos cambian la calidad, la latencia y la fidelidad del ranking;
- separar la métrica de similitud del algoritmo de acceso: HNSW no mejora la representación y tampoco elimina la necesidad de medir recall.

### 3. Filtrado

La recuperación no debe ser solo semántica. La base vectorial debe aceptar restricciones sobre metadatos (en este caso, la marca) como parte de la consulta.

La decisión tomada es:

- ejecutar primero la búsqueda vectorial sobre el conjunto de candidatos potenciales;
- aplicar el filtro sobre la marca como condición del conjunto viable;
- verificar que el filtro se aplica en la base y no como postprocesado a ciegas, para evitar que se silencien productos incorrectos.

### 4. Mutaciones y consistencia

Siguiendo el trabajo de las sesiones de clase:

- los eventos de catálogo se aplican en orden cronológico por `sequence`;
- se distingue entre `UPSERT` y `DELETE`;
- la estrategia es idempotente: ejecutar dos veces la misma secuencia no debe cambiar el estado final;
- la visibilidad de las escrituras se valida con lecturas por ID y consultas vectoriales.

### 5. Detección de duplicados

Se usa una regla reproducible basada en dos piezas:

- score del mejor candidato;
- margen con respecto al segundo candidato.

La pareja de umbrales se calibra sobre `altas_desarrollo.csv` para maximizar F1, pero la decisión final debe justificar el coste de falsos positivos y falsos negativos. En la práctica, un falso positivo puede bloquear una alta válida, mientras que un falso negativo puede dejar publicar un duplicado.

### 6. Resultados Generados

- `resultados_busqueda.csv` para recuperación ciega;
- `resultados_duplicados.csv` para decisiones de alta;
- `metricas_desarrollo.json` con nDCG, recall y MRR;

# StockAssistant (Jupyter)
## Índice recomendado para implementar una BD vectorial con chunks

### Objetivo

Guardar chunks de texto, cada uno con su vector de embeddings, sus metadatos y su estado de visibilidad. Esto es la base para una búsqueda semántica y un sistema de descubrimiento de documentos o productos.

### Índice sugerido

1. Definir el contrato del chunk
   - `chunk_id` (UUID estable o hash del contenido + fuente + offset)
   - `document_id`
   - `source`
   - `section`
   - `text`
   - `embedding`
   - `metadata` (marca, categoría, idioma, fecha, version, etc.)
   - `created_at`, `updated_at`, `active`

2. Elegir el motor
   - Chroma o Qdrant para un despliegue local y reproducible.
   - Qdrant suele ser muy útil cuando se quiere un control más claro de HNSW, filtros por metadatos y almacenamiento de payloads.
   - Chroma es más directo para prototipos y pruebas rápidas.
   - En la práctica de Aurum Market, una elección razonable es utilizar un motor local con HNSW y filtros sobre `brand`.

3. Definir el esquema vectorial
   - dimensión del embedding = 384 para `all-MiniLM-L6-v2` o la dimensión del modelo elegido;
   - métrica = cosine o dot product según la normalización;
   - índice = HNSW con parámetros explícitos: `M`, `ef_construction`, `ef_search`;
   - payload con metadatos para permitir filtros antes o durante la búsqueda.

4. Normalizar y documentar el contrato
   - aplicar la misma normalización del embedding en ingest y en query;
   - registrar el modelo exacto, prefijo y política de texto;
   - guardar la dimensión y el tipo (`float32`) para evitar incompatibilidades.

5. Ingesta por lotes e idempotente
   - usar `upsert` sobre `chunk_id` o `document_id + offset`;
   - procesar por lotes con reintentos y control de errores;
   - no duplicar registros si la ingesta se repite.

6. Búsqueda semántica
   - `search(query, k=10)`
   - `search(query, k=10, filters={"brand": "Nike"})`
   - devolver `chunk_id`, `document_id`, `score`, `metadata`, `text` y `rank`.

7. Mutaciones y consistencia
   - gestionar `upsert`, `delete`, `reindex` y `soft delete`;
   - comprobar visibilidad con lecturas por ID y consultas vectoriales;
   - no considerar la ingesta completa hasta que el motor confirme el recuento final.

8. Evaluación
   - medir `nDCG@10`, `Recall@10`, `MRR@10` sobre desarrollo;
   - comparar con un oráculo exacto para detectar pérdida del ANN;
   - registrar latencia p50/p95 y filtros de marca.


Forma más facil de implementar la BD vectorial es:

- modelo: embeddings denso normalizados;
- motor: Qdrant o Chroma local;
- índice: HNSW;
- esquema: ids estables, metadata de negocio y texto a buscar;
- operación: `upsert` idempotente + filtros por metadata;
- validación: recuento, visibilidad, ranking y métricas.

