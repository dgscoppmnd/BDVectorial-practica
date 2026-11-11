"""Preparación de texto y normalización de metadatos del catálogo."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import pandas as pd

# Composiciones de texto comparadas en el notebook (sección 6).
COMPOSICIONES = ("c1_titulo", "c2_titulo_atributos", "c3_completo")

# Límite de caracteres de la descripción para controlar la longitud de la
# secuencia (los modelos usados truncan en 256-512 tokens; ver sección 6.1).
MAX_DESC_CHARS = 600


def _clean(value: Any) -> str:
    """Convierte a texto seguro: None/NaN -> cadena vacía, sin espacios extra."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def normalize_brand(value: Any) -> Optional[str]:
    """Marca normalizada para el filtrado en el motor (minúsculas, sin espacios).

    En el catálogo conviven grafías como ``NIKE``/``Nike`` o
    ``SAMSUNG``/``Samsung``; sin normalizar, un filtro de igualdad exacta
    devuelve resultados incompletos o vacíos.
    """
    cleaned = _clean(value)
    return cleaned.lower() if cleaned else None


def build_product_text(
    row: Mapping[str, Any],
    composition: str = "c3_completo",
    max_desc_chars: int = MAX_DESC_CHARS,
) -> str:
    """Construye el texto a vectorizar a partir de una ficha de producto.

    Contrato: nunca incorpora nulos como texto (no aparecen "nan" ni campos
    vacíos), la salida es determinista y la descripción se trunca a
    ``max_desc_chars`` caracteres para controlar la longitud de secuencia.
    """
    if composition not in COMPOSICIONES:
        raise ValueError(f"Composición desconocida: {composition!r}")

    title = _clean(row.get("title"))
    brand = _clean(row.get("brand"))
    color = _clean(row.get("color"))
    desc = _clean(row.get("text"))[:max_desc_chars]

    parts = [title] if title else []
    if composition in ("c2_titulo_atributos", "c3_completo"):
        if brand:
            parts.append(f"Marca: {brand}")
        if color:
            parts.append(f"Color: {color}")
    if composition == "c3_completo" and desc:
        parts.append(desc)
    return " | ".join(parts)
