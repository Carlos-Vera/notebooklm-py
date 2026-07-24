"""Stable request payload builders for the account-level *collection* RPCs.

A collection is a source-``Label`` of type ``3`` with **no notebook parent**, so
these builders reuse the four label RPCs (``I3xc3c`` / ``agX4Bc`` / ``le8sX`` /
``GyzE7e``) with three wire differences vs. :mod:`notebooklm._label.params`
(owner-captured on the live Gemini-Notebook UI, issue #2006):

1. ``notebook_id`` (label slot ``[1]``) is ``None`` — collections are
   account-level, not notebook-scoped.
2. A type discriminator ``3`` rides in the **last** slot of every request.
3. The request-options wrapper (arg ``[0]``) ends in ``[1, 3]`` instead of the
   label wrapper's ``[1]``.

Every builder returns a **fresh** structure per call so callers never alias a
shared mutable wrapper (cf. :func:`notebooklm._label.params._opts`).
"""

from __future__ import annotations

from typing import Any

# Type discriminator that marks a label RPC as operating on collections (type 3
# labels with a null notebook parent). Rides the last slot of every request.
_COLLECTION_TYPE = 3


def _opts() -> list[Any]:
    """Fresh request-options wrapper (arg ``[0]`` of every collection RPC).

    Identical to the label wrapper except the trailing context list is
    ``[1, 3]`` (not ``[1]``) — the collection-scope marker. Returned fresh so
    callers never alias a shared mutable list.
    """
    return [2, None, None, [1, None, None, None, None, None, None, None, None, None, [1, 3]]]


def build_list_collections_params() -> list[Any]:
    """LIST_LABELS (``I3xc3c``) for collections: ``[opts, None, 3]``.

    Response echoes ``[None, [ [name, [[nb_id], ...], collection_id, emoji], ... ]]``.
    """
    return [_opts(), None, _COLLECTION_TYPE]


def build_create_collection_params(name: str) -> list[Any]:
    """CREATE_LABEL (``agX4Bc``) for collections — manual create.

    ``[opts, None, None, None, None, None, None, [[name]], 3]``. Unlike a source
    label, the create wire carries the name at slot ``[7]`` and has **no emoji
    slot** (collections get an emoji via a later update, if at all).
    """
    return [_opts(), None, None, None, None, None, None, [[name]], _COLLECTION_TYPE]


def build_rename_collection_params(
    collection_id: str, name: str, emoji: str | None = None
) -> list[Any]:
    """UPDATE_LABEL (``le8sX``) rename for collections.

    Fieldmask slot ``[3]`` = ``[[[name]]]`` (name-only, matching the captured UI
    rename) or ``[[[name, emoji]]]`` when ``emoji`` is supplied. Whether a
    length-1 ``name_emoji`` PRESERVES an existing emoji or clears it is
    unverified on the wire (same open question as labels), so the API layer
    passes the current emoji explicitly to preserve it.
    """
    name_emoji: list[Any] = [name] if emoji is None else [name, emoji]
    return [_opts(), None, collection_id, [[name_emoji]], _COLLECTION_TYPE]


def build_update_collection_notebooks_params(
    collection_id: str,
    *,
    add_notebook_id: str | None = None,
    remove_notebook_id: str | None = None,
) -> list[Any]:
    """UPDATE_LABEL (``le8sX``) notebook membership for collections.

    Fieldmask slot ``[3]`` is a **two-group** list ``[add_group, remove_group]``
    where each group is ``[None, None, None, [[notebook_id]]]`` (the notebook id
    rides group-slot ``[3]``) or ``[]`` when that operation is unused:

    * **add** (wire-captured): ``[[None, None, None, [[nb_id]]], []]``.
    * **remove** (INFERRED, unverified on the wire): ``[[], [None, None, None,
      [[nb_id]]]]``. The empty second group of the captured *add* payload is
      almost certainly the un-assign list — this mirrors the confirmed label
      ``sources_add`` / ``sources_remove`` two-slot fieldmask (``le8sX``, same
      obfuscated method id), where removing an absent member is a silent no-op.
      Contributor ``tomihe0720`` offered to capture the real un-assign flow;
      until then this shape is a high-confidence symmetric inference, and its
      worst case is a reversible membership no-op (never data loss).

    The wire honours only the FIRST id per group per call, so the builder is
    **singular** — pass at most one ``add_notebook_id`` and one
    ``remove_notebook_id`` (the API layer loops one call per id).
    """
    add_group: list[Any] = (
        [None, None, None, [[add_notebook_id]]] if add_notebook_id is not None else []
    )
    remove_group: list[Any] = (
        [None, None, None, [[remove_notebook_id]]] if remove_notebook_id is not None else []
    )
    return [_opts(), None, collection_id, [add_group, remove_group], _COLLECTION_TYPE]


def build_delete_collections_params(collection_ids: list[str]) -> list[Any]:
    """DELETE_LABEL (``GyzE7e``) for collections — batch, array of ids.

    ``[opts, None, [collection_id, ...], 3]``.
    """
    return [_opts(), None, list(collection_ids), _COLLECTION_TYPE]
