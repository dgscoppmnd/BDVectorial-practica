"""Tests de comportamiento del contrato con la base vectorial.

Usan el modo en memoria del SDK de Qdrant con vectores sintéticos, de modo que
prueban ingesta por lotes, IDs estables, filtrado en el motor, mutaciones e
idempotencia sin necesitar el servidor Docker ni los modelos de embeddings.
"""

import uuid

import numpy as np
import pytest
from qdrant_client import QdrantClient, models

from aurum.texto import normalize_brand

DIM = 16
N = 40


@pytest.fixture()
def cliente():
    cli = QdrantClient(location=":memory:")
    cli.create_collection(
        collection_name="test",
        vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE),
    )
    yield cli
    cli.close()


def _vectores(n, semilla=0):
    rng = np.random.default_rng(semilla)
    v = rng.normal(size=(n, DIM)).astype(np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def _puntos():
    vecs = _vectores(N)
    marcas = ["NIKE", "Nike", "SAMSUNG", None] * (N // 4)
    return [
        models.PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"prod-{i}")),
            vector=vecs[i].tolist(),
            payload={"product_id": f"P{i:03d}", "brand": marcas[i],
                     "brand_norm": normalize_brand(marcas[i]), "active": True},
        )
        for i in range(N)
    ]


def _ingesta_por_lotes(cli, puntos, batch=16):
    for i in range(0, len(puntos), batch):
        cli.upsert("test", points=puntos[i:i + batch], wait=True)


def test_ingesta_por_lotes_y_recuento(cliente):
    _ingesta_por_lotes(cliente, _puntos())
    assert cliente.count("test", exact=True).count == N


def test_reingesta_idempotente(cliente):
    puntos = _puntos()
    _ingesta_por_lotes(cliente, puntos)
    _ingesta_por_lotes(cliente, puntos)  # repetir no duplica (IDs estables)
    assert cliente.count("test", exact=True).count == N


def test_filtro_de_marca_en_el_motor(cliente):
    _ingesta_por_lotes(cliente, _puntos())
    consulta = _vectores(1, semilla=99)[0]
    flt = models.Filter(must=[models.FieldCondition(
        key="brand_norm", match=models.MatchValue(value="nike"))])
    res = cliente.query_points("test", query=consulta.tolist(), limit=10,
                               query_filter=flt, with_payload=True)
    assert len(res.points) == 10
    # El filtro normalizado une las grafías NIKE y Nike.
    assert all(p.payload["brand_norm"] == "nike" for p in res.points)
    assert {p.payload["brand"] for p in res.points} == {"NIKE", "Nike"}


def test_filtro_sin_coincidencias_devuelve_vacio(cliente):
    _ingesta_por_lotes(cliente, _puntos())
    consulta = _vectores(1, semilla=99)[0]
    flt = models.Filter(must=[models.FieldCondition(
        key="brand_norm", match=models.MatchValue(value="marca-inexistente"))])
    res = cliente.query_points("test", query=consulta.tolist(), limit=10, query_filter=flt)
    assert res.points == []


def test_scores_descendentes_y_contrato_de_respuesta(cliente):
    _ingesta_por_lotes(cliente, _puntos())
    consulta = _vectores(1, semilla=7)[0]
    res = cliente.query_points("test", query=consulta.tolist(), limit=10, with_payload=True)
    scores = [p.score for p in res.points]
    assert scores == sorted(scores, reverse=True)
    assert all("product_id" in p.payload for p in res.points)


def test_mutaciones_upsert_delete_e_idempotencia(cliente):
    puntos = _puntos()
    _ingesta_por_lotes(cliente, puntos)
    objetivo = puntos[0].id
    nuevo_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "prod-nuevo"))
    vec = _vectores(1, semilla=123)[0]

    def aplicar_eventos():
        # UPSERT sobre existente (revisión), UPSERT nuevo (alta), DELETE por ID.
        cliente.upsert("test", points=[models.PointStruct(
            id=objetivo, vector=vec.tolist(),
            payload={"product_id": "P000", "brand": "ACME", "brand_norm": "acme",
                     "active": True, "catalog_version": 2})], wait=True)
        cliente.upsert("test", points=[models.PointStruct(
            id=nuevo_id, vector=vec.tolist(),
            payload={"product_id": "PNEW", "brand": None, "brand_norm": None,
                     "active": True, "catalog_version": 2})], wait=True)
        cliente.delete("test", points_selector=models.PointIdsList(points=[puntos[1].id]), wait=True)

    aplicar_eventos()
    assert cliente.count("test", exact=True).count == N  # +1 alta, -1 borrado
    assert cliente.retrieve("test", ids=[puntos[1].id]) == []
    revisado = cliente.retrieve("test", ids=[objetivo], with_payload=True)[0]
    assert revisado.payload["catalog_version"] == 2

    estado_1 = cliente.retrieve("test", ids=[objetivo, nuevo_id], with_payload=True)
    aplicar_eventos()  # repetir el lote debe ser idempotente
    estado_2 = cliente.retrieve("test", ids=[objetivo, nuevo_id], with_payload=True)
    assert cliente.count("test", exact=True).count == N
    assert [p.payload for p in estado_1] == [p.payload for p in estado_2]
