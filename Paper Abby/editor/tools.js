// Marks for the level editor.
//
// Add a later item by appending an entry. The grid and the solver read this
// list. icon, when set, is a path to a PNG (for example "../assets/bone.png")
// drawn in place of the built-in mark. scores counts toward the score.
// points is how many; a scoring item with no points is worth one.
// A tennis ball is three. A stick is one.
// grants is energy returned after paying for that dot, still capped at 24.
// unlocks is the terrain that item opens (the vest opens water, the lamp a cave).
// needs, on a terrain, is the item required before the line may enter.
// A kind the print tool does not already allow also has to be added to the
// allow-list in tools/paper_abby.py before that file can be solved there.

(function (root) {
  const TOOLS = [
    { id: "dot", group: "terrain", label: "Dot", paints: "cell" },
    { id: "tree", group: "terrain", label: "Tree", paints: "cell" },
    { id: "ridge", group: "terrain", label: "Ridge", paints: "edge" },
    { id: "water", group: "terrain", label: "Water", paints: "cell", needs: "vest" },
    { id: "cave", group: "terrain", label: "Cave", paints: "cell", needs: "lamp" },

    { id: "stick", group: "item", label: "Stick", scores: true, points: 1 },
    { id: "ball", group: "item", label: "Ball", scores: true, points: 3 },
    { id: "vest", group: "item", label: "Vest", unlocks: "water" },
    { id: "lamp", group: "item", label: "Lamp", unlocks: "cave" },
    { id: "treat", group: "item", label: "Treat", scores: true, grants: 3, points: 1 },

    { id: "abby", group: "place", label: "Abby" },
    { id: "flag", group: "place", label: "Flag" },
  ];

  const byId = new Map(TOOLS.map((tool) => [tool.id, tool]));

  function tool(id) {
    return byId.get(id) || null;
  }

  // Terrain id -> item id required to enter it.
  function gates() {
    const map = new Map();
    for (const entry of TOOLS) {
      if (entry.unlocks) map.set(entry.unlocks, entry.id);
    }
    for (const entry of TOOLS) {
      if (entry.needs) map.set(entry.id, entry.needs);
    }
    return map;
  }

  root.ABBY_TOOLS = TOOLS;
  root.abbyTool = tool;
  root.abbyGates = gates;
})(globalThis);
