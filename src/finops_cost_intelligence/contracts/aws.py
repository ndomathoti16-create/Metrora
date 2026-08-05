"""Contracts for optional AWS storage and query results."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AthenaQueryResult:
    """Completed Athena query metadata and tabular output."""

    query_execution_id: str
    state: str
    output_location: str
    dataframe: Any

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["dataframe"] = self.dataframe.to_dict(orient="records")
        return result
