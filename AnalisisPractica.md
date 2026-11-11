# Análisis y decisiones de diseño

Este documento resume las decisiones de la solución; el desarrollo completo con evidencia
ejecutada está en `notebook/Aurum_Market_Practica.ipynb` y el informe en `informe/INFORME.pdf`.

## 1. Contrato del sistema

El caso se traduce a cinco capacidades con criterios de aceptación verificables (tabla en la
portada del notebook): búsqueda semántica (top-10 para las 12 consultas ciegas), búsqueda
filtrada por marca **ejecutada en el motor** (4/4 consultas con resultados y 100% de la marca),
mutaciones idempotentes y visibles (24 eventos), control de duplicados (regla calibrada +
decisión para 14 altas ciegas) y operativa (latencia p50/p95, persistencia).

## 2. Base de datos vectorial (Qdrant)

- **Motor**: Qdrant v1.20 en Docker (`docker-compose.yml`) con volumen persistente
  `./qdrant_storage`; SDK nativo `qdrant-client`. Sin Docker, el notebook cae al modo local
  persistente del SDK (mismo API), aunque el modo medido es el servidor.
- **Esquema**: colección `aurum_catalogo`, vectores de 384 dims con distancia coseno, HNSW
  explícito (`m=16`, `ef_construct=128`), payload con `product_id`, `title`, `brand`,
  `brand_norm`, `color`, `locale`, `catalog_version`, `active` e índices de payload
  keyword/bool.
- **IDs**: los `record_id` (UUIDv5 estables) son los IDs de punto → reingesta idempotente.
- **Ingesta**: catálogo completo (15.000) por lotes de 256 con `wait=True`; se verifica
  recuento, estado `green`, reingesta sin duplicados y persistencia tras reconectar.

## 3. Representación

- **Preparación de texto** (`src/aurum/texto.py`): tres composiciones comparadas (solo título;
  título+atributos; título+atributos+descripción truncada a 600 caracteres para controlar la
  longitud de secuencia). Los nulos nunca se incorporan como texto (probado en tests).
- **Modelo**: comparación controlada (misma muestra, mismas consultas, búsqueda exacta para
  aislar la representación) entre `all-MiniLM-L6-v2` (inglés) y `intfloat/multilingual-e5-small`
  (multilingüe, con contrato de prefijos `query:`/`passage:` respetado). Gana el multilingüe;
  versiones y dimensión fijadas, coste de codificación medido.
- **Geometría**: vectores unitarios → producto escalar ≡ coseno (verificado numéricamente);
  se conserva el score nativo del motor y mayor = mejor.

## 4. Métricas corregidas

`src/aurum/metricas.py` corrige los dos errores señalados en la evaluación anterior:
el IDCG del nDCG usa **todos los juicios** de la consulta (no solo lo recuperado) y
Recall/MRR cuentan **solo los relevantes** (relevancia > 0, excluyendo los juzgados `I`).
Validado con ejemplos a mano en el notebook y en `tests/test_metricas.py`.

## 5. Evaluación

- Baseline TF-IDF y sistema denso comparados sobre el **catálogo completo** con el mismo
  protocolo (consultas, juicios, k, métricas).
- **Fidelidad ANN**: recall@10 del HNSW frente al oráculo exacto del propio motor
  (`exact=True`) para `hnsw_ef ∈ {4,16,64,128,256}`, con latencia por configuración; la
  elección de producción (`ef=128`) se justifica con esa tabla.
- **Latencia**: calentamiento + 20 repeticiones × 8 consultas; percentiles reales
  (`np.percentile`) separando codificación de consulta y búsqueda; entorno registrado.

## 6. Mutaciones

Los 24 eventos se aplican **sobre la colección** en orden `sequence`: `UPSERT` recodifica el
texto y upserta el punto (con `catalog_version` para trazabilidad); `DELETE` borra solo por ID
explícito (nunca por filtro amplio). Verificación por ID (retrieve) y por búsqueda
(visibilidad del revisado, ausencia del borrado), recuento final contra el estado esperado y
repetición completa del lote para demostrar idempotencia en el motor.

## 7. Duplicados

Candidatos top-5 **desde la base vectorial sobre el catálogo completo**; regla
`score_top1 ≥ umbral` y `margen ≥ margen_min` calibrada en desarrollo maximizando F1 con
desempate por precisión (coste asimétrico: un falso positivo fusiona fichas distintas).
Se reportan precision/recall/F1 y la regla congelada se aplica a las 14 altas ciegas.

## 8. Atribución de errores

Cuatro casos analizados con evidencia (notebook §14): representación (peor consulta con
top-10 ANN = exacto → la pérdida no es del índice), índice ANN (vecinos perdidos con `ef`
bajo), datos/filtros (66 marcas con varias grafías → filtro sobre `brand_norm`) y regla de
duplicados (scores comprimidos cerca del umbral, riesgo de sobreajuste con 14 casos).

## 9. Ingeniería

- Componentes compartidos en `src/aurum/`; tests en `tests/` (métricas a mano, contrato de
  texto, contrato con Qdrant usando el modo en memoria del SDK, y esquema de artefactos).
- `scriptss/validate_content.py` valida estructura y artefactos; `make test/validate/informe`.
- Los artefactos se exportan desde la colección **antes** de aplicar los eventos (los juicios
  de evaluación están definidos sobre el catálogo base) y se validan automáticamente.
- Sin secretos en el código: la configuración vive en `.env` (plantilla `.env.example`).

## 10. Qué queda fuera (propuestas, no implementadas)

Reranking cross-encoder sobre el top-50, búsqueda híbrida (denso + BM25 con RRF),
cuantización escalar y monitorización de deriva del catálogo.
