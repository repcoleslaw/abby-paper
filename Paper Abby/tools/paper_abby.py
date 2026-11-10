"""Solve Paper Abby levels and draw the half-letter sheets.

A legal line starts on Abby, ends on the flag, and steps only to a
side-by-side dot. It never reuses a dot, enters a tree, crosses a cliff,
or steps into water before the vest or a cave before the lamp. Each new
dot costs one energy. A treat gives three back, after that cost. The flag
may be entered on the last point.

Score is sticks + 3×balls + treats - steps. A stick is one point, a
tennis ball is three, and a treat is one. The vest and the lamp do not
score. The search reports the highest score a legal line can reach.
Several lines may share it.

A PNG in assets/ replaces one drawn mark. The name is the mark:
paw.png, flag.png, vest.png, lamp.png, stick.png, ball.png,
treat.png, tree.png, water.png, cave.png, cliff.png. The sheet
keeps its own copy of the file.
"""

from __future__ import annotations

import base64
import heapq
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "levels"
PRINT = ROOT / "print"
ASSETS = ROOT / "assets"
ANSWER_KEY = ROOT / "Answer Key.md"

COLS = "ABCDEF"
SCORING = frozenset({"stick", "ball", "treat"})
# Points added when the line enters the dot. A stick is one. A ball is three.
POINTS = {"stick": 1, "ball": 3, "treat": 1}
ASSET_KINDS = (
    "paw",
    "flag",
    "vest",
    "lamp",
    "stick",
    "ball",
    "treat",
    "tree",
    "water",
    "cave",
    "cliff",
)
DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))

PAGE_W = 139.7
PAGE_H = 215.9
CELL = 12.0
# PNG slots, in millimeters on the printed sheet. The canvas is scaled
# into the slot, so margin inside the file shrinks the drawing.
MARK_MM = 4.0
TILE_MM = 9.0
CLIFF_W = 2.3
CLIFF_H = CELL - 1.4
GRID_X = 10.0
GRID_Y = 33.0
INK = "#1c1915"
MUTED = "#5e564c"
ANSWER = "#9c2f2f"
PAPER = "#fbf6ee"


class MapError(Exception):
    pass


@dataclass
class Level:
    level: int
    name: str
    blurb: str
    aside: str
    rows: int
    cols: int
    start: tuple[int, int]
    flag: tuple[int, int]
    energy: int
    treat_energy: int
    energy_cap: int
    trees: set[tuple[int, int]]
    water: set[tuple[int, int]]
    caves: set[tuple[int, int]]
    cliffs: set[tuple[tuple[int, int], tuple[int, int]]]
    pickups: dict[tuple[int, int], tuple[int, str]]
    pickup_list: list[tuple[tuple[int, int], str]]
    expect: list[tuple[int, int]]
    checks: dict
    scoring_indexes: list[int] = field(default_factory=list)
    treat_indexes: list[int] = field(default_factory=list)


@dataclass
class Route:
    path: list[tuple[int, int]]
    score: int
    steps: int
    ties: int
    trace: list[tuple[tuple[int, int], int, str | None]]
    sticks: int
    balls: int
    treats: int
    nodes: int


def cell_name(rc: tuple[int, int]) -> str:
    r, c = rc
    return f"{COLS[c]}{r + 1}"


def parse_cell(token, rows: int, cols: int) -> tuple[int, int]:
    if isinstance(token, str):
        text = token.strip().upper()
        if len(text) < 2 or text[0] not in COLS:
            raise MapError(f"bad cell {token!r}")
        col = COLS.index(text[0])
        try:
            row = int(text[1:]) - 1
        except ValueError as exc:
            raise MapError(f"bad cell {token!r}") from exc
    elif isinstance(token, (list, tuple)) and len(token) == 2:
        row, col = int(token[0]), int(token[1])
    else:
        raise MapError(f"bad cell {token!r}")
    if not (0 <= row < rows and 0 <= col < cols):
        raise MapError(f"{token!r} is off the {cols} by {rows} board")
    return row, col


def load_level(path: Path) -> Level:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = int(data.get("rows", 10))
    cols = int(data.get("cols", 6))

    def cells(key):
        return [parse_cell(item, rows, cols) for item in data.get(key, [])]

    start = parse_cell(data["start"], rows, cols)
    flag = parse_cell(data["flag"], rows, cols)
    if "trees" in data:
        if "open" in data:
            raise MapError("use open or trees, not both")
        tree_cells = set(cells("trees"))
        open_cells = {
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if (r, c) not in tree_cells
        }
    else:
        open_cells = set(cells("open"))
    water = set(cells("water"))
    caves = set(cells("caves"))
    expect = [parse_cell(item, rows, cols) for item in data.get("expect") or []]
    pickup_list = []
    for item in data.get("pickups", []):
        pickup_list.append((parse_cell(item["at"], rows, cols), item["kind"]))
    cliff_pairs = []
    for pair in data.get("cliffs", []):
        if len(pair) != 2:
            raise MapError(f"cliff {pair!r} needs two cells")
        cliff_pairs.append(
            (parse_cell(pair[0], rows, cols), parse_cell(pair[1], rows, cols))
        )

    trees = {
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if (r, c) not in open_cells
    }
    cliffs: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for a, b in cliff_pairs:
        cliffs.add((a, b))
        cliffs.add((b, a))

    pickups = {}
    for index, (at, kind) in enumerate(pickup_list):
        if at in pickups:
            raise MapError(f"two items on {cell_name(at)}")
        pickups[at] = (index, kind)

    level = Level(
        level=int(data["level"]),
        name=data["name"],
        blurb=data["blurb"],
        aside=data.get("aside", ""),
        rows=rows,
        cols=cols,
        start=start,
        flag=flag,
        energy=int(data.get("energy", 12)),
        treat_energy=int(data.get("treat_energy", 3)),
        energy_cap=int(data.get("energy_cap", 24)),
        trees=trees,
        water=water,
        caves=caves,
        cliffs=cliffs,
        pickups=pickups,
        pickup_list=pickup_list,
        expect=expect,
        checks=data.get("checks", {}),
    )
    level.scoring_indexes = [
        i for i, (_, kind) in enumerate(pickup_list) if kind in SCORING
    ]
    level.treat_indexes = [
        i for i, (_, kind) in enumerate(pickup_list) if kind == "treat"
    ]
    validate(level)
    return level


