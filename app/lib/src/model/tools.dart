// Marks the walk can use. The editor's list is Paper Abby/editor/tools.js.
// A new kind there needs an entry here before a puzzle that uses it will load.

class AbbyTool {
  const AbbyTool({
    required this.id,
    required this.label,
    required this.plural,
    required this.group,
    this.scores = false,
    this.points = 1,
    this.grants = 0,
    this.unlocks,
    this.needs,
  });

  final String id;
  final String label;
  final String plural;
  final String group;
  final bool scores;
  final int points;
  final int grants;
  final String? unlocks;
  final String? needs;
}

const abbyTools = <AbbyTool>[
  AbbyTool(id: 'dot', label: 'Dot', plural: 'dots', group: 'terrain'),
  AbbyTool(id: 'tree', label: 'Tree', plural: 'trees', group: 'terrain'),
  AbbyTool(id: 'ridge', label: 'Ridge', plural: 'ridges', group: 'terrain'),
  AbbyTool(
    id: 'water',
    label: 'Water',
    plural: 'water',
    group: 'terrain',
    needs: 'vest',
  ),
  AbbyTool(
    id: 'cave',
    label: 'Cave',
    plural: 'caves',
    group: 'terrain',
    needs: 'lamp',
  ),
  AbbyTool(
    id: 'stick',
    label: 'Stick',
    plural: 'sticks',
    group: 'item',
    scores: true,
    points: 1,
  ),
  AbbyTool(
    id: 'ball',
    label: 'Ball',
    plural: 'balls',
    group: 'item',
    scores: true,
    points: 3,
  ),
  AbbyTool(
    id: 'vest',
    label: 'Vest',
    plural: 'vests',
    group: 'item',
    unlocks: 'water',
  ),
  AbbyTool(
    id: 'lamp',
    label: 'Lamp',
    plural: 'lamps',
    group: 'item',
    unlocks: 'cave',
  ),
  AbbyTool(
    id: 'treat',
    label: 'Treat',
    plural: 'treats',
    group: 'item',
    scores: true,
    grants: 3,
    points: 1,
  ),
  AbbyTool(id: 'abby', label: 'Abby', plural: 'Abbys', group: 'place'),
  AbbyTool(id: 'flag', label: 'Flag', plural: 'flags', group: 'place'),
];

final Map<String, AbbyTool> _byId = {
  for (final tool in abbyTools) tool.id: tool,
};

AbbyTool? toolById(String id) => _byId[id];

/// Terrain id that requires an item before the line may enter it.
String? gateItem(String terrain) {
  String? need;
  for (final tool in abbyTools) {
    if (tool.unlocks == terrain) need = tool.id;
  }
  for (final tool in abbyTools) {
    if (tool.needs != null && tool.id == terrain) need = tool.needs;
  }
  return need;
}

int pointsFor(String kind) {
  final tool = toolById(kind);
  if (tool == null || !tool.scores) return 0;
  return tool.points;
}

int grantFor(String kind, {required int treatEnergy}) {
  if (kind == 'treat') return treatEnergy;
  return toolById(kind)?.grants ?? 0;
}
