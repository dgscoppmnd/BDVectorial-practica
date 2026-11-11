"""Tests de las métricas de ranking corregidas (valores calculados a mano)."""

import math

import pytest

from aurum.metricas import dcg, mrr_at_k, ndcg_at_k, recall_at_k, relevant_set

JUICIOS = {"A": 3, "B": 2, "C": 0, "D": 1}  # C está juzgado como irrelevante


def test_dcg_valores_manuales():
    assert dcg([3]) == pytest.approx(7.0)
    assert dcg([3, 2]) == pytest.approx(7.0 + 3.0 / math.log2(3))


def test_ndcg_ideal_usa_todos_los_juzgados():
    # Recuperar solo "D" (rel 1) con IDCG de TODOS los juicios: lejos de 1.
    valor = ndcg_at_k(["D"], JUICIOS, k=10)
    idcg = dcg([3, 2, 1, 0][:10])
    assert valor == pytest.approx(dcg([1]) / idcg)
    # El error antiguo (ideal solo con lo recuperado) habría dado 1.0.
    assert valor < 0.2


def test_ndcg_ranking_perfecto():
    assert ndcg_at_k(["A", "B", "D", "C"], JUICIOS, k=10) == pytest.approx(1.0)


def test_ndcg_sin_juicios_es_cero():
    assert ndcg_at_k(["A"], {}, k=10) == 0.0


def test_recall_excluye_irrelevantes():
    # C está juzgado (rel 0) pero no cuenta como acierto ni en el denominador.
    assert relevant_set(JUICIOS) == {"A", "B", "D"}
    assert recall_at_k(["C", "A"], JUICIOS, k=10) == pytest.approx(1 / 3)
    assert recall_at_k(["A", "B", "D"], JUICIOS, k=10) == pytest.approx(1.0)


def test_mrr_ignora_irrelevantes_juzgados():
    # El error antiguo habría devuelto 1.0 (C juzgado en posición 1).
    assert mrr_at_k(["C", "A"], JUICIOS, k=10) == pytest.approx(0.5)
    assert mrr_at_k(["X", "Y"], JUICIOS, k=10) == 0.0


def test_corte_en_k():
    assert recall_at_k(["X", "A"], JUICIOS, k=1) == 0.0
    assert mrr_at_k(["X", "A"], JUICIOS, k=1) == 0.0
