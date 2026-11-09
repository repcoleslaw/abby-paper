// Local level painter. The board autosaves in localStorage. Save to folder
// writes a level JSON file through the File System Access API.

(function () {
  const STORAGE_KEY = "abby-editor-levels";
  const DB_NAME = "abby-editor";
  const STORE = "handles";
  const COLS = ["A", "B", "C", "D", "E", "F"];

  const MARKS = {
    dot: '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="4" fill="#1c1915"/></svg>',
    tree: '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="14" y="18" width="4" height="10" rx="1" fill="#6a4324"/><circle cx="16" cy="14" r="9" fill="#2f6b3a"/><circle cx="11" cy="16" r="5" fill="#3d7d49"/></svg>',
    ridge: '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="14" y="4" width="4" height="24" rx="1" fill="#1c1915"/><path d="M8 10 h16 M8 16 h16 M8 22 h16" stroke="#1c1915" stroke-width="1.4"/></svg>',
    water: '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M3 14 q4-4 8 0 t8 0 t8 0" fill="none" stroke="#2a6f9c" stroke-width="2"/><path d="M3 21 q4-4 8 0 t8 0 t8 0" fill="none" stroke="#2a6f9c" stroke-width="2"/></svg>',
    cave: '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M6 26 V14 q0-10 10-10 t10 10 V26" fill="none" stroke="#5c4d66" stroke-width="2.4"/></svg>',
    stick: '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M8 24 L22 8" stroke="#8a5a2a" stroke-width="3" stroke-linecap="round"/><path d="M18 8 l4-2 M20 12 l4-1" stroke="#6d4520" stroke-width="1.6" stroke-linecap="round"/></svg>',
    ball: '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="8" fill="#d6c43a"/><path d="M10 13 q6 2 12-2 M11 20 q6-3 11 1" fill="none" stroke="#fffdf8" stroke-width="1.4"/></svg>',
    vest: '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M11 8 l5 3 5-3 3 4 -3 2 v12 h-10 V14 l-3-2 z" fill="#e07a3d"/><path d="M16 11 v15" stroke="#fffdf8" stroke-width="1.5"/></svg>',
    lamp: '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 6 v4" stroke="#1c1915" stroke-width="1.6"/><rect x="12" y="10" width="8" height="10" rx="3" fill="#e6c84a"/><path d="M13 22 h6 l-1 4 h-4 z" fill="#5e564c"/></svg>',
    treat: '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="9" cy="13" r="3.2" fill="#e0c7a2"/><circle cx="9" cy="20" r="3.2" fill="#e0c7a2"/><circle cx="23" cy="13" r="3.2" fill="#e0c7a2"/><circle cx="23" cy="20" r="3.2" fill="#e0c7a2"/><rect x="10" y="14" width="12" height="5" rx="2.5" fill="#e0c7a2"/></svg>',
    abby: '<svg viewBox="0 0 32 32" aria-hidden="true"><ellipse cx="16" cy="21" rx="7" ry="5.5" fill="#8a5a32"/><circle cx="8" cy="13" r="2.7" fill="#8a5a32"/><circle cx="13" cy="9" r="2.8" fill="#8a5a32"/><circle cx="19" cy="9" r="2.8" fill="#8a5a32"/><circle cx="24" cy="13" r="2.5" fill="#8a5a32"/></svg>',
    flag: '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M11 5 v22" stroke="#1c1915" stroke-width="2"/><path d="M12 6 h13 l-3 5 3 5 H12 z" fill="#9c2f2f"/></svg>',
  };

  const board = document.querySelector("#board");
  const grid = document.querySelector("#grid");
  const toolsEl = document.querySelector("#tools");
  const levelsEl = document.querySelector("#levels");
  const statusEl = document.querySelector("#status");
  const folderEl = document.querySelector("#folder");
  const levelInput = document.querySelector("#level-num");
  const nameInput = document.querySelector("#level-name");
  const blurbInput = document.querySelector("#level-blurb");
  const testButton = document.querySelector("#test");
  const fileInput = document.querySelector("#import-file");
  const answerEmpty = document.querySelector("#answer-empty");
  const answerBody = document.querySelector("#answer-body");
  const answerError = document.querySelector("#answer-error");
  const scoreEl = document.querySelector("#score");
  const lineEl = document.querySelector("#line");
  const tieEl = document.querySelector("#tie");
  const examplesLabel = document.querySelector("#examples-label");
  const examplesEl = document.querySelector("#examples");

  let library = loadLibrary();
  let tool = "tree";
  let painting = false;
  let paintKind = "tree";
  let folderHandle = null;

  function esc(value) {
    return String(value).replace(/[&<>"']/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    }[ch]));
  }

  function labelOf(id) {
    const entry = abbyTool(id);
    return entry ? entry.label.toLowerCase() : id;
  }

  function loadLibrary() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const data = JSON.parse(raw);
      if (!data || !Array.isArray(data.levels) || data.levels.length === 0) return null;
      data.levels.forEach(normalizeDoc);
      return data;
    } catch (err) {
      return null;
    }
  }

  function normalizeDoc(doc) {
    doc.terrain = doc.terrain || {};
    doc.ridges = doc.ridges || [];
    doc.pickups = doc.pickups || [];
    doc.rows = 10;
    doc.cols = 6;
    if (doc.energy == null) doc.energy = 12;
    if (doc.treatEnergy == null) doc.treatEnergy = 3;
    if (doc.energyCap == null) doc.energyCap = 24;
    if (!doc.start) doc.start = "A10";
    if (!doc.flag) doc.flag = "F6";
    return doc;
  }

  function nextLevelNumber() {
    let max = 25;
    const levels = library && library.levels ? library.levels : [];
    for (const level of levels) {
      const n = Number(level.level);
      if (Number.isInteger(n) && n > max) max = n;
    }
    return Math.max(26, max + 1);
  }

  function blankLevel() {
    return normalizeDoc({
      id: crypto.randomUUID(),
      level: nextLevelNumber(),
      name: "New walk",
      blurb: "One line from Abby to the flag.",
      start: "A10",
      flag: "F6",
      terrain: {},
      ridges: [],
      pickups: [],
      answer: null,
    });
  }

  if (!library) {
    const first = blankLevel();
    library = { version: 1, activeId: first.id, levels: [first] };
    saveLibrary();
  }

  function current() {
    let doc = library.levels.find((level) => level.id === library.activeId);
    if (!doc) {
      doc = library.levels[0];
      library.activeId = doc.id;
    }
    return doc;
  }

  function saveLibrary() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      version: 1,
      activeId: library.activeId,
      levels: library.levels,
    }));
  }

  function setStatus(message) {
    statusEl.textContent = message || "";
  }

  function ground(doc, name) {
    return (doc.terrain && doc.terrain[name]) || "dot";
  }

  function takeItem(doc, name) {
    const index = doc.pickups.findIndex((item) => item.at === name);
    if (index < 0) return null;
    const kind = doc.pickups[index].kind;
    doc.pickups.splice(index, 1);
    return kind;
  }

  function fileNameFor(level) {
    const n = Number(level);
    if (!Number.isInteger(n) || n < 1) return null;
    return (n < 100 ? String(n).padStart(2, "0") : String(n)) + ".json";
  }

  function paperText(doc) {
    const copy = Object.assign({}, doc, {
      name: String(doc.name || "").trim(),
      blurb: String(doc.blurb == null ? "" : doc.blurb).trim(),
    });
    return JSON.stringify(abbyPaperFromDoc(copy), null, 2) + "\n";
  }

  function saveNote(lead) {
    const answer = current().answer;
    if (answer && !answer.ok) {
      return lead + " This map has no legal best score, so paper_abby.py will reject this file.";
    }
    if (answer && answer.ok && answer.ties > 1) {
      return lead + " " + answer.ties + " lines reach that score.";
    }
    return lead;
  }

  function readyToWrite() {
    const doc = current();
    if (!fileNameFor(doc.level)) {
      setStatus("Set a level number before saving.");
      return false;
    }
    if (!String(doc.name || "").trim()) {
      setStatus("Add a name before saving.");
      return false;
    }
    return true;
  }

  function iconHtml(id, className) {
    const entry = abbyTool(id);
    if (entry && entry.icon) {
      return '<img class="' + className + '" alt="" src="' + esc(entry.icon) + '">';
    }
    const mark = MARKS[id];
    if (!mark) return "";
    return '<span class="' + className + '">' + mark + "</span>";
  }

  function renderTools() {
    const groups = [
      ["terrain", "Terrain"],
      ["item", "Items"],
      ["place", "Place"],
    ];
    toolsEl.innerHTML = groups.map(([group, title]) => {
      const buttons = ABBY_TOOLS.filter((entry) => entry.group === group).map((entry) => {
        const pressed = entry.id === tool ? "true" : "false";
        return (
          '<button type="button" class="tool" data-tool="' + entry.id + '" aria-pressed="' + pressed + '">' +
          iconHtml(entry.id, "swatch") + esc(entry.label) + "</button>"
        );
      }).join("");
      return '<div class="toolset"><span class="toolset-name">' + title + "</span>" + buttons + "</div>";
    }).join("");
  }

  function selectTool(id) {
    tool = id;
    board.dataset.tool = id;
    for (const button of toolsEl.querySelectorAll(".tool")) {
      button.setAttribute("aria-pressed", button.dataset.tool === id ? "true" : "false");
    }
  }

  function metrics() {
    const style = getComputedStyle(grid);
    const read = (name, fallback) => {
      const value = parseFloat(style.getPropertyValue(name));
      return Number.isFinite(value) ? value : fallback;
    };
    return {
      label: read("--label", 26),
      cell: read("--cell", 52),
      gap: read("--gap", 6),
    };
  }

  function pathMarks(path) {
    const marks = new Map();
    if (!path || path.length < 2) return marks;
    const add = (name, dir) => {
      if (!marks.has(name)) marks.set(name, []);
      marks.get(name).push(dir);
    };
    const back = { n: "s", s: "n", e: "w", w: "e" };
    for (let i = 0; i < path.length - 1; i += 1) {
      const from = abbyParseCell(path[i], 10, 6);
      const to = abbyParseCell(path[i + 1], 10, 6);
      const dr = to[0] - from[0];
      const dc = to[1] - from[1];
      const dir = dr === -1 ? "n" : dr === 1 ? "s" : dc === 1 ? "e" : "w";
      add(path[i], dir);
      add(path[i + 1], back[dir]);
    }
    return marks;
  }

  function ridgeSet(doc) {
    const set = new Set();
    for (const pair of doc.ridges) set.add(pair[0] + "|" + pair[1]);
    return set;
  }

  function renderBoard() {
    const doc = current();
    const marks = pathMarks(doc.answer && doc.answer.ok ? doc.answer.path : null);
    const ridges = ridgeSet(doc);
    const m = metrics();
    let html = '<div class="corner"></div>';
    for (const col of COLS) html += '<div class="colhead">' + col + "</div>";
    for (let r = 0; r < 10; r += 1) {
      html += '<div class="rowhead">' + (r + 1) + "</div>";
      for (let c = 0; c < 6; c += 1) {
        const name = abbyCellName(r, c);
        const terrain = ground(doc, name);
        const item = doc.pickups.find((entry) => entry.at === name);
        let who = "";
        if (doc.start === name) who = "abby";
        else if (doc.flag === name) who = "flag";
        const bits = [name];
        if (terrain !== "dot") bits.push(labelOf(terrain));
        if (who) bits.push(who === "abby" ? "Abby" : "flag");
        if (item) bits.push(labelOf(item.kind));
        const segs = (marks.get(name) || []).map((dir) => '<span class="seg ' + dir + '"></span>').join("");
        let pictures = "";
        if (terrain === "tree" || terrain === "water" || terrain === "cave") {
          pictures += iconHtml(terrain, "mark terrain");
        }
        if (who) pictures += iconHtml(who, "mark who");
        else if (item) pictures += iconHtml(item.kind, "mark item");
        const dot = '<i class="dot"></i>';
        html +=
          '<div class="cell" data-cell="' + name + '" data-terrain="' + terrain + '"' +
          (who ? ' data-who="' + who + '"' : "") +
          (item ? ' data-item="' + item.kind + '"' : "") +
          ' role="img" aria-label="' + esc(bits.join(", ")) + '">' +
          segs + pictures + dot + "</div>";
      }
    }
    const edge = (spec, vertical, left, top) => {
      const on = ridges.has(spec);
      const [a, b] = spec.split("|");
      const label = (on ? "Ridge between " : "Side between ") + a + " and " + b;
      const size = vertical
        ? "left:" + left + "px;top:" + top + "px;width:18px;height:" + m.cell + "px"
        : "left:" + left + "px;top:" + top + "px;width:" + m.cell + "px;height:18px";
      return (
        '<button type="button" class="edge ' + (vertical ? "v" : "h") + (on ? " on" : "") +
        '" data-edge="' + spec + '" aria-pressed="' + (on ? "true" : "false") +
        '" aria-label="' + label + '" style="' + size + '"><span class="bar"></span></button>'
      );
    };
    for (let r = 0; r < 10; r += 1) {
      for (let c = 0; c < 5; c += 1) {
        const spec = abbyCellName(r, c) + "|" + abbyCellName(r, c + 1);
        const center = m.label + m.gap + c * (m.cell + m.gap) + m.cell + m.gap / 2;
        const top = m.label + m.gap + r * (m.cell + m.gap);
        html += edge(spec, true, center - 9, top);
      }
    }
    for (let r = 0; r < 9; r += 1) {
      for (let c = 0; c < 6; c += 1) {
        const spec = abbyCellName(r, c) + "|" + abbyCellName(r + 1, c);
        const left = m.label + m.gap + c * (m.cell + m.gap);
        const center = m.label + m.gap + r * (m.cell + m.gap) + m.cell + m.gap / 2;
        html += edge(spec, false, left, center - 9);
      }
    }
    grid.innerHTML = html;
  }

  function renderLibrary() {
    const active = current().id;
    levelsEl.innerHTML = library.levels.map((level) => {
      const label = level.level + ". " + (level.name || "Untitled");
      const cls = level.id === active ? "level active" : "level";
      return '<button type="button" class="' + cls + '" data-id="' + esc(level.id) + '">' + esc(label) + "</button>";
    }).join("");
  }

  function renderAnswer() {
    const answer = current().answer;
    answerEmpty.hidden = Boolean(answer);
    answerBody.hidden = !answer || !answer.ok;
    answerError.hidden = !answer || answer.ok;
    if (!answer) {
      answerEmpty.textContent = "Paint a walk, then test it.";
      return;
    }
    if (!answer.ok) {
      answerError.textContent = answer.message;
      return;
    }
    scoreEl.textContent = answer.scoreText + ".";
    lineEl.textContent = answer.lineText + ".";
    tieEl.textContent = answer.tieNote;
    const list = answer.examples || [];
    const show = answer.ties > 1 && list.length > 0;
    examplesEl.hidden = !show;
    examplesLabel.hidden = !show;
    examplesEl.innerHTML = show ? list.map((item) => "<li>" + esc(item) + "</li>").join("") : "";
    if (show) {
      examplesLabel.textContent = answer.ties > list.length ? list.length + " of them." : "Those lines.";
    }
  }

  function showLevel() {
    const doc = current();
    levelInput.value = doc.level;
    nameInput.value = doc.name || "";
    blurbInput.value = doc.blurb || "";
    renderLibrary();
    renderBoard();
    renderAnswer();
  }

  function commitMap() {
    current().answer = null;
    saveLibrary();
    renderBoard();
    renderAnswer();
  }

  function applyTerrain(name, kind) {
    const doc = current();
    if (ground(doc, name) === kind) return;
    if (kind === "tree" && (name === doc.start || name === doc.flag)) {
      setStatus("A tree cannot cover Abby or the flag.");
      return;
    }
    if (kind === "dot") delete doc.terrain[name];
    else doc.terrain[name] = kind;
    if (kind === "tree") {
      const removed = takeItem(doc, name);
      doc.ridges = doc.ridges.filter((pair) => pair[0] !== name && pair[1] !== name);
      if (removed) setStatus("The " + labelOf(removed) + " cannot sit on a tree.");
    }
    if (kind === "water" || kind === "cave") {
      const removed = takeItem(doc, name);
      if (removed) {
        const place = kind === "water" ? "the water" : "a cave";
        setStatus("The " + labelOf(removed) + " cannot sit in " + place + ".");
      }
    }
    commitMap();
  }

  function placeItem(name) {
    const doc = current();
    if (ground(doc, name) !== "dot") {
      setStatus("A " + labelOf(tool) + " needs a dot.");
      return;
    }
    if (name === doc.start || name === doc.flag) {
      setStatus("A " + labelOf(tool) + " cannot sit on Abby or the flag.");
      return;
    }
    const index = doc.pickups.findIndex((item) => item.at === name);
    if (index >= 0 && doc.pickups[index].kind === tool) doc.pickups.splice(index, 1);
    else if (index >= 0) doc.pickups[index] = { at: name, kind: tool };
    else doc.pickups.push({ at: name, kind: tool });
    commitMap();
  }

  function moveToken(name) {
    const doc = current();
    const which = tool === "abby" ? "start" : "flag";
    const title = tool === "abby" ? "Abby" : "The flag";
    if (doc[which] === name) return;
    if (ground(doc, name) === "tree") {
      setStatus(title + " cannot stand on a tree.");
      return;
    }
    const other = which === "start" ? doc.flag : doc.start;
    if (name === other) {
      setStatus("Abby is already on the flag.");
      return;
    }
    if (doc.pickups.some((item) => item.at === name)) {
      setStatus("Clear the item on that dot first.");
      return;
    }
    doc[which] = name;
    commitMap();
  }

  function toggleRidge(spec) {
    const doc = current();
    const parts = spec.split("|");
    if (ground(doc, parts[0]) === "tree" || ground(doc, parts[1]) === "tree") {
      setStatus("A ridge cannot touch a tree.");
      return;
    }
    const index = doc.ridges.findIndex((pair) => pair[0] === parts[0] && pair[1] === parts[1]);
    if (index >= 0) doc.ridges.splice(index, 1);
    else doc.ridges.push(parts);
    commitMap();
  }

  function cellTerrain(id) {
    const entry = abbyTool(id);
    return entry && entry.group === "terrain" && entry.paints === "cell";
  }

  toolsEl.addEventListener("click", (event) => {
    const button = event.target.closest("[data-tool]");
    if (!button) return;
    selectTool(button.dataset.tool);
  });

  board.addEventListener("pointerdown", (event) => {
    const edge = event.target.closest("[data-edge]");
    if (edge) {
      if (tool !== "ridge") return;
      event.preventDefault();
      toggleRidge(edge.dataset.edge);
      return;
    }
    const cell = event.target.closest("[data-cell]");
    if (!cell || !board.contains(cell)) return;
    event.preventDefault();
    const name = cell.dataset.cell;
    if (tool === "ridge") {
      setStatus("Click the side between two dots.");
      return;
    }
    if (cellTerrain(tool)) {
      painting = true;
      paintKind = tool;
      applyTerrain(name, paintKind);
      return;
    }
    if (abbyTool(tool).group === "item") placeItem(name);
    else moveToken(name);
  });

  window.addEventListener("pointermove", (event) => {
    if (!painting) return;
    const el = document.elementFromPoint(event.clientX, event.clientY);
    const cell = el && el.closest ? el.closest("[data-cell]") : null;
    if (!cell || !board.contains(cell)) return;
    applyTerrain(cell.dataset.cell, paintKind);
  });

  window.addEventListener("pointerup", () => {
    painting = false;
  });
  window.addEventListener("pointercancel", () => {
    painting = false;
  });

  levelsEl.addEventListener("click", (event) => {
    const button = event.target.closest("[data-id]");
    if (!button) return;
    library.activeId = button.dataset.id;
    saveLibrary();
    showLevel();
  });

  levelInput.addEventListener("input", () => {
    const n = Number(levelInput.value);
    if (!Number.isInteger(n) || n < 1) return;
    current().level = n;
    saveLibrary();
    renderLibrary();
  });

  nameInput.addEventListener("input", () => {
    current().name = nameInput.value;
    saveLibrary();
    renderLibrary();
  });

  blurbInput.addEventListener("input", () => {
    current().blurb = blurbInput.value;
    saveLibrary();
  });

  document.querySelector("#new").addEventListener("click", () => {
    const doc = blankLevel();
    library.levels.push(doc);
    library.activeId = doc.id;
    saveLibrary();
    showLevel();
    setStatus("Started level " + doc.level + ".");
  });

  document.querySelector("#delete").addEventListener("click", () => {
    const doc = current();
    const label = doc.level + ". " + (doc.name || "Untitled");
    if (!confirm("Delete " + label + "?")) return;
    library.levels = library.levels.filter((level) => level.id !== doc.id);
    if (library.levels.length === 0) library.levels.push(blankLevel());
    library.activeId = library.levels[0].id;
    saveLibrary();
    showLevel();
    setStatus("Deleted " + label + ".");
  });

  document.querySelector("#import").addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files && fileInput.files[0];
    fileInput.value = "";
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      const doc = normalizeDoc(abbyDocFromPaper(data));
      doc.id = crypto.randomUUID();
      doc.answer = null;
      library.levels.push(doc);
      library.activeId = doc.id;
      saveLibrary();
      showLevel();
      setStatus("Imported " + file.name + ".");
    } catch (err) {
      setStatus(err.message || "That file is not a level.");
    }
  });

  document.querySelector("#download").addEventListener("click", () => {
    if (!readyToWrite()) return;
    const name = fileNameFor(current().level);
    const blob = new Blob([paperText(current())], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
    setStatus(saveNote("Downloaded " + name + "."));
  });

  function openDb() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, 1);
      request.onupgradeneeded = () => request.result.createObjectStore(STORE);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function readHandle() {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, "readonly");
      const request = tx.objectStore(STORE).get("directory");
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  async function writeHandle(handle) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, "readwrite");
      tx.objectStore(STORE).put(handle, "directory");
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  async function permit(handle) {
    const opts = { mode: "readwrite" };
    if ((await handle.queryPermission(opts)) === "granted") return true;
    return (await handle.requestPermission(opts)) === "granted";
  }

  function showFolder(handle) {
    folderEl.textContent = "Folder: " + handle.name;
  }

  async function ensureFolder() {
    if (folderHandle && (await permit(folderHandle))) return folderHandle;
    try {
      const stored = await readHandle();
      if (stored && (await permit(stored))) {
        folderHandle = stored;
        return stored;
      }
    } catch (err) {
      // Ask again if the stored handle cannot be read.
    }
    if (!window.showDirectoryPicker) return null;
    const picked = await window.showDirectoryPicker({
      id: "abby-levels",
      mode: "readwrite",
    });
    await writeHandle(picked);
    folderHandle = picked;
    return picked;
  }

  document.querySelector("#save").addEventListener("click", async () => {
    if (!readyToWrite()) return;
    if (!window.showDirectoryPicker) {
      setStatus("This browser cannot write to a folder. Download the JSON instead.");
      return;
    }
    const name = fileNameFor(current().level);
    let dir;
    try {
      dir = await ensureFolder();
    } catch (err) {
      if (err && err.name === "AbortError") return;
      setStatus("The folder could not be opened.");
      return;
    }
    if (!dir) {
      setStatus("This browser cannot write to a folder. Download the JSON instead.");
      return;
    }
    showFolder(dir);
    try {
      let exists = false;
      try {
        await dir.getFileHandle(name);
        exists = true;
      } catch (err) {
        if (!err || err.name !== "NotFoundError") throw err;
      }
      if (exists && !confirm("Replace " + name + " in this folder?")) return;
      const file = await dir.getFileHandle(name, { create: true });
      const writable = await file.createWritable();
      await writable.write(paperText(current()));
      await writable.close();
      setStatus(saveNote("Saved " + name + "."));
    } catch (err) {
      if (err && err.name === "AbortError") return;
      setStatus("Could not write " + name + ".");
    }
  });

  testButton.addEventListener("click", () => {
    testButton.disabled = true;
    testButton.textContent = "Testing…";
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const doc = current();
        let result;
        try {
          result = abbySolve(doc);
        } catch (err) {
          result = { ok: false, message: err.message || "The search failed." };
        }
        doc.answer = result;
        saveLibrary();
        renderBoard();
        renderAnswer();
        testButton.disabled = false;
        testButton.textContent = "Test";
      });
    });
  });

  let resizeTimer = 0;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(renderBoard, 120);
  });

  async function rememberFolder() {
    try {
      const stored = await readHandle();
      if (!stored) return;
      if ((await stored.queryPermission({ mode: "readwrite" })) === "granted") {
        folderHandle = stored;
        showFolder(stored);
      }
    } catch (err) {
      // The page still saves in the browser if the folder cannot be restored.
    }
  }

  renderTools();
  selectTool(tool);
  showLevel();
  rememberFolder();
})();
