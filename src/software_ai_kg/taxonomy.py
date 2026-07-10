from __future__ import annotations

from collections import defaultdict, deque


def _build_children(edges: list[dict]) -> dict[str, list[str]]:
    children: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        children[edge["parent"]].append(edge["child"])
    return children


def _find_path(children: dict[str, list[str]], start: str, target: str) -> list[str] | None:
    """Return one existing path from start to target in the current taxonomy."""
    queue = deque([start])
    visited = {start}
    parent_map = {start: None}
    while queue:
        node = queue.popleft()
        if node == target:
            path = [target]
            while parent_map[path[-1]] is not None:
                path.append(parent_map[path[-1]])
            path.reverse()
            return path
        for child in children.get(node, []):
            if child not in visited:
                visited.add(child)
                parent_map[child] = node
                queue.append(child)
    return None


def _has_path(children: dict[str, list[str]], start: str, target: str) -> bool:
    return _find_path(children, start, target) is not None


def remove_cycle_edges(
    edges: list[dict],
    include_metadata: bool = False,
) -> tuple[list[dict], list[dict]]:
    kept: list[dict] = []
    removed: list[dict] = []
    children: dict[str, list[str]] = defaultdict(list)

    for edge in edges:
        parent = edge["parent"]
        child = edge["child"]
        # The graph is built incrementally. If child can already reach parent,
        # adding parent -> child would create a cycle, so the new edge is pruned.
        cycle_path = [parent] if parent == child else _find_path(children, child, parent)
        if cycle_path is not None:
            if include_metadata:
                removed.append(
                    {
                        "parent": parent,
                        "child": child,
                        "reason": "cycle",
                        "cycle_path": cycle_path + [child] if cycle_path[-1] == parent else cycle_path,
                    }
                )
            else:
                removed.append(edge)
            continue
        kept.append(edge)
        children[parent].append(child)
    return kept, removed


def assign_single_parent(
    edges: list[dict],
    preferred_parents: list[str] | None = None,
    parent_overrides: dict[str, str] | None = None,
    include_metadata: bool = False,
) -> tuple[list[dict], list[dict]]:
    preferred_parents = preferred_parents or []
    parent_overrides = parent_overrides or {}
    parent_rank = {name: index for index, name in enumerate(preferred_parents)}

    grouped: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        grouped[edge["child"]].append(edge["parent"])

    kept: list[dict] = []
    dropped: list[dict] = []

    for child, parents in grouped.items():
        chosen = None
        selection_reason = "preferred_parent_rank"

        # Manual overrides encode the course taxonomy, for example forcing
        # "浏览器" under "客户端软件" instead of keeping multiple Wikidata parents.
        override = parent_overrides.get(child)
        if override in parents:
            chosen = override
            selection_reason = "canonical_override"

        if chosen is None:
            # When no override exists, choose the highest ranked parent so every
            # node has exactly one stable parent in the final tree.
            ranked = sorted(
                parents,
                key=lambda parent: (parent_rank.get(parent, len(parent_rank) + 1), parent),
            )
            chosen = ranked[0]

        if include_metadata:
            kept.append(
                {
                    "parent": chosen,
                    "child": child,
                    "selection_reason": selection_reason,
                    "candidate_parents": sorted(parents),
                }
            )
        else:
            kept.append({"parent": chosen, "child": child})
        for parent in sorted(parents):
            if parent == chosen:
                continue
            if include_metadata:
                dropped.append(
                    {
                        "parent": parent,
                        "child": child,
                        "chosen_parent": chosen,
                        "reason": selection_reason,
                    }
                )
            else:
                dropped.append({"parent": parent, "child": child})

    kept.sort(key=lambda edge: (edge["parent"], edge["child"]))
    dropped.sort(key=lambda edge: (edge["parent"], edge["child"]))
    return kept, dropped


def build_tree_lines(root: str, edges: list[dict]) -> list[str]:
    children = defaultdict(list)
    for edge in edges:
        children[edge["parent"]].append(edge["child"])

    for parent in children:
        children[parent] = sorted(children[parent])

    lines = [root]

    def visit(node: str, prefix: str) -> None:
        """Render a deterministic text tree for reports and manual inspection."""
        node_children = children.get(node, [])
        for index, child in enumerate(node_children):
            is_last = index == len(node_children) - 1
            branch = "└── " if is_last else "├── "
            lines.append(f"{prefix}{branch}{child}")
            next_prefix = prefix + ("    " if is_last else "│   ")
            visit(child, next_prefix)

    visit(root, "")
    return lines
