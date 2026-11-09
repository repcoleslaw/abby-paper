"""Draw the existing levels into the Abby layout frame.

The frame is the yellow header, the puzzle area, the vertical step
circles, and the vest and lamp rows. Sheets land in "Abby Layout
Update". The pages in print/ stay as they are.

Coordinates below are pixels of that frame, 297 by 420, mapped onto
a 5.5 inch width so the circles stay round.
"""

from __future__ import annotations

import sys
from pathlib import Path

import paper_abby as pa

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Abby Layout Update"

FRAME_W = 297.0
FRAME_H = 420.0
PAGE_W = 139.7
PAGE_H = FRAME_H * PAGE_W / FRAME_W
SCALE = PAGE_W / FRAME_W

YELLOW = "#f4dd9d"
TITLE = "#50260c"
LABEL = "#a28255"
BOX = "#c4c4c4"
INK = pa.INK
FONT = '"Segoe UI", "Helvetica Neue", Arial, sans-serif'

# Measured edges of the frame, in its own pixels.
HEADER_H = 57
WELL_X, WELL_Y, WELL_X2, WELL_Y2 = 16, 73, 230, 330
SOLID_X, DASH_X = 248, 271
CIRCLE_Y0, CIRCLE_PITCH, CIRCLE_R = 78, 17, 5.4
STEPS_BOX = (237, 290, 284, 330)
SCORE_BOX = (237, 346, 284, 403)
ROW_Y = (346, 378)
ROW_H = 25
ICON_X, CHECK_X, PAIR_X2 = 16, 42, 67
BAR_X, BAR_X2 = 76, 229


def mm(px: float) -> float:
    return px * SCALE


def esc(text: str) -> str:
    return pa.esc(text)


