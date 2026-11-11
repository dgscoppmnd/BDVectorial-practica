# Aurum Market · Práctica de Bases de Datos Vectoriales

Motor de descubrimiento y control de catálogo para Aurum Market sobre una **base de datos
vectorial persistente (Qdrant)**: búsqueda semántica, filtrado por metadatos ejecutado en el
motor, mutaciones idempotentes del catálogo y control de altas duplicadas.

## Qué resuelve

| Capacidad | Cómo |
|---|---|
| Búsqueda semántica | Embeddings multilingües (`intfloat/multilingual-e5-small`, 384 dims) + Qdrant (coseno, HNSW `m=16`, `ef_construct=128`) sobre el **catálogo completo de 15.000 productos** |
| Búsqueda filtrada por marca | Filtro de payload `brand_norm` (marca normalizada) ejecutado **en el motor**, con índice keyword |
| Mutaciones del catálogo | Los 24 eventos (`UPSERT`/`DELETE`) se aplican sobre la colección, se verifican por ID y por búsqueda, y son idempotentes |
| Control de duplicados | Vecinos desde la base vectorial + regla `umbral de score` × `margen top1-top2` calibrada en desarrollo (precision/recall/F1) |
| Evaluación | nDCG@10, Recall@10 y MRR@10 corregidos, baseline TF-IDF comparable, fidelidad ANN medida frente a oráculo exacto, latencia p50/p95 con repeticiones |

## Ejecución rápida

```bash
# 1. Levantar Qdrant (persistente en ./qdrant_storage)
docker compose up -d

# 2. Preparar el entorno (uv) e instalar el kernel
make setup          # o ver INSTALLATION.md para pasos manuales / pip

# 3. Abrir y ejecutar el notebook completo
make lab            # notebook/Aurum_Market_Practica.ipynb (Run All)

# 4. Pruebas y validación
make test           # pytest: métricas, texto, contrato Qdrant, artefactos
make validate       # estructura del proyecto + esquema de results/
```

Sin Docker, el notebook cae automáticamente al modo local persistente del SDK de Qdrant
(`./qdrant_local`); el modo recomendado y medido es el servidor.

## Estructura

```
├── data/                   # datos de la práctica (ESCI, ver data/ATRIBUCION_DATOS.md)
├── notebook/
│   └── Aurum_Market_Practica.ipynb   # recorrido completo ejecutado
├── src/aurum/              # componentes reutilizados por notebook y tests
│   ├── metricas.py         # nDCG/Recall/MRR corregidos
│   └── texto.py            # composiciones de texto y normalización de marca
├── tests/                  # pruebas de métricas, texto, contrato Qdrant y artefactos
├── results/                # artefactos del contrato de resultados
│   ├── resultados_busqueda.csv       # top-10 de las 12 consultas ciegas
│   ├── resultados_duplicados.csv     # decisión para las 14 altas ciegas
│   └── metricas_desarrollo.json      # métricas, latencia, fidelidad ANN y protocolo
├── scriptss/
│   ├── validate_content.py # validación de estructura y artefactos
│   └── generar_informe.py  # genera informe/INFORME.pdf desde los resultados
├── informe/                # informe de la práctica (Markdown + PDF)
├── docker-compose.yml      # Qdrant v1.20 con volumen persistente
└── AnalisisPractica.md     # análisis de decisiones (resumen del informe)
```

## Decisiones clave (detalle en el notebook e informe)

- **Modelo**: comparación controlada `all-MiniLM-L6-v2` (inglés) vs `multilingual-e5-small`
  (multilingüe, prefijos `query:`/`passage:`) con el mismo protocolo; gana el multilingüe en un
  catálogo en español. Versiones fijadas en `requirements.txt`.
- **Texto**: tres composiciones comparadas; la elegida es título + marca + color + descripción
  truncada a 600 caracteres (control de longitud de secuencia). Los nulos nunca se incorporan.
- **Métrica**: coseno con vectores unitarios (= producto escalar, verificado numéricamente);
  score nativo del motor, mayor = mejor.
- **Fidelidad ANN**: recall@10 del HNSW frente a búsqueda exacta (`exact=True`) para
  `hnsw_ef ∈ {4,16,64,128,256}`; producción usa `ef=128` con evidencia.
- **Artefactos**: se exportan antes de aplicar los eventos, desde la colección con el catálogo
  base completo, y se validan automáticamente.

## Resultados

Ver `results/metricas_desarrollo.json` (métricas de desarrollo, latencias p50/p95 con
protocolo de repeticiones y entorno) y el informe en `informe/`.
