// Best score for a Paper Abby board.
//
// The search follows tools/paper_abby.py: a best-cost walk, then a count of
// simple paths at that score. A legal line never reuses a dot. Several
// lines may share the best score. If the only walks at the best cost reuse
// a dot, the search continues for the best legal score. The node cap is
// the same 2,000,000.

(function (root) {
  const COLS = "ABCDEF";
  const DIRS = [
    [-1, 0],
    [1, 0],
    [0, -1],
    [0, 1],
  ];
  const NODE_LIMIT = 2000000;

  function cellName(r, c) {
    return COLS[c] + (r + 1);
  }

  function parseCell(token, rows, cols) {
    if (typeof token !== "string") {
      throw new Error("Bad cell " + String(token) + ".");
    }
    const text = token.trim().toUpperCase();
    const col = COLS.indexOf(text[0]);
    const row = Number(text.slice(1)) - 1;
    if (
      col < 0 ||
      text.length < 2 ||
      !Number.isInteger(row) ||
      row < 0 ||
      col >= cols ||
      row >= rows
    ) {
      throw new Error(token + " is off the 6 by 10 board.");
    }
    return [row, col];
  }

  function keyOf(r, c) {
    return r + "," + c;
  }

  function canonicalPair(a, b, rows, cols) {
    const left = parseCell(a, rows, cols);
    const right = parseCell(b, rows, cols);
    const nameA = cellName(left[0], left[1]);
    const nameB = cellName(right[0], right[1]);
    if (left[0] < right[0] || (left[0] === right[0] && left[1] <= right[1])) {
      return [nameA, nameB];
    }
    return [nameB, nameA];
  }

  function abbyDocFromPaper(data) {
    const rows = data.rows == null ? 10 : Number(data.rows);
    const cols = data.cols == null ? 6 : Number(data.cols);
    if (rows !== 10 || cols !== 6) {
      throw new Error("This editor paints a 6 by 10 board.");
    }
    if (!data.start || !data.flag) {
      throw new Error("A level needs Abby and the flag.");
    }
    const terrain = {};
    const hasTrees = Array.isArray(data.trees);
    const hasOpen = Array.isArray(data.open);
    if (hasTrees && hasOpen) {
      throw new Error("Use open or trees, not both.");
    }
    if (hasTrees) {
      for (const token of data.trees) {
        const rc = parseCell(token, rows, cols);
        terrain[cellName(rc[0], rc[1])] = "tree";
      }
    } else if (hasOpen) {
      const open = new Set();
      for (const token of data.open) {
        const rc = parseCell(token, rows, cols);
        open.add(cellName(rc[0], rc[1]));
      }
      for (let r = 0; r < rows; r += 1) {
        for (let c = 0; c < cols; c += 1) {
          const name = cellName(r, c);
          if (!open.has(name)) terrain[name] = "tree";
        }
      }
    }
    for (const token of data.water || []) {
      const rc = parseCell(token, rows, cols);
      const name = cellName(rc[0], rc[1]);
      if (terrain[name] === "tree") {
        throw new Error(name + " is a tree and a gate.");
      }
      terrain[name] = "water";
    }
    for (const token of data.caves || []) {
      const rc = parseCell(token, rows, cols);
      const name = cellName(rc[0], rc[1]);
      if (terrain[name] === "tree") {
        throw new Error(name + " is a tree and a gate.");
      }
      if (terrain[name] === "water") {
        throw new Error("A tile cannot be water and a cave.");
      }
      terrain[name] = "cave";
    }
    const ridges = [];
    for (const pair of data.cliffs || []) {
      if (!Array.isArray(pair) || pair.length !== 2) {
        throw new Error("A ridge needs two cells.");
      }
      ridges.push(canonicalPair(pair[0], pair[1], rows, cols));
    }
    const pickups = [];
    for (const item of data.pickups || []) {
      const rc = parseCell(item.at, rows, cols);
      pickups.push({ at: cellName(rc[0], rc[1]), kind: item.kind });
    }
    const checks = {};
    if (data.checks && typeof data.checks === "object" && !Array.isArray(data.checks)) {
      for (const name of Object.keys(data.checks)) checks[name] = data.checks[name];
    }
    const expect = [];
    if (Array.isArray(data.expect)) {
      for (const token of data.expect) {
        const rc = parseCell(token, rows, cols);
        expect.push(cellName(rc[0], rc[1]));
      }
    }
    return {
      level: data.level == null ? 1 : data.level,
      name: data.name == null ? "Imported walk" : data.name,
      blurb: data.blurb == null ? "" : data.blurb,
      aside: data.aside == null ? "" : String(data.aside),
      rows,
      cols,
      start: cellName(...parseCell(data.start, rows, cols)),
      flag: cellName(...parseCell(data.flag, rows, cols)),
      terrain,
      ridges,
      pickups,
      energy: data.energy == null ? 12 : Number(data.energy),
      treatEnergy:
        data.treat_energy == null ? 3 : Number(data.treat_energy),
      energyCap: data.energy_cap == null ? 24 : Number(data.energy_cap),
      checks,
      expect: expect.length ? expect : null,
      shape: hasTrees ? "trees" : "open",
      answer: null,
    };
  }

  function abbyPaperFromDoc(doc) {
    const rows = doc.rows || 10;
    const cols = doc.cols || 6;
    const open = [];
    const trees = [];
    const water = [];
    const caves = [];
    for (let r = 0; r < rows; r += 1) {
      for (let c = 0; c < cols; c += 1) {
        const name = cellName(r, c);
        const kind = (doc.terrain && doc.terrain[name]) || "dot";
        if (kind === "tree") trees.push(name);
        else open.push(name);
        if (kind === "water") water.push(name);
        if (kind === "cave") caves.push(name);
      }
    }
    const paper = {
      level: Number(doc.level),
      name: doc.name,
      blurb: doc.blurb == null ? "" : doc.blurb,
    };
    if (doc.aside) paper.aside = doc.aside;
    paper.start = doc.start;
    paper.flag = doc.flag;
    if (doc.shape === "trees") paper.trees = trees;
    else paper.open = open;
    if (water.length) paper.water = water;
    if (caves.length) paper.caves = caves;
    if (doc.ridges && doc.ridges.length) {
      paper.cliffs = doc.ridges.map((pair) => pair.slice());
    }
    if (doc.pickups && doc.pickups.length) {
      paper.pickups = doc.pickups.map((item) => ({
        at: item.at,
        kind: item.kind,
      }));
    }
    if (doc.energy != null && doc.energy !== 12) paper.energy = doc.energy;
    if (doc.treatEnergy != null && doc.treatEnergy !== 3) {
      paper.treat_energy = doc.treatEnergy;
    }
    if (doc.energyCap != null && doc.energyCap !== 24) {
      paper.energy_cap = doc.energyCap;
    }
    const fresh =
      doc.answer && doc.answer.ok && Array.isArray(doc.answer.path) && doc.answer.path.length
        ? doc.answer.path
        : null;
    const line = fresh || (Array.isArray(doc.expect) ? doc.expect : null);
    if (line && line.length) paper.expect = line.slice();
    if (doc.checks && typeof doc.checks === "object" && !Array.isArray(doc.checks)) {
      const names = Object.keys(doc.checks);
      if (names.length) {
        const checks = {};
        for (const name of names) checks[name] = doc.checks[name];
        paper.checks = checks;
      }
    }
    return paper;
  }

  function pointValue(kind) {
    const tool = root.abbyTool(kind);
    if (!tool || !tool.scores) return 0;
    return tool.points == null ? 1 : tool.points;
  }

  function grantAmount(kind, doc) {
    if (kind === "treat") {
      if (doc.treatEnergy != null) return doc.treatEnergy;
      const tool = root.abbyTool("treat");
      return tool && tool.grants ? tool.grants : 3;
    }
    const tool = root.abbyTool(kind);
    return tool && tool.grants ? tool.grants : 0;
  }

  function compile(doc) {
    const rows = doc.rows || 10;
    const cols = doc.cols || 6;
    const n = rows * cols;
    const tree = new Uint8Array(n);
    const water = new Uint8Array(n);
    const cave = new Uint8Array(n);
    const terrain = doc.terrain || {};
    for (const name of Object.keys(terrain)) {
      const rc = parseCell(name, rows, cols);
      const id = rc[0] * cols + rc[1];
      const kind = terrain[name];
      if (kind === "tree") tree[id] = 1;
      else if (kind === "water") water[id] = 1;
      else if (kind === "cave") cave[id] = 1;
      else if (kind !== "dot") {
        throw new Error("Unknown ground at " + name + ".");
      }
    }
    const cliff = new Uint8Array(n * n);
    const ridgePairs = [];
    for (const pair of doc.ridges || []) {
      const a = parseCell(pair[0], rows, cols);
      const b = parseCell(pair[1], rows, cols);
      const ia = a[0] * cols + a[1];
      const ib = b[0] * cols + b[1];
      cliff[ia * n + ib] = 1;
      cliff[ib * n + ia] = 1;
      ridgePairs.push([a, b]);
    }
    const pickupList = [];
    const pickupAt = new Int16Array(n);
    pickupAt.fill(-1);
    for (const item of doc.pickups || []) {
      const rc = parseCell(item.at, rows, cols);
      const id = rc[0] * cols + rc[1];
      const index = pickupList.length;
      pickupList.push({ id, kind: item.kind, at: rc });
      pickupAt[id] = index;
    }
    const bits = pickupList.map((_, index) => 1n << BigInt(index));
    const scoringIndexes = [];
    const grant = pickupList.map((item) => grantAmount(item.kind, doc));
    const points = pickupList.map((item) => pointValue(item.kind));
    const kindIndexes = new Map();
    pickupList.forEach((item, index) => {
      const tool = root.abbyTool(item.kind);
      if (tool && tool.scores) scoringIndexes.push(index);
      if (!kindIndexes.has(item.kind)) kindIndexes.set(item.kind, []);
      kindIndexes.get(item.kind).push(index);
    });
    const start = parseCell(doc.start, rows, cols);
    const flag = parseCell(doc.flag, rows, cols);
    return {
      rows,
      cols,
      n,
      tree,
      water,
      cave,
      cliff,
      ridgePairs,
      pickupList,
      pickupAt,
      bits,
      scoringIndexes,
      grant,
      points,
      kindIndexes,
      gates: root.abbyGates(),
      start,
      flag,
      startId: start[0] * cols + start[1],
      flagId: flag[0] * cols + flag[1],
      energy: doc.energy == null ? 12 : doc.energy,
      energyCap: doc.energyCap == null ? 24 : doc.energyCap,
    };
  }

  function cellLabel(level, id) {
    return cellName((id / level.cols) | 0, id % level.cols);
  }

  function validate(level) {
    if (level.startId === level.flagId) {
      return "Abby is already on the flag.";
    }
    if (level.tree[level.startId] || level.tree[level.flagId]) {
      return "Abby or the flag is on a tree.";
    }
    for (let id = 0; id < level.n; id += 1) {
      if (level.water[id] && level.tree[id]) {
        return cellLabel(level, id) + " is a tree and a gate.";
      }
      if (level.cave[id] && level.tree[id]) {
        return cellLabel(level, id) + " is a tree and a gate.";
      }
      if (level.water[id] && level.cave[id]) {
        return "A tile cannot be water and a cave.";
      }
    }
    const seen = new Set();
    for (const item of level.pickupList) {
      if (seen.has(item.id)) {
        return "Two items on " + cellLabel(level, item.id) + ".";
      }
      seen.add(item.id);
      const tool = root.abbyTool(item.kind);
      if (!tool || tool.group !== "item") {
        return "Unknown item: " + item.kind + ".";
      }
      if (level.tree[item.id]) {
        return item.kind + " on a tree at " + cellLabel(level, item.id) + ".";
      }
      if (level.water[item.id] || level.cave[item.id]) {
        return (
          item.kind +
          " is sitting inside a gate at " +
          cellLabel(level, item.id) +
          "."
        );
      }
      if (item.id === level.startId || item.id === level.flagId) {
        return item.kind + " is on Abby or the flag.";
      }
    }
    for (const pair of level.ridgePairs) {
      const dr = Math.abs(pair[0][0] - pair[1][0]);
      const dc = Math.abs(pair[0][1] - pair[1][1]);
      const nameA = cellName(pair[0][0], pair[0][1]);
      const nameB = cellName(pair[1][0], pair[1][1]);
      if (dr + dc !== 1) {
        return "The ridge " + nameA + "–" + nameB + " is not a side.";
      }
      const ia = pair[0][0] * level.cols + pair[0][1];
      const ib = pair[1][0] * level.cols + pair[1][1];
      if (level.tree[ia] || level.tree[ib]) {
        return "The ridge " + nameA + "–" + nameB + " touches a tree.";
      }
    }
    return null;
  }

  function hasKind(level, mask, kind) {
    const indexes = level.kindIndexes.get(kind);
    if (!indexes) return false;
    for (const index of indexes) {
      if ((mask & level.bits[index]) !== 0n) return true;
    }
    return false;
  }

  function findCount(level, mask) {
    let total = 0;
    for (const index of level.scoringIndexes) {
      if ((mask & level.bits[index]) !== 0n) total += level.points[index];
    }
    return total;
  }

  function scoringLeft(level, mask) {
    let total = 0;
    for (const index of level.scoringIndexes) {
      if ((mask & level.bits[index]) === 0n) total += level.points[index];
    }
    return total;
  }

  function grantsLeft(level, mask) {
    let total = 0;
    for (let index = 0; index < level.grant.length; index += 1) {
      if (!level.grant[index]) continue;
      if ((mask & level.bits[index]) === 0n) total += level.grant[index];
    }
    return total;
  }

  function stepBlocked(level, src, dst, mask) {
    if (level.tree[dst]) return true;
    if (level.cliff[src * level.n + dst]) return true;
    if (level.water[dst]) {
      const need = level.gates.get("water");
      if (need && !hasKind(level, mask, need)) return true;
    }
    if (level.cave[dst]) {
      const need = level.gates.get("cave");
      if (need && !hasKind(level, mask, need)) return true;
    }
    return false;
  }

  function enter(level, dst, energy, mask) {
    if (energy < 1) throw new Error("Step with no energy.");
    let nextEnergy = energy - 1;
    let kind = null;
    const index = level.pickupAt[dst];
    if (index >= 0) {
      const bit = level.bits[index];
      if ((mask & bit) === 0n) {
        mask |= bit;
        kind = level.pickupList[index].kind;
        const bonus = level.grant[index];
        if (bonus) {
          nextEnergy = Math.min(level.energyCap, nextEnergy + bonus);
        }
      }
    }
    return { energy: nextEnergy, mask, kind };
  }

  function distances(level) {
    const dist = new Int16Array(level.n);
    dist.fill(999);
    dist[level.flagId] = 0;
    const queue = [level.flagId];
    let head = 0;
    while (head < queue.length) {
      const id = queue[head];
      head += 1;
      const r = (id / level.cols) | 0;
      const c = id % level.cols;
      for (const dir of DIRS) {
        const nr = r + dir[0];
        const nc = c + dir[1];
        if (nr < 0 || nc < 0 || nr >= level.rows || nc >= level.cols) continue;
        const nxt = nr * level.cols + nc;
        if (level.tree[nxt]) continue;
        if (level.cliff[id * level.n + nxt]) continue;
        if (dist[nxt] <= dist[id] + 1) continue;
        dist[nxt] = dist[id] + 1;
        queue.push(nxt);
      }
    }
    return dist;
  }

  function heapPush(heap, item) {
    heap.push(item);
    let i = heap.length - 1;
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (heap[parent].cost <= item.cost) break;
      heap[i] = heap[parent];
      i = parent;
    }
    heap[i] = item;
  }

  function dijkstra(level) {
    const startKey = level.startId + "," + level.energy + ",0";
    const best = new Map([[startKey, 0]]);
    const parent = new Map([[startKey, null]]);
    const heap = [
      {
        cost: 0,
        id: level.startId,
        energy: level.energy,
        mask: 0n,
        key: startKey,
      },
    ];
    let goal = null;
    const dist = distances(level);
    while (heap.length) {
      const current = siftPop(heap);
      if (current.cost !== best.get(current.key)) continue;
      const steps = current.cost + findCount(level, current.mask);
      if (current.id === level.flagId && steps > 0) {
        if (!goal || current.cost < goal.cost) goal = current;
        continue;
      }
      if (current.energy < 1) continue;
      // A ball is worth more than the step onto it, so the first time the
      // flag is reached may not be the best. A state is finished once the
      // points still out cannot beat the best flag already found.
      if (goal) {
        const hopeful =
          current.cost + dist[current.id] - scoringLeft(level, current.mask);
        if (hopeful >= goal.cost) continue;
      }
      const r = (current.id / level.cols) | 0;
      const c = current.id % level.cols;
      for (const dir of DIRS) {
        const nr = r + dir[0];
        const nc = c + dir[1];
        if (nr < 0 || nc < 0 || nr >= level.rows || nc >= level.cols) continue;
        const dst = nr * level.cols + nc;
        if (stepBlocked(level, current.id, dst, current.mask)) continue;
        let next;
        try {
          next = enter(level, dst, current.energy, current.mask);
        } catch (err) {
          continue;
        }
        const nfinds = findCount(level, next.mask);
        const ncost = steps + 1 - nfinds;
        const nkey = dst + "," + next.energy + "," + next.mask.toString();
        if (ncost < (best.has(nkey) ? best.get(nkey) : 1e9)) {
          best.set(nkey, ncost);
          parent.set(nkey, current.key);
          heapPush(heap, {
            cost: ncost,
            id: dst,
            energy: next.energy,
            mask: next.mask,
            key: nkey,
          });
        }
      }
    }
    if (!goal) return null;
    const ids = [];
    let cursor = goal.key;
    while (cursor != null) {
      ids.push(Number(cursor.split(",")[0]));
      cursor = parent.get(cursor);
    }
    ids.reverse();
    return { ids, score: -best.get(goal.key) };
  }

  function siftPop(heap) {
    const top = heap[0];
    const last = heap.pop();
    if (heap.length === 0) return top;
    let i = 0;
    heap[0] = last;
    while (true) {
      let best = i;
      const left = i * 2 + 1;
      const right = left + 1;
      if (left < heap.length && heap[left].cost < heap[best].cost) best = left;
      if (right < heap.length && heap[right].cost < heap[best].cost) best = right;
      if (best === i) break;
      const swap = heap[best];
      heap[best] = heap[i];
      heap[i] = swap;
      i = best;
    }
    return top;
  }

  function walk(level, target, dist, seekBest) {
    let nodes = 0;
    let capped = false;
    let ties = 0;
    let bestScore = seekBest ? null : target;
    const examples = [];
    const flagId = level.flagId;

    function dfs(id, energy, mask, steps, finds, visited, path) {
      if (capped) return;
      nodes += 1;
      if (nodes > NODE_LIMIT) {
        capped = true;
        return;
      }
      if (steps > 0 && id === flagId) {
        const score = finds - steps;
        if (seekBest) {
          if (bestScore === null || score > bestScore) {
            bestScore = score;
            ties = 1;
            examples.length = 0;
            examples.push(path.slice());
          } else if (score === bestScore) {
            ties += 1;
            if (examples.length < 6) examples.push(path.slice());
          }
        } else if (score > target) {
          capped = true;
          examples.length = 0;
          examples.push(path.slice());
          ties = -1;
        } else if (score === target) {
          ties += 1;
          if (examples.length < 6) examples.push(path.slice());
        }
        return;
      }
      const away = dist[id];
      if (bestScore !== null && !seekBest) {
        if (finds + scoringLeft(level, mask) - steps - away < target) return;
      }
      if (seekBest && bestScore !== null) {
        if (finds + scoringLeft(level, mask) - steps - away < bestScore) return;
      }
      if (energy + grantsLeft(level, mask) < away) return;
      if (energy < 1) return;
      const r = (id / level.cols) | 0;
      const c = id % level.cols;
      for (const dir of DIRS) {
        if (capped) return;
        const nr = r + dir[0];
        const nc = c + dir[1];
        if (nr < 0 || nc < 0 || nr >= level.rows || nc >= level.cols) continue;
        const dst = nr * level.cols + nc;
        const mark = 1n << BigInt(dst);
        if ((visited & mark) !== 0n) continue;
        if (stepBlocked(level, id, dst, mask)) continue;
        const next = enter(level, dst, energy, mask);
        path.push(dst);
        dfs(
          dst,
          next.energy,
          next.mask,
          steps + 1,
          findCount(level, next.mask),
          visited | mark,
          path
        );
        path.pop();
      }
    }

    dfs(
      level.startId,
      level.energy,
      0n,
      0,
      0,
      1n << BigInt(level.startId),
      [level.startId]
    );
    return { ties, examples, nodes, capped, bestScore };
  }

  function idsToPath(level, ids) {
    return ids.map((id) => [
      (id / level.cols) | 0,
      id % level.cols,
    ]);
  }

  function sameIds(a, b) {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i += 1) {
      if (a[i] !== b[i]) return false;
    }
    return true;
  }

  function repeats(ids) {
    return new Set(ids).size !== ids.length;
  }

  function simulate(level, ids) {
    let energy = level.energy;
    let mask = 0n;
    const trace = [
      { id: ids[0], energy, kind: null },
    ];
    for (let i = 1; i < ids.length; i += 1) {
      const src = ids[i - 1];
      const dst = ids[i];
      const sr = (src / level.cols) | 0;
      const sc = src % level.cols;
      const dr = (dst / level.cols) | 0;
      const dc = dst % level.cols;
      if (Math.abs(sr - dr) + Math.abs(sc - dc) !== 1) {
        throw new Error(
          cellLabel(level, src) +
            " does not share a side with " +
            cellLabel(level, dst) +
            "."
        );
      }
      if (stepBlocked(level, src, dst, mask)) {
        throw new Error("The line cannot step to " + cellLabel(level, dst) + ".");
      }
      const next = enter(level, dst, energy, mask);
      energy = next.energy;
      mask = next.mask;
      trace.push({ id: dst, energy, kind: next.kind });
    }
    const steps = ids.length - 1;
    const finds = findCount(level, mask);
    return { score: finds - steps, steps, trace, finds, energy };
  }

  function tally(level, ids) {
    const onPath = new Set(ids);
    const counts = {};
    for (const item of level.pickupList) {
      if (!onPath.has(item.id)) continue;
      counts[item.kind] = (counts[item.kind] || 0) + 1;
    }
    return counts;
  }

  function scoreBit(kind, n) {
    const tool = root.abbyTool(kind);
    const word = (tool && (tool.scoreWord || tool.label || kind)) || kind;
    const name = word.toLowerCase();
    const label = n + " " + name + (n === 1 ? "" : "s");
    const each = tool && tool.points != null ? tool.points : 1;
    if (each === 1) return label;
    return n + "×" + each + " " + name + (n === 1 ? "" : "s");
  }

  function scoreText(counts, steps, score) {
    const bits = [];
    for (const kind of ["stick", "ball", "treat"]) {
      const n = counts[kind] || 0;
      if (!n) continue;
      bits.push(scoreBit(kind, n));
    }
    for (const kind of Object.keys(counts)) {
      if (kind === "stick" || kind === "ball" || kind === "treat") continue;
      const tool = root.abbyTool(kind);
      if (!tool || !tool.scores) continue;
      bits.push(scoreBit(kind, counts[kind]));
    }
    if (!bits.length) bits.push("no finds");
    return bits.join(" + ") + " − " + steps + " steps = " + score;
  }

  function traceText(level, trace) {
    return trace
      .map((step, index) => {
        let label = cellLabel(level, step.id);
        if (step.kind) label += " " + step.kind;
        if (index === trace.length - 1) label += " flag";
        return label + " (" + step.energy + ")";
      })
      .join(" → ");
  }

  function arrowText(level, ids) {
    return ids.map((id) => cellLabel(level, id)).join(" → ");
  }

  function finish(level, ids, ties, examples, nodes) {
    const played = simulate(level, ids);
    const counts = tally(level, ids);
    const names = ids.map((id) => cellLabel(level, id));
    let tieNote = "No other line reaches this score.";
    let shown = [];
    if (ties > 1) {
      tieNote = ties + " lines reach this score.";
      shown = examples.map((sample) => arrowText(level, sample));
    }
    return {
      ok: true,
      path: names,
      score: played.score,
      steps: played.steps,
      scoreText: scoreText(counts, played.steps, played.score),
      lineText: traceText(level, played.trace),
      ties,
      tieNote,
      examples: shown,
      nodes,
    };
  }

  function abbySolve(data) {
    const doc = data && data.terrain ? data : abbyDocFromPaper(data);
    let level;
    try {
      level = compile(doc);
    } catch (err) {
      return { ok: false, message: err.message };
    }
    const problem = validate(level);
    if (problem) return { ok: false, message: problem };
    const dist = distances(level);
    const found = dijkstra(level);
    if (!found) {
      return { ok: false, message: "No legal line reaches the flag." };
    }
    const counted = walk(level, found.score, dist, false);
    if (counted.ties === -1) {
      return {
        ok: false,
        message:
          "A line scores better than the route the search settled on. The map needs another look.",
      };
    }
    if (counted.capped) {
      return {
        ok: false,
        message:
          "The search got too large. This map is too open to prove the best line.",
      };
    }
    if (counted.ties >= 1) {
      let ids = counted.examples[0];
      if (!repeats(found.ids) && !sameIds(ids, found.ids) && counted.ties === 1) {
        ids = found.ids;
      }
      return finish(level, ids, counted.ties, counted.examples, counted.nodes);
    }
    const simple = walk(level, null, dist, true);
    if (simple.capped) {
      return {
        ok: false,
        message:
          "The search got too large. This map is too open to prove the best line.",
      };
    }
    if (simple.ties < 1) {
      return { ok: false, message: "No legal line reaches the flag." };
    }
    return finish(
      level,
      simple.examples[0],
      simple.ties,
      simple.examples,
      counted.nodes + simple.nodes
    );
  }

  root.abbyCellName = cellName;
  root.abbyParseCell = parseCell;
  root.abbyDocFromPaper = abbyDocFromPaper;
  root.abbyPaperFromDoc = abbyPaperFromDoc;
  root.abbySolve = abbySolve;
})(globalThis);
