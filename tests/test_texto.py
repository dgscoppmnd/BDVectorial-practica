"""Tests del contrato de preparación de texto y normalización de marcas."""

import numpy as np
import pytest

from aurum.texto import MAX_DESC_CHARS, build_product_text, normalize_brand


def ficha(**kwargs):
    base = {"title": "Zapatillas Runner", "brand": "NIKE", "color": "Negro",
            "text": "Zapatillas de running ligeras."}
    base.update(kwargs)
    return base


def test_composicion_completa():
    texto = build_product_text(ficha(), "c3_completo")
    assert texto == ("Zapatillas Runner | Marca: NIKE | Color: Negro | "
                     "Zapatillas de running ligeras.")


def test_composicion_solo_titulo():
    assert build_product_text(ficha(), "c1_titulo") == "Zapatillas Runner"


def test_nulos_no_se_incorporan_como_texto():
    texto = build_product_text(ficha(brand=None, color=np.nan, text=float("nan")), "c3_completo")
    assert "nan" not in texto.lower()
    assert "Marca:" not in texto
    assert texto == "Zapatillas Runner"


def test_descripcion_truncada():
    texto = build_product_text(ficha(text="x" * 5000), "c3_completo")
    assert len(texto) < 5000
    assert texto.endswith("x" * 10)
    assert texto.count("x") == MAX_DESC_CHARS


def test_composicion_desconocida_falla():
    with pytest.raises(ValueError):
        build_product_text(ficha(), "c99")


def test_normalize_brand():
    assert normalize_brand("  NIKE ") == "nike"
    assert normalize_brand("Nike") == "nike"
    assert normalize_brand(None) is None
    assert normalize_brand(np.nan) is None
    assert normalize_brand("") is None
