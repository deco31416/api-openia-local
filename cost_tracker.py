"""
Cost Tracker — Acumula tokens y calcula costo en USD.
Simula lo que pagarías usando la API real de OpenAI.
"""

import time
import json
from pathlib import Path
from typing import Optional


# ═══════════════════════════════════════════════════════════
# Precios oficiales OpenAI por 1M tokens (USD)
# ═══════════════════════════════════════════════════════════

PRICING: dict[str, dict[str, float]] = {
    # o3 5.5
    "o3-5.5-instant":  {"input": 3.00,  "output": 12.00},
    "o3-5.5-thinking": {"input": 10.00, "output": 40.00},
    # GPT family
    "o4-mini":         {"input": 1.10,  "output": 4.40},
    "gpt-4o":          {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":     {"input": 0.15,  "output": 0.60},
    "gpt-4.1":         {"input": 2.00,  "output": 8.00},
}


def get_price(model: str, input_tokens: int, output_tokens: int) -> tuple[float, float, float]:
    """Calcula costo para un modelo dado. Retorna (costo_input, costo_output, costo_total)."""
    pricing = PRICING.get(model, {"input": 2.50, "output": 10.00})
    cost_in = (input_tokens / 1_000_000) * pricing["input"]
    cost_out = (output_tokens / 1_000_000) * pricing["output"]
    return round(cost_in, 6), round(cost_out, 6), round(cost_in + cost_out, 6)


class CostTracker:
    """
    Acumula tokens por modelo y calcula ahorro vs API real.
    Persiste en usage.json para sobrevivir a reinicios.
    """

    def __init__(self, filepath: str = "usage.json"):
        self._path = Path(filepath)
        self._data: dict = self._load()

    def track(self, model: str, prompt_tokens: int, completion_tokens: int):
        """Registra un uso de tokens para un modelo."""
        now = int(time.time())
        entry = self._data.setdefault(model, {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_input_usd": 0.0,
            "cost_output_usd": 0.0,
            "cost_total_usd": 0.0,
            "calls": 0,
            "first_call_at": now,
            "last_call_at": now,
        })
        entry["prompt_tokens"] += prompt_tokens
        entry["completion_tokens"] += completion_tokens
        entry["total_tokens"] += prompt_tokens + completion_tokens
        ci, co, ct = get_price(model, prompt_tokens, completion_tokens)
        entry["cost_input_usd"] = round(entry["cost_input_usd"] + ci, 6)
        entry["cost_output_usd"] = round(entry["cost_output_usd"] + co, 6)
        entry["cost_total_usd"] = round(entry["cost_total_usd"] + ct, 6)
        entry["calls"] += 1
        entry["last_call_at"] = now
        self._flush()

    def summary(self) -> dict:
        """Devuelve resumen de uso por modelo + totales."""
        total_prompt = sum(m["prompt_tokens"] for m in self._data.values())
        total_completion = sum(m["completion_tokens"] for m in self._data.values())
        total_tokens = total_prompt + total_completion
        total_cost = round(sum(m["cost_total_usd"] for m in self._data.values()), 6)
        return {
            "by_model": self._data,
            "totals": {
                "prompt_tokens": total_prompt,
                "completion_tokens": total_completion,
                "total_tokens": total_tokens,
                "cost_total_usd": total_cost,
                "calls": sum(m["calls"] for m in self._data.values()),
            },
        }

    def reset(self):
        """Reinicia todas las métricas."""
        self._data = {}
        self._flush()

    # ── Internals ────────────────────────────────────────

    def _load(self) -> dict:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text("utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _flush(self):
        self._path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), "utf-8")


# ── Singleton ────────────────────────────────────────────

_tracker: Optional[CostTracker] = None


def get_tracker() -> CostTracker:
    global _tracker
    if _tracker is None:
        _tracker = CostTracker()
    return _tracker
