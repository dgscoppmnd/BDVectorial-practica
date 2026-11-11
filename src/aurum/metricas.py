"""Métricas de ranking corregidas para la práctica Aurum Market.

Correcciones respecto a la versión anterior de la práctica:

- ``ndcg_at_k``: el DCG ideal (IDCG) se calcula con **todos los juicios de la
  consulta** (no solo con los documentos recuperados). Si el sistema no
  recupera los mejores documentos juzgados, el nDCG baja, como debe ser.
- ``recall_at_k`` y ``mrr_at_k``: el conjunto de referencia contiene **solo los
  productos relevantes** (relevancia > 0). Los juzgados como irrelevantes
  (etiqueta ESCI ``I``, relevancia 0) no cuentan como aciertos.
"""

from __future__ import annotations

import math
from typing import Mapping, Sequence


def dcg(gains: Sequence[float]) -> float:
    """DCG con ganancia exponencial: sum((2^rel - 1) / log2(pos + 1))."""
    return sum((2.0**g - 1.0) / math.log2(i + 2) for i, g in enumerate(gains))


def ndcg_at_k(ranked_ids: Sequence[str], judgments: Mapping[str, int], k: int = 10) -> float:
    """nDCG@k. ``judgments`` contiene TODOS los juicios de la consulta.

    El IDCG usa el top-k de todas las relevancias juzgadas, de modo que no
    recuperar los documentos más relevantes penaliza la métrica.
    """
    gains = [judgments.get(pid, 0) for pid in ranked_ids[:k]]
    ideal = sorted(judgments.values(), reverse=True)[:k]
    idcg = dcg(ideal)
    return dcg(gains) / idcg if idcg > 0 else 0.0


def relevant_set(judgments: Mapping[str, int]) -> set[str]:
    """Productos con relevancia > 0 (E, S o C). Excluye los irrelevantes."""
    return {pid for pid, rel in judgments.items() if rel > 0}


def recall_at_k(ranked_ids: Sequence[str], judgments: Mapping[str, int], k: int = 10) -> float:
    """Recall@k sobre el conjunto de relevantes (relevancia > 0)."""
    relevant = relevant_set(judgments)
    if not relevant:
        return 0.0
    return len(set(ranked_ids[:k]) & relevant) / len(relevant)


def mrr_at_k(ranked_ids: Sequence[str], judgments: Mapping[str, int], k: int = 10) -> float:
    """MRR@k: inverso de la posición del primer resultado relevante (>0)."""
    relevant = relevant_set(judgments)
    for pos, pid in enumerate(ranked_ids[:k], start=1):
        if pid in relevant:
            return 1.0 / pos
    return 0.0