def validate(level: Level) -> None:
    if level.start == level.flag:
        raise MapError("Abby is already on the flag")
    if level.start in level.trees or level.flag in level.trees:
        raise MapError("Abby or the flag is on a tree")
    for cell in level.water | level.caves:
        if cell in level.trees:
            raise MapError(f"{cell_name(cell)} is a tree and a gate")
    if level.water & level.caves:
        raise MapError("a tile cannot be water and a cave")
    kinds = {kind for _, kind in level.pickup_list}
    unknown = kinds - {"vest", "lamp", "stick", "ball", "treat"}
    if unknown:
        raise MapError(f"unknown items: {', '.join(sorted(unknown))}")
    for cell, kind in level.pickup_list:
        if cell in level.trees:
            raise MapError(f"{kind} on a tree at {cell_name(cell)}")
        if cell in level.water or cell in level.caves:
            raise MapError(f"{kind} is sitting inside a gate at {cell_name(cell)}")
        if cell in (level.start, level.flag):
            raise MapError(f"{kind} is on Abby or the flag")
    for a, b in level.cliffs:
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            raise MapError(f"cliff {cell_name(a)}-{cell_name(b)} is not a side")
        if a in level.trees or b in level.trees:
            raise MapError(f"cliff {cell_name(a)}-{cell_name(b)} touches a tree")
    if level.expect:
        if level.expect[0] != level.start or level.expect[-1] != level.flag:
            raise MapError("expect must run from Abby to the flag")
        simulate(level, level.expect)


def has_kind(level: Level, mask: int, kind: str) -> bool:
    return any(
        item_kind == kind and mask & (1 << index)
        for index, (_, item_kind) in enumerate(level.pickup_list)
    )


def find_count(level: Level, mask: int) -> int:
    return sum(
        POINTS[level.pickup_list[index][1]]
        for index in level.scoring_indexes
        if mask & (1 << index)
    )


def points_left(level: Level, mask: int) -> int:
    return sum(
        POINTS[level.pickup_list[index][1]]
        for index in level.scoring_indexes
        if not mask & (1 << index)
    )


def bit(level: Level, cell: tuple[int, int]) -> int:
    return 1 << (cell[0] * level.cols + cell[1])


def walkable(level: Level, cell: tuple[int, int]) -> bool:
    r, c = cell
    return (
        0 <= r < level.rows
        and 0 <= c < level.cols
        and cell not in level.trees
    )


def step_blocks(level: Level, src, dst, mask: int, cliffs=None) -> str | None:
    cliffs = level.cliffs if cliffs is None else cliffs
    if not walkable(level, dst):
        return "tree"
    if (src, dst) in cliffs:
        return "cliff"
    if dst in level.water and not has_kind(level, mask, "vest"):
        return "water"
    if dst in level.caves and not has_kind(level, mask, "lamp"):
        return "cave"
    return None


def enter(level: Level, dst, energy: int, mask: int):
    """Pay for dst, then pick up what is there. Energy is the balance before the step."""
    if energy < 1:
        raise MapError("step with no energy")
    energy -= 1
    kind = None
    if dst in level.pickups:
        index, kind = level.pickups[dst]
        if mask & (1 << index) == 0:
            mask |= 1 << index
            if kind == "treat":
                energy = min(level.energy_cap, energy + level.treat_energy)
        else:
            kind = None
    return energy, mask, kind


def simulate(level: Level, path: list[tuple[int, int]], cliffs=None):
    if path[0] != level.start:
        raise MapError("line does not start on Abby")
    seen = {path[0]}
    energy = level.energy
    mask = 0
    trace = [(path[0], energy, None)]
    for src, dst in zip(path, path[1:]):
        if abs(src[0] - dst[0]) + abs(src[1] - dst[1]) != 1:
            raise MapError(f"{cell_name(src)} does not share a side with {cell_name(dst)}")
        if dst in seen:
            raise MapError(f"{cell_name(dst)} is reused")
        reason = step_blocks(level, src, dst, mask, cliffs)
        if reason == "tree":
            raise MapError(f"{cell_name(dst)} is a tree")
        if reason == "cliff":
            raise MapError(f"cliff between {cell_name(src)} and {cell_name(dst)}")
        if reason == "water":
            raise MapError(f"water at {cell_name(dst)} before the vest")
        if reason == "cave":
            raise MapError(f"cave at {cell_name(dst)} before the lamp")
        energy, mask, kind = enter(level, dst, energy, mask)
        seen.add(dst)
        trace.append((dst, energy, kind))
    if path[-1] != level.flag:
        raise MapError("line does not end on the flag")
    steps = len(path) - 1
    finds = find_count(level, mask)
    return {
        "score": finds - steps,
        "steps": steps,
        "trace": trace,
        "mask": mask,
        "finds": finds,
        "energy": energy,
    }


def distances(level: Level, cliffs=None) -> list[list[int]]:
    cliffs = level.cliffs if cliffs is None else cliffs
    dist = [[999] * level.cols for _ in range(level.rows)]
    fr, fc = level.flag
    dist[fr][fc] = 0
    queue = [(fr, fc)]
    head = 0
    while head < len(queue):
        r, c = queue[head]
        head += 1
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if not walkable(level, nxt):
                continue
            if ((r, c), nxt) in cliffs:
                continue
            if dist[nr][nc] <= dist[r][c] + 1:
                continue
            dist[nr][nc] = dist[r][c] + 1
            queue.append(nxt)
    return dist