def wrap(text: str, limit: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = word if not current else f"{current} {word}"
        if len(trial) <= limit:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def cells_of(level: pa.Level, kind: str) -> list[tuple[int, int]]:
    found = [cell for cell, item_kind in level.pickup_list if item_kind == kind]
    return sorted(found, key=pa.cell_name)


def fit_grid(level: pa.Level) -> None:
    """Square cells, centered in the puzzle area. Letters sit in the margin."""
    well_w = mm(WELL_X2 - WELL_X)
    well_h = mm(WELL_Y2 - WELL_Y)
    cell = min(well_w / level.cols, well_h / level.rows)
    grid_w = cell * level.cols
    grid_h = cell * level.rows
    pa.CELL = cell
    pa.GRID_X = mm(WELL_X) + (well_w - grid_w) / 2
    pa.GRID_Y = mm(WELL_Y) + (well_h - grid_h) / 2
    pa.CLIFF_H = cell - 1.4 * cell / 12.0
    pa.CLIFF_W = 2.3 * cell / 12.0
    pa.MARK_MM = 4.0 * cell / 12.0
    pa.TILE_MM = 9.0 * cell / 12.0


def save_geometry() -> dict:
    names = ("GRID_X", "GRID_Y", "CELL", "MARK_MM", "TILE_MM", "CLIFF_W", "CLIFF_H")
    return {name: getattr(pa, name) for name in names}


def restore_geometry(saved: dict) -> None:
    for name, value in saved.items():
        setattr(pa, name, value)


def render(level: pa.Level, route: pa.Route | None) -> str:
    answer = route is not None
    fit_grid(level)
    parts: list[str] = []
    add = parts.append
    link = ' xmlns:xlink="http://www.w3.org/1999/xlink"' if pa.using_assets() else ""
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add(
        f'<svg xmlns="http://www.w3.org/2000/svg"{link} '
        f'width="5.5in" height="{PAGE_H / 25.4:.4f}in" '
        f'viewBox="0 0 {PAGE_W:.3f} {PAGE_H:.3f}">'
    )
    add("<!--")
    add("  Paper Abby, layout update. Print at actual size.")
    add("  The sheet is 5.5 inches wide and keeps the frame's proportion.")
    add("  Groups: header, grid, terrain, dots, items, steps, tally"
        + (", answer" if answer else "") + ".")
    add("-->")
    add("<style>")
    add(f"  text {{ font-family: {FONT}; }}")
    add(f"  .ink {{ fill: {INK}; }}")
    add(f"  .title {{ fill: {TITLE}; }}")
    add(f"  .label {{ fill: {LABEL}; }}")
    add(f"  .paper {{ fill: #ffffff; }}")
    add(f"  .header {{ fill: {YELLOW}; }}")
    add("  .open { fill: #fffdf8; }")
    add("  .tree { fill: #e4f0da; }")
    add("  .canopy { fill: #d5e7c6; stroke: #243024; stroke-width: 0.32; }")
    add("  .trunk { stroke: #243024; stroke-width: 0.4; stroke-linecap: round; }")
    add("  .water { fill: #d5eaf2; }")
    add("  .wave { fill: none; stroke: #1d4c5c; stroke-width: 0.28; stroke-linecap: round; }")
    add("  .cave { fill: #e7e0d6; }")
    add("  .arch { fill: #d4cdc2; stroke: #1c1915; stroke-width: 0.35; }")
    add("  .cliff { stroke: #3a2c1e; stroke-linecap: round; }")
    add("  .gridline { fill: none; stroke: #cfc6b8; stroke-width: 0.28; }")
    add(f"  .frame {{ fill: none; stroke: {INK}; stroke-width: 0.45; }}")
    add(f"  .dot {{ fill: #fffdf8; stroke: {INK}; stroke-width: 0.38; }}")
    add(f"  .item {{ fill: none; stroke: {INK}; stroke-width: 0.36; stroke-linecap: round; stroke-linejoin: round; }}")
    add(f"  .item-fill {{ fill: {INK}; stroke: none; }}")
    add(f"  .answer-line {{ fill: none; stroke: {pa.ANSWER}; stroke-width: 1.15; stroke-linecap: round; stroke-linejoin: round; }}")
    add(f"  .answer-ink {{ fill: {pa.ANSWER}; }}")
    add(f"  .box {{ fill: #ffffff; stroke: {BOX}; stroke-width: 0.45; }}")
    add("  .tally-tool .item { stroke: #8d8478; stroke-width: 0.48; vector-effect: non-scaling-stroke; }")
    add(f"  .circle {{ fill: #ffffff; stroke: {INK}; stroke-width: 0.42; }}")
    add(f"  .circle-dash {{ fill: #ffffff; stroke: {INK}; stroke-width: 0.38; stroke-dasharray: 0.28 0.62; stroke-linecap: round; }}")
    add("</style>")
    suffix = " answer" if answer else ""
    add(f"<title>Paper Abby {level.level}. {esc(level.name)}{suffix}</title>")
    add(f'<rect class="paper" x="0" y="0" width="{PAGE_W:.3f}" height="{PAGE_H:.3f}"/>')

    add('<g id="header">')
    add(f'<rect class="header" x="0" y="0" width="{PAGE_W:.3f}" height="{mm(HEADER_H):.3f}"/>')
    add(
        f'<text class="label" x="{mm(18):.2f}" y="{mm(22):.2f}" font-size="3.5" '
        f'letter-spacing="0.08">Level {level.level}</text>'
    )
    add(description_svg(level.blurb, answer))
    add(
        f'<text class="title" x="{mm(18):.2f}" y="{mm(46):.2f}" font-size="8.2" '
        f'font-weight="700">{esc(level.name)}</text>'
    )
    if answer:
        add(
            f'<text class="answer-ink" x="{mm(284):.2f}" y="{mm(46):.2f}" font-size="3.2" '
            f'text-anchor="end" letter-spacing="0.14" font-weight="700">ANSWER</text>'
        )
    add("</g>")

    add('<g id="grid">')
    add(grid_svg(level))
    add("</g>")

    add('<g id="terrain">')
    add(terrain_svg(level))
    add("</g>")

    if answer:
        points = " ".join(
            f"{pa.center(level, cell)[0]:.2f},{pa.center(level, cell)[1]:.2f}"
            for cell in route.path
        )
        add('<g id="answer">')
        add(f'<polyline class="answer-line" points="{points}"/>')
        add("</g>")

    add('<g id="dots">')
    for r in range(level.rows):
        for c in range(level.cols):
            cell = (r, c)
            if cell in level.trees:
                continue
            cx, cy = pa.center(level, cell)
            add(f'<circle class="dot" cx="{cx:.2f}" cy="{cy:.2f}" r="0.72"/>')
    add("</g>")

    add('<g id="items">')
    add(items_svg(level))
    add("</g>")

    add('<g id="steps">')
    add(steps_svg(level, route))
    add("</g>")

    add('<g id="tally">')
    add(tally_svg(level, route))
    add("</g>")

    add("</svg>")
    return "\n".join(parts) + "\n"


def description_svg(blurb: str, answer: bool) -> str:
    # The right side of the top band. Answer sheets keep the corner clear.
    limit = 32 if answer else 36
    lines = wrap(blurb, limit)
    x = mm(168)
    y = mm(16)
    lead = 3.5
    chunks = []
    for index, line in enumerate(lines[:3]):
        chunks.append(
            f'<text class="label" x="{x:.2f}" y="{y + index * lead:.2f}" font-size="2.7">'
            f"{esc(line)}</text>"
        )
    return "\n".join(chunks)


def grid_svg(level: pa.Level) -> str:
    lines = []
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
            x = pa.GRID_X + c * pa.CELL
            y = pa.GRID_Y + r * pa.CELL
            lines.append(
                f'<rect class="{klass}" x="{x:.2f}" y="{y:.2f}" '
                f'width="{pa.CELL:.2f}" height="{pa.CELL:.2f}"/>'
            )
    width = level.cols * pa.CELL
    height = level.rows * pa.CELL
    for r in range(level.rows + 1):
        y = pa.GRID_Y + r * pa.CELL
        lines.append(
            f'<line class="gridline" x1="{pa.GRID_X:.2f}" y1="{y:.2f}" '
            f'x2="{pa.GRID_X + width:.2f}" y2="{y:.2f}"/>'
        )
    for c in range(level.cols + 1):
        x = pa.GRID_X + c * pa.CELL
        lines.append(
            f'<line class="gridline" x1="{x:.2f}" y1="{pa.GRID_Y:.2f}" '
            f'x2="{x:.2f}" y2="{pa.GRID_Y + height:.2f}"/>'
        )
    lines.append(
        f'<rect class="frame" x="{pa.GRID_X:.2f}" y="{pa.GRID_Y:.2f}" '
        f'width="{width:.2f}" height="{height:.2f}"/>'
    )
    for c in range(level.cols):
        x = pa.GRID_X + (c + 0.5) * pa.CELL
        lines.append(
            f'<text class="label" x="{x:.2f}" y="{pa.GRID_Y - 2.3:.2f}" font-size="2.8" '
            f'text-anchor="middle">{pa.COLS[c]}</text>'
        )
    for r in range(level.rows):
        y = pa.GRID_Y + (r + 0.5) * pa.CELL + 0.9
        lines.append(
            f'<text class="label" x="{pa.GRID_X - 1.8:.2f}" y="{y:.2f}" font-size="2.6" '
            f'text-anchor="end">{r + 1}</text>'
        )
    return "\n".join(lines)


def terrain_svg(level: pa.Level) -> str:
    lines = []
    scale = pa.CELL / 12.0
    for r in range(level.rows):
        for c in range(level.cols):
            cell = (r, c)
            cx, cy = pa.center(level, cell)
            if cell in level.trees:
                lines.append(f'<g id="tree-{pa.cell_name(cell)}" transform="translate({cx:.2f},{cy:.2f})">')
                drawn = pa.picture("tree", pa.TILE_MM, pa.TILE_MM)
                if drawn:
                    lines.append(drawn)
                else:
                    lines.append(f'<g transform="scale({scale:.4f})">')
                    flip = 1 if (r + c) % 2 == 0 else -1
                    lines.append('<line class="trunk" x1="0" y1="0.9" x2="0" y2="3.5"/>')
                    lines.append(f'<circle class="canopy" cx="{0.35 * flip:.2f}" cy="-0.55" r="2.15"/>')
                    lines.append(f'<circle class="canopy" cx="{-0.95 * flip:.2f}" cy="0.55" r="1.45"/>')
                    lines.append("</g>")
                lines.append("</g>")
            elif cell in level.water:
                lines.append(f'<g id="water-{pa.cell_name(cell)}" transform="translate({cx:.2f},{cy:.2f})">')
                drawn = pa.picture("water", pa.TILE_MM, pa.TILE_MM)
                if drawn:
                    lines.append(drawn)
                else:
                    lines.append(f'<g transform="scale({scale:.4f})">')
                    for wy in (-1.7, 0.0, 1.7):
                        lines.append(
                            f'<path class="wave" d="M-3.6,{wy:.1f} Q-1.8,{wy - 0.75:.2f} 0,{wy:.1f} '
                            f'T3.6,{wy:.1f}"/>'
                        )
                    lines.append("</g>")
                lines.append("</g>")
            elif cell in level.caves:
                lines.append(f'<g id="cave-{pa.cell_name(cell)}" transform="translate({cx:.2f},{cy:.2f})">')
                drawn = pa.picture("cave", pa.TILE_MM, pa.TILE_MM)
                if drawn:
                    lines.append(drawn)
                else:
                    lines.append(f'<g transform="scale({scale:.4f})">')
                    lines.append(
                        '<path class="arch" d="M-2.7,2.5 L-2.7,-0.2 Q-2.7,-2.9 0,-2.9 '
                        'Q2.7,-2.9 2.7,-0.2 L2.7,2.5 Z"/>'
                    )
                    lines.append("</g>")
                lines.append("</g>")
    seen = set()
    for a, b in level.cliffs:
        key = tuple(sorted((a, b)))
        if key in seen:
            continue
        seen.add(key)
        lines.append(pa.cliff_svg(level, key[0], key[1]))
    return "\n".join(lines)


def items_svg(level: pa.Level) -> str:
    lines = []
    letters = {"vest": "V", "lamp": "L", "stick": "S", "ball": "B", "treat": "T"}
    lift = 3.15 * pa.CELL / 12.0
    for cell, (_index, kind) in level.pickups.items():
        cx, cy = pa.center(level, cell)
        lines.append(
            f'<g id="{kind}-{pa.cell_name(cell)}" transform="translate({cx:.2f},{cy - lift:.2f})">'
        )
        lines.append(scaled_mark(kind, pa.CELL / 12.0))
        lines.append("</g>")
        lines.append(
            f'<text class="label" x="{cx + 3.3 * pa.CELL / 12:.2f}" y="{cy + 4.15 * pa.CELL / 12:.2f}" '
            f'font-size="1.7" text-anchor="middle">{letters[kind]}</text>'
        )
    sx, sy = pa.center(level, level.start)
    lines.append(f'<g id="abby" transform="translate({sx:.2f},{sy - lift:.2f})">')
    lines.append(scaled_mark("paw", pa.CELL / 12.0))
    lines.append("</g>")
    fx, fy = pa.center(level, level.flag)
    lines.append(f'<g id="flag" transform="translate({fx:.2f},{fy - lift:.2f})">')
    lines.append(scaled_mark("flag", pa.CELL / 12.0))
    lines.append("</g>")
    return "\n".join(lines)


def scaled_mark(kind: str, scale: float) -> str:
    """One scale for a drawn mark or a PNG, so a picture is not enlarged twice."""
    drawn = pa.picture(kind, 4, 4) or pa.icon(kind)
    return f'<g transform="scale({scale:.4f})">{drawn}</g>'


def circle_svg(cx: float, cy: float, radius: float, dashed: bool, filled: bool) -> str:
    if filled:
        return f'<circle fill="{INK}" cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}"/>'
    klass = "circle-dash" if dashed else "circle"
    return f'<circle class="{klass}" cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}"/>'


def steps_svg(level: pa.Level, route: pa.Route | None) -> str:
    lines = []
    used = route.steps if route else 0
    radius = mm(CIRCLE_R)
    for index in range(level.energy):
        cy = mm(CIRCLE_Y0 + index * CIRCLE_PITCH)
        lines.append(circle_svg(mm(SOLID_X), cy, radius, False, index < used))
        lines.append(
            circle_svg(mm(DASH_X), cy, radius, True, level.energy + index < used)
        )
    x1, y1, x2, y2 = STEPS_BOX
    lines.append(
        f'<rect class="box" x="{mm(x1):.2f}" y="{mm(y1):.2f}" '
        f'width="{mm(x2 - x1):.2f}" height="{mm(y2 - y1):.2f}"/>'
    )
    lines.append(
        f'<text class="label" x="{mm(x1) + 1.5:.2f}" y="{mm(y1) + 3.6:.2f}" font-size="2.5">steps</text>'
    )
    if route:
        lines.append(
            f'<text class="answer-ink" x="{mm((x1 + x2) / 2):.2f}" y="{mm(y1) + 12.5:.2f}" '
            f'font-size="7" text-anchor="middle" font-weight="700">{route.steps}</text>'
        )
    return "\n".join(lines)


def tool_row(kind: str, bar_kind: str, top: float, marked: bool, answer: bool) -> str:
    y = mm(top)
    height = mm(ROW_H)
    left = mm(ICON_X)
    mid = mm(CHECK_X)
    right = mm(PAIR_X2)
    lines = [
        f'<rect class="box" x="{left:.2f}" y="{y:.2f}" width="{mid - left:.2f}" height="{height:.2f}"/>',
        f'<rect class="box" x="{mid:.2f}" y="{y:.2f}" width="{right - mid:.2f}" height="{height:.2f}"/>',
        f'<rect class="box" x="{mm(BAR_X):.2f}" y="{y:.2f}" width="{mm(BAR_X2 - BAR_X):.2f}" height="{height:.2f}"/>',
    ]
    icon_scale = 3.1 * (pa.CELL / 12.0)
    drawn = pa.picture(kind, 4, 4) or pa.icon(kind)
    cx = (left + mid) / 2
    cy = y + height / 2
    lines.append(
        f'<g class="tally-tool" transform="translate({cx:.2f},{cy:.2f}) scale({icon_scale:.3f})">{drawn}</g>'
    )
    if marked:
        color = pa.ANSWER if answer else INK
        x0 = mid + 2.1
        y0 = y + 2.0
        lines.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="0.7" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'points="{x0:.2f},{y0 + 3.4:.2f} {x0 + 2.2:.2f},{y0 + 5.6:.2f} {x0 + 6.4:.2f},{y0 + 1.2:.2f}"/>'
        )
    # The wide bar is the stick or the ball, drawn as thin as the vest and lamp.
    bar_mark = pa.picture(bar_kind, 4, 4) or pa.icon(bar_kind)
    lines.append(
        f'<g class="tally-tool" transform="translate({mm(BAR_X) + 6.4:.2f},{cy:.2f}) scale({icon_scale:.3f})">{bar_mark}</g>'
    )
    return "\n".join(lines)


