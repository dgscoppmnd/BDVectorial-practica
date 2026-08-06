# Aurum Market · Práctica de Bases de Datos Vectoriales

## Descripción del proyecto

Este proyecto contiene un notebook de práctica para construir un motor local de búsqueda y control de catálogo sobre un dataset de productos. El notebook implementa:

- Un baseline léxico TF-IDF sobre `title + text`.
- Una representación densa para búsqueda semántica con embeddings.
- Filtrado por marca durante la recuperación.
- Ingesta de eventos de catálogo ordenados y idempotentes.
- Calibración de detección de duplicados mediante umbrales de similitud y margen.
- Exportación de artefactos de resultados y métricas.

## Archivos principales

- `notebook/Aurum_Market_Practica.ipynb`: notebook principal con toda la solución.
- `data/`: carpeta con los datos de catálogo, consultas, relevancias, duplicados y eventos.
- `results/`: carpeta con los resultados generados por el notebook.
- `results/resultados_busqueda.csv`: salida de búsqueda sobre el conjunto de evaluación.
- `results/resultados_duplicados.csv`: salida de detección de duplicados, si el archivo de evaluación estuvo disponible.
- `results/metricas_desarrollo.json`: métricas de evaluación calculadas sobre el conjunto de desarrollo.

## Requisitos

- Python 3.10+ (la práctica se ha probado en Python 3.14).
- Bibliotecas Python:
  - `pandas`
  - `numpy`
  - `scikit-learn`
  - `sentence-transformers` (opcional, para usar embeddings reales)
  - `faiss-cpu` (opcional, para índice ANN)

Si no se dispone de `sentence-transformers` o `faiss-cpu`, el notebook usa un fallback local con TF-IDF para embeddings y búsqueda exhaustiva.

## Instalación

1. Crea un entorno virtual (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instala las dependencias principales:

```powershell
pip install pandas numpy scikit-learn
```

3. Instala dependencias opcionales si deseas usar embeddings y Faiss:

```powershell
pip install sentence-transformers faiss-cpu
```

## Ejecución

1. Abre `notebook/Aurum_Market_Practica.ipynb` en VS Code o Jupyter.
2. Ejecuta las celdas en orden de arriba hacia abajo.
3. Revisa las siguientes salidas y archivos generados en `results/`:
   - `results/resultados_busqueda.csv`
   - `results/resultados_duplicados.csv`
   - `results/metricas_desarrollo.json`

## Notas de uso

- Si `sentence-transformers` no está disponible, el notebook usa TF-IDF como respaldo para embeddings.
- Si `faiss-cpu` no está disponible, la búsqueda densa usa cálculo exhaustivo con NumPy.
- El notebook ya maneja compatibilidad con versiones de scikit-learn que no aceptan `stop_words="spanish"`.

## Siguientes pasos (TODO)

-

