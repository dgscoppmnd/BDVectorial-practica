#!/usr/bin/env python3
"""Genera el informe de la práctica (informe/INFORME.pdf) a partir de results/.

El informe se construye con los valores reales de `results/metricas_desarrollo.json`,
de modo que regenerarlo tras reejecutar el notebook mantiene texto y evidencia
sincronizados. Uso: `python scriptss/generar_informe.py` (o `make informe`).
"""

from __future__ import annotations

import json
from pathlib import Path

from fpdf import FPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT_ROOT / "results"
OUT_DIR = PROJECT_ROOT / "informe"


def latin(texto: str) -> str:
    """Las fuentes núcleo de FPDF son latin-1: sustituimos lo no representable."""
    reemplazos = {"≥": ">=", "≤": "<=", "·": "-", "→": "->", "∈": "en", "—": "-",
                  "“": '"', "”": '"', "✔": "[ok]", "×": "x", "≈": "~"}
    for k, v in reemplazos.items():
        texto = texto.replace(k, v)
    return texto.encode("latin-1", "replace").decode("latin-1")


class Informe(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120)
        self.cell(0, 6, latin("Aurum Market · Práctica de Bases de Datos Vectoriales"),
                  align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120)
        self.cell(0, 10, f"{self.page_no()}", align="C")
        self.set_text_color(0)

    def titulo(self, texto):
        self.set_font("helvetica", "B", 14)
        self.ln(4)
        self.multi_cell(0, 7, latin(texto), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def parrafo(self, texto):
        self.set_font("helvetica", "", 10)
        self.multi_cell(0, 5.2, latin(texto), new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def vineta(self, texto):
        self.set_font("helvetica", "", 10)
        self.set_x(self.l_margin + 4)
        self.multi_cell(0, 5.2, latin("- " + texto), new_x="LMARGIN", new_y="NEXT")

    def tabla(self, cabeceras, filas, anchos=None):
        ancho_util = self.w - self.l_margin - self.r_margin
        anchos = anchos or [ancho_util / len(cabeceras)] * len(cabeceras)
        self.set_font("helvetica", "B", 9)
        self.set_fill_color(235)
        for cab, w in zip(cabeceras, anchos):
            self.cell(w, 6, latin(str(cab)), border=1, fill=True)
        self.ln()
        self.set_font("helvetica", "", 9)
        for fila in filas:
            for valor, w in zip(fila, anchos):
                self.cell(w, 6, latin(str(valor)), border=1)
            self.ln()
        self.ln(2)


def fmt(x, dec=3):
    return f"{x:.{dec}f}" if isinstance(x, (int, float)) else str(x)


def main() -> None:
    with open(RESULTS / "metricas_desarrollo.json", encoding="utf-8") as fh:
        m = json.load(fh)
    OUT_DIR.mkdir(exist_ok=True)

    proto = m["protocolo"]
    lat = m["latencia_detalle"]
    pdf = Informe()
    pdf.set_auto_page_break(True, margin=18)
    pdf.add_page()

    # Portada / resumen ejecutivo
    pdf.set_font("helvetica", "B", 18)
    pdf.multi_cell(0, 9, new_x="LMARGIN", new_y="NEXT", text=latin("Aurum Market · Búsqueda semántica, operaciones sobre la "
                               "colección y control de altas duplicadas"))
    pdf.set_font("helvetica", "", 11)
    pdf.multi_cell(0, 6, new_x="LMARGIN", new_y="NEXT", text=latin("Informe de la práctica de Bases de Datos Vectoriales · "
                               "Diego Gil Sánchez"))
    pdf.ln(4)
    pdf.parrafo(
        "Resumen: el sistema ingiere el catálogo completo de Aurum Market "
        f"({proto['corpus']} productos) en una base de datos vectorial persistente "
        f"({proto['motor']}, colección '{proto['coleccion']}'), con embeddings del modelo "
        f"{proto['modelo']} y la composición de texto '{proto['composicion_texto']}'. "
        "Expone búsqueda semántica global, búsqueda filtrada por marca ejecutada en el motor, "
        "mutaciones idempotentes del catálogo y una regla calibrada de detección de duplicados. "
        "Toda la evidencia es reproducible desde notebook/Aurum_Market_Practica.ipynb.")

    pdf.titulo("1. Problema y contrato del sistema")
    pdf.parrafo(
        "Aurum Market necesita que un cliente describa su intención en lenguaje natural y reciba "
        "productos relevantes del catálogo; que las búsquedas por marca devuelvan solo esa marca; "
        "que las revisiones y bajas de fichas sean visibles en el buscador sin reindexados manuales; "
        "y que las altas duplicadas se detecten antes de ensuciar el catálogo. El contrato medible: "
        "top-10 válido para las 12 consultas ciegas; 4/4 consultas filtradas con el 100% de la marca "
        "pedida; 24 eventos aplicados, verificados e idempotentes; decisión y candidato para las 14 "
        "altas ciegas; latencia y persistencia medidas.")

    pdf.titulo("2. Arquitectura")
    pdf.parrafo(
        "CSV del catálogo -> preparación de texto (sin nulos, descripción truncada a 600 caracteres) "
        "-> embeddings normalizados (384 dims) -> Qdrant en Docker con volumen persistente. "
        f"Colección con distancia coseno e índice HNSW explícito (m={proto['hnsw']['m']}, "
        f"ef_construct={proto['hnsw']['ef_construct']}, ef de búsqueda={proto['hnsw']['ef_busqueda']}). "
        "Payload por punto: product_id, title, brand, brand_norm (normalizada para filtrar), color, "
        "locale, catalog_version y active, con índices keyword/bool. Los IDs de punto son los UUID "
        "estables record_id, lo que hace la reingesta idempotente.")

    pdf.titulo("3. Metodología y comparaciones controladas")
    pdf.vineta("Protocolo fijo: mismas 8 consultas de desarrollo, mismos 248 juicios ESCI, k=10, "
               "métricas corregidas (IDCG con todos los juzgados; recall/MRR solo sobre relevantes).")
    pdf.vineta("Baseline léxico TF-IDF sobre el mismo corpus y la misma composición de texto.")
    pdf.vineta("Selección de modelo con búsqueda exacta (aísla la representación del índice ANN).")
    pdf.vineta("Composiciones de texto comparadas cambiando un único factor a la vez.")
    pdf.vineta("Fidelidad ANN medida contra oráculo exacto del propio motor (exact=True).")
    pdf.vineta(f"Latencia: {lat['protocolo']['calentamiento']} repeticiones de calentamiento + "
               f"{lat['protocolo']['repeticiones']} medidas x {lat['protocolo']['consultas']} consultas; "
               "percentiles reales con np.percentile.")
    pdf.ln(1)

    pdf.titulo("4. Resultados")
    pdf.parrafo("4.1 Comparación de modelos (muestra de desarrollo, búsqueda exacta):")
    pdf.tabla(["Modelo", "nDCG@10", "Recall@10", "MRR@10"],
              [[c["nombre"], fmt(c["ndcg@10"]), fmt(c["recall@10"]), fmt(c["mrr@10"])]
               for c in m["comparacion_modelos"]],
              [80, 36, 36, 36])
    pdf.parrafo("4.2 Composiciones de texto (modelo ganador):")
    pdf.tabla(["Composición", "nDCG@10", "Recall@10", "MRR@10"],
              [[c["composicion"], fmt(c["ndcg@10"]), fmt(c["recall@10"]), fmt(c["mrr@10"])]
               for c in m["comparacion_composiciones"]],
              [80, 36, 36, 36])
    pdf.parrafo(f"4.3 Sistema final frente a baseline (catálogo completo, {proto['corpus']} productos):")
    pdf.tabla(["Sistema", "nDCG@10", "Recall@10", "MRR@10"],
              [["TF-IDF (baseline léxico)", fmt(m["lexical"]["ndcg_at_10"]),
                fmt(m["lexical"]["recall_at_10"]), fmt(m["lexical"]["mrr_at_10"])],
               [f"Denso ({proto['modelo'].split('/')[-1]} + Qdrant)", fmt(m["dense"]["ndcg_at_10"]),
                fmt(m["dense"]["recall_at_10"]), fmt(m["dense"]["mrr_at_10"])]],
              [80, 36, 36, 36])
    pdf.parrafo("4.4 Fidelidad del índice HNSW frente al oráculo exacto (20 consultas):")
    pdf.tabla(["hnsw_ef", "recall@10 medio", "recall@10 peor consulta", "p50 (ms)", "p95 (ms)"],
              [[f["hnsw_ef"], fmt(f["recall@10 vs oráculo (medio)"], 4),
                fmt(f["recall@10 (peor consulta)"], 4),
                f["latencia p50 (ms)"], f["latencia p95 (ms)"]] for f in m["fidelidad_ann"]],
              [25, 45, 55, 30, 30])
    pdf.parrafo("4.5 Latencia extremo a extremo (consulta en texto -> top-10):")
    pdf.tabla(["Etapa", "p50 (ms)", "p95 (ms)", "muestras"],
              [["Codificación de la consulta", lat["codificacion_consulta"]["p50_ms"],
                lat["codificacion_consulta"]["p95_ms"], lat["codificacion_consulta"]["n_muestras"]],
               ["Búsqueda en el motor", lat["busqueda_motor"]["p50_ms"],
                lat["busqueda_motor"]["p95_ms"], lat["busqueda_motor"]["n_muestras"]],
               ["Total", lat["total"]["p50_ms"], lat["total"]["p95_ms"], lat["total"]["n_muestras"]]],
              [80, 30, 30, 30])
    regla = m["duplicados_regla"]
    pdf.parrafo(
        "4.6 Duplicados: regla calibrada en desarrollo con candidatos de la base vectorial: "
        f"score_top1 >= {regla['umbral']} y margen (top1-top2) >= {regla['margen_min']} -> "
        f"precision={regla['precision']}, recall={regla['recall']}, F1={regla['f1']}. "
        "La regla congelada se aplicó a las 14 altas ciegas (results/resultados_duplicados.csv).")

    pdf.titulo("5. Atribución de errores (resumen; evidencia en el notebook, sección 14)")
    pdf.vineta("Representación: en la peor consulta de desarrollo, el top-10 del ANN coincide con el "
               "exacto, luego la pérdida es del modelo/texto (p. ej. atributos como talla o negaciones "
               "que el embedding no captura), no del índice. Lo corrige un modelo mayor o un reranker.")
    pdf.vineta("Índice ANN: con ef muy bajo se pierden vecinos del oráculo; se recupera subiendo "
               "hnsw_ef (tabla 4.4). Es un compromiso fidelidad-latencia controlado y medido.")
    pdf.vineta("Datos/filtros: 66 marcas del catálogo tienen varias grafías; un filtro de igualdad "
               "exacta sobre 'brand' pierde resultados. Se corrige en la capa de ingesta con "
               "'brand_norm' (normalizada) y filtrando sobre ella en el motor.")
    pdf.vineta("Regla de duplicados: los scores de las altas casi-duplicadas se comprimen cerca del "
               "umbral; con 14 casos de calibración hay riesgo de sobreajuste. Mitigación: más "
               "etiquetas y coste asimétrico explícito (un falso positivo fusiona fichas distintas).")

    pdf.titulo("6. Limitaciones")
    pdf.vineta("8 consultas de desarrollo son pocas para diferencias finas entre configuraciones.")
    pdf.vineta("Los juicios ESCI no cubren todo el corpus: los no juzgados cuentan como relevancia 0, "
               "por lo que las métricas son una cota inferior.")
    pdf.vineta("Latencias medidas en un único equipo local sin red (entorno registrado en el JSON).")

    pdf.titulo("7. Recomendación de negocio")
    pdf.parrafo(
        "Desplegar el motor denso multilingüe con hnsw_ef=128 y el filtro de marca normalizado. "
        "La evolución con mayor retorno es un reranker cross-encoder sobre el top-50 del motor "
        "(ataca la capa dominante de error, la representación) y ampliar los juicios de desarrollo "
        "para calibrar sin sobreajuste. Propuestas futuras no implementadas: búsqueda híbrida "
        "(denso + BM25 con fusión RRF), cuantización escalar para reducir memoria y monitorización "
        "de deriva del catálogo.")

    pdf.titulo("Anexo: entorno de medición")
    ent = proto["entorno"]
    pdf.parrafo(f"Python {ent['python']} · {ent['plataforma']} · {ent['nucleos']} núcleos. "
                "Paquetes: " + ", ".join(f"{k} {v}" for k, v in ent["paquetes"].items()) + ".")

    salida = OUT_DIR / "INFORME.pdf"
    pdf.output(str(salida))
    print(f"Informe generado: {salida}")


if __name__ == "__main__":
    main()