def tally_svg(level: pa.Level, route: pa.Route | None) -> str:
    on_path = set(route.path) if route else set()
    lines = []
    # Top bar is the stick, bottom bar is the tennis ball, matching the frame.
    for kind, bar_kind, top in (("vest", "stick", ROW_Y[0]), ("lamp", "ball", ROW_Y[1])):
        found = cells_of(level, kind)
        marked = bool(found) and all(cell in on_path for cell in found)
        lines.append(tool_row(kind, bar_kind, top, marked and route is not None, route is not None))
    x1, y1, x2, y2 = SCORE_BOX
    lines.append(
        f'<rect class="box" x="{mm(x1):.2f}" y="{mm(y1):.2f}" '
        f'width="{mm(x2 - x1):.2f}" height="{mm(y2 - y1):.2f}"/>'
    )
    lines.append(
        f'<text class="label" x="{mm(x1) + 1.5:.2f}" y="{mm(y1) + 3.6:.2f}" font-size="2.5">score</text>'
    )
    if route:
        score = f"−{abs(route.score)}" if route.score < 0 else str(route.score)
        lines.append(
            f'<text class="answer-ink" x="{mm((x1 + x2) / 2):.2f}" y="{mm(y1) + 16:.2f}" '
            f'font-size="6.4" text-anchor="middle" font-weight="700">{score}</text>'
        )
    return "\n".join(lines)