def solve(level: Level, require_kind: str | None = None, cliffs=None, blocked=None, require_at=None):
    """Best score, then one path. None if no legal finish.

    require_kind keeps only finishes that picked that item up.
    blocked cells are treated as trees for this search.
    """
    cliffs = level.cliffs if cliffs is None else cliffs
    blocked = blocked or set()
    dist = distances(level, cliffs)
    # A blocked flag or a wall of extra trees still uses walkable(), so fold
    # the extra blocks into a tiny wrapper by rejecting them as steps.
    require_index = None
    if require_at is not None:
        if require_at not in level.pickups:
            raise MapError(f"no item at {cell_name(require_at)}")
        require_index = level.pickups[require_at][0]
    elif require_kind:
        matches = [i for i, (_, kind) in enumerate(level.pickup_list) if kind == require_kind]
        if len(matches) != 1:
            raise MapError(f"expected one {require_kind}")
        require_index = matches[0]

    sr, sc = level.start
    start_state = (sr, sc, level.energy, 0)
    best_cost = {start_state: 0}
    parent = {start_state: None}
    heap = [(0, sr, sc, level.energy, 0)]
    goal = None
    goal_cost = None

    while heap:
        cost, r, c, energy, mask = heapq.heappop(heap)
        state = (r, c, energy, mask)
        if cost != best_cost.get(state):
            continue
        steps = cost + find_count(level, mask)
        if (r, c) == level.flag and steps > 0:
            if require_index is None or mask & (1 << require_index):
                if goal_cost is None or cost < goal_cost:
                    goal = state
                    goal_cost = cost
            continue
        if energy < 1:
            continue
        # A ball is worth more than the step that picks it up, so a later
        # step can still lower the cost. Keep the best flag, and skip a
        # state once the points still on the map cannot beat it.
        if goal_cost is not None:
            if cost + dist[r][c] - points_left(level, mask) >= goal_cost:
                continue
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            dst = (nr, nc)
            if dst in blocked or step_blocks(level, (r, c), dst, mask, cliffs):
                continue
            try:
                nenergy, nmask, _kind = enter(level, dst, energy, mask)
            except MapError:
                continue
            nfinds = find_count(level, nmask)
            nsteps = steps + 1
            ncost = nsteps - nfinds
            nstate = (nr, nc, nenergy, nmask)
            if ncost < best_cost.get(nstate, 10**9):
                best_cost[nstate] = ncost
                parent[nstate] = state
                heapq.heappush(heap, (ncost, nr, nc, nenergy, nmask))

    if goal is None:
        return None

    cells = []
    state = goal
    while state is not None:
        cells.append((state[0], state[1]))
        state = parent[state]
    cells.reverse()
    score = -goal_cost
    return cells, score, dist


def count_simple(level: Level, target: int, dist, cliffs=None) -> tuple[int, list, int]:
    cliffs = level.cliffs if cliffs is None else cliffs
    nodes = 0
    examples: list[list[tuple[int, int]]] = []

    def treats_left(mask: int) -> int:
        return sum(1 for index in level.treat_indexes if not mask & (1 << index))

    def dfs(r, c, energy, mask, steps, finds, visited, path) -> int:
        nonlocal nodes
        nodes += 1
        if nodes > 2_000_000:
            raise MapError("the search got too large; the map is too open")
        if steps > 0 and (r, c) == level.flag:
            score = finds - steps
            if score > target:
                raise MapError(f"a line scores {score}, better than the route already found")
            if score == target:
                if len(examples) < 6:
                    examples.append(list(path))
                return 1
            return 0
        away = dist[r][c]
        if finds + points_left(level, mask) - steps - away < target:
            return 0
        if energy + level.treat_energy * treats_left(mask) < away:
            return 0
        total = 0
        if energy < 1:
            return 0
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            dst = (nr, nc)
            if not walkable(level, dst):
                continue
            mark = bit(level, dst)
            if visited & mark:
                continue
            if step_blocks(level, (r, c), dst, mask, cliffs):
                continue
            nenergy, nmask, _kind = enter(level, dst, energy, mask)
            path.append(dst)
            total += dfs(
                nr,
                nc,
                nenergy,
                nmask,
                steps + 1,
                find_count(level, nmask),
                visited | mark,
                path,
            )
            path.pop()
        return total

    start = level.start
    total = dfs(
        start[0],
        start[1],
        level.energy,
        0,
        0,
        0,
        bit(level, start),
        [start],
    )
    return total, examples, nodes


def tally(level: Level, path: list[tuple[int, int]]) -> dict[str, int]:
    counts = {"stick": 0, "ball": 0, "treat": 0, "vest": 0, "lamp": 0}
    seen = set(path)
    for cell, kind in level.pickup_list:
        if cell in seen:
            counts[kind] += 1
    return counts


def route_from(level: Level, path: list[tuple[int, int]], ties: int, nodes: int) -> Route:
    played = simulate(level, path)
    counts = tally(level, path)
    return Route(
        path=path,
        score=played["score"],
        steps=played["steps"],
        ties=ties,
        trace=played["trace"],
        sticks=counts["stick"],
        balls=counts["ball"],
        treats=counts["treat"],
        nodes=nodes,
    )


def best_route(level: Level) -> Route:
    """Highest legal score, and one line that reaches it.

    Several lines may share that score. A stored line is kept when it
    is one of them.
    """
    found = solve(level)
    if found is None:
        raise MapError("no legal line reaches the flag")
    dijkstra_path, score, dist = found
    repeats = len(dijkstra_path) != len(set(dijkstra_path))
    target = score
    while True:
        ties, examples, nodes = count_simple(level, target, dist)
        if ties >= 1:
            break
        # The cost search may revisit a dot. A printed line cannot.
        if not repeats:
            raise MapError("the best score uses a line that reuses a dot")
        target -= 1
        if score - target > 48:
            raise MapError("no simple line reaches the flag")
    path = examples[0]
    if not repeats and path != dijkstra_path and ties == 1 and target == score:
        path = dijkstra_path
    if level.expect and path != level.expect:
        played = simulate(level, level.expect)
        if played["score"] == target:
            path = level.expect
    return route_from(level, path, ties, nodes)


def variant_score(level: Level, name: str):
    if name == "without_cliffs":
        found = solve(level, cliffs=set())
    elif name == "with_ball":
        found = solve(level, require_kind="ball")
    elif name == "avoiding_water":
        found = solve(level, blocked=set(level.water))
    elif name == "avoiding_cave":
        found = solve(level, blocked=set(level.caves))
    else:
        raise MapError(f"unknown check {name}")
    if found is None:
        return None
    _path, score, _dist = found
    return score


def run_checks(level: Level) -> list[str]:
    notes = []
    for name, expected in level.checks.items():
        got = variant_score(level, name)
        if got != expected:
            raise MapError(f"check {name}: got {got}, expected {expected}")
        label = "impossible" if got is None else str(got)
        notes.append(f"{name} {label}")
    return notes


