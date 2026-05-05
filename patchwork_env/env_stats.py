"""Compute aggregate statistics across one or more parsed .env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EnvStats:
    total_keys: int = 0
    empty_keys: int = 0
    numeric_keys: int = 0
    boolean_keys: int = 0
    url_keys: int = 0
    long_value_keys: int = 0  # values > 80 chars
    key_lengths: List[int] = field(default_factory=list)
    value_lengths: List[int] = field(default_factory=list)

    def summary(self) -> str:
        avg_key = (
            sum(self.key_lengths) / len(self.key_lengths) if self.key_lengths else 0
        )
        avg_val = (
            sum(self.value_lengths) / len(self.value_lengths)
            if self.value_lengths
            else 0
        )
        return (
            f"total={self.total_keys} empty={self.empty_keys} "
            f"numeric={self.numeric_keys} boolean={self.boolean_keys} "
            f"url={self.url_keys} long={self.long_value_keys} "
            f"avg_key_len={avg_key:.1f} avg_val_len={avg_val:.1f}"
        )


_BOOLEAN_VALUES = {"true", "false", "yes", "no", "1", "0", "on", "off"}


def compute_env_stats(env: Dict[str, str]) -> EnvStats:
    """Return an EnvStats for a single parsed env dict."""
    stats = EnvStats()
    for key, value in env.items():
        stats.total_keys += 1
        stats.key_lengths.append(len(key))
        stats.value_lengths.append(len(value))

        if value == "":
            stats.empty_keys += 1
        elif value.lower() in _BOOLEAN_VALUES:
            stats.boolean_keys += 1
        elif _is_numeric(value):
            stats.numeric_keys += 1

        if value.startswith(("http://", "https://", "ftp://")):
            stats.url_keys += 1

        if len(value) > 80:
            stats.long_value_keys += 1

    return stats


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def merge_stats(stats_list: List[EnvStats]) -> EnvStats:
    """Aggregate multiple EnvStats into one combined report."""
    merged = EnvStats()
    for s in stats_list:
        merged.total_keys += s.total_keys
        merged.empty_keys += s.empty_keys
        merged.numeric_keys += s.numeric_keys
        merged.boolean_keys += s.boolean_keys
        merged.url_keys += s.url_keys
        merged.long_value_keys += s.long_value_keys
        merged.key_lengths.extend(s.key_lengths)
        merged.value_lengths.extend(s.value_lengths)
    return merged