def instructions_svg() -> str:
    """Front page for the layout sheets. The marks are the old legend drawings."""
    parts: list[str] = []
    add = parts.append
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="5.5in" height="{PAGE_H / 25.4:.4f}in" '
        f'viewBox="0 0 {PAGE_W:.3f} {PAGE_H:.3f}">'
    )
    add("<!--")
    add("  Paper Abby, how to play. Print at actual size, with the layout sheets.")
    add("  Groups: header, welcome, how-to-play, icons, how-to-score.")
    add("-->")
    add("<style>")
    add(f"  text {{ font-family: {FONT}; }}")
    add(f"  .ink {{ fill: {INK}; }}")
    add(f"  .title {{ fill: {TITLE}; }}")
    add(f"  .label {{ fill: {LABEL}; }}")
    add("  .quiet { fill: #5e564c; }")
    add(f"  .paper {{ fill: #ffffff; }}")
    add(f"  .header {{ fill: {YELLOW}; }}")
    add("  .open { fill: #fffdf8; }")
    add("  .tree { fill: #e4f0da; }")
    add("  .canopy { fill: #d5e7c6; stroke: #243024; stroke-width: 0.32; }")
    add("  .trunk { stroke: #243024; stroke-width: 0.4; stroke-linecap: round; }")
    add("  .water { fill: #d5eaf2; }")
    add("  .wave { fill: none; stroke: #1d4c5c; stroke-width: 0.28; stroke-linecap: round; }")
    add("  .cave { fill: #e7e0d6; }")
    add("  .arch { fill: #d4cdc2; stroke: #1c1915; stroke-width: 0.35; }")
    add("  .cliff { stroke: #3a2c1e; stroke-linecap: round; }")
    add(f"  .dot {{ fill: #fffdf8; stroke: {INK}; stroke-width: 0.38; }}")
    add(f"  .item {{ fill: none; stroke: {INK}; stroke-width: 0.36; stroke-linecap: round; stroke-linejoin: round; }}")
    add(f"  .item-fill {{ fill: {INK}; stroke: none; }}")
    add(f"  .formula {{ fill: #fbf6ea; }}")
    add("</style>")
    add("<title>Paper Abby. How to play</title>")
    add(f'<rect class="paper" x="0" y="0" width="{PAGE_W:.3f}" height="{PAGE_H:.3f}"/>')

    add('<g id="header">')
    add(f'<rect class="header" x="0" y="0" width="{PAGE_W:.3f}" height="{mm(HEADER_H):.3f}"/>')
    add(
        f'<text class="label" x="{mm(18):.2f}" y="{mm(22):.2f}" font-size="3.5" '
        f'letter-spacing="0.08">instructions</text>'
    )
    add(
        f'<text class="label" x="{mm(168):.2f}" y="{mm(18):.2f}" font-size="2.7">Erase is free.</text>'
    )
    add(
        f'<text class="label" x="{mm(168):.2f}" y="{mm(32):.2f}" font-size="2.7">Higher is better.</text>'
    )
    add(
        f'<text class="title" x="{mm(18):.2f}" y="{mm(46):.2f}" font-size="8.2" '
        f'font-weight="700">Paper Abby</text>'
    )
    add("</g>")

    left = 8.4
    right = PAGE_W - 8.4

    def heading(y: float, title: str) -> float:
        add(
            f'<text class="title" x="{left:.2f}" y="{y:.2f}" font-size="4.15" '
            f'font-weight="700">{esc(title)}</text>'
        )
        add(
            f'<line x1="{left:.2f}" y1="{y + 1.35:.2f}" x2="{right:.2f}" y2="{y + 1.35:.2f}" '
            f'stroke="#e2d0a0" stroke-width="0.35"/>'
        )
        return y + 5.15

    def body(y: float, lines: list[str], lead: float = 3.58, blank: float | None = None) -> float:
        skip = lead if blank is None else blank
        for line in lines:
            if line:
                add(
                    f'<text class="ink" x="{left:.2f}" y="{y:.2f}" font-size="2.92">{esc(line)}</text>'
                )
                y += lead
            else:
                y += skip
        return y

    y = mm(HEADER_H) + 6.4
    add('<g id="welcome">')
    y = heading(y, "Welcome")
    y = body(
        y,
        [
            "Abby is the paw. The flag is the last dot. Draw one line from her",
            "to the flag. The pencil is the piece. Erase a line that goes wrong",
            "and draw another. The page is not lost.",
        ],
    )
    add("</g>")

    y += 2.7
    add('<g id="how-to-play">')
    y = heading(y, "How to Play")
    y = body(
        y,
        [
            "The paw is free. Each new dot fills one circle. You start with twelve",
            "solid circles. Dashed circles are not yours until a treat inks three,",
            "after you pay for that dot. Twenty-four is the cap. None left: erase",
            "and redraw. The flag may take the last circle. That still counts.",
            "",
            "Step only to a dot that shares a side. No diagonals, and no dot twice,",
            "so the line never crosses itself. The flag is the last dot.",
            "",
            "Trees have no dot. A heavy edge is a cliff: go around. Waves need the",
            "vest. An arch needs the lamp. Pick it up, then step in. Circle a find",
            "the line enters, and mark it. A thing you only looked at stays blank.",
        ],
        lead=3.52,
        blank=1.7,
    )
    add("</g>")

    y += 2.7
    add('<g id="icons">')
    y = heading(y, "Icons")
    icons = [
        ("paw", "Paw", "", "Abby. You start here, and this dot is free."),
        ("flag", "Flag", "", "The last dot. The line stops when it enters."),
        ("dot", "Dot", "", "One step, only to a dot that shares a side."),
        ("tree", "Tree", "", "No dot. You cannot enter. Go around."),
        ("cliff", "Cliff", "", "A closed edge. Reach either dot another way."),
        ("water", "Water", "", "Waves. Enter only after the vest is checked."),
        ("cave", "Cave", "", "An arch. Enter only after the lamp is checked."),
        ("vest", "Vest", "V", "Pick it up before the water. It does not score."),
        ("lamp", "Lamp", "L", "Pick it up before the cave. It does not score."),
        ("stick", "Stick", "S", "One point when the line enters its dot."),
        ("ball", "Ball", "B", "Three points when the line enters its dot."),
        ("treat", "Treat", "T", "One point, plus three circles inked back."),
    ]
    columns = [left, left + 64.4]
    row_h = 8.05
    origin = y - 1.15
    for index, (kind, name, letter, meaning) in enumerate(icons):
        col = index % 2
        row = index // 2
        x = columns[col]
        cy = origin + row * row_h + 3.15
        add(f'<g transform="translate({x + 3.35:.2f},{cy + 0.35:.2f})">{legend_mark(kind)}</g>')
        name_x = x + 7.7
        initial = (
            f'<tspan class="label" font-weight="400" font-size="2.4" dx="1.5">{esc(letter)}</tspan>'
            if letter
            else ""
        )
        add(
            f'<text class="ink" x="{name_x:.2f}" y="{cy - 0.95:.2f}" font-size="2.7" '
            f'font-weight="700">{esc(name)}{initial}</text>'
        )
        add(
            f'<text class="quiet" x="{name_x:.2f}" y="{cy + 2.05:.2f}" font-size="2.4">'
            f"{esc(meaning)}</text>"
        )
    y = origin + 6 * row_h + 0.2
    add("</g>")

    y += 2.5
    add('<g id="how-to-score">')
    y = heading(y, "How to Score")
    box_top = y - 3.15
    add(
        f'<rect class="formula" x="{left:.2f}" y="{box_top:.2f}" '
        f'width="{right - left:.2f}" height="6.5"/>'
    )
    add(
        f'<text class="title" x="{(left + right) / 2:.2f}" y="{box_top + 4.25:.2f}" '
        f'font-size="3.35" text-anchor="middle" font-weight="700">'
        f"sticks + 3×balls + treats − steps</text>"
    )
    y = box_top + 10.0
    y = body(
        y,
        [
            "Steps are the filled circles, one for each new dot. A stick is one",
            "point. A tennis ball is three. A treat is one. A step is one point",
            "the other way. Two sticks, a ball, and a treat, in fourteen steps:",
            "2 + 3 + 1 − 14 = −8.",
            "The vest and the lamp are not in that sum. A one-step detour for a",
            "stick ties the line you already had. A two-step detour for a stick",
            "loses. A ball pays for two extra steps. Higher is better, even below zero.",
            "Minus seven beats minus twelve. You win by touching the flag.",
            "The score is how two lines compare, if you want to compare them.",
        ],
        lead=3.48,
    )
    add("</g>")
    add("</svg>")
    if y > PAGE_H - 3.5:
        raise pa.MapError(f"instruction page overflows: {y:.1f} > {PAGE_H - 3.5:.1f}")
    return "\n".join(parts) + "\n"


