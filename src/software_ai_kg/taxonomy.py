from __future__ import annotations

from collections import defaultdict, deque


def _build_children(edges: list[dict]) -> dict[str, list[str]]:
    children: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        children[edge["parent"]].append(edge["child"])
    return children


def _has_path(children: dict[str, list[str]], start: str, target: str) -> bool:
    queue = deque([start])
    visited = {start}
    while queue:
        node = queue.popleft()
        if node == target:
            return True
        for child in children.get(node, []):
            if child not in visited:
                visited.add(child)
                queue.append(child)
    return False


def remove_cycle_edges(edges: list[dict]) -> tuple[list[dict], list[dict]]:
    kept: list[dict] = []
    removed: list[dict] = []
    children: dict[str, list[str]] = defaultdict(list)

    for edge in edges:
        parent = edge["parent"]
        child = edge["child"]
        if parent == child or _has_path(children, child, parent):
            removed.append(edge)
            continue
        kept.append(edge)
        children[parent].append(child)
    return kept, removed


def assign_single_parent(
    edges: list[dict],
    preferred_parents: list[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    preferred_parents = preferred_parents or []
    parent_rank = {name: index for index, name in enumerate(preferred_parents)}

    grouped: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        grouped[edge["child"]].append(edge["parent"])

    kept: list[dict] = []
    dropped: list[dict] = []

    for child, parents in grouped.items():
        ranked = sorted(
            parents,
            key=lambda parent: (parent_rank.get(parent, len(parent_rank) + 1), parent),
        )
        chosen = ranked[0]
        kept.append({"parent": chosen, "child": child})
        for parent in ranked[1:]:
            dropped.append({"parent": parent, "child": child})

    kept.sort(key=lambda edge: (edge["parent"], edge["child"]))
    dropped.sort(key=lambda edge: (edge["parent"], edge["child"]))
    return kept, dropped