def preview(level: Level, path=None) -> str:
    on_path = set(path or [])
    lines = ["   " + " ".join(COLS[: level.cols])]
    for r in range(level.rows):
        row = []
        for c in range(level.cols):
            cell = (r, c)
            if cell == level.start:
                mark = "A"
            elif cell == level.flag:
                mark = "F"
            elif cell in level.pickups:
                mark = {"vest": "v", "lamp": "L", "stick": "s", "ball": "b", "treat": "t"}[
                    level.pickups[cell][1]
                ]
            elif cell in level.water:
                mark = "~"
            elif cell in level.caves:
                mark = "^"
            elif cell in level.trees:
                mark = "#"
            else:
                mark = "."
            if path and cell in on_path and mark not in "AF":
                mark = mark.upper() if mark.islower() else mark
            row.append(mark)
        lines.append(f"{r + 1:2} " + " ".join(row))
    if level.cliffs:
        edges = []
        seen = set()
        for a, b in level.cliffs:
            key = tuple(sorted((a, b)))
            if key in seen:
                continue
            seen.add(key)
            edges.append(f"{cell_name(a)}-{cell_name(b)}")
        lines.append("cliffs " + ", ".join(edges))
    return "\n".join(lines)


def trace_text(route: Route) -> str:
    parts = []
    for index, (cell, energy, kind) in enumerate(route.trace):
        label = cell_name(cell)
        if kind:
            label += f" {kind}"
        if index == len(route.trace) - 1:
            label += " flag"
        parts.append(f"{label} ({energy})")
    return " → ".join(parts)


def score_term(count: int, word: str, each: int) -> str:
    name = word if count == 1 else word + "s"
    if each == 1:
        return f"{count} {name}"
    return f"{count}×{each} {name}"


def score_text(route: Route) -> str:
    bits = []
    if route.sticks:
        bits.append(score_term(route.sticks, "stick", POINTS["stick"]))
    if route.balls:
        bits.append(score_term(route.balls, "ball", POINTS["ball"]))
    if route.treats:
        bits.append(score_term(route.treats, "treat", POINTS["treat"]))
    if not bits:
        bits.append("no finds")
    total = " + ".join(bits)
    return f"{total} − {route.steps} steps = {route.score}"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def center(level: Level, cell: tuple[int, int]) -> tuple[float, float]:
    r, c = cell
    return GRID_X + (c + 0.5) * CELL, GRID_Y + (r + 0.5) * CELL


_asset_hrefs: dict[str, str] = {}


def asset_href(kind: str) -> str | None:
    cached = _asset_hrefs.get(kind)
    if cached is not None:
        return cached
    path = ASSETS / f"{kind}.png"
    if not path.is_file():
        return None
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    href = f"data:image/png;base64,{payload}"
    _asset_hrefs[kind] = href
    return href


def picture(kind: str, w: float, h: float) -> str | None:
    """The PNG for this mark, fitted to a slot centered on the current origin."""
    href = asset_href(kind)
    if href is None:
        return None
    return (
        f'<image href="{href}" xlink:href="{href}" '
        f'x="{-w / 2:.2f}" y="{-h / 2:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'preserveAspectRatio="xMidYMid meet"/>'
    )


def using_assets() -> bool:
    return any((ASSETS / f"{kind}.png").is_file() for kind in ASSET_KINDS)


def report_pictures() -> None:
    found = [kind for kind in ASSET_KINDS if (ASSETS / f"{kind}.png").is_file()]
    if found:
        print("Pictures: " + ", ".join(f"{kind}.png" for kind in found))


FONT = "Georgia, 'Palatino Linotype', Palatino, 'Times New Roman', serif"