def legend_mark(kind: str) -> str:
    """One old-legend drawing, centered on the origin, about 6 mm tall."""
    if kind == "dot":
        return (
            '<rect class="open" x="-2.55" y="-2.55" width="5.1" height="5.1" '
            'stroke="#cfc6b8" stroke-width="0.28"/>'
            '<circle class="dot" cx="0" cy="0" r="0.85"/>'
        )
    scale = {
        "paw": 1.55,
        "flag": 1.55,
        "tree": 1.08,
        "cliff": 1.05,
        "water": 1.05,
        "cave": 1.12,
        "vest": 1.38,
        "lamp": 1.38,
        "stick": 1.38,
        "ball": 1.38,
        "treat": 1.38,
    }[kind]
    body = pa.icon(kind) if kind in ("paw", "flag") else pa.glyph(kind)
    return f'<g transform="scale({scale:.2f})">{body}</g>'


def write_instructions() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "00-instructions.svg"
    path.write_text(instructions_svg(), encoding="utf-8")
    return path


def sheet_paths(level: pa.Level) -> tuple[Path, Path]:
    stem = f"{level.level:02d}"
    return OUT / f"{stem}-paper-abby.svg", OUT / f"{stem}-answer.svg"


def write_sheets(solved: list[tuple[pa.Level, pa.Route]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    saved = save_geometry()
    try:
        for level, route in solved:
            player, answer = sheet_paths(level)
            player.write_text(render(level, None), encoding="utf-8")
            answer.write_text(render(level, route), encoding="utf-8")
    finally:
        restore_geometry(saved)


def write_all() -> list[tuple[pa.Level, pa.Route]]:
    solved = []
    for path in pa.level_paths():
        level = pa.load_level(path)
        route = pa.route_from(level, level.expect, 1, 0)
        solved.append((level, route))
    write_sheets(solved)
    write_instructions()
    print(f"Wrote {len(solved)} layout sheets and the instruction page to {OUT.name}.")
    return solved


def main(argv: list[str]) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) > 1 and argv[1] == "instructions":
        path = write_instructions()
        print(f"Wrote {path.name}.")
        return
    if len(argv) > 1:
        level = pa.load_level(Path(argv[1]))
        route = pa.route_from(level, level.expect, 1, 0)
        write_sheets([(level, route)])
        print(f"Wrote level {level.level} to {OUT.name}.")
        return
    write_all()


if __name__ == "__main__":
    main(sys.argv)
