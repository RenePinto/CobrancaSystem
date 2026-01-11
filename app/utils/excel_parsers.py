from decimal import Decimal
from typing import Any

import pandas as pd
from io import BytesIO


class ExcelParseError(Exception):
    pass


ITAU_COLUMNS = {
    "cliente": ["cliente", "sacado", "nome do cliente"],
    "data_vencimento": ["vencimento", "data vencimento", "data_vencimento"],
    "descricao": ["descricao", "descrição", "historico"],
    "valor_original": ["valor", "valor original", "valor_original"],
    "vendedor": ["vendedor", "carteira", "responsavel"],
}

CONTA_AZUL_COLUMNS = {
    "cliente": ["cliente", "razao social", "nome"],
    "data_vencimento": ["vencimento", "data de vencimento", "data_vencimento"],
    "descricao": ["descricao", "descrição", "observacao"],
    "valor_original": ["valor original", "valor", "valor_original"],
    "vendedor": ["vendedor", "responsavel", "conta"],
}


def _normalize_columns(df: pd.DataFrame) -> dict[str, str]:
    normalized = {col.lower().strip(): col for col in df.columns}
    return normalized


def _pick_column(columns: dict[str, str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        key = candidate.lower().strip()
        if key in columns:
            return columns[key]
    return None


def _build_rows(df: pd.DataFrame, mapping: dict[str, list[str]]) -> list[dict[str, Any]]:
    columns = _normalize_columns(df)
    resolved = {}
    for target, candidates in mapping.items():
        source = _pick_column(columns, candidates)
        if not source:
            raise ExcelParseError(f"Coluna obrigatória ausente: {target}")
        resolved[target] = source

    rows = []
    for _, record in df.iterrows():
        rows.append(
            {
                "cliente": record[resolved["cliente"]],
                "data_vencimento": record[resolved["data_vencimento"]],
                "descricao": record[resolved["descricao"]],
                "valor_original": record[resolved["valor_original"]],
                "vendedor": record[resolved["vendedor"]],
            }
        )
    return rows


def _normalize_row(row: dict[str, Any], origem: str) -> dict[str, Any]:
    return {
        "cliente": str(row["cliente"]).strip() if row["cliente"] is not None else "",
        "data_vencimento": pd.to_datetime(row["data_vencimento"], errors="coerce").date()
        if row["data_vencimento"] is not None
        else None,
        "descricao": str(row["descricao"]).strip() if row["descricao"] is not None else "",
        "valor_original": Decimal(str(row["valor_original"]))
        if row["valor_original"] is not None
        else Decimal("0"),
        "vendedor": str(row["vendedor"]).strip() if row["vendedor"] is not None else "",
        "origem": origem,
    }


def parse_itau(content: bytes) -> list[dict[str, Any]]:
    df = pd.read_excel(BytesIO(content))
    rows = _build_rows(df, ITAU_COLUMNS)
    return [_normalize_row(row, "ITAU") for row in rows]


def parse_conta_azul(content: bytes) -> list[dict[str, Any]]:
    df = pd.read_excel(BytesIO(content))
    rows = _build_rows(df, CONTA_AZUL_COLUMNS)
    return [_normalize_row(row, "CONTA_AZUL") for row in rows]
