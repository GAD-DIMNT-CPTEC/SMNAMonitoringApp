"""Leitor compatível das tabelas Jo (GSI 3.4) e J (GSI 3.7)."""

import re

import numpy as np
import pandas as pd


_BEGIN_34 = re.compile(r"^Begin Jo table (inner|outer) loop$")
_END_34 = re.compile(r"^End Jo table (inner|outer) loop$")
_BEGIN_37 = re.compile(r"^Begin J table inner/outer loop\s+(\d+)\s+(\d+)$")
# O cabeçalho 3.7 usa "J", mas o terminador ainda diz "Jo".
_END_37 = re.compile(r"^End Jo? table inner/outer loop\s+(\d+)\s+(\d+)$")
_FLOAT = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"
_ROW_34 = re.compile(
    r"^(?P<obstype>.+?\S)\s+(?P<nobs>\d+)\s+"
    rf"(?P<jo>{_FLOAT})\s+(?P<jon>{_FLOAT})$"
)
_ROW_37 = re.compile(rf"^(?P<obstype>.+?\S)\s+(?P<jo>{_FLOAT})$")


def _number(value):
    """Converte a notação Fortran (inclusive D) e preserva sentinelas."""
    return np.nan if value == "-999.999" else float(value.replace("D", "E"))


def _iter_label_v34(table_kind, outer_number, inner_number):
    """Rótulos compatíveis com os usados no dataframe histórico."""
    def ordinal(number):
        suffix = "th" if 10 < number % 100 < 14 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
        return f"{number}{suffix}"

    if table_kind == "outer":
        return "OMF" if outer_number == 1 else f"OMA (AFTER {ordinal(outer_number - 1)} OUTER LOOP)"
    prefix = "OMF" if outer_number == 1 else "OMA"
    return f"{prefix} ({ordinal(inner_number)} INNER LOOP)"


def read_jo_tables(fname):
    """Retorna todas as tabelas Jo/J existentes em *fname*.

    No GSI 3.4, as colunas ``Nobs``, ``Jo`` e ``Jo/n`` são lidas.
    No GSI 3.7, a tabela ``J`` só traz a contribuição ``Jo`` (a coluna
    recebe esse nome para manter o esquema de saída); ``Nobs`` e ``Jo/n``
    ficam como NaN porque não podem ser obtidos desse log.
    """
    rows = []
    layout = None
    table_kind = None
    outer_number = 0
    inner_number = 0
    iter_label = None

    with open(fname, encoding="utf-8", errors="replace") as file:
        for raw_line in file:
            line = raw_line.strip()

            match = _BEGIN_34.match(line)
            if match:
                layout = "3.4"
                table_kind = match.group(1)
                if table_kind == "outer":
                    outer_number += 1
                    inner_number = 0
                else:
                    inner_number += 1
                iter_label = _iter_label_v34(table_kind, outer_number, inner_number)
                continue

            match = _BEGIN_37.match(line)
            if match:
                layout = "3.7"
                inner, outer = map(int, match.groups())
                # No 3.7, a tabela é emitida no início da minimização:
                # inner=0, outer=1 é OMF; outer>1 é a análise do outer anterior.
                suffix = "th" if 10 < (outer - 1) % 100 < 14 else {1: "st", 2: "nd", 3: "rd"}.get((outer - 1) % 10, "th")
                iter_label = "OMF" if outer == 1 else f"OMA (AFTER {outer - 1}{suffix} OUTER LOOP)"
                continue

            if _END_34.match(line) or _END_37.match(line):
                layout = None
                continue
            if layout is None or not line or line.startswith("-"):
                continue

            if layout == "3.4":
                match = _ROW_34.match(line)
                if not match:  # cabeçalhos não correspondem ao padrão de dados
                    continue
                values = match.groupdict()
                rows.append({
                    "Observation Type": values["obstype"],
                    "Nobs": int(values["nobs"]),
                    "Jo": _number(values["jo"]),
                    "Jo/n": _number(values["jon"]),
                    "Iter": iter_label,
                    "GSI format": "3.4",
                })
            else:
                match = _ROW_37.match(line)
                if not match or line.startswith("J term"):
                    continue
                values = match.groupdict()
                obstype = values["obstype"].strip()
                # Normaliza a grafia para que a série histórica seja comparável.
                if obstype == "J Global":
                    obstype = "Jo Global"
                rows.append({
                    "Observation Type": obstype,
                    "Nobs": np.nan,
                    "Jo": _number(values["jo"]),
                    "Jo/n": np.nan,
                    "Iter": iter_label,
                    "GSI format": "3.7",
                })

    return pd.DataFrame(rows, columns=[
        "Observation Type", "Nobs", "Jo", "Jo/n", "Iter", "GSI format"
    ])
