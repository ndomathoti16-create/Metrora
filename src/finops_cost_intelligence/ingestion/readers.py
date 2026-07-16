"""Safe readers for CSV, Excel, and Parquet sources."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, TextIO

import pandas as pd

SUPPORTED_EXTENSIONS = frozenset({".csv", ".xlsx", ".xls", ".parquet"})
Source = str | Path | bytes | BinaryIO | TextIO | Any


class IngestionError(RuntimeError):
    """Base class for expected upload and parsing failures."""


class SourceNotFoundError(IngestionError):
    """Raised when a path source does not exist or is not a regular file."""


class UnsupportedFileTypeError(IngestionError):
    """Raised when the source extension is not supported."""


class FileTooLargeError(IngestionError):
    """Raised before parsing when the source exceeds the configured limit."""


class EmptyTableError(IngestionError):
    """Raised when a source has no usable tabular rows and columns."""


class UnreadableFileError(IngestionError):
    """Raised when a supported file cannot be parsed as a table."""


class MissingDependencyError(IngestionError):
    """Raised when a format-specific optional parser is unavailable."""


@dataclass(frozen=True)
class LoadedTable:
    """Loaded source data plus metadata needed for profiling and lineage."""

    dataframe: pd.DataFrame
    source_name: str
    file_format: str
    source_size_bytes: int | None
    sheet_name: str | None = None


def _source_name(source: Source, explicit_name: str | None) -> str:
    if explicit_name and explicit_name.strip():
        return Path(explicit_name).name

    if isinstance(source, (str, Path)):
        return Path(source).name

    candidate = getattr(source, "name", None)
    if isinstance(candidate, str) and candidate.strip():
        return Path(candidate).name

    return "uploaded_file"


def _source_payload(source: Source, source_name: str) -> tuple[Any, str, int | None]:
    if isinstance(source, (str, Path)):
        path = Path(source).expanduser()
        if not path.exists():
            raise SourceNotFoundError(f"Source file does not exist: {path}")
        if not path.is_file():
            raise SourceNotFoundError(f"Source path is not a regular file: {path}")
        return path, path.name, path.stat().st_size

    if isinstance(source, bytes):
        return io.BytesIO(source), source_name, len(source)

    size = _file_like_size(source)
    return source, source_name, size


def _file_like_size(source: Any) -> int | None:
    """Get a file-like size without changing its current read position."""
    declared_size = getattr(source, "size", None)
    if isinstance(declared_size, int) and declared_size >= 0:
        return declared_size

    getbuffer = getattr(source, "getbuffer", None)
    if callable(getbuffer):
        try:
            return len(getbuffer())
        except (TypeError, ValueError):
            pass

    getvalue = getattr(source, "getvalue", None)
    if callable(getvalue):
        try:
            value = getvalue()
            return len(value.encode()) if isinstance(value, str) else len(value)
        except (TypeError, ValueError):
            pass

    tell = getattr(source, "tell", None)
    seek = getattr(source, "seek", None)
    if callable(tell) and callable(seek):
        try:
            current_position = tell()
            seek(0, 2)
            size = tell()
            seek(current_position)
            return int(size)
        except (OSError, ValueError, TypeError):
            return None

    return None


def _rewind(source: Any) -> None:
    seek = getattr(source, "seek", None)
    if callable(seek):
        try:
            seek(0)
        except (OSError, ValueError):
            return


def _read_excel(source: Any, suffix: str) -> tuple[pd.DataFrame, str]:
    engine = "xlrd" if suffix == ".xls" else "openpyxl"
    try:
        workbook = pd.ExcelFile(source, engine=engine)
    except ImportError as exc:
        dependency = "xlrd" if suffix == ".xls" else "openpyxl"
        raise MissingDependencyError(
            f"Reading {suffix} files requires the {dependency} package."
        ) from exc
    except (OSError, ValueError, TypeError) as exc:
        raise UnreadableFileError(f"Could not open Excel workbook: {exc}") from exc

    first_header_only_sheet: tuple[pd.DataFrame, str] | None = None
    try:
        for sheet_name in workbook.sheet_names:
            try:
                candidate = pd.read_excel(workbook, sheet_name=sheet_name)
            except (OSError, ValueError, TypeError) as exc:
                raise UnreadableFileError(
                    f"Could not read worksheet {sheet_name!r}: {exc}"
                ) from exc

            if len(candidate.columns) > 0 and candidate.empty:
                first_header_only_sheet = (candidate, sheet_name)
                continue
            if len(candidate.columns) > 0:
                return candidate, sheet_name
    finally:
        workbook.close()

    if first_header_only_sheet is not None:
        return first_header_only_sheet
    raise EmptyTableError("Excel workbook contains no worksheet with tabular data.")


def _read_by_format(source: Any, suffix: str) -> tuple[pd.DataFrame, str | None]:
    if suffix == ".csv":
        return (
            pd.read_csv(source, low_memory=False, on_bad_lines="error"),
            None,
        )
    if suffix in {".xlsx", ".xls"}:
        return _read_excel(source, suffix)
    if suffix == ".parquet":
        return pd.read_parquet(source), None
    raise UnsupportedFileTypeError(
        f"Unsupported file type {suffix or '<none>'}. "
        f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
    )


def load_table(
    source: Source,
    *,
    source_name: str | None = None,
    max_bytes: int | None = None,
) -> LoadedTable:
    """Load one supported tabular source without silently changing its columns.

    Args:
        source: A filesystem path, bytes, or a readable file-like object. Streamlit's
            UploadedFile is supported through its ``name``, ``size``, and read methods.
        source_name: Optional name used for in-memory uploads that have no ``name``.
        max_bytes: Optional hard byte limit checked before parsing.
    """
    if max_bytes is not None and max_bytes <= 0:
        raise ValueError("max_bytes must be greater than zero when provided.")

    name = _source_name(source, source_name)
    payload, name, source_size_bytes = _source_payload(source, name)
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type for {name!r}. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
        )
    if max_bytes is not None and source_size_bytes is not None and source_size_bytes > max_bytes:
        limit_mb = max_bytes / (1024 * 1024)
        actual_mb = source_size_bytes / (1024 * 1024)
        raise FileTooLargeError(
            f"{name!r} is {actual_mb:.2f} MB, above the configured {limit_mb:.2f} MB limit."
        )

    _rewind(payload)
    try:
        dataframe, sheet_name = _read_by_format(payload, suffix)
    except IngestionError:
        raise
    except UnicodeDecodeError as exc:
        raise UnreadableFileError(
            f"Could not decode {name!r} as text. Check the file encoding."
        ) from exc
    except pd.errors.EmptyDataError as exc:
        raise EmptyTableError(f"{name!r} contains no tabular data.") from exc
    except pd.errors.ParserError as exc:
        raise UnreadableFileError(
            f"Could not parse {name!r}. Check for malformed rows or delimiters."
        ) from exc
    except ImportError as exc:
        dependency = "pyarrow" if suffix == ".parquet" else "the format parser"
        raise MissingDependencyError(
            f"Reading {suffix} files requires {dependency}. Install project dependencies first."
        ) from exc
    except (OSError, ValueError, TypeError) as exc:
        raise UnreadableFileError(f"Could not read {name!r}: {exc}") from exc

    if dataframe.shape[1] == 0:
        raise EmptyTableError(f"{name!r} contains no columns.")
    if dataframe.shape[0] == 0:
        raise EmptyTableError(f"{name!r} contains column headers but no data rows.")

    return LoadedTable(
        dataframe=dataframe,
        source_name=name,
        file_format=suffix.removeprefix("."),
        source_size_bytes=source_size_bytes,
        sheet_name=sheet_name,
    )
