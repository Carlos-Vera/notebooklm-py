"""Pure-value type for a NotebookLM collection (account-level notebook group).

Re-exported from ``notebooklm.types``. A ``Collection`` groups whole notebooks
(account-level, playlist-style) — the wire tuple ``[name, member_notebook_ids,
collection_id, emoji]`` is structurally identical to a source ``Label``
(``[name, sources, id, emoji]``), so decoding reuses :class:`LabelRow`; only the
second slot's meaning differs (member *notebook* ids, not source ids).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Collection:
    """A NotebookLM collection (a named, emoji-labeled group of notebooks).

    Account-level (unlike a notebook-scoped :class:`~notebooklm.types.Label`):
    it carries no notebook parent. Membership is many-to-many — a notebook may
    belong to multiple collections, and a collection owns a list of notebook IDs
    (the notebook carries no back-reference). Nesting and sharing are not
    supported by the service.
    """

    id: str
    name: str
    emoji: str | None = None
    # Member notebook UUIDs. Empty for a freshly-created (still empty) collection.
    notebook_ids: list[str] = field(default_factory=list)

    @classmethod
    def from_api_response(cls, data: list[Any], *, method_id: str | None = None) -> Collection:
        """Parse one collection 4-tuple ``[name, notebook_ids, collection_id, emoji]``.

        Reuses :class:`LabelRow` — the wire tuple is byte-for-byte the same shape
        as a source label — mapping the (strictly-decoded) member ids into
        :attr:`notebook_ids`.
        """
        from .._row_adapters.labels import LabelRow

        row = LabelRow.from_label_tuple(data, method_id=method_id)
        return cls(
            id=row.id,
            name=row.name,
            emoji=row.emoji or None,
            notebook_ids=list(row.source_ids),
        )
