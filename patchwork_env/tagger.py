"""Tag env keys with arbitrary labels for grouping and filtering."""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class TagResult:
    tagged: Dict[str, List[str]] = field(default_factory=dict)   # key -> [tags]
    untagged: List[str] = field(default_factory=list)

    def has_tags(self) -> bool:
        return bool(self.tagged)

    def summary(self) -> str:
        t = len(self.tagged)
        u = len(self.untagged)
        return f"{t} tagged key(s), {u} untagged key(s)"

    def keys_for_tag(self, tag: str) -> List[str]:
        """Return all keys that carry the given tag."""
        return [k for k, tags in self.tagged.items() if tag in tags]

    def all_tags(self) -> Set[str]:
        """Return the full set of distinct tags in use."""
        out: Set[str] = set()
        for tags in self.tagged.values():
            out.update(tags)
        return out


def tag_env(
    env: Dict[str, str],
    tag_map: Dict[str, List[str]],
) -> TagResult:
    """Apply *tag_map* (key -> list[tag]) to *env*.

    Keys present in env but absent from tag_map land in ``untagged``.
    Keys in tag_map that are not in env are silently ignored.
    """
    result = TagResult()
    for key in env:
        tags = tag_map.get(key)
        if tags:
            result.tagged[key] = list(tags)
        else:
            result.untagged.append(key)
    return result


def tag_by_prefix(
    env: Dict[str, str],
    prefix_tags: Dict[str, str],
) -> TagResult:
    """Auto-tag keys whose names start with a known prefix.

    *prefix_tags* maps prefix -> tag label, e.g. ``{"DB_": "database"}``.
    A key may receive multiple tags if it matches several prefixes.
    """
    tag_map: Dict[str, List[str]] = {}
    for key in env:
        labels = [tag for prefix, tag in prefix_tags.items() if key.startswith(prefix)]
        if labels:
            tag_map[key] = labels
    return tag_env(env, tag_map)
