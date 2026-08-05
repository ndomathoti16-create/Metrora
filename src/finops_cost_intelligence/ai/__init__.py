"""Provider-agnostic, fact-grounded explanation layer."""

from .fact_pack import build_fact_pack
from .summarizer import summarize_fact_pack

__all__ = ["build_fact_pack", "summarize_fact_pack"]
