# Análisis de la práctica y decisiones tomadas

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
- `catalogo_muestra.csv` se utiliza como catálogo de referencia para desarrollar y validar la lógica.
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
- Se añadió validación de idempotencia repitiendo el mismo conjunto de eventos y comparando el catálogo resultante.

### 6. Detección de duplicados

- Se usa la información de `altas_desarrollo.csv` para calibrar umbrales.
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