def render(level: Level, route: Route | None) -> str:
    answer = route is not None
    parts: list[str] = []
    add = parts.append
    add('<?xml version="1.0" encoding="UTF-8"?>')
    link = ' xmlns:xlink="http://www.w3.org/1999/xlink"' if using_assets() else ""
    add(
        f'<svg xmlns="http://www.w3.org/2000/svg"{link} width="5.5in" height="8.5in" '
        f'viewBox="0 0 {PAGE_W} {PAGE_H}">'
    )
    add("<!--")
    add("  Paper Abby. Print at actual size, 5.5 by 8.5 inches.")
    add("  Groups: header, grid, terrain, dots, items, journal, legend"
        + (", answer" if answer else "") + ".")
    add("  Recolor the sheet from the style block. Delete one obstacle by its id,")
    add("  for example tree-C4 or cliff-D8-D7. Moving a gate belongs in the level")
    add("  file, then run the tool again so the answer stays true.")
    add("-->")
    add("<style>")
    add(f"  text {{ font-family: {FONT}; }}")
    add(f"  .ink {{ fill: {INK}; }}")
    add(f"  .muted {{ fill: {MUTED}; }}")
    add(f"  .paper {{ fill: {PAPER}; }}")
    add("  .open { fill: #fffdf8; }")
    add("  .tree { fill: #e4f0da; }")
    add("  .canopy { fill: #d5e7c6; stroke: #243024; stroke-width: 0.32; }")
    add("  .trunk { stroke: #243024; stroke-width: 0.4; stroke-linecap: round; }")
    add("  .water { fill: #d5eaf2; }")
    add("  .wave { fill: none; stroke: #1d4c5c; stroke-width: 0.28; stroke-linecap: round; }")
    add("  .cave { fill: #e7e0d6; }")
    add("  .arch { fill: #d4cdc2; stroke: #1c1915; stroke-width: 0.35; }")
    add("  .cliff { stroke: #3a2c1e; stroke-linecap: round; }")
    add(f"  .gridline {{ fill: none; stroke: #cfc6b8; stroke-width: 0.28; }}")
    add(f"  .frame {{ fill: none; stroke: {INK}; stroke-width: 0.45; }}")
    add(f"  .dot {{ fill: #fffdf8; stroke: {INK}; stroke-width: 0.38; }}")
    add(f"  .item {{ fill: none; stroke: {INK}; stroke-width: 0.36; stroke-linecap: round; stroke-linejoin: round; }}")
    add(f"  .item-fill {{ fill: {INK}; stroke: none; }}")
    add(f"  .answer-line {{ fill: none; stroke: {ANSWER}; stroke-width: 1.15; stroke-linecap: round; stroke-linejoin: round; }}")
    add(f"  .answer-ink {{ fill: {ANSWER}; }}")
    add("</style>")
    add(f'<title>Paper Abby {level.level}. {esc(level.name)}</title>')
    add(f'<rect class="paper" x="0" y="0" width="{PAGE_W}" height="{PAGE_H}"/>')
    add(f'<rect class="frame" x="4.2" y="4.2" width="{PAGE_W - 8.4}" height="{PAGE_H - 8.4}"/>')

    add('<g id="header">')
    add(f'<text class="muted" x="8" y="10" font-size="2.3" letter-spacing="0.22">PAPER APP</text>')
    if answer:
        add(f'<text class="answer-ink" x="{PAGE_W - 8}" y="10" font-size="2.6" text-anchor="end" letter-spacing="0.16">ANSWER</text>')
    add(f'<text class="ink" x="8" y="17.2" font-size="7.2">Paper Abby</text>')
    add(
        f'<text class="ink" x="8" y="22.6" font-size="3.3">Level {level.level}'
        f'<tspan class="muted">   {esc(level.name)}</tspan></text>'
    )
    add(f'<text class="muted" x="8" y="27.4" font-size="2.7">{esc(level.blurb)}</text>')
    add("</g>")

    add('<g id="grid">')
    for r in range(level.rows):
        for c in range(level.cols):
            cell = (r, c)
            if cell in level.water:
                klass = "water"
            elif cell in level.caves:
                klass = "cave"
            elif cell in level.trees:
                klass = "tree"
            else:
                klass = "open"
            x = GRID_X + c * CELL
            y = GRID_Y + r * CELL
            add(f'<rect class="{klass}" x="{x:.2f}" y="{y:.2f}" width="{CELL}" height="{CELL}"/>')
    for r in range(level.rows + 1):
        y = GRID_Y + r * CELL
        x2 = GRID_X + level.cols * CELL
        add(f'<line class="gridline" x1="{GRID_X}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}"/>')
    for c in range(level.cols + 1):
        x = GRID_X + c * CELL
        y2 = GRID_Y + level.rows * CELL
        add(f'<line class="gridline" x1="{x:.2f}" y1="{GRID_Y}" x2="{x:.2f}" y2="{y2:.2f}"/>')
    border = (
        f'<rect class="frame" x="{GRID_X}" y="{GRID_Y}" '
        f'width="{level.cols * CELL}" height="{level.rows * CELL}"/>'
    )
    add(border)
    for c in range(level.cols):
        x = GRID_X + (c + 0.5) * CELL
        add(
            f'<text class="muted" x="{x:.2f}" y="{GRID_Y - 1.6}" font-size="2.4" '
            f'text-anchor="middle">{COLS[c]}</text>'
        )
    for r in range(level.rows):
        y = GRID_Y + (r + 0.5) * CELL + 0.8
        add(
            f'<text class="muted" x="{GRID_X - 1.5}" y="{y:.2f}" font-size="2.3" '
            f'text-anchor="end">{r + 1}</text>'
        )
    add("</g>")

    add('<g id="terrain">')
    for r in range(level.rows):
        for c in range(level.cols):
            cell = (r, c)
            cx, cy = center(level, cell)
            if cell in level.trees:
                add(f'<g id="tree-{cell_name(cell)}" transform="translate({cx:.2f},{cy:.2f})">')
                drawn = picture("tree", TILE_MM, TILE_MM)
                if drawn:
                    add(drawn)
                else:
                    flip = 1 if (r + c) % 2 == 0 else -1
                    add(f'<line class="trunk" x1="0" y1="0.9" x2="0" y2="3.5"/>')
                    add(f'<circle class="canopy" cx="{0.35 * flip:.2f}" cy="-0.55" r="2.15"/>')
                    add(f'<circle class="canopy" cx="{-0.95 * flip:.2f}" cy="0.55" r="1.45"/>')
                add("</g>")
            elif cell in level.water:
                add(f'<g id="water-{cell_name(cell)}" transform="translate({cx:.2f},{cy:.2f})">')
                drawn = picture("water", TILE_MM, TILE_MM)
                if drawn:
                    add(drawn)
                else:
                    for wy in (-1.7, 0.0, 1.7):
                        add(
                            f'<path class="wave" d="M-3.6,{wy:.1f} Q-1.8,{wy - 0.75:.2f} 0,{wy:.1f} '
                            f'T3.6,{wy:.1f}"/>'
                        )
                add("</g>")
            elif cell in level.caves:
                add(f'<g id="cave-{cell_name(cell)}" transform="translate({cx:.2f},{cy:.2f})">')
                drawn = picture("cave", TILE_MM, TILE_MM)
                if drawn:
                    add(drawn)
                else:
                    add(
                        '<path class="arch" d="M-2.7,2.5 L-2.7,-0.2 Q-2.7,-2.9 0,-2.9 '
                        'Q2.7,-2.9 2.7,-0.2 L2.7,2.5 Z"/>'
                    )
                add("</g>")
    seen_edges = set()
    for a, b in level.cliffs:
        key = tuple(sorted((a, b)))
        if key in seen_edges:
            continue
        seen_edges.add(key)
        add(cliff_svg(level, key[0], key[1]))
    add("</g>")

    if answer:
        points = " ".join(f"{center(level, cell)[0]:.2f},{center(level, cell)[1]:.2f}" for cell in route.path)
        add('<g id="answer">')
        add(f'<polyline class="answer-line" points="{points}"/>')
        add("</g>")

    add('<g id="dots">')
    for r in range(level.rows):
        for c in range(level.cols):
            cell = (r, c)
            if cell in level.trees:
                continue
            cx, cy = center(level, cell)
            add(f'<circle class="dot" cx="{cx:.2f}" cy="{cy:.2f}" r="0.72"/>')
    add("</g>")

    add('<g id="items">')
    letters = {"vest": "V", "lamp": "L", "stick": "S", "ball": "B", "treat": "T"}
    for cell, (_index, kind) in level.pickups.items():
        cx, cy = center(level, cell)
        add(f'<g id="{kind}-{cell_name(cell)}" transform="translate({cx:.2f},{cy - 3.15:.2f})">')
        add(picture(kind, MARK_MM, MARK_MM) or icon(kind))
        add("</g>")
        add(
            f'<text class="muted" x="{cx + 3.3:.2f}" y="{cy + 4.15:.2f}" font-size="1.7" '
            f'text-anchor="middle">{letters[kind]}</text>'
        )
    sx, sy = center(level, level.start)
    add(f'<g id="abby" transform="translate({sx:.2f},{sy - 3.15:.2f})">')
    add(picture("paw", MARK_MM, MARK_MM) or icon("paw"))
    add("</g>")
    fx, fy = center(level, level.flag)
    add(f'<g id="flag" transform="translate({fx:.2f},{fy - 3.15:.2f})">')
    add(picture("flag", MARK_MM, MARK_MM) or icon("flag"))
    add("</g>")
    add("</g>")

    add('<g id="journal">')
    add(journal_svg(level, route))
    add("</g>")

    add('<g id="legend">')
    add(legend_svg())
    add("</g>")

    add(
        f'<text class="muted" x="{PAGE_W / 2:.2f}" y="210.2" font-size="2.3" '
        f'text-anchor="middle">Erase is free. Higher is better.</text>'
    )
    add("</svg>")
    return "\n".join(parts) + "\n"


def cliff_svg(level: Level, a, b) -> str:
    name = f"cliff-{cell_name(a)}-{cell_name(b)}"
    drawn = picture("cliff", CLIFF_W, CLIFF_H)
    if a[0] == b[0]:
        left = min(a[1], b[1])
        x = GRID_X + (left + 1) * CELL
        y0 = GRID_Y + a[0] * CELL + 0.7
        y1 = y0 + CELL - 1.4
        if drawn:
            mid = (y0 + y1) / 2
            return (
                f'<g id="{name}" transform="translate({x:.2f},{mid:.2f})">'
                f"{drawn}</g>"
            )
        ticks = []
        for i in range(1, 5):
            y = y0 + (y1 - y0) * i / 5
            ticks.append(
                f'<line class="cliff" x1="{x - 1.15:.2f}" y1="{y:.2f}" '
                f'x2="{x + 1.15:.2f}" y2="{y:.2f}" stroke-width="0.32"/>'
            )
        bar = (
            f'<line class="cliff" x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" '
            f'y2="{y1:.2f}" stroke-width="0.95"/>'
        )
    else:
        top = min(a[0], b[0])
        y = GRID_Y + (top + 1) * CELL
        x0 = GRID_X + a[1] * CELL + 0.7
        x1 = x0 + CELL - 1.4
        if drawn:
            mid = (x0 + x1) / 2
            return (
                f'<g id="{name}" transform="translate({mid:.2f},{y:.2f}) rotate(90)">'
                f"{drawn}</g>"
            )
        ticks = []
        for i in range(1, 5):
            x = x0 + (x1 - x0) * i / 5
            ticks.append(
                f'<line class="cliff" x1="{x:.2f}" y1="{y - 1.15:.2f}" '
                f'x2="{x:.2f}" y2="{y + 1.15:.2f}" stroke-width="0.32"/>'
            )
        bar = (
            f'<line class="cliff" x1="{x0:.2f}" y1="{y:.2f}" x2="{x1:.2f}" '
            f'y2="{y:.2f}" stroke-width="0.95"/>'
        )
    return f'<g id="{name}">' + bar + "".join(ticks) + "</g>"


def icon(kind: str) -> str:
    if kind == "paw":
        return (
            '<ellipse class="item-fill" cx="0" cy="0.55" rx="1.22" ry="0.92"/>'
            '<circle class="item-fill" cx="-1.05" cy="-0.82" r="0.4"/>'
            '<circle class="item-fill" cx="-0.36" cy="-1.22" r="0.4"/>'
            '<circle class="item-fill" cx="0.38" cy="-1.22" r="0.4"/>'
            '<circle class="item-fill" cx="1.08" cy="-0.78" r="0.4"/>'
        )
    if kind == "flag":
        return (
            '<line class="item" x1="-0.15" y1="-1.7" x2="-0.15" y2="1.55"/>'
            '<path class="item-fill" d="M-0.15,-1.6 L1.65,-0.8 L-0.15,-0.05 Z"/>'
        )
    if kind == "vest":
        return (
            '<path class="item" d="M-1.25,-1.35 L-1.25,1.25 L1.25,1.25 L1.25,-1.35 '
            'L0.42,-1.35 L0.42,-0.25 L-0.42,-0.25 L-0.42,-1.35 Z"/>'
            '<line class="item" x1="0" y1="-0.25" x2="0" y2="1.25"/>'
        )
    if kind == "lamp":
        return (
            '<path class="item" d="M-1.35,-0.15 Q0,-1.45 1.35,-0.15"/>'
            '<circle class="item" cx="0.15" cy="0.35" r="0.62"/>'
            '<line class="item" x1="0.7" y1="0.05" x2="1.35" y2="-0.35"/>'
            '<line class="item" x1="0.85" y1="0.45" x2="1.55" y2="0.45"/>'
            '<line class="item" x1="0.7" y1="0.85" x2="1.3" y2="1.2"/>'
        )
    if kind == "stick":
        return (
            '<line class="item" x1="-1.45" y1="1.05" x2="1.35" y2="-1.15"/>'
            '<line class="item" x1="0.05" y1="-0.15" x2="1.1" y2="0.5"/>'
        )
    if kind == "ball":
        return (
            '<circle class="item" cx="0" cy="0" r="1.15"/>'
            '<path class="item" d="M-0.75,-0.65 Q0.05,0.15 0.8,-0.6"/>'
            '<path class="item" d="M-0.75,0.65 Q0.05,-0.15 0.8,0.6"/>'
        )
    if kind == "treat":
        return (
            '<rect class="item-fill" x="-1.05" y="-0.36" width="2.1" height="0.72" rx="0.3"/>'
            '<circle class="item-fill" cx="-1.15" cy="-0.42" r="0.4"/>'
            '<circle class="item-fill" cx="-1.15" cy="0.42" r="0.4"/>'
            '<circle class="item-fill" cx="1.15" cy="-0.42" r="0.4"/>'
            '<circle class="item-fill" cx="1.15" cy="0.42" r="0.4"/>'
        )
    raise MapError(kind)


def journal_svg(level: Level, route: Route | None) -> str:
    x = GRID_X + level.cols * CELL + 5
    width = PAGE_W - x - 7
    y = GRID_Y
    lines = [
        f'<text class="ink" x="{x:.2f}" y="{y + 3.2:.2f}" font-size="3.6">Journal</text>'
    ]
    y += 8
    lines.append(
        f'<text class="muted" x="{x:.2f}" y="{y:.2f}" font-size="2.4">Energy {level.energy}. A treat adds {level.treat_energy}.</text>'
    )
    y += 3.2
    used = route.steps if route else 0
    gap = 3.45
    radius = 1.15
    for i in range(level.energy):
        cx = x + radius + (i % 12) * gap
        cy = y + radius
        fill = ' class="item-fill"' if i < used else ' class="item"'
        # item class is stroke-only; hollow circles need a local stroke.
        if i < used:
            lines.append(f'<circle fill="{INK}" cx="{cx:.2f}" cy="{cy:.2f}" r="{radius}"/>')
        else:
            lines.append(
                f'<circle fill="none" stroke="{INK}" stroke-width="0.35" '
                f'cx="{cx:.2f}" cy="{cy:.2f}" r="{radius}"/>'
            )
    extra = level.energy_cap - level.energy
    for i in range(extra):
        cx = x + radius + (i % 12) * gap
        cy = y + radius + 4.0
        if level.energy + i < used:
            lines.append(f'<circle fill="{INK}" cx="{cx:.2f}" cy="{cy:.2f}" r="{radius}"/>')
        else:
            lines.append(
                f'<circle fill="none" stroke="{INK}" stroke-width="0.28" '
                f'stroke-dasharray="0.42 0.38" cx="{cx:.2f}" cy="{cy:.2f}" r="{radius}"/>'
            )
    y += 11.2
    lines.append(f'<text class="muted" x="{x:.2f}" y="{y:.2f}" font-size="2.15">Fill one each new dot.</text>')
    y += 3.3
    lines.append(f'<text class="muted" x="{x:.2f}" y="{y:.2f}" font-size="2.15">Ink three dashed circles per treat.</text>')
    y += 5.2
    names = {"vest": "Vest", "lamp": "Lamp", "stick": "Stick", "ball": "Ball", "treat": "Treat"}
    order = {"vest": 0, "lamp": 1, "stick": 2, "ball": 3, "treat": 4}
    items = sorted(level.pickup_list, key=lambda item: (order[item[1]], cell_name(item[0])))
    taken = set(route.path) if route else set()
    for cell, kind in items:
        mark = cell in taken
        box = checkbox(x, y, mark, answer=route is not None)
        lines.append(box)
        lines.append(
            f'<text class="ink" x="{x + 3.6:.2f}" y="{y + 2.15:.2f}" font-size="2.55">'
            f'{names[kind]}  {cell_name(cell)}</text>'
        )
        y += 4.8
    y += 1.2
    step_label = str(route.steps) if route else ""
    lines.append(checkbox(x, y, bool(route), answer=route is not None))
    flag_name = cell_name(level.flag)
    lines.append(
        f'<text class="ink" x="{x + 3.6:.2f}" y="{y + 2.15:.2f}" font-size="2.55">Flag  {flag_name}</text>'
    )
    y += 6
    lines.append(f'<text class="muted" x="{x:.2f}" y="{y:.2f}" font-size="2.3">Steps</text>')
    lines.append(
        f'<line stroke="{INK}" stroke-width="0.3" x1="{x + 12:.2f}" y1="{y + 0.4:.2f}" '
        f'x2="{x + width - 1:.2f}" y2="{y + 0.4:.2f}"/>'
    )
    if step_label:
        lines.append(
            f'<text class="answer-ink" x="{x + 14:.2f}" y="{y - 0.5:.2f}" font-size="2.8">{step_label}</text>'
        )
    y += 5
    lines.append(
        f'<text class="muted" x="{x:.2f}" y="{y:.2f}" font-size="2.15">sticks + 3×balls + treats − steps</text>'
    )
    y += 4.6
    lines.append(f'<text class="ink" x="{x:.2f}" y="{y:.2f}" font-size="2.7">Score</text>')
    lines.append(
        f'<line stroke="{INK}" stroke-width="0.3" x1="{x + 13:.2f}" y1="{y + 0.5:.2f}" '
        f'x2="{x + width - 1:.2f}" y2="{y + 0.5:.2f}"/>'
    )
    if route:
        lines.append(
            f'<text class="answer-ink" x="{x + 15:.2f}" y="{y - 0.4:.2f}" font-size="3.1">{route.score}</text>'
        )
    return "\n".join(lines)


def checkbox(x, y, marked: bool, answer: bool) -> str:
    stroke = ANSWER if marked and answer else INK
    box = (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="2.4" height="2.4" fill="#fffdf8" '
        f'stroke="{stroke}" stroke-width="0.35"/>'
    )
    if not marked:
        return box
    color = ANSWER if answer else INK
    x1, y1 = x + 0.4, y + 1.2
    x2, y2 = x + 1.0, y + 1.9
    x3, y3 = x + 2.0, y + 0.45
    return box + (
        f'<polyline fill="none" stroke="{color}" stroke-width="0.4" stroke-linecap="round" '
        f'stroke-linejoin="round" points="{x1:.2f},{y1:.2f} {x2:.2f},{y2:.2f} {x3:.2f},{y3:.2f}"/>'
    )


def legend_svg() -> str:
    top = GRID_Y + 10 * CELL + 7
    glyphs = [
        ("tree", "Tree"),
        ("cliff", "Cliff"),
        ("water", "Water"),
        ("cave", "Cave"),
        ("vest", "Vest"),
        ("lamp", "Lamp"),
        ("stick", "Stick"),
        ("ball", "Ball"),
        ("treat", "Treat"),
    ]
    slot = 13.6
    x0 = 9
    lines = []
    for index, (kind, label) in enumerate(glyphs):
        x = x0 + index * slot
        lines.append(f'<g transform="translate({x + 4:.2f},{top + 4:.2f})">{glyph(kind)}</g>')
        lines.append(
            f'<text class="muted" x="{x + 4:.2f}" y="{top + 11.2:.2f}" font-size="2.15" '
            f'text-anchor="middle">{label}</text>'
        )
    rules = [
        "Paw is Abby. Flag is the last dot. Trees have no dot. A heavy edge is a cliff: go around.",
        "Waves need the vest. An arch needs the lamp. Pick it up, then step in.",
        "One circle each new dot. A treat inks three more. None left: erase and redraw.",
        "The flag may take the last circle. Score is sticks + 3×balls + treats − steps. Higher is better.",
    ]
    y = top + 16.5
    for rule in rules:
        lines.append(f'<text class="ink" x="8" y="{y:.2f}" font-size="2.35">{esc(rule)}</text>')
        y += 4.5
    return "\n".join(lines)


def glyph(kind: str) -> str:
    drawn = picture(kind, MARK_MM, MARK_MM)
    if drawn:
        return drawn
    if kind == "tree":
        return (
            '<line class="trunk" x1="0" y1="0.4" x2="0" y2="2.4"/>'
            '<circle class="canopy" cx="0.2" cy="-1.1" r="1.55"/>'
            '<circle class="canopy" cx="-0.7" cy="0.15" r="1.05"/>'
        )
    if kind == "cliff":
        return (
            '<line class="cliff" x1="0" y1="-2.2" x2="0" y2="2.2" stroke-width="0.9"/>'
            '<line class="cliff" x1="-1.2" y1="-1.1" x2="1.2" y2="-1.1" stroke-width="0.32"/>'
            '<line class="cliff" x1="-1.2" y1="0" x2="1.2" y2="0" stroke-width="0.32"/>'
            '<line class="cliff" x1="-1.2" y1="1.1" x2="1.2" y2="1.1" stroke-width="0.32"/>'
        )
    if kind == "water":
        return (
            '<rect class="water" x="-2.4" y="-2.2" width="4.8" height="4.4"/>'
            '<path class="wave" d="M-2,-1.1 Q-1,-1.7 0,-1.1 T2,-1.1"/>'
            '<path class="wave" d="M-2,0.2 Q-1,-0.4 0,0.2 T2,0.2"/>'
            '<path class="wave" d="M-2,1.4 Q-1,0.8 0,1.4 T2,1.4"/>'
        )
    if kind == "cave":
        return '<path class="arch" d="M-2,2 L-2,-0.4 Q-2,-2.2 0,-2.2 Q2,-2.2 2,-0.4 L2,2 Z"/>'
    return icon(kind)


def answer_key(levels: list[tuple[Level, Route]]) -> str:
    chunks = [
        "---",
        "tags: [gift, anniversary, paper-games, path]",
        "created: 2026-11-03",
        "---",
        "",
        "# Answer Key",
        "",
        "Back to [[00 Paper Abby]].",
        "",
        "These lines are for you. Her sheets are the files without \"answer\" in the name.",
        "",
        "Higher is better. A stick is one point, a tennis ball is three, and a treat is one. A step is one point the other way, and the walk is longer than the pocketful, so the number usually sits below zero. The score on a page is the highest a legal line can reach. More than one line may share it.",
        "",
    ]
    for level, route in levels:
        chunks.append(f"## Level {level.level} — {level.name}")
        chunks.append("")
        chunks.append(level.blurb)
        chunks.append("")
        chunks.append(f"**Score.** {score_text(route)}.")
        chunks.append("")
        chunks.append(f"**Line.** {trace_text(route)}.")
        chunks.append("")
        if route.ties == 1:
            chunks.append("No other line reaches this score.")
        else:
            chunks.append(f"{route.ties} lines reach this score.")
        chunks.append("")
        if level.aside:
            chunks.append(level.aside)
            chunks.append("")
    chunks.append("The sheets were drawn by `tools/paper_abby.py`. Run `all` again after a map changes, and replace this note if a score moves.")
    chunks.append("")
    return "\n".join(chunks)


def report(level: Level, route: Route, checks: list[str]) -> str:
    lines = [
        f"Level {level.level} — {level.name}",
        preview(level, route.path),
        score_text(route),
        trace_text(route),
        (
            "1 line reaches this score"
            if route.ties == 1
            else f"{route.ties} lines reach this score"
        )
        + f"   nodes {route.nodes}",
    ]
    if level.expect and level.expect != route.path:
        played = simulate(level, level.expect)
        if played["score"] != route.score:
            lines.append(f"stored line scores {played['score']}")
    if checks:
        lines.append("checks " + ", ".join(checks))
    return "\n".join(lines)


def level_paths() -> list[Path]:
    return sorted(LEVELS.glob("*.json"))


def cmd_all() -> None:
    solved = []
    blocks = []
    for path in level_paths():
        level = load_level(path)
        route = best_route(level)
        checks = run_checks(level)
        blocks.append(report(level, route, checks))
        solved.append((level, route))
    PRINT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    for level, route in solved:
        stem = f"{level.level:02d}"
        player = render(level, None)
        answer = render(level, route)
        (PRINT / f"{stem}-paper-abby.svg").write_text(player, encoding="utf-8")
        (PRINT / f"{stem}-answer.svg").write_text(answer, encoding="utf-8")
    ANSWER_KEY.write_text(answer_key(solved), encoding="utf-8")
    import abby_layout
    abby_layout.write_sheets(solved)
    print("\n\n".join(blocks))
    report_pictures()
    print(f"\nWrote {len(solved)} sheets, the layout copies, and the answer key.")


def cmd_one(command: str, file_arg: str) -> None:
    level = load_level(Path(file_arg))
    if command == "preview":
        print(preview(level, level.expect))
        return
    route = best_route(level)
    checks = run_checks(level)
    print(report(level, route, checks))
    if command == "render":
        PRINT.mkdir(parents=True, exist_ok=True)
        ASSETS.mkdir(parents=True, exist_ok=True)
        stem = f"{level.level:02d}"
        (PRINT / f"{stem}-paper-abby.svg").write_text(render(level, None), encoding="utf-8")
        (PRINT / f"{stem}-answer.svg").write_text(render(level, route), encoding="utf-8")
        import abby_layout
        abby_layout.write_sheets([(level, route)])
        report_pictures()


def main(argv: list[str]) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) < 2 or argv[1] not in {"all", "solve", "render", "preview"}:
        raise SystemExit(
            "usage: paper_abby.py all | solve FILE | render FILE | preview FILE"
        )
    if argv[1] == "all":
        cmd_all()
        return
    if len(argv) < 3:
        raise SystemExit("which level file?")
    cmd_one(argv[1], argv[2])


if __name__ == "__main__":
    main(sys.argv)
